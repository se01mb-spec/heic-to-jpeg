# ARJSOFT HEIC Converter

**A simple, fast and offline Windows app to convert HEIC / HEIF photos to JPEG.**

ARJSOFT HEIC Converter is the first desktop utility in the ARJSOFT software collection. It is designed for straightforward batch conversion without uploading personal photos to an online service.

## Features

- Batch conversion of HEIC and HEIF images
- Add individual photos or scan a folder and its subfolders
- Adjustable JPEG quality (1–100; default: 95)
- Choose a custom output folder
- Preserve EXIF metadata and embedded color profile when available
- Correct image orientation automatically
- Progress indicator and per-file error reporting
- Automatically opens the destination folder when conversion finishes
- High-resolution ARJSOFT branding and a custom Windows application icon
- Built-in About section with a link to the official ARJSOFT website
- Persian and English interface
- Offline conversion; photos remain on your computer

## Windows downloads

Every successful GitHub Actions build publishes an artifact named **ARJSOFT-HEIC-Converter-Windows**. It contains:

- **ARJSOFT-HEIC-Converter-Setup.exe** — guided Windows installer
- **ARJSOFT-HEIC-Converter/** — portable application folder

Open the repository's **Actions** tab, select the latest successful build, and download the artifact.

## Run from source

Requires Python 3.8 on Windows.

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Compatibility

The current build targets 64-bit Windows 10 and Windows 11. Windows 7 is not supported or verified at this stage.

## Product information

- Product: ARJSOFT HEIC Converter
- Publisher: ARJSOFT
- Version: 1.0.0
- Website: https://arjsoft.ir

The application includes an About section with a direct link to the official website.

## License

MIT
