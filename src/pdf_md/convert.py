import re
import shutil
import time
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRefMode

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
IMAGE_LINK_RE = re.compile(r"(!\[[^\]]*\]\()([^)]+)(\))")


def find_pdfs(directory: Path) -> list[Path]:
    return sorted(p for p in directory.iterdir() if p.is_file() and p.suffix.lower() == ".pdf")


def convert_one(pdf_path: Path, out_dir: Path, *, ocr: bool) -> float:
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = ocr
    pipeline_options.images_scale = 2.0
    pipeline_options.generate_picture_images = True

    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )

    start = time.time()
    result = converter.convert(pdf_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / f"{pdf_path.stem}.md"
    result.document.save_as_markdown(md_path, image_mode=ImageRefMode.REFERENCED)
    _organize_images(md_path)
    return time.time() - start


def _organize_images(md_path: Path) -> None:
    out_dir = md_path.parent
    images_dir = out_dir / "images"
    moved_names: set[str] = set()
    for sibling in list(out_dir.iterdir()):
        if sibling == md_path or sibling.is_dir():
            continue
        if sibling.suffix.lower() in IMAGE_SUFFIXES:
            images_dir.mkdir(exist_ok=True)
            shutil.move(str(sibling), str(images_dir / sibling.name))
            moved_names.add(sibling.name)

    if not moved_names:
        return

    text = md_path.read_text(encoding="utf-8")

    def repl(m: re.Match[str]) -> str:
        prefix, target, suffix = m.group(1), m.group(2), m.group(3)
        target_clean = target.strip().lstrip("./")
        if target_clean in moved_names:
            return f"{prefix}images/{target_clean}{suffix}"
        return m.group(0)

    md_path.write_text(IMAGE_LINK_RE.sub(repl, text), encoding="utf-8")
