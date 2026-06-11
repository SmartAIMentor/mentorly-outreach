#!/usr/bin/env python3
"""从模板文件渲染触达文案，支持 {{first_name}} 等占位符。"""

from __future__ import annotations

from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def load_template(name: str, **kwargs: str) -> str:
    path = TEMPLATES_DIR / name
    text = path.read_text(encoding="utf-8").strip()
    for key, val in kwargs.items():
        text = text.replace(f"{{{{{key}}}}}", val)
    return text


def render_email_v2(first_name: str) -> tuple[str, str]:
    raw = load_template("EMAIL_en_v2.txt", first_name=first_name)
    lines = raw.splitlines()
    subject = lines[0].replace("Subject:", "").strip()
    body = "\n".join(lines[2:]).strip()
    return subject, body


def render_dm_v2(first_name: str) -> str:
    return load_template("DM_en_v2.txt", first_name=first_name)
