from pathlib import Path

import typer

from .convert import convert_one, find_pdfs

# cli.py(0) → pdf_md(1) → src(2) → pdf-md(3) → tools(4) → Learning(5? — workspace)
WORKSPACE = Path(__file__).resolve().parents[4]
DEFAULT_INPUT = WORKSPACE / "input"
DEFAULT_OUTPUT = WORKSPACE / "input"

app = typer.Typer(no_args_is_help=True, add_completion=False, help="Convert PDFs to Markdown.")


@app.callback()
def _main() -> None:
    """pdf-md: PDF to Markdown via Docling."""


@app.command()
def convert(
    filename: str | None = typer.Argument(
        None, help="PDF basename inside input dir; omit to batch all"
    ),
    input_dir: Path = typer.Option(DEFAULT_INPUT, "--input-dir", help="Directory holding PDFs"),
    output_dir: Path = typer.Option(DEFAULT_OUTPUT, "--output-dir", help="Output directory"),
    ocr: bool = typer.Option(False, "--ocr/--no-ocr", help="Enable Docling OCR"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing output"),
) -> None:
    if not input_dir.is_dir():
        typer.echo(f"input dir missing: {input_dir}", err=True)
        raise typer.Exit(2)
    output_dir.mkdir(parents=True, exist_ok=True)

    if filename:
        target = input_dir / filename
        if not target.is_file():
            typer.echo(f"file not found: {target}", err=True)
            raise typer.Exit(2)
        pdfs = [target]
    else:
        pdfs = find_pdfs(input_dir)

    if not pdfs:
        typer.echo("no pdfs found")
        raise typer.Exit(1)

    total = len(pdfs)
    for i, pdf in enumerate(pdfs, 1):
        out_sub = output_dir / pdf.stem
        out_md = out_sub / f"{pdf.stem}.md"
        if out_md.exists() and not force:
            typer.echo(f"[{i}/{total}] {pdf.name} ... skip (exists)")
            continue
        typer.echo(f"[{i}/{total}] {pdf.name} ...", nl=False)
        try:
            elapsed = convert_one(pdf, out_sub, ocr=ocr)
        except Exception as e:
            typer.echo(f" failed: {e}", err=True)
            raise typer.Exit(1) from e
        typer.echo(f" done ({elapsed:.1f}s)")
