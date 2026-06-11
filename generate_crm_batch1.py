#!/usr/bin/env python3
"""从 creators_tiktok.csv 生成飞书 CRM 导入表（batch1 前 250 人）。"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
_MENTORAIXS = ROOT.parent.parent


def _paths() -> tuple[Path, Path]:
    creators = ROOT / "creators_tiktok.csv"
    crm_mentoraixs = _MENTORAIXS / "docs" / "crm-触达追踪_飞书导入.csv"
    if crm_mentoraixs.parent.exists() and (_MENTORAIXS / "docs" / "运营事项_更新.csv").exists():
        return creators, crm_mentoraixs
    return creators, ROOT / "crm-触达追踪_飞书导入.csv"


CREATORS, OUT = _paths()
BATCH1_LIMIT = 250

HEADERS = [
    "name",
    "email",
    "platform",
    "handle_or_url",
    "niche",
    "followers",
    "channel",
    "email_batch",
    "dm_sent",
    "status",
    "reply_at",
    "registered_at",
    "activated_at",
    "notes",
]


def main() -> None:
    if not CREATORS.exists():
        raise SystemExit(f"缺少 {CREATORS}，先运行 ./run.sh import")

    rows: list[dict] = []
    with CREATORS.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= BATCH1_LIMIT:
                break
            rows.append(
                {
                    "name": row.get("name", ""),
                    "email": row.get("email", ""),
                    "platform": row.get("platform", "tiktok"),
                    "handle_or_url": row.get("handle_or_url", ""),
                    "niche": row.get("niche", ""),
                    "followers": row.get("followers", ""),
                    "channel": "email",
                    "email_batch": "batch1",
                    "dm_sent": "no",
                    "status": "待触达",
                    "reply_at": "",
                    "registered_at": "",
                    "activated_at": "",
                    "notes": row.get("notes", ""),
                }
            )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ 已写入 {OUT}（batch1 {len(rows)} 人）")


if __name__ == "__main__":
    main()
