"""
Preprocessing and Image Partitioning Module.
Role: Mahasiswa 1 (Preprocessing dan Pembagian Blok Citra).
Handles grayscale conversion, dimension alignment, range block non-overlapping partitioning,
and domain block sliding extraction with spatial downsampling.
"""

from typing import Tuple, List, Dict, Any
import numpy as np
from PIL import Image


def load_and_preprocess_image(
    filepath: str,
    target_dim: int = None,
    block_multiple: int = 16
) -> np.ndarray:
    """
    Loads an image from disk, converts to grayscale, normalizes to float32 [0.0, 255.0],
    and crops/resizes to ensure dimensions are multiples of block_multiple.
    """
    img = Image.open(filepath).convert("L")

    if target_dim is not None:
        img = img.resize((target_dim, target_dim), Image.Resampling.BILINEAR)

    w, h = img.size
    aligned_w = (w // block_multiple) * block_multiple
    aligned_h = (h // block_multiple) * block_multiple

    if aligned_w == 0 or aligned_h == 0:
        raise ValueError(
            f"Image dimensions ({w}x{h}) too small for block multiple {block_multiple}"
        )

    if aligned_w != w or aligned_h != h:
        left = (w - aligned_w) // 2
        top = (h - aligned_h) // 2
        img = img.crop((left, top, left + aligned_w, top + aligned_h))

    return np.array(img, dtype=np.float32)


def partition_range_blocks(
    image: np.ndarray,
    range_size: int = 8
) -> Tuple[np.ndarray, List[Dict[str, int]]]:
    """
    Partitions the image into non-overlapping Range blocks of size range_size x range_size.

    Returns:
        range_blocks: ndarray of shape (num_ranges, range_size, range_size)
        coordinates: list of dicts with {'rx': x, 'ry': y, 'index': i}
    """
    h, w = image.shape
    if h % range_size != 0 or w % range_size != 0:
        raise ValueError(f"Image shape {h}x{w} is not divisible by range_size {range_size}")

    blocks = []
    coordinates = []
    idx = 0

    for y in range(0, h, range_size):
        for x in range(0, w, range_size):
            block = image[y : y + range_size, x : x + range_size]
            blocks.append(block)
            coordinates.append({"rx": x, "ry": y, "index": idx})
            idx += 1

    return np.array(blocks, dtype=np.float32), coordinates


def extract_domain_blocks(
    image: np.ndarray,
    domain_size: int = 16,
    stride: int = 8
) -> Tuple[np.ndarray, List[Dict[str, int]]]:
    """
    Extracts sliding candidate Domain blocks of size domain_size x domain_size
    sampled across the image with a defined spatial step (stride).

    Returns:
        domain_blocks: ndarray of shape (num_domains, domain_size, domain_size)
        coordinates: list of dicts with {'dx': x, 'dy': y, 'index': i}
    """
    h, w = image.shape
    if domain_size > h or domain_size > w:
        raise ValueError(f"Domain size {domain_size} exceeds image dimensions {h}x{w}")

    blocks = []
    coordinates = []
    idx = 0

    for y in range(0, h - domain_size + 1, stride):
        for x in range(0, w - domain_size + 1, stride):
            block = image[y : y + domain_size, x : x + domain_size]
            blocks.append(block)
            coordinates.append({"dx": x, "dy": y, "index": idx})
            idx += 1

    return np.array(blocks, dtype=np.float32), coordinates


def downsample_domain_blocks(
    domain_blocks: np.ndarray,
    target_size: int
) -> np.ndarray:
    """
    Averages pixel groups to contract domain blocks down to target_size x target_size.
    Ensures spatial contraction (Barnsley & Jacquin Contraction Mapping condition).
    """
    num_blocks, h, w = domain_blocks.shape
    if h % target_size != 0 or w % target_size != 0:
        raise ValueError(f"Domain block size {h}x{w} must be divisible by target {target_size}")

    scale = h // target_size
    # Reshape and average over scale x scale sub-windows
    downsampled = domain_blocks.reshape(
        num_blocks, target_size, scale, target_size, scale
    ).mean(axis=(2, 4))

    return downsampled.astype(np.float32)
