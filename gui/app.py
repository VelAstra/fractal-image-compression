"""
Interactive Graphical User Interface (GUI) for Fractal Image Compression.
Role: Rayhan Haldi Hermawan (GUI, Evaluation, & Integration).
Built with Python Tkinter and Pillow.
"""

import os
import threading
import time
from typing import Optional
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from PIL import Image, ImageTk

from fic.preprocessing import load_and_preprocess_image
from fic.encoder import FractalEncoder, FractalModel
from fic.decoder import FractalDecoder
from fic.binary_format import save_fic, load_fic
from fic.evaluation import calculate_psnr, calculate_ssim, calculate_compression_ratio


class FractalCompressionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplikasi Kompresi Citra Berbasis Fraktal (FIC Engine)")
        self.geometry("1100x750")
        self.minsize(950, 650)
        self.configure(bg="#F8FAFC")

        # Application State
        self.current_image_path: Optional[str] = None
        self.original_array: Optional[np.ndarray] = None
        self.current_model: Optional[FractalModel] = None
        self.reconstructed_array: Optional[np.ndarray] = None
        self.cached_original_tk: Optional[ImageTk.PhotoImage] = None
        self.cached_recon_tk: Optional[ImageTk.PhotoImage] = None

        self._init_styles()
        self._build_ui()

        # Load default sample if present
        sample_path = os.path.join(os.path.dirname(__file__), "..", "sample_data", "geometric.png")
        if os.path.exists(sample_path):
            self.load_image(os.path.abspath(sample_path))

    def _init_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Palette: Clean Slate and Deep Teal
        style.configure("TFrame", background="#F8FAFC")
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), background="#0F172A", foreground="#FFFFFF", padding=10)
        style.configure("SubHeader.TLabel", font=("Segoe UI", 10), background="#0F172A", foreground="#94A3B8")
        style.configure("Card.TFrame", background="#FFFFFF", relief="ridge", borderwidth=1)
        style.configure("Param.TLabel", font=("Segoe UI", 9, "bold"), background="#FFFFFF", foreground="#334155")
        style.configure("Value.TLabel", font=("Segoe UI", 9), background="#FFFFFF", foreground="#0F172A")
        style.configure("MetricTitle.TLabel", font=("Segoe UI", 8), background="#F1F5F9", foreground="#64748B")
        style.configure("MetricVal.TLabel", font=("Segoe UI", 12, "bold"), background="#F1F5F9", foreground="#0F766E")

        style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"), background="#0F766E", foreground="#FFFFFF")
        style.map("Primary.TButton", background=[("active", "#115E59")])
        style.configure("Secondary.TButton", font=("Segoe UI", 9), background="#E2E8F0", foreground="#1E293B")
        style.map("Secondary.TButton", background=[("active", "#CBD5E1")])

    def _build_ui(self):
        # 1. Header Banner
        header_frame = tk.Frame(self, bg="#0F172A", height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        lbl_title = tk.Label(
            header_frame,
            text="FRACTAL IMAGE COMPRESSION & RECONSTRUCTION STUDIO",
            font=("Segoe UI", 14, "bold"),
            bg="#0F172A",
            fg="#F8FAFC",
        )
        lbl_title.pack(anchor="w", padx=20, pady=(12, 2))

        lbl_sub = tk.Label(
            header_frame,
            text="Proyek Capstone: Partisi Domain-Range, Transformasi Kontraksi Affine, dan Rekonstruksi IFS",
            font=("Segoe UI", 9),
            bg="#0F172A",
            fg="#94A3B8",
        )
        lbl_sub.pack(anchor="w", padx=20)

        # 2. Main Content Split (Controls on Top, Viewport Center, Metrics Bottom)
        main_container = tk.Frame(self, bg="#F8FAFC", padx=15, pady=10)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Control Strip
        control_card = tk.Frame(main_container, bg="#FFFFFF", relief="groove", bd=1, padx=12, pady=10)
        control_card.pack(fill=tk.X, pady=(0, 10))

        # File actions row
        f_row = tk.Frame(control_card, bg="#FFFFFF")
        f_row.pack(fill=tk.X, pady=(0, 8))

        btn_browse = ttk.Button(f_row, text="Pilih Citra Input...", style="Primary.TButton", command=self.on_browse_image)
        btn_browse.pack(side=tk.LEFT, padx=(0, 6))

        btn_sample = ttk.Button(f_row, text="Gunakan Citra Fraktal", style="Secondary.TButton", command=self.on_load_fractal_sample)
        btn_sample.pack(side=tk.LEFT, padx=(0, 12))

        btn_save_fic = ttk.Button(f_row, text="Simpan .FIC", style="Secondary.TButton", command=self.on_save_fic)
        btn_save_fic.pack(side=tk.LEFT, padx=(0, 6))

        btn_load_fic = ttk.Button(f_row, text="Buka .FIC", style="Secondary.TButton", command=self.on_load_fic)
        btn_load_fic.pack(side=tk.LEFT, padx=(0, 12))

        btn_export = ttk.Button(f_row, text="Ekspor Hasil PNG", style="Secondary.TButton", command=self.on_export_image)
        btn_export.pack(side=tk.LEFT, padx=(0, 6))

        # Parameters row
        p_row = tk.Frame(control_card, bg="#FFFFFF")
        p_row.pack(fill=tk.X)

        tk.Label(p_row, text="Ukuran Range:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.range_var = tk.IntVar(value=8)
        rb4 = ttk.Radiobutton(p_row, text="4x4", variable=self.range_var, value=4)
        rb4.pack(side=tk.LEFT, padx=(0, 4))
        rb8 = ttk.Radiobutton(p_row, text="8x8", variable=self.range_var, value=8)
        rb8.pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(p_row, text="Domain Stride:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.stride_var = tk.IntVar(value=8)
        cb_stride = ttk.Combobox(p_row, textvariable=self.stride_var, values=[4, 8, 16], width=4, state="readonly")
        cb_stride.pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(p_row, text="Iterasi IFS:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.iter_var = tk.IntVar(value=8)
        scale_iter = tk.Scale(p_row, from_=1, to=12, orient=tk.HORIZONTAL, variable=self.iter_var, bg="#FFFFFF", highlightthickness=0, length=90)
        scale_iter.pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(p_row, text="Kanvas Awal:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.init_mode_var = tk.StringVar(value="uniform_gray")
        cb_init = ttk.Combobox(p_row, textvariable=self.init_mode_var, values=["uniform_gray", "black", "white", "random"], width=12, state="readonly")
        cb_init.pack(side=tk.LEFT, padx=(0, 15))

        # Action Buttons
        self.btn_encode = ttk.Button(p_row, text="Kompres (Encode)", style="Primary.TButton", command=self.on_start_encode)
        self.btn_encode.pack(side=tk.RIGHT, padx=4)

        self.btn_decode = ttk.Button(p_row, text="Rekonstruksi (Decode)", style="Primary.TButton", command=self.on_start_decode)
        self.btn_decode.pack(side=tk.RIGHT, padx=4)

        # 3. Viewport (Original Image vs Reconstructed Image)
        views_frame = tk.Frame(main_container, bg="#F8FAFC")
        views_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Left: Original
        self.left_panel = tk.Frame(views_frame, bg="#FFFFFF", relief="groove", bd=1)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        tk.Label(self.left_panel, text="CITRA ASLI (PREPROCESSED GRAYSCALE)", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#334155").pack(pady=6)
        self.canvas_orig = tk.Label(self.left_panel, bg="#F1F5F9", text="Belum ada citra dipilih")
        self.canvas_orig.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Right: Reconstructed
        self.right_panel = tk.Frame(views_frame, bg="#FFFFFF", relief="groove", bd=1)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        tk.Label(self.right_panel, text="CITRA HASIL REKONSTRUKSI FRAKTAL (ATTRACTOR)", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#0F766E").pack(pady=6)
        self.canvas_recon = tk.Label(self.right_panel, bg="#F1F5F9", text="Menunggu proses dekompresi...")
        self.canvas_recon.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # 4. Metrics Dashboard
        metrics_frame = tk.Frame(main_container, bg="#FFFFFF", relief="groove", bd=1, padx=10, pady=8)
        metrics_frame.pack(fill=tk.X)

        self.metric_labels = {}
        metric_configs = [
            ("cr", "Compression Ratio", "-"),
            ("saving", "Space Saving", "-"),
            ("fic_size", "Ukuran .FIC", "-"),
            ("psnr", "PSNR (Fidelity)", "-"),
            ("ssim", "SSIM (Structure)", "-"),
            ("enc_time", "Waktu Encode", "-"),
            ("dec_time", "Waktu Decode", "-"),
        ]

        for idx, (key, title, default_val) in enumerate(metric_configs):
            box = tk.Frame(metrics_frame, bg="#F1F5F9", padx=10, pady=4, relief="flat")
            box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)

            t_lbl = tk.Label(box, text=title, font=("Segoe UI", 8), bg="#F1F5F9", fg="#64748B")
            t_lbl.pack(anchor="w")

            v_lbl = tk.Label(box, text=default_val, font=("Segoe UI", 11, "bold"), bg="#F1F5F9", fg="#0F172A")
            v_lbl.pack(anchor="w")

            self.metric_labels[key] = v_lbl

        # 5. Progress and Status Bar
        status_bar = tk.Frame(self, bg="#E2E8F0", height=28, padx=10)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.lbl_status = tk.Label(status_bar, text="Siap.", font=("Segoe UI", 8), bg="#E2E8F0", fg="#334155")
        self.lbl_status.pack(side=tk.LEFT)

        self.progress_bar = ttk.Progressbar(status_bar, orient=tk.HORIZONTAL, length=200, mode="determinate")
        self.progress_bar.pack(side=tk.RIGHT, pady=3)

    def set_status(self, text: str, progress: float = 0.0):
        self.lbl_status.config(text=text)
        self.progress_bar["value"] = int(progress * 100)
        self.update_idletasks()

    def load_image(self, filepath: str):
        try:
            self.current_image_path = filepath
            # Preprocess to 256x256 for quick interactive demonstration
            arr = load_and_preprocess_image(filepath, target_dim=256, block_multiple=16)
            self.original_array = arr

            # Update display
            pil_img = Image.fromarray(np.uint8(arr)).resize((280, 280), Image.Resampling.NEAREST)
            self.cached_original_tk = ImageTk.PhotoImage(pil_img)
            self.canvas_orig.config(image=self.cached_original_tk, text="")

            raw_bytes = arr.shape[0] * arr.shape[1]
            self.set_status(f"Citra dimuat: {os.path.basename(filepath)} ({arr.shape[1]}x{arr.shape[0]}, {raw_bytes:,} B)")
        except Exception as e:
            messagebox.showerror("Gagal Membaca Citra", str(e))

    def on_browse_image(self):
        f = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff"), ("All Files", "*.*")]
        )
        if f:
            self.load_image(f)

    def on_load_fractal_sample(self):
        sample_path = os.path.join(os.path.dirname(__file__), "..", "sample_data", "sierpinski.png")
        if not os.path.exists(sample_path):
            from sample_data.generate_samples import generate_fractal_sample
            generate_fractal_sample(256, sample_path)
        self.load_image(os.path.abspath(sample_path))

    def on_start_encode(self):
        if self.original_array is None:
            messagebox.showwarning("Peringatan", "Silakan pilih citra input terlebih dahulu.")
            return

        self.btn_encode.config(state="disabled")
        self.btn_decode.config(state="disabled")

        r_size = self.range_var.get()
        stride = self.stride_var.get()

        def worker():
            try:
                encoder = FractalEncoder(range_size=r_size, domain_stride=stride)

                def prog(p, msg):
                    self.after(0, lambda: self.set_status(msg, p))

                t0 = time.perf_counter()
                model = encoder.encode(self.original_array, progress_callback=prog)
                enc_time = time.perf_counter() - t0
                self.current_model = model

                # Save to temporary memory buffer to gauge size
                temp_path = "temp_gui_encoded.fic"
                fic_bytes = save_fic(model, temp_path)
                raw_bytes = self.original_array.shape[0] * self.original_array.shape[1]
                cr, saving = calculate_compression_ratio(raw_bytes, fic_bytes)

                def update_ui():
                    self.metric_labels["cr"].config(text=f"{cr:.2f}x")
                    self.metric_labels["saving"].config(text=f"{saving:.1f}%")
                    self.metric_labels["fic_size"].config(text=f"{fic_bytes:,} B")
                    self.metric_labels["enc_time"].config(text=f"{enc_time:.2f} s")
                    self.set_status(f"Encoding selesai: {len(model.transforms)} blok terkompresi.")
                    self.btn_encode.config(state="normal")
                    self.btn_decode.config(state="normal")
                    # Auto trigger decode
                    self.on_start_decode()

                self.after(0, update_ui)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error Encoding", str(e)))
                self.after(0, lambda: self.btn_encode.config(state="normal"))

        threading.Thread(target=worker, daemon=True).start()

    def on_start_decode(self):
        if self.current_model is None:
            messagebox.showwarning("Peringatan", "Belum ada model fraktal terkompresi. Jalankan Encode terlebih dahulu.")
            return

        self.btn_decode.config(state="disabled")
        iters = self.iter_var.get()
        init_mode = self.init_mode_var.get()

        def worker():
            try:
                decoder = FractalDecoder(self.current_model)

                def prog(p, msg):
                    self.after(0, lambda: self.set_status(msg, p))

                t0 = time.perf_counter()
                recon, meta = decoder.reconstruct(
                    iterations=iters,
                    initial_mode=init_mode,
                    progress_callback=prog,
                )
                dec_time = time.perf_counter() - t0
                self.reconstructed_array = recon

                psnr_val = calculate_psnr(self.original_array, recon) if self.original_array is not None else 0.0
                ssim_val = calculate_ssim(self.original_array, recon) if self.original_array is not None else 0.0

                def update_ui():
                    pil_img = Image.fromarray(np.uint8(recon)).resize((280, 280), Image.Resampling.NEAREST)
                    self.cached_recon_tk = ImageTk.PhotoImage(pil_img)
                    self.canvas_recon.config(image=self.cached_recon_tk, text="")

                    self.metric_labels["dec_time"].config(text=f"{dec_time:.2f} s")
                    self.metric_labels["psnr"].config(text=f"{psnr_val:.2f} dB")
                    self.metric_labels["ssim"].config(text=f"{ssim_val:.4f}")
                    self.set_status(f"Rekonstruksi selesai ({iters} iterasi, delta: {meta['deltas'][-1]:.2f})", 1.0)
                    self.btn_decode.config(state="normal")

                self.after(0, update_ui)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error Decoding", str(e)))
                self.after(0, lambda: self.btn_decode.config(state="normal"))

        threading.Thread(target=worker, daemon=True).start()

    def on_save_fic(self):
        if self.current_model is None:
            messagebox.showwarning("Peringatan", "Belum ada model fraktal untuk disimpan.")
            return
        f = filedialog.asksaveasfilename(defaultextension=".fic", filetypes=[("Fractal Binary", "*.fic")])
        if f:
            b = save_fic(self.current_model, f)
            messagebox.showinfo("Berhasil", f"Model berhasil disimpan ({b:,} bytes).")

    def on_load_fic(self):
        f = filedialog.askopenfilename(filetypes=[("Fractal Binary", "*.fic")])
        if f:
            try:
                model = load_fic(f)
                self.current_model = model
                self.range_var.set(model.range_size)
                self.stride_var.set(model.domain_stride)
                self.metric_labels["fic_size"].config(text=f"{os.path.getsize(f):,} B")
                self.set_status(f"Model .FIC dimuat: {os.path.basename(f)} ({model.width}x{model.height})")
                self.on_start_decode()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membaca .FIC: {e}")

    def on_export_image(self):
        if self.reconstructed_array is None:
            messagebox.showwarning("Peringatan", "Belum ada citra hasil rekonstruksi.")
            return
        f = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg")])
        if f:
            Image.fromarray(np.uint8(self.reconstructed_array)).save(f)
            messagebox.showinfo("Berhasil", f"Citra tersimpan di {f}")


def launch_gui():
    app = FractalCompressionApp()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
