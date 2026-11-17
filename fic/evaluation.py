"""
Evaluation Metrics and Ablation Study Module.
Role: Rayhan Haldi Hermawan (GUI, Evaluation, & Integration).
Implements exact mathematical formulations for PSNR, SSIM, Compression Ratio,
and systematic benchmark sweeps.
"""

from typing import Dict, Any, List, Tuple
import math
import time
import numpy as np
from scipy.ndimage import uniform_filter

from .encoder import FractalEncoder
from .decoder import FractalDecoder
from .binary_format import save_fic, HEADER_SIZE, RECORD_SIZE


def calculate_psnr(original: np.ndarray, reconstructed: np.ndarray) -> float:
    """
    Computes Peak Signal-to-Noise Ratio (PSNR) in decibels (dB).
    Higher PSNR indicates superior reconstruction fidelity.
    """
    orig = original.astype(np.float64)
    recon = reconstructed.astype(np.float64)

    mse = np.mean((orig - recon) ** 2)
    if mse < 1e-10:
        return float("inf")

    max_pixel = 255.0
    psnr = 10.0 * math.log10((max_pixel ** 2) / mse)
    return float(psnr)


def calculate_ssim(
    original: np.ndarray,
    reconstructed: np.ndarray,
    window_size: int = 11,
    k1: float = 0.01,
    k2: float = 0.03,
    l_max: float = 255.0
) -> float:
    """
    Computes Mean Structural Similarity Index (SSIM) based on Wang et al. (2004).
    Produces value in [-1.0, 1.0], where 1.0 denotes identical perceptual structure.
    """
    x = original.astype(np.float64)
    y = reconstructed.astype(np.float64)

    c1 = (k1 * l_max) ** 2
    c2 = (k2 * l_max) ** 2

    # Local means using uniform box filtering
    mu_x = uniform_filter(x, size=window_size)
    mu_y = uniform_filter(y, size=window_size)

    mu_x_sq = mu_x ** 2
    mu_y_sq = mu_y ** 2
    mu_xy = mu_x * mu_y

    # Local variances and covariance
    sigma_x_sq = uniform_filter(x ** 2, size=window_size) - mu_x_sq
    sigma_y_sq = uniform_filter(y ** 2, size=window_size) - mu_y_sq
    sigma_xy = uniform_filter(x * y, size=window_size) - mu_xy

    # SSIM formula
    numerator = (2.0 * mu_xy + c1) * (2.0 * sigma_xy + c2)
    denominator = (mu_x_sq + mu_y_sq + c1) * (sigma_x_sq + sigma_y_sq + c2)

    ssim_map = numerator / (denominator + 1e-12)
    return float(np.mean(ssim_map))


def calculate_compression_ratio(
    raw_bytes: int,
    compressed_bytes: int
) -> Tuple[float, float]:
    """
    Returns:
        cr: Compression Ratio (e.g., 9.12 means 9.12 : 1)
        space_saving_pct: Percentage of file size reduced (e.g., 89.04%)
    """
    if compressed_bytes <= 0:
        return 0.0, 0.0

    cr = raw_bytes / float(compressed_bytes)
    space_saving_pct = (1.0 - (float(compressed_bytes) / raw_bytes)) * 100.0
    return float(cr), float(space_saving_pct)


def run_ablation_study(
    image: np.ndarray,
    range_sizes: List[int] = None,
    domain_strides: List[int] = None,
    iterations: int = 8,
    temp_fic_path: str = "temp_eval.fic"
) -> List[Dict[str, Any]]:
    """
    Runs systematic ablation studies across parameter combinations.
    """
    if range_sizes is None:
        range_sizes = [4, 8]
    if domain_strides is None:
        domain_strides = [8, 16]

    h, w = image.shape
    raw_bytes = h * w  # 1 byte per grayscale pixel
    results = []

    for r_size in range_sizes:
        for stride in domain_strides:
            encoder = FractalEncoder(
                range_size=r_size,
                domain_scale=2,
                domain_stride=stride,
            )

            t0_enc = time.perf_counter()
            model = encoder.encode(image)
            enc_time = time.perf_counter() - t0_enc

            # Measure actual file size
            fic_bytes = save_fic(model, temp_fic_path)
            cr, saving = calculate_compression_ratio(raw_bytes, fic_bytes)

            # Reconstruct
            decoder = FractalDecoder(model)
            t0_dec = time.perf_counter()
            recon, meta = decoder.reconstruct(iterations=iterations)
            dec_time = time.perf_counter() - t0_dec

            psnr_val = calculate_psnr(image, recon)
            ssim_val = calculate_ssim(image, recon)

            record = {
                "range_size": r_size,
                "domain_stride": stride,
                "num_ranges": len(model.transforms),
                "fic_bytes": fic_bytes,
                "raw_bytes": raw_bytes,
                "compression_ratio": cr,
                "space_saving_pct": saving,
                "psnr_db": psnr_val,
                "ssim": ssim_val,
                "encode_time_sec": enc_time,
                "decode_time_sec": dec_time,
                "iterations": iterations,
            }
            results.append(record)

    return results
