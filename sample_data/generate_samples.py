"""
Synthetic Test Image Generator for Fractal Image Compression Benchmarks.
Generates self-similar geometric patterns, textures, and gradient surfaces.
"""

import os
import numpy as np
from PIL import Image, ImageDraw


def generate_geometric_sample(size: int = 256, filepath: str = "sample_data/geometric.png") -> str:
    """Generates an image with overlapping geometric shapes, gradients, and lines."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img = Image.new("L", (size, size), color=240)
    draw = ImageDraw.Draw(img)

    # Concentric circles
    center = size // 2
    for r in range(20, size // 2 - 10, 25):
        draw.ellipse([center - r, center - r, center + r, center + r], outline=60, width=3)

    # Nested rectangles
    draw.rectangle([30, 30, size // 3, size // 3], fill=100, outline=20)
    draw.rectangle([size - 80, size - 80, size - 20, size - 20], fill=180, outline=40)

    # Cross grid
    draw.line([0, center, size, center], fill=40, width=2)
    draw.line([center, 0, center, size], fill=40, width=2)

    img.save(filepath)
    return filepath


def generate_fractal_sample(size: int = 256, filepath: str = "sample_data/sierpinski.png") -> str:
    """Generates a multi-scale Sierpinski-like square carpet fractal pattern."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    arr = np.full((size, size), 255, dtype=np.uint8)

    def draw_carpet(x, y, s):
        if s < 3:
            return
        sub = s // 3
        # Fill center square
        arr[y + sub : y + 2 * sub, x + sub : x + 2 * sub] = 30
        for dx in range(3):
            for dy in range(3):
                if dx == 1 and dy == 1:
                    continue
                draw_carpet(x + dx * sub, y + dy * sub, sub)

    draw_carpet(0, 0, size)
    img = Image.fromarray(arr, mode="L")
    img.save(filepath)
    return filepath


def generate_all_samples():
    p1 = generate_geometric_sample(256, "sample_data/geometric.png")
    p2 = generate_fractal_sample(256, "sample_data/sierpinski.png")
    print(f"Generated samples: {p1}, {p2}")


if __name__ == "__main__":
    generate_all_samples()
