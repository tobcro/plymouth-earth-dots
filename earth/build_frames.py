#!/usr/bin/env python3
"""Rebuild the theme's animation frames (theme/earth-dots/earth-NNNN.png).

Usage: python3 earth/build_frames.py [size_px] [frames]
Defaults: 240 px, 180 frames (2 degrees of rotation per frame).
If you change the frame count, update FRAMES in theme/earth-dots/earth-dots.script.
"""
import os, sys, tempfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render

size = int(sys.argv[1]) if len(sys.argv) > 1 else 240
frames = int(sys.argv[2]) if len(sys.argv) > 2 else 180
out = os.path.join(HERE, "..", "theme", "earth-dots")

with tempfile.TemporaryDirectory() as tmp:
    render.render_dots(size, frames, tmp)
    for old in os.listdir(out):
        if old.startswith("earth-0") and old.endswith(".png"):
            os.remove(os.path.join(out, old))
    for i in range(1, frames + 1):
        name = f"earth-{i:04d}.png"
        frame = Image.open(os.path.join(tmp, name))
        # Flatten onto black and store as a 32-colour palette PNG: much smaller
        # than RGBA, and the splash background is black anyway.
        bg = Image.new("RGBA", frame.size, (0, 0, 0, 255))
        bg.alpha_composite(frame)
        bg.convert("L").quantize(32).save(os.path.join(out, name), optimize=True)
print(f"Wrote {frames} frames of {size}x{size} px to {os.path.normpath(out)}")
