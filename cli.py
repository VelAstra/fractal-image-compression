"""
Command-Line Interface (CLI) for Fractal Image Compression Suite.
Role: Mahasiswa 4 (Integrasi dan Evaluasi Sistem).
Supports encoding, decoding, ablation benchmarking, and launching the GUI.
"""

import argparse
import sys
import os
import time
import numpy as np
from PIL import Image

from fic.preprocessing import load_and_preprocess_image
from fic.encoder import FractalEncoder
from fic.decoder import FractalDecoder
from fic.binary_format import save_fic, load_fic
from fic.evaluation import (
    calculate_psnr,
    calculate_ssim,
    calculate_compression_ratio,
    run_ablation_study,
)


def cmd_encode(args):
    print(f"[FIC Encoder] Membaca citra: {args.input}")
    img = load_and_preprocess_image(args.input, target_dim=args.size, block_multiple=args.range_size * 2)
    h, w = img.shape
    raw_bytes = h * w
    print(f"Dimensi citra terproses: {w}x{h} (Raw: {raw_bytes:,} bytes)")

    encoder = FractalEncoder(
        range_size=args.range_size,
        domain_scale=args.domain_scale,
        domain_stride=args.stride,
        max_scale=args.max_scale,
    )

    def on_progress(p, msg):
        pct = int(p * 100)
        sys.stdout.write(f"\r[{pct:3d}%] {msg}")
        sys.stdout.flush()

    print(f"Konfigurasi: Range Block = {args.range_size}x{args.range_size}, Domain Step = {args.stride}")
    model = encoder.encode(img, progress_callback=on_progress)
    print()

    out_path = args.output or os.path.splitext(args.input)[0] + ".fic"
    fic_bytes = save_fic(model, out_path)
    cr, saving = calculate_compression_ratio(raw_bytes, fic_bytes)

    print(f"Hasil kompresi tersimpan di: {out_path}")
    print(f"Ukuran File .FIC     : {fic_bytes:,} bytes")
    print(f"Compression Ratio (CR): {cr:.2f}x")
    print(f"Space Saving         : {saving:.2f}%")
    print(f"Waktu Encoding       : {model.encode_time_seconds:.3f} detik")


def cmd_decode(args):
    print(f"[FIC Decoder] Membaca file model fraktal: {args.input}")
    model = load_fic(args.input)
    print(f"Citra target: {model.width}x{model.height}, Range: {model.range_size}x{model.range_size}, Transformasi: {len(model.transforms)}")

    decoder = FractalDecoder(model)

    def on_progress(p, msg):
        pct = int(p * 100)
        sys.stdout.write(f"\r[{pct:3d}%] {msg}")
        sys.stdout.flush()

    recon, meta = decoder.reconstruct(
        iterations=args.iterations,
        initial_mode=args.initial_mode,
        return_history=False,
        progress_callback=on_progress,
    )
    print()

    out_path = args.output or os.path.splitext(args.input)[0] + "_reconstructed.png"
    out_img = Image.fromarray(np.uint8(recon), mode="L")
    out_img.save(out_path)

    print(f"Citra hasil rekonstruksi disimpan di: {out_path}")
    print(f"Waktu Dekompresi     : {meta['decode_time_seconds']:.3f} detik")
    print(f"Jumlah Iterasi       : {args.iterations}")

    if args.compare_with:
        orig = load_and_preprocess_image(args.compare_with, target_dim=model.width)
        psnr_val = calculate_psnr(orig, recon)
        ssim_val = calculate_ssim(orig, recon)
        print(f"PSNR Rekonstruksi    : {psnr_val:.2f} dB")
        print(f"SSIM Rekonstruksi    : {ssim_val:.4f}")


def cmd_evaluate(args):
    print(f"[FIC Evaluator] Menjalankan studi ablasi pada: {args.input}")
    img = load_and_preprocess_image(args.input, target_dim=args.size, block_multiple=16)

    range_sizes = [int(x) for x in args.range_sizes]
    strides = [int(x) for x in args.strides]

    results = run_ablation_study(
        img,
        range_sizes=range_sizes,
        domain_strides=strides,
        iterations=args.iterations,
    )

    print("\n" + "=" * 90)
    print(f"{'Range':<7}{'Stride':<8}{'Blocks':<8}{'FIC (B)':<10}{'CR':<8}{'PSNR(dB)':<10}{'SSIM':<8}{'Enc(s)':<8}{'Dec(s)':<8}")
    print("=" * 90)
    for r in results:
        print(
            f"{r['range_size']:<7}"
            f"{r['domain_stride']:<8}"
            f"{r['num_ranges']:<8}"
            f"{r['fic_bytes']:<10}"
            f"{r['compression_ratio']:<8.2f}"
            f"{r['psnr_db']:<10.2f}"
            f"{r['ssim']:<8.4f}"
            f"{r['encode_time_sec']:<8.3f}"
            f"{r['decode_time_sec']:<8.3f}"
        )
    print("=" * 90 + "\n")


