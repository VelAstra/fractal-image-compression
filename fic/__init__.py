"""
Fractal Image Compression (FIC) and Iterative Reconstruction Suite.
Capstone Project - Department of Computer Science / Informatics.
"""

from .preprocessing import load_and_preprocess_image, partition_range_blocks, extract_domain_blocks
from .transforms import get_isometries, apply_isometry
from .encoder import FractalEncoder, FractalModel, BlockTransform
from .decoder import FractalDecoder
from .binary_format import save_fic, load_fic
from .evaluation import calculate_psnr, calculate_ssim, calculate_compression_ratio, run_ablation_study

__all__ = [
    "load_and_preprocess_image",
    "partition_range_blocks",
    "extract_domain_blocks",
    "get_isometries",
    "apply_isometry",
    "FractalEncoder",
    "FractalModel",
    "BlockTransform",
    "FractalDecoder",
    "save_fic",
    "load_fic",
    "calculate_psnr",
    "calculate_ssim",
    "calculate_compression_ratio",
    "run_ablation_study",
]
