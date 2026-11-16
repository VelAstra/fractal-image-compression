"""
Fractal Encoding Engine with Vectorized Domain-Range Matching.
Role: Mahasiswa 2 (Domain-Range Matching dan Fractal Encoding).
Computes optimal affine contraction transformations (contrast s and brightness offset o)
over the 8 dihedral isometries of candidate domain blocks using least-squares optimization.
"""

from dataclasses import dataclass
from typing import List, Callable, Optional, Dict, Any
import time
import numpy as np

from .preprocessing import (
    partition_range_blocks,
    extract_domain_blocks,
    downsample_domain_blocks,
)
from .transforms import generate_all_isometries_batch


@dataclass
class BlockTransform:
    """Stores the optimal fractal affine mapping for a single Range block."""
    rx: int
    ry: int
    dx: int
    dy: int
    isometry: int
    scale: float
    offset: float
    mse: float


@dataclass
class FractalModel:
    """Stores the complete compressed fractal representation of an image."""
    width: int
    height: int
    range_size: int
    domain_size: int
    domain_stride: int
    transforms: List[BlockTransform]
    encode_time_seconds: float = 0.0


class FractalEncoder:
    """
    Encoder implementing Partitioned Iterated Function Systems (PIFS).
    Optimized with vectorized NumPy matrix operations for fast execution.
    """

    def __init__(
        self,
        range_size: int = 8,
        domain_scale: int = 2,
        domain_stride: int = 8,
        max_scale: float = 0.95,
        range_batch_size: int = 256
    ):
        self.range_size = range_size
        self.domain_size = range_size * domain_scale
        self.domain_stride = domain_stride
        self.max_scale = max_scale
        self.range_batch_size = range_batch_size

    def encode(
        self,
        image: np.ndarray,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> FractalModel:
        """
        Encodes a 2D grayscale image into a FractalModel.
        """
        start_time = time.perf_counter()
        h, w = image.shape

        if progress_callback:
            progress_callback(0.05, "Mengekstraksi range dan domain blocks...")

        # 1. Partition range blocks
        range_blocks, range_coords = partition_range_blocks(image, self.range_size)
        num_ranges = len(range_coords)

        # 2. Extract domain blocks
        domain_blocks, domain_coords = extract_domain_blocks(
            image, self.domain_size, self.domain_stride
        )
        num_domains = len(domain_coords)

        if progress_callback:
            progress_callback(0.15, "Menyusutkan domain blocks dan membangkitkan isometri...")

        # 3. Contract domain blocks to range size
        downsampled_domains = downsample_domain_blocks(domain_blocks, self.range_size)

        # 4. Generate all 8 dihedral symmetries for each domain block
        # candidates shape: (num_domains * 8, range_size, range_size)
        candidates_2d = generate_all_isometries_batch(downsampled_domains)
        num_candidates = candidates_2d.shape[0]

        # Flatten blocks to 1D vectors of length P = range_size^2
        p = self.range_size * self.range_size
        candidates_flat = candidates_2d.reshape(num_candidates, p).astype(np.float32)

        # 5. Precompute domain candidate statistics
        # D_bar: (num_candidates, 1)
        d_bar = candidates_flat.mean(axis=1, keepdims=True)
        d_tilde = candidates_flat - d_bar
        # var_d: (num_candidates,) sum of squared deviations
        var_d = np.sum(d_tilde ** 2, axis=1)

        # Mask flat domain blocks to avoid division by zero
        flat_mask = var_d < 1e-5
        var_d_safe = np.where(flat_mask, 1.0, var_d)

        transforms: List[BlockTransform] = []

        if progress_callback:
            progress_callback(0.25, "Melakukan matching domain-range (Least Squares)...")

        # 6. Process Range blocks in batches to optimize cache and vectorization
        ranges_flat = range_blocks.reshape(num_ranges, p).astype(np.float32)

        for batch_start in range(0, num_ranges, self.range_batch_size):
            batch_end = min(batch_start + self.range_batch_size, num_ranges)
            r_batch = ranges_flat[batch_start:batch_end]  # (B, P)
            b_size = r_batch.shape[0]

            r_bar = r_batch.mean(axis=1, keepdims=True)  # (B, 1)
            r_tilde = r_batch - r_bar                    # (B, P)
            var_r = np.sum(r_tilde ** 2, axis=1)         # (B,)

            # Cross-covariance matrix between all candidates and all range blocks in batch
            # Shape: (num_candidates, B)
            cov_mat = np.dot(d_tilde, r_tilde.T)

            # Compute optimal contrast factor s for all pairs
            # Broadcast var_d_safe across columns: (num_candidates, 1)
            s_mat = cov_mat / var_d_safe[:, np.newaxis]
            s_mat = np.clip(s_mat, -self.max_scale, self.max_scale)

            # If domain block is flat, force s = 0
            if np.any(flat_mask):
                s_mat[flat_mask, :] = 0.0

            # Compute Sum of Squared Errors: SSE = s^2 * var_d - 2*s * cov + var_r
            # Shape: (num_candidates, B)
            sse_mat = (
                (s_mat ** 2) * var_d[:, np.newaxis]
                - 2.0 * s_mat * cov_mat
                + var_r[np.newaxis, :]
            )

            # Find best candidate for each range block in batch: index in [0, num_candidates - 1]
            best_candidates = np.argmin(sse_mat, axis=0)  # (B,)

            for i, best_idx in enumerate(best_candidates):
                global_r_idx = batch_start + i
                rc = range_coords[global_r_idx]

                d_idx = best_idx // 8
                iso_idx = best_idx % 8
                dc = domain_coords[d_idx]

                s_val = float(s_mat[best_idx, i])
                # Brightness offset o = r_bar - s * d_bar
                o_val = float(r_bar[i, 0] - s_val * d_bar[best_idx, 0])
                mse_val = float(sse_mat[best_idx, i] / p)

                transforms.append(
                    BlockTransform(
                        rx=rc["rx"],
                        ry=rc["ry"],
                        dx=dc["dx"],
                        dy=dc["dy"],
                        isometry=iso_idx,
                        scale=s_val,
                        offset=o_val,
                        mse=mse_val,
                    )
                )

            if progress_callback:
                frac = 0.25 + 0.70 * (batch_end / num_ranges)
                progress_callback(
                    frac,
                    f"Telah mengkodekan {batch_end}/{num_ranges} range blocks..."
                )

        total_time = time.perf_counter() - start_time

        if progress_callback:
            progress_callback(1.0, f"Selesai dalam {total_time:.2f} detik.")

        return FractalModel(
            width=w,
            height=h,
            range_size=self.range_size,
            domain_size=self.domain_size,
            domain_stride=self.domain_stride,
            transforms=transforms,
            encode_time_seconds=total_time,
        )
