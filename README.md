# plymouth-earth-dots

A minimal [Plymouth](https://gitlab.freedesktop.org/plymouth/plymouth) boot splash for Ubuntu: a dot-matrix earth spinning slowly in the middle of a black screen. There's no vendor logo and no spinner. Any text, such as a disk-encryption password prompt, is set in [Inter](https://rsms.me/inter/).

![Preview: the dot-matrix earth (right) next to an unused solid variant (left)](earth-preview.gif)

*The preview shows two styles; the theme uses the dot-matrix one on the right.*

- 180 pre-rendered frames at 240 × 240 px (about 4 MB), one full turn every 18 s, with a cross-fade between frames so the spin stays smooth
- Earth tilted 23.4° and seen from slightly above the equator, turning west to east
- Continent outlines are hand-drawn and coarse on purpose; no map data is downloaded

Built and tested on Ubuntu 26.10 (Plymouth 24.004, dracut), 3440 × 1440.

## Install

Needs Plymouth's `script` plugin (part of the `plymouth` package) and, for text, the Inter font (`fonts-inter`).

```bash
git clone https://github.com/tobcro/plymouth-earth-dots.git
cd plymouth-earth-dots
./theme/install.sh
```

`install.sh` asks for sudo. It:

1. saves your current theme setting to `/etc/plymouth/default-theme.backup` (only the first time)
2. copies the theme to `/usr/share/plymouth/themes/earth-dots/`
3. registers it with `update-alternatives` and selects it
4. rebuilds the initramfs with `update-initramfs -u`

## Try it without rebooting

```bash
./theme/test.sh
```

It switches to text console 3 by itself, shows the splash for about 20 s (with a test message and a password prompt: type anything and press Enter), switches back to your desktop, and prints any theme errors.

## Go back to the stock splash

```bash
./theme/revert.sh
```

This removes the theme, lets Ubuntu pick its default again (`bgrt` with the vendor logo), and rebuilds the initramfs. Without this repo:

```bash
sudo update-alternatives --auto default.plymouth && sudo update-initramfs -u
```

## Customize

- **Speed:** `TICKS` in [`theme/earth-dots/earth-dots.script`](theme/earth-dots/earth-dots.script). Seconds per turn = 180 × `TICKS` / 50.
- **Size, frame count, dot spacing:** regenerate the frames with Python 3 and Pillow (`python3-pil`), then run `install.sh` again:
  ```bash
  python3 earth/build_frames.py 280 180   # size in px, number of frames
  ```
  Dot spacing (`step`), tilt and viewing angle are at the top of [`earth/render.py`](earth/render.py). The coastlines are in [`earth/geo.py`](earth/geo.py). If you change the frame count, update `FRAMES` in the script too.
- **Font:** `FONT` in the script (a Pango font name) and `Font=` in [`earth-dots.plymouth`](theme/earth-dots/earth-dots.plymouth). `Font=` is only there so that `plymouth-populate-initrd` copies the font into the initramfs.

## Things worth knowing

- **`Font=` must be a bare family name.** With `Font=Inter 13`, fontconfig reads "Inter 13" as the family name, matches Noto Sans instead, and Inter never reaches the initramfs. `Font=Inter` works.
- **Testing `plymouthd` from a desktop terminal picks the wrong GPU on multi-GPU machines.** When `DISPLAY` is set, plymouthd turns off udev and falls back to `/dev/dri/card0`, which may have no monitor connected (it reports "no pixel displays"). `test.sh` unsets `DISPLAY` for this reason. A real boot isn't affected.
- Recent Ubuntu builds the initramfs with dracut. `update-initramfs` is now a wrapper around it, and Plymouth's `plymouth-populate-initrd` copies the whole theme folder.

## License

MIT
