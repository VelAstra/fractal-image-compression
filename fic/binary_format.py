"""
Binary File Format Container (.fic) for Fractal Compressed Images.
Role: Penyimpanan parameter koefisien transformasi terkompresi.
Implements compact bit-packing for true measurable Compression Ratio.
"""

from typing import List
import struct
import numpy as np

from .encoder import FractalModel, BlockTransform

# Magic bytes: 'FIC1' (Fractal Image Compression version 1)
MAGIC_HEADER = b"FIC1"
HEADER_FORMAT = "<4sHHBBBI"  # magic (4s), w (H), h (H), range_size (B), domain_size (B), stride (B), num_transforms (I)
RECORD_FORMAT = "<HHbhB"    # dx (H), dy (H), scale_q (b: int8), offset_q (h: int16), isometry (B: uint8)

HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
RECORD_SIZE = struct.calcsize(RECORD_FORMAT)


def quantize_scale(s: float) -> int:
    """Quantizes contrast factor s in [-1.0, 1.0] to signed int8 in [-127, 127]."""
    clamped = max(-1.0, min(1.0, s))
    return int(round(clamped * 127.0))


def dequantize_scale(s_q: int) -> float:
    """Restores contrast factor s from signed int8."""
    return float(s_q) / 127.0


def quantize_offset(o: float) -> int:
    """
    Quantizes brightness offset o into signed int16 with fixed-point scale factor of 10.
    Supports range [-3276.8, 3276.7] with 0.1 intensity precision, eliminating saturation.
    """
    scaled = round(o * 10.0)
    clamped = max(-32768, min(32767, int(scaled)))
    return clamped


def dequantize_offset(o_q: int) -> float:
    """Restores brightness offset o from signed int16."""
    return float(o_q) / 10.0


def save_fic(model: FractalModel, filepath: str) -> int:
    """
    Serializes a FractalModel into a compact binary .fic file.
    Returns total bytes written.
    """
    num_transforms = len(model.transforms)
    header_bytes = struct.pack(
        HEADER_FORMAT,
        MAGIC_HEADER,
        model.width,
        model.height,
        model.range_size,
        model.domain_size,
        model.domain_stride,
        num_transforms,
    )

    records = bytearray()
    for tf in model.transforms:
        s_q = quantize_scale(tf.scale)
        o_q = quantize_offset(tf.offset)
        iso_q = tf.isometry & 0x07  # 3 bits
        record_bytes = struct.pack(
            RECORD_FORMAT,
            tf.dx,
            tf.dy,
            s_q,
            o_q,
            iso_q,
        )
        records.extend(record_bytes)

    with open(filepath, "wb") as f:
        f.write(header_bytes)
        f.write(records)

    return HEADER_SIZE + len(records)


def load_fic(filepath: str) -> FractalModel:
    """
    Deserializes a binary .fic file into a FractalModel ready for reconstruction.
    """
    with open(filepath, "rb") as f:
        data = f.read()

    if len(data) < HEADER_SIZE:
        raise ValueError(f"Corrupt or invalid .fic file (size {len(data)} < {HEADER_SIZE})")

    magic, w, h, r_size, d_size, stride, num_transforms = struct.unpack_from(
        HEADER_FORMAT, data, 0
    )

    if magic != MAGIC_HEADER:
        raise ValueError(f"Invalid magic bytes in .fic file: {magic}")

    expected_size = HEADER_SIZE + num_transforms * RECORD_SIZE
    if len(data) < expected_size:
        raise ValueError(
            f"Truncated .fic payload: expected {expected_size} bytes, got {len(data)}"
        )

    # Reconstruct range grid positions in deterministic row-major order
    rx_coords = []
    ry_coords = []
    for y in range(0, h, r_size):
        for x in range(0, w, r_size):
            rx_coords.append(x)
            ry_coords.append(y)

    transforms: List[BlockTransform] = []
    offset = HEADER_SIZE

    for i in range(num_transforms):
        dx, dy, s_q, o_q, iso_q = struct.unpack_from(RECORD_FORMAT, data, offset)
        offset += RECORD_SIZE

        rx = rx_coords[i] if i < len(rx_coords) else 0
        ry = ry_coords[i] if i < len(ry_coords) else 0

        scale = dequantize_scale(s_q)
        offset_val = dequantize_offset(o_q)

        transforms.append(
            BlockTransform(
                rx=rx,
                ry=ry,
                dx=dx,
                dy=dy,
                isometry=iso_q,
                scale=scale,
                offset=offset_val,
                mse=0.0,
            )
        )

    return FractalModel(
        width=w,
        height=h,
        range_size=r_size,
        domain_size=d_size,
        domain_stride=stride,
        transforms=transforms,
    )
