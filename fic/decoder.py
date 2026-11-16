"""
Fractal Decoding and Iterative Reconstruction Engine.
Role: Mahasiswa 3 (Fractal Decoding dan Rekonstruksi).
Implements the Iterated Function System (IFS) iterative attractor convergence
grounded in Banach's Fixed-Point Theorem.
"""

from typing import List, Tuple, Optional, Callable, Dict, Any
import time
import numpy as np

from .encoder import FractalModel
from .transforms import apply_isometry


class FractalDecoder:
    """
    Decodes a FractalModel into a reconstructed image by iteratively
    applying the partitioned affine transformations until attractor convergence.
    """

    def __init__(self, model: FractalModel):
        self.model = model

    def create_initial_canvas(
        self,
        mode: str = "uniform_gray",
        seed: Optional[int] = 42
    ) -> np.ndarray:
        """
        Creates the starting canvas I_0.
        Modes: 'uniform_gray' (128), 'black' (0), 'white' (255), 'random' (uniform noise).
        """
        h, w = self.model.height, self.model.width
        if mode == "uniform_gray":
            return np.full((h, w), 128.0, dtype=np.float32)
        elif mode == "black":
            return np.zeros((h, w), dtype=np.float32)
        elif mode == "white":
            return np.full((h, w), 255.0, dtype=np.float32)
        elif mode == "random":
            rng = np.random.default_rng(seed)
            return rng.uniform(0.0, 255.0, size=(h, w)).astype(np.float32)
        else:
            return np.full((h, w), 128.0, dtype=np.float32)

    def reconstruct(
        self,
        iterations: int = 8,
        initial_mode: str = "uniform_gray",
        custom_initial: Optional[np.ndarray] = None,
        return_history: bool = False,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Runs IFS reconstruction across a specified number of iterations.

        Returns:
            final_image: 2D ndarray of float32 in [0, 255]
            metadata: dict containing 'history', 'deltas', 'decode_time_seconds'
        """
        start_time = time.perf_counter()

        if custom_initial is not None:
            current_canvas = custom_initial.astype(np.float32)
        else:
            current_canvas = self.create_initial_canvas(initial_mode)

        h, w = self.model.height, self.model.width
        r_size = self.model.range_size
        d_size = self.model.domain_size
        scale_factor = d_size // r_size

        history: List[np.ndarray] = [current_canvas.copy()]
        deltas: List[float] = []

        if progress_callback:
            progress_callback(0.0, f"Memulai rekonstruksi IFS (Iterasi 0/{iterations})...")

        for it in range(1, iterations + 1):
            next_canvas = np.zeros_like(current_canvas)

            # Process all affine transformations in the model
            for tf in self.model.transforms:
                # 1. Extract domain block from current_canvas
                d_block = current_canvas[tf.dy : tf.dy + d_size, tf.dx : tf.dx + d_size]

                # 2. Downsample domain block to range block size
                downsampled = d_block.reshape(
                    r_size, scale_factor, r_size, scale_factor
                ).mean(axis=(1, 3))

                # 3. Apply dihedral isometry transformation
                transformed = apply_isometry(downsampled, tf.isometry)

                # 4. Apply intensity affine transformation: s * D + o
                mapped_block = tf.scale * transformed + tf.offset

                # 5. Place into destination range block coordinates
                next_canvas[tf.ry : tf.ry + r_size, tf.rx : tf.rx + r_size] = mapped_block

            # Clip pixel values to valid display range [0, 255]
            next_canvas = np.clip(next_canvas, 0.0, 255.0)

            # Calculate convergence delta: root mean squared difference from previous iteration
            delta = float(np.sqrt(np.mean((next_canvas - current_canvas) ** 2)))
            deltas.append(delta)

            current_canvas = next_canvas
            if return_history:
                history.append(current_canvas.copy())

            if progress_callback:
                frac = it / iterations
                progress_callback(
                    frac,
                    f"Iterasi IFS {it}/{iterations} selesai (Delta: {delta:.3f})."
                )

        decode_time = time.perf_counter() - start_time

        meta = {
            "decode_time_seconds": decode_time,
            "deltas": deltas,
            "iterations": iterations,
            "history": history if return_history else [current_canvas],
        }

        return current_canvas, meta
