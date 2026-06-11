#!/usr/bin/env python3
"""从 creators_tiktok.csv 批量生成冷邮件（无需 TikHub，用表内粉丝/互动率）。"""

from __future__ import annotations

import argparse
import csv
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from template_render import render_email_v2

ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT / "creators_tiktok.csv"
DEFAULT_OUT = ROOT / "output"
FORM_URL = os.environ.get(
    "MENTORLY_BETA_FORM_URL", "https://tally.so/r/Bz05RK"
)


def load_dotenv() -> None:
    for path in (ROOT / ".env", ROOT.parent.parent / ".env.local"):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


@dataclass
class Row:
    name: str
    handle: str
    email: str
    tiktok_url: str
    niche: str
    followers: int
    engagement_rate_pct: float | None
    hook: str
    email_subject: str
    email_body: str
    status: str = "待触达"


def first_name(name: str, handle: str) -> str:
    for part in name.replace("|", " ").split():
        word = "".join(c for c in part if c.isalpha())
        if len(word) >= 2:
            return word.capitalize()
    return handle.lstrip("@").split(".")[0].capitalize() or "there"


def build_hook(followers: int, eng: float | None, niche: str) -> str:
    niche_label = niche or "your niche"
    if followers and eng is not None and eng > 20:
        return (
            f"At ~{followers:,} TikTok followers with strong engagement in {niche_label}, "
            f"your account stands out for brand deals."
        )
    if followers and eng is not None:
        bench = 5.0
        comp = "above" if eng >= bench else "below"
        return (
            f"Your TikTok (~{followers:,} followers) shows ~{eng}% engagement — "
            f"that's {comp} typical for {niche_label} creators we've analyzed."
        )
    if followers:
        return (
            f"At ~{followers:,} TikTok followers in {niche_label}, "
            f"you're in the range where pricing and brand-fit matter most."
        )
    return f"Your TikTok in {niche_label} caught our attention from public stats."


def render_email(first: str, hook: str, form_url: str, tiktok_url: str) -> tuple[str, str]:
    return render_email_v2(first)


def parse_row(r: dict[str, str], form_url: str) -> Row | None:
    email = (r.get("email") or "").strip()
    url = (r.get("handle_or_url") or "").strip()
    if not email or "@" not in email:
        return None
    handle = url.split("@")[-1].rstrip("/") if "@" in url else url
    name = (r.get("name") or handle).strip()
    niche = (r.get("niche") or "creator").strip()
    try:
        followers = int(float(r.get("followers") or 0))
    except (TypeError, ValueError):
        followers = 0
    eng_raw = r.get("engagement_rate_pct") or ""
    try:
        eng = float(eng_raw) if eng_raw != "" else None
    except ValueError:
        eng = None
    first = first_name(name, handle)
    hook = build_hook(followers, eng, niche)
    subj, body = render_email(first, hook, form_url, url)
    return Row(
        name=name,
        handle=handle,
        email=email,
        tiktok_url=url,
        niche=niche,
        followers=followers,
        engagement_rate_pct=eng,
        hook=hook,
        email_subject=subj,
        email_body=body,
    )


def write_outputs(rows: list[Row], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    csv_path = out_dir / f"tiktok_email_ready_{ts}.csv"
    copy_path = out_dir / f"TIKTOK_EMAIL_COPY_{ts}.txt"
    mail_dir = out_dir / "email"
    mail_dir.mkdir(exist_ok=True)

    fields = list(asdict(rows[0]).keys())
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow(asdict(row))

    blocks: list[str] = []
    for row in rows:
        safe = row.handle.replace("/", "_")[:40]
        mf = mail_dir / f"{safe}_email.txt"
        mf.write_text(
            f"To: {row.email}\nSubject: {row.email_subject}\n\n{row.email_body}",
            encoding="utf-8",
        )
        blocks.append(
            f"\n{'='*60}\n{row.name} | {row.tiktok_url}\n"
            f"Email: {row.email} | 粉丝: {row.followers:,}\n"
            f"Subject: {row.email_subject}\n\n{row.email_body}\n"
        )
    copy_path.write_text("\n".join(blocks), encoding="utf-8")
    print(f"✅ 飞书/Excel 导入: {csv_path}")
    print(f"✅ 一键复制: {copy_path}")
    print(f"✅ 单人邮件: {mail_dir}/ ({len(rows)} 封)")


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--limit", type=int, default=0, help="只处理前 N 人，0=全部")
    parser.add_argument("--form-url", default=FORM_URL)
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"请先运行: python import_xlsx.py\n缺少: {args.input}")

    with args.input.open(encoding="utf-8-sig", newline="") as f:
        raw = list(csv.DictReader(f))

    rows: list[Row] = []
    for r in raw:
        parsed = parse_row(r, args.form_url)
        if parsed:
            rows.append(parsed)
        if args.limit and len(rows) >= args.limit:
            break

    if not rows:
        print("没有有效邮箱行")
        return

    write_outputs(rows, args.output)
    print(f"共 {len(rows)} 封邮件待发送（Gmail 手发或后续 Instantly）")


if __name__ == "__main__":
    main()