def cmd_demo(args):
    sample_path = "sample_data/geometric.png"
    if not os.path.exists(sample_path):
        from sample_data.generate_samples import generate_geometric_sample
        generate_geometric_sample(256, sample_path)

    print("[FIC Demo] Menjalankan demonstrasi end-to-end pada sample data...")
    fic_path = "sample_data/demo.fic"
    recon_path = "sample_data/demo_recon.png"

    img = load_and_preprocess_image(sample_path)
    raw_bytes = img.shape[0] * img.shape[1]

    # Encode
    encoder = FractalEncoder(range_size=8, domain_stride=8)
    t0 = time.perf_counter()
    model = encoder.encode(img)
    enc_time = time.perf_counter() - t0
    fic_bytes = save_fic(model, fic_path)
    cr, saving = calculate_compression_ratio(raw_bytes, fic_bytes)

    # Decode
    decoder = FractalDecoder(model)
    t0 = time.perf_counter()
    recon, meta = decoder.reconstruct(iterations=8, return_history=True)
    dec_time = time.perf_counter() - t0

    Image.fromarray(np.uint8(recon), mode="L").save(recon_path)

    psnr_val = calculate_psnr(img, recon)
    ssim_val = calculate_ssim(img, recon)

    print("Hasil Demonstrasi Capstone FIC:")
    print(f"- Ukuran Citra Asli       : {img.shape[1]}x{img.shape[0]} ({raw_bytes:,} bytes)")
    print(f"- Ukuran File .FIC        : {fic_bytes:,} bytes")
    print(f"- Compression Ratio (CR)  : {cr:.2f}x (Space saving: {saving:.2f}%)")
    print(f"- PSNR Rekonstruksi       : {psnr_val:.2f} dB")
    print(f"- SSIM Rekonstruksi       : {ssim_val:.4f}")
    print(f"- Waktu Kompresi (Encode) : {enc_time:.3f} s")
    print(f"- Waktu Rekonstruksi      : {dec_time:.3f} s")
    print(f"- Konvergensi Delta (Iter 1 -> 8): {meta['deltas'][0]:.2f} -> {meta['deltas'][-1]:.2f}")


def cmd_gui(args):
    from gui.app import launch_gui
    launch_gui()


def main():
    parser = argparse.ArgumentParser(description="Fractal Image Compression Suite (FIC)")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Encode command
    p_enc = subparsers.add_parser("encode", help="Encode an image to .fic")
    p_enc.add_argument("input", help="Input image file path")
    p_enc.add_argument("-o", "--output", help="Output .fic path")
    p_enc.add_argument("--range-size", type=int, default=8, help="Range block size (default: 8)")
    p_enc.add_argument("--domain-scale", type=int, default=2, help="Domain block scale factor (default: 2)")
    p_enc.add_argument("--stride", type=int, default=8, help="Domain sliding stride (default: 8)")
    p_enc.add_argument("--max-scale", type=float, default=0.95, help="Max affine contrast contractivity")
    p_enc.add_argument("--size", type=int, default=None, help="Resize target dim (optional)")

    # Decode command
    p_dec = subparsers.add_parser("decode", help="Decode a .fic file to reconstructed image")
    p_dec.add_argument("input", help="Input .fic model file")
    p_dec.add_argument("-o", "--output", help="Output reconstructed image file path")
    p_dec.add_argument("--iterations", type=int, default=8, help="Number of IFS reconstruction iterations")
    p_dec.add_argument("--initial-mode", default="uniform_gray", choices=["uniform_gray", "black", "white", "random"])
    p_dec.add_argument("--compare-with", help="Original image file to compute PSNR & SSIM")

    # Evaluate command
    p_eval = subparsers.add_parser("evaluate", help="Run ablation benchmark sweeps")
    p_eval.add_argument("input", help="Input image file")
    p_eval.add_argument("--range-sizes", nargs="+", default=[4, 8], help="Range block sizes to test")
    p_eval.add_argument("--strides", nargs="+", default=[8, 16], help="Domain strides to test")
    p_eval.add_argument("--iterations", type=int, default=8, help="IFS iterations")
    p_eval.add_argument("--size", type=int, default=None, help="Square crop/resize dimension")

    # Demo command
    subparsers.add_parser("demo", help="Run quick synthetic demo")

    # GUI command
    subparsers.add_parser("gui", help="Launch interactive graphical interface")

    args = parser.parse_args()
    if args.command == "encode":
        cmd_encode(args)
    elif args.command == "decode":
        cmd_decode(args)
    elif args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "demo":
        cmd_demo(args)
    elif args.command == "gui":
        cmd_gui(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
