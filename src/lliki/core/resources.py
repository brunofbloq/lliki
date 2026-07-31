from __future__ import annotations

import json
import os
from importlib import resources
from pathlib import Path
from typing import Iterable, Optional

from .models import TemplateFile, TemplatePack


def built_in_template_root():
    return resources.files("lliki").joinpath("templates")


def template_root():
    override = os.environ.get("LLIKI_TEMPLATE_DIR")
    if override:
        path = Path(override).expanduser().resolve()
        if not path.is_dir():
            raise FileNotFoundError(f"LLIKI_TEMPLATE_DIR is not a directory: {path}")
        return path
    return built_in_template_root()


def read_template(relative_path: str, *, built_in: bool = False) -> str:
    root = built_in_template_root() if built_in else template_root()
    item = root.joinpath(*Path(relative_path).parts)
    return item.read_text(encoding="utf-8")


def iter_template_paths(prefix: str) -> Iterable[str]:
    root = template_root().joinpath(*Path(prefix).parts)
    if not root.is_dir():
        return []
    return [str(Path(prefix) / child.name) for child in root.iterdir() if child.is_file()]


def load_template_pack() -> TemplatePack:
    raw = json.loads(read_template("template-pack.json"))
    files = tuple(
        TemplateFile(
            template=item["template"],
            target=item["target"],
            strategy=item["strategy"],
            section_id=item.get("section_id"),
            needs_context=bool(item.get("needs_context", False)),
        )
        for item in raw["files"]
    )
    return TemplatePack(
        schema_version=int(raw["schema_version"]),
        version=str(raw["template_pack_version"]),
        directories=tuple(raw["directories"]),
        files=files,
    )


def export_built_in_templates(destination: Path, force: bool = False) -> None:
    destination = destination.resolve()
    if destination.exists() and any(destination.iterdir()) and not force:
        raise FileExistsError(f"Destination is not empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)

    def copy_tree(src, dst: Path) -> None:
        for child in src.iterdir():
            target = dst / child.name
            if child.is_dir():
                target.mkdir(exist_ok=True)
                copy_tree(child, target)
            else:
                target.write_bytes(child.read_bytes())

    copy_tree(built_in_template_root(), destination)


def validate_template_pack(root: Optional[Path] = None) -> list[str]:
    old = os.environ.get("LLIKI_TEMPLATE_DIR")
    if root is not None:
        os.environ["LLIKI_TEMPLATE_DIR"] = str(root.resolve())
    errors: list[str] = []
    try:
        pack = load_template_pack()
        for item in pack.files:
            try:
                text = read_template(item.template)
            except (FileNotFoundError, OSError):
                errors.append(f"Missing template: {item.template}")
                continue
            if item.strategy == "managed-section" and item.section_id:
                if f"id={item.section_id}" not in text:
                    errors.append(f"Managed template {item.template} lacks section {item.section_id}")
        for prompt_path in iter_template_paths("prompts"):
            text = read_template(prompt_path)
            if not text.startswith("---\n"):
                errors.append(f"Prompt lacks front matter: {prompt_path}")
    finally:
        if root is not None:
            if old is None:
                os.environ.pop("LLIKI_TEMPLATE_DIR", None)
            else:
                os.environ["LLIKI_TEMPLATE_DIR"] = old
    return errors
