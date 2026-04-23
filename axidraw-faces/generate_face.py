"""
Geometric Face Generator for AxiDraw Pen Plotter
Generates random SVG faces using simple geometric shapes.
Each run produces a unique face.

Usage:
    pip install svgwrite
    python generate_face.py            # generates one face
    python generate_face.py --count 5  # generates five faces
"""

import svgwrite
import random
import math
import argparse
import os


def random_polygon(cx, cy, radius, sides, rotation=0):
    """Generate points for a regular polygon."""
    points = []
    for i in range(sides):
        angle = (2 * math.pi * i / sides) + rotation
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        points.append((x, y))
    return points


def draw_eye(dwg, cx, cy, size, style="circle"):
    """Draw an eye with various geometric styles."""
    g = dwg.g()

    if style == "circle":
        g.add(dwg.circle(center=(cx, cy), r=size, fill="none", stroke="black", stroke_width=1.2))
        g.add(dwg.circle(center=(cx, cy), r=size * 0.4, fill="none", stroke="black", stroke_width=1.2))

    elif style == "triangle":
        pts = random_polygon(cx, cy, size, 3, rotation=-math.pi / 2)
        g.add(dwg.polygon(pts, fill="none", stroke="black", stroke_width=1.2))
        g.add(dwg.circle(center=(cx, cy), r=size * 0.3, fill="none", stroke="black", stroke_width=1.2))

    elif style == "square":
        pts = random_polygon(cx, cy, size, 4, rotation=math.pi / 4)
        g.add(dwg.polygon(pts, fill="none", stroke="black", stroke_width=1.2))
        g.add(dwg.circle(center=(cx, cy), r=size * 0.3, fill="none", stroke="black", stroke_width=1.2))

    elif style == "concentric":
        for i in range(3):
            r = size * (1 - i * 0.3)
            g.add(dwg.circle(center=(cx, cy), r=r, fill="none", stroke="black", stroke_width=1.2))

    elif style == "cross":
        g.add(dwg.circle(center=(cx, cy), r=size, fill="none", stroke="black", stroke_width=1.2))
        g.add(dwg.line(start=(cx - size * 0.5, cy), end=(cx + size * 0.5, cy), stroke="black", stroke_width=1.2))
        g.add(dwg.line(start=(cx, cy - size * 0.5), end=(cx, cy + size * 0.5), stroke="black", stroke_width=1.2))

    elif style == "dot":
        g.add(dwg.circle(center=(cx, cy), r=size, fill="none", stroke="black", stroke_width=1.2))
        g.add(dwg.circle(center=(cx, cy), r=2, fill="black", stroke="none"))

    return g


def draw_nose(dwg, cx, cy, size, style="line"):
    """Draw a nose with various geometric styles."""
    g = dwg.g()

    if style == "line":
        g.add(dwg.line(start=(cx, cy - size), end=(cx, cy + size), stroke="black", stroke_width=1.2))

    elif style == "triangle":
        pts = random_polygon(cx, cy, size, 3, rotation=math.pi / 2)
        g.add(dwg.polygon(pts, fill="none", stroke="black", stroke_width=1.2))

    elif style == "circle":
        g.add(dwg.circle(center=(cx, cy), r=size * 0.5, fill="none", stroke="black", stroke_width=1.2))

    elif style == "dots":
        g.add(dwg.circle(center=(cx - size * 0.3, cy + size * 0.3), r=2, fill="black", stroke="none"))
        g.add(dwg.circle(center=(cx + size * 0.3, cy + size * 0.3), r=2, fill="black", stroke="none"))

    elif style == "angle":
        path = dwg.path(d=f"M {cx},{cy - size} L {cx + size * 0.4},{cy + size * 0.5} L {cx},{cy + size * 0.3}",
                        fill="none", stroke="black", stroke_width=1.2)
        g.add(path)

    return g


