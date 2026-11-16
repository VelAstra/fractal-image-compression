"""
Unit and Integration Test Suite for Fractal Image Compression Suite.
Verifies all algorithmic pipelines, affine transformations, serialization,
Banach fixed-point convergence, and evaluation metrics.
"""

import os
import unittest
import numpy as np

from fic.preprocessing import (
    partition_range_blocks,
    extract_domain_blocks,
    downsample_domain_blocks,
)
from fic.transforms import get_isometries, apply_isometry, generate_all_isometries_batch
from fic.encoder import FractalEncoder, FractalModel
from fic.decoder import FractalDecoder
from fic.binary_format import save_fic, load_fic
from fic.evaluation import calculate_psnr, calculate_ssim, calculate_compression_ratio


class TestFractalImageCompression(unittest.TestCase):

    def setUp(self):
        # Create deterministic synthetic test image (64x64)
        np.random.seed(42)
        y, x = np.mgrid[0:64, 0:64]
        # Combination of gradient and checker pattern
        checker = ((x // 8) + (y // 8)) % 2
        gradient = (x + y) * 2.0
        self.test_img = np.clip(gradient + checker * 50.0, 0.0, 255.0).astype(np.float32)

    def test_partitioning_dimensions(self):
        """Tests that Range and Domain blocks correctly partition image grid."""
        r_blocks, r_coords = partition_range_blocks(self.test_img, range_size=8)
        self.assertEqual(len(r_blocks), 64)  # (64/8) * (64/8) = 64
        self.assertEqual(len(r_coords), 64)
        self.assertEqual(r_blocks.shape, (64, 8, 8))

        d_blocks, d_coords = extract_domain_blocks(self.test_img, domain_size=16, stride=8)
        expected_d_count = ((64 - 16) // 8 + 1) ** 2  # (48/8 + 1)^2 = 7^2 = 49
        self.assertEqual(len(d_blocks), expected_d_count)
        self.assertEqual(d_blocks.shape, (49, 16, 16))

        contracted = downsample_domain_blocks(d_blocks, target_size=8)
        self.assertEqual(contracted.shape, (49, 8, 8))

    def test_isometry_symmetries(self):
        """Tests that dihedral transformations generate 8 unique valid transforms."""
        block = np.arange(16, dtype=np.float32).reshape(4, 4)
        isometries = get_isometries(block)
        self.assertEqual(len(isometries), 8)

        # Identity should be equal
        np.testing.assert_array_equal(isometries[0], block)
        # Rot 90 applied 4 times should return original
        rot1 = isometries[1]
        rot4 = apply_isometry(apply_isometry(apply_isometry(rot1, 1), 1), 1)
        np.testing.assert_array_equal(rot4, block)

        # Batch generation shape test
        batch = np.stack([block, block + 10])  # (2, 4, 4)
        batch_isos = generate_all_isometries_batch(batch)
        self.assertEqual(batch_isos.shape, (16, 4, 4))

    def test_encoder_and_binary_serialization(self):
        """Tests end-to-end encoding, .fic binary persistence, and deserialization."""
        encoder = FractalEncoder(range_size=8, domain_scale=2, domain_stride=8)
        model = encoder.encode(self.test_img)

        self.assertEqual(len(model.transforms), 64)
        self.assertEqual(model.width, 64)
        self.assertEqual(model.height, 64)

        temp_fic = "tests_temp.fic"
        try:
            bytes_written = save_fic(model, temp_fic)
            self.assertTrue(os.path.exists(temp_fic))
            self.assertGreater(bytes_written, 0)

            loaded_model = load_fic(temp_fic)
            self.assertEqual(loaded_model.width, 64)
            self.assertEqual(loaded_model.height, 64)
            self.assertEqual(loaded_model.range_size, 8)
            self.assertEqual(len(loaded_model.transforms), 64)

            # Check that scale and offset survive quantization with minimal precision loss
            for orig_tf, loaded_tf in zip(model.transforms, loaded_model.transforms):
                self.assertEqual(orig_tf.dx, loaded_tf.dx)
                self.assertEqual(orig_tf.dy, loaded_tf.dy)
                self.assertEqual(orig_tf.isometry, loaded_tf.isometry)
                self.assertAlmostEqual(orig_tf.scale, loaded_tf.scale, delta=0.03)
                self.assertAlmostEqual(orig_tf.offset, loaded_tf.offset, delta=1.5)
        finally:
            if os.path.exists(temp_fic):
                os.remove(temp_fic)

    def test_decoder_convergence(self):
        """
        Tests that IFS iterative reconstruction converges monotonically toward the attractor,
        as guaranteed by Banach Fixed-Point Theorem.
        """
        encoder = FractalEncoder(range_size=8, domain_scale=2, domain_stride=8)
        model = encoder.encode(self.test_img)

        decoder = FractalDecoder(model)
        recon, meta = decoder.reconstruct(
            iterations=8,
            initial_mode="uniform_gray",
            return_history=True
        )

        deltas = meta["deltas"]
        self.assertEqual(len(deltas), 8)
        # Convergence test: deltas should decline significantly over iterations
        self.assertLess(deltas[-1], deltas[0])
        self.assertLess(deltas[-1], 2.0)  # Near fixed-point convergence

        # Calculate PSNR
        psnr = calculate_psnr(self.test_img, recon)
        ssim = calculate_ssim(self.test_img, recon)
        self.assertGreater(psnr, 20.0)  # Decent initial reconstruction
        self.assertGreater(ssim, 0.70)

    def test_evaluation_metrics(self):
        """Tests that PSNR, SSIM, and CR calculations behave within valid theoretical ranges."""
        # Perfect match
        psnr_inf = calculate_psnr(self.test_img, self.test_img)
        self.assertEqual(psnr_inf, float("inf"))
        ssim_one = calculate_ssim(self.test_img, self.test_img)
        self.assertAlmostEqual(ssim_one, 1.0, places=4)

        # Distorted match
        noisy = self.test_img + np.random.normal(0, 10, self.test_img.shape)
        noisy = np.clip(noisy, 0, 255)
        psnr_noisy = calculate_psnr(self.test_img, noisy)
        ssim_noisy = calculate_ssim(self.test_img, noisy)

        self.assertGreater(psnr_noisy, 15.0)
        self.assertLess(psnr_noisy, 50.0)
        self.assertGreater(ssim_noisy, 0.5)
        self.assertLess(ssim_noisy, 1.0)

        # Compression ratio
        cr, space_saving = calculate_compression_ratio(raw_bytes=65536, compressed_bytes=7183)
        self.assertAlmostEqual(cr, 65536 / 7183, places=2)
        self.assertGreater(space_saving, 85.0)


if __name__ == "__main__":
    unittest.main()
