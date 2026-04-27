# pdf-md

A simple, batch-friendly CLI that converts PDFs to clean Markdown — preserving headings, tables, and figures — using [IBM's Docling](https://docling-project.github.io/docling/) under the hood and [Typer](https://typer.tiangolo.com/) for the command-line interface.

Drop PDFs into `./input/`, run `pdf-md convert`, get one folder per document in `./output/` containing the Markdown file and any extracted images.

## Features

- **Batch or single-file** — process every PDF in `input/`, or just one by name.
- **Structured tables** — Docling emits GFM tables where possible, HTML for complex layouts.
- **Image extraction** — figures are saved as PNGs (at 2× resolution) and referenced from the Markdown.
- **Clean output layout** — each PDF gets its own subfolder: `output/<stem>/<stem>.md` plus `output/<stem>/images/`.
- **Idempotent** — already-converted files are skipped; pass `--force` to overwrite.
- **Optional OCR** — `--ocr` for scanned PDFs (off by default; OCR is slow and pulls extra ML models).
- **Auto hardware acceleration** — Docling picks GPU (CUDA/MPS) when available, CPU otherwise.

## Requirements

- Python **3.11+**
- [`uv`](https://docs.astral.sh/uv/) for dependency management

## Install

Clone and sync:

```bash
git clone https://github.com/K2412/pdf-md.git
cd pdf-md
uv sync
```

To install `pdf-md` as a global command on your `PATH`:

```bash
uv tool install .
```

> The first conversion downloads Docling's layout model (~hundreds of MB). It's cached after that.

## Usage

```bash
# Batch every PDF in ./input/
uv run pdf-md convert

# Convert a single file (basename inside the input dir)
uv run pdf-md convert paper.pdf

# Use different directories
uv run pdf-md convert --input-dir /path/to/pdfs --output-dir /path/to/out

# Enable OCR for scanned PDFs
uv run pdf-md convert --ocr

# Re-run and overwrite existing output
uv run pdf-md convert --force
```

### Output layout

Per converted PDF:

```
output/
└── <stem>/
    ├── <stem>.md
    └── images/
        ├── image_000000_<hash>.png
        └── ...
```

The Markdown links images with relative paths (`./images/...`), so the folder is portable — copy it anywhere and the images still render.

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `FILENAME` (positional) | — | Single PDF basename inside the input dir; omit to batch all |
| `--input-dir` | `./input` | Where to read source PDFs from |
| `--output-dir` | `./output` | Where to write converted Markdown |
| `--ocr` / `--no-ocr` | `--no-ocr` | Toggle OCR (needed for scanned PDFs) |
| `--force` | off | Overwrite existing `.md` outputs |

### Behavior notes

- If `output/<stem>/<stem>.md` already exists and `--force` is not set, that file is **skipped** (logged as `skip (exists)`).
- In batch mode, the run **fails fast**: the first error aborts the whole run with a non-zero exit code.
- The `output/` directory is auto-created if missing. The `input/` directory must exist.

## How it works

`pdf-md` is a thin wrapper around Docling's Python API:

1. Configure `PdfPipelineOptions` with `do_ocr`, `images_scale=2.0`, and `generate_picture_images=True`.
2. Run `DocumentConverter.convert(pdf_path)` to get a structured `DoclingDocument`.
3. Call `document.save_as_markdown(path, image_mode=ImageRefMode.REFERENCED)` to emit Markdown with externally referenced images.
4. Move the emitted PNGs into an `images/` subfolder and rewrite the Markdown links accordingly.

See [`src/pdf_md/convert.py`](./src/pdf_md/convert.py) for the full implementation (~50 lines).

## Project layout

```
pdf-md/
├── pyproject.toml
├── README.md
├── input/        # drop your PDFs here
├── output/       # converted Markdown lands here (gitignored)
└── src/
    └── pdf_md/
        ├── __init__.py
        ├── cli.py       # Typer app + `convert` subcommand
        └── convert.py   # Docling wrapper
```

## Development

Install dev dependencies and lint:

```bash
uv sync --all-groups
uv run ruff check .
uv run ruff format .
```

## Acknowledgements

- [Docling](https://github.com/docling-project/docling) by IBM Research — the heavy lifting (layout detection, table structure, figure extraction).
- [Typer](https://typer.tiangolo.com/) by Sebastián Ramírez — the CLI framework.

## License

MIT — see [LICENSE](./LICENSE).