def draw_mouth(dwg, cx, cy, width, style="arc"):
    """Draw a mouth with various geometric styles."""
    g = dwg.g()

    if style == "arc":
        path = dwg.path(
            d=f"M {cx - width},{cy} Q {cx},{cy + width * 0.8} {cx + width},{cy}",
            fill="none", stroke="black", stroke_width=1.2
        )
        g.add(path)

    elif style == "line":
        g.add(dwg.line(start=(cx - width, cy), end=(cx + width, cy), stroke="black", stroke_width=1.2))

    elif style == "zigzag":
        pts = [(cx - width, cy)]
        segments = random.randint(3, 6)
        for i in range(1, segments):
            x = cx - width + (2 * width * i / segments)
            y = cy + ((-1) ** i) * width * 0.3
            pts.append((x, y))
        pts.append((cx + width, cy))
        g.add(dwg.polyline(pts, fill="none", stroke="black", stroke_width=1.2))

    elif style == "oval":
        g.add(dwg.ellipse(center=(cx, cy), r=(width, width * 0.4), fill="none", stroke="black", stroke_width=1.2))

    elif style == "rectangle":
        g.add(dwg.rect(
            insert=(cx - width, cy - width * 0.2),
            size=(width * 2, width * 0.4),
            fill="none", stroke="black", stroke_width=1.2
        ))

    elif style == "wavy":
        d = f"M {cx - width},{cy} "
        d += f"C {cx - width * 0.5},{cy - width * 0.4} {cx - width * 0.2},{cy + width * 0.4} {cx},{cy} "
        d += f"C {cx + width * 0.2},{cy - width * 0.4} {cx + width * 0.5},{cy + width * 0.4} {cx + width},{cy}"
        g.add(dwg.path(d=d, fill="none", stroke="black", stroke_width=1.2))

    return g


def draw_head(dwg, cx, cy, size, style="circle"):
    """Draw a head outline."""
    g = dwg.g()

    if style == "circle":
        g.add(dwg.circle(center=(cx, cy), r=size, fill="none", stroke="black", stroke_width=1.5))

    elif style == "square":
        s = size * 1.6
        g.add(dwg.rect(insert=(cx - s / 2, cy - s / 2), size=(s, s),
                        rx=size * 0.1, ry=size * 0.1,
                        fill="none", stroke="black", stroke_width=1.5))

    elif style == "pentagon":
        pts = random_polygon(cx, cy, size, 5, rotation=-math.pi / 2)
        g.add(dwg.polygon(pts, fill="none", stroke="black", stroke_width=1.5))

    elif style == "hexagon":
        pts = random_polygon(cx, cy, size, 6, rotation=0)
        g.add(dwg.polygon(pts, fill="none", stroke="black", stroke_width=1.5))

    elif style == "oval":
        g.add(dwg.ellipse(center=(cx, cy), r=(size * 0.85, size), fill="none", stroke="black", stroke_width=1.5))

    return g


def add_decoration(dwg, cx, cy, head_size):
    """Optionally add decorative elements like hair, hat lines, etc."""
    g = dwg.g()
    deco = random.choice(["none", "none", "lines_top", "dots", "spikes", "hat"])

    if deco == "lines_top":
        for i in range(random.randint(3, 7)):
            x = cx + random.uniform(-head_size * 0.6, head_size * 0.6)
            y_start = cy - head_size
            y_end = y_start - random.uniform(head_size * 0.2, head_size * 0.6)
            g.add(dwg.line(start=(x, y_start), end=(x + random.uniform(-10, 10), y_end),
                           stroke="black", stroke_width=1.2))

    elif deco == "dots":
        for _ in range(random.randint(3, 8)):
            angle = random.uniform(0, 2 * math.pi)
            dist = head_size * random.uniform(1.1, 1.4)
            x = cx + dist * math.cos(angle)
            y = cy + dist * math.sin(angle)
            g.add(dwg.circle(center=(x, y), r=random.uniform(1.5, 3), fill="black", stroke="none"))

    elif deco == "spikes":
        n = random.randint(5, 10)
        for i in range(n):
            angle = -math.pi * 0.1 + (math.pi * 1.2 * i / (n - 1))
            angle = angle - math.pi / 2
            x1 = cx + head_size * math.cos(angle)
            y1 = cy + head_size * math.sin(angle)
            length = random.uniform(head_size * 0.15, head_size * 0.4)
            x2 = cx + (head_size + length) * math.cos(angle)
            y2 = cy + (head_size + length) * math.sin(angle)
            g.add(dwg.line(start=(x1, y1), end=(x2, y2), stroke="black", stroke_width=1.2))

    elif deco == "hat":
        hat_w = head_size * 1.2
        hat_h = head_size * 0.5
        hat_y = cy - head_size - hat_h * 0.3
        g.add(dwg.rect(insert=(cx - hat_w / 2, hat_y), size=(hat_w, hat_h),
                        fill="none", stroke="black", stroke_width=1.2))
        brim_w = head_size * 1.6
        g.add(dwg.line(start=(cx - brim_w / 2, hat_y + hat_h),
                        end=(cx + brim_w / 2, hat_y + hat_h),
                        stroke="black", stroke_width=1.5))

    return g


