# ARJSOFT HEIC to JPEG

A lightweight, offline Windows desktop application for converting HEIC/HEIF photos to JPEG.

## Features
- Convert multiple HEIC/HEIF images at once
- Add individual files or scan folders
- Adjustable JPEG quality
- Choose an output folder
- Preserve EXIF metadata when available
- Apply EXIF orientation automatically
- Progress indicator and per-file error reporting
- English / Persian interface
- No internet connection required during conversion

## Run locally
The initial build uses a legacy-compatible Python dependency set.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Build
GitHub Actions builds a Windows executable when code is pushed to `main`. Download the `HEIC-to-JPEG-Windows` artifact from the Actions run.

## Compatibility
The project targets Windows 10/11. Windows 7 compatibility is not yet verified and requires testing on a Windows 7 machine.

## License
MIT
