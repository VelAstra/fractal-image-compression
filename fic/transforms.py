"""
Geometric Isometry Transformations for Fractal Image Compression.
Defines the 8 affine symmetries of the dihedral group D4 for square image blocks.
"""

from typing import List
import numpy as np


def apply_isometry(block: np.ndarray, isometry_index: int) -> np.ndarray:
    """
    Applies one of 8 dihedral symmetry operations to a 2D block.

    0: Identity
    1: Rotate 90 degrees clockwise
    2: Rotate 180 degrees clockwise
    3: Rotate 270 degrees clockwise
    4: Horizontal reflection (flip left-right)
    5: Vertical reflection (flip up-down)
    6: Transpose (reflection across main diagonal)
    7: Anti-transpose (reflection across secondary diagonal)
    """
    idx = isometry_index % 8
    if idx == 0:
        return block
    elif idx == 1:
        return np.rot90(block, -1)
    elif idx == 2:
        return np.rot90(block, -2)
    elif idx == 3:
        return np.rot90(block, -3)
    elif idx == 4:
        return np.fliplr(block)
    elif idx == 5:
        return np.flipud(block)
    elif idx == 6:
        return block.T
    elif idx == 7:
        return np.fliplr(np.flipud(block.T))
    return block


def get_isometries(block: np.ndarray) -> List[np.ndarray]:
    """Generates all 8 dihedral transformations for a single 2D block."""
    return [apply_isometry(block, i) for i in range(8)]


def generate_all_isometries_batch(blocks: np.ndarray) -> np.ndarray:
    """
    Applies all 8 dihedral symmetries to a batch of blocks of shape (K, B, B).
    Returns an array of shape (8 * K, B, B).
    """
    k, b, _ = blocks.shape
    candidates = np.empty((8, k, b, b), dtype=blocks.dtype)

    candidates[0] = blocks                                     # Identity
    candidates[1] = np.rot90(blocks, -1, axes=(1, 2))          # Rot 90 CW
    candidates[2] = np.rot90(blocks, -2, axes=(1, 2))          # Rot 180 CW
    candidates[3] = np.rot90(blocks, -3, axes=(1, 2))          # Rot 270 CW
    candidates[4] = np.flip(blocks, axis=2)                    # Flip Horizontal
    candidates[5] = np.flip(blocks, axis=1)                    # Flip Vertical
    candidates[6] = np.transpose(blocks, (0, 2, 1))            # Transpose
    candidates[7] = np.flip(np.flip(np.transpose(blocks, (0, 2, 1)), axis=1), axis=2)  # Anti-transpose

    # Reshape to (8 * K, B, B) where candidate i has block index (i // 8) and isometry (i % 8)
    # Order: [b0_iso0, b0_iso1, ..., b0_iso7, b1_iso0, ...]
    interleaved = np.transpose(candidates, (1, 0, 2, 3)).reshape(8 * k, b, b)
    return interleaved