def generate_face(filename="face.svg", width=200, height=200, seed=None):
    """Generate a single random geometric face SVG."""
    if seed is not None:
        random.seed(seed)

    dwg = svgwrite.Drawing(filename, size=(f"{width}mm", f"{height}mm"),
                           viewBox=f"0 0 {width} {height}")

    cx, cy = width / 2, height / 2
    head_size = min(width, height) * 0.35

    # Head
    head_style = random.choice(["circle", "square", "pentagon", "hexagon", "oval"])
    dwg.add(draw_head(dwg, cx, cy, head_size, head_style))

    # Eyes
    eye_style = random.choice(["circle", "triangle", "square", "concentric", "cross", "dot"])
    eye_spacing = head_size * random.uniform(0.45, 0.6)
    eye_y = cy - head_size * random.uniform(0.15, 0.3)
    eye_size = head_size * random.uniform(0.12, 0.22)

    dwg.add(draw_eye(dwg, cx - eye_spacing, eye_y, eye_size, eye_style))
    dwg.add(draw_eye(dwg, cx + eye_spacing, eye_y, eye_size, eye_style))

    # Eyebrows (sometimes)
    if random.random() > 0.4:
        brow_y = eye_y - eye_size * 1.8
        brow_w = eye_size * 1.2
        for bx in [cx - eye_spacing, cx + eye_spacing]:
            angle = random.uniform(-0.2, 0.2)
            x1 = bx - brow_w * math.cos(angle)
            y1 = brow_y - brow_w * math.sin(angle)
            x2 = bx + brow_w * math.cos(angle)
            y2 = brow_y + brow_w * math.sin(angle)
            dwg.add(dwg.line(start=(x1, y1), end=(x2, y2), stroke="black", stroke_width=1.2))

    # Nose
    nose_style = random.choice(["line", "triangle", "circle", "dots", "angle"])
    nose_size = head_size * random.uniform(0.12, 0.2)
    dwg.add(draw_nose(dwg, cx, cy + head_size * 0.05, nose_size, nose_style))

    # Mouth
    mouth_style = random.choice(["arc", "line", "zigzag", "oval", "rectangle", "wavy"])
    mouth_width = head_size * random.uniform(0.25, 0.45)
    mouth_y = cy + head_size * random.uniform(0.35, 0.5)
    dwg.add(draw_mouth(dwg, cx, mouth_y, mouth_width, mouth_style))

    # Decoration
    dwg.add(add_decoration(dwg, cx, cy, head_size))

    dwg.save()
    return filename


def main():
    parser = argparse.ArgumentParser(description="Generate geometric faces for AxiDraw pen plotter")
    parser.add_argument("--count", type=int, default=1, help="Number of faces to generate")
    parser.add_argument("--size", type=int, default=200, help="Canvas size in mm (default: 200)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--output", type=str, default=".", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    for i in range(args.count):
        seed = args.seed + i if args.seed is not None else None
        if args.count == 1:
            fname = os.path.join(args.output, "face.svg")
        else:
            fname = os.path.join(args.output, f"face_{i + 1:03d}.svg")

        generate_face(fname, width=args.size, height=args.size, seed=seed)
        print(f"Generated: {fname}")


if __name__ == "__main__":
    main()
