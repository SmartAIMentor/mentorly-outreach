#!/usr/bin/env python3
"""从 运营事项.xlsx 同步任务清单与 EchoTik 达人邮箱到 outreach CSV。"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
XLSX = REPO / "运营事项.xlsx"
OUT_CREATORS = ROOT / "creators_echotik.csv"
OUT_TASKS = REPO / "docs" / "运营事项_任务清单.csv"

TASK_COLUMNS = [
    "序号",
    "任务",
    "渠道类型",
    "优先级",
    "自动化",
    "负责人",
    "频率",
    "钩子",
    "执行步骤",
    "KPI",
    "工具",
    "状态",
    "备注",
]


def import_tasks() -> int:
    df = pd.read_excel(XLSX, sheet_name="运营事项", header=None)
    rows: list[dict[str, str]] = []
    for _, r in df.iterrows():
        if pd.isna(r.iloc[0]) or str(r.iloc[0]).strip() == "":
            continue
        try:
            int(r.iloc[0])
        except (ValueError, TypeError):
            continue
        rows.append(
            {
                TASK_COLUMNS[0]: str(int(r.iloc[0])),
                TASK_COLUMNS[1]: str(r.iloc[1] or "").strip(),
                TASK_COLUMNS[2]: str(r.iloc[2] or "").strip(),
                TASK_COLUMNS[3]: str(r.iloc[3] or "").strip(),
                TASK_COLUMNS[4]: str(r.iloc[4] or "").strip(),
                TASK_COLUMNS[5]: str(r.iloc[5] or "").strip(),
                TASK_COLUMNS[6]: str(r.iloc[6] or "").strip(),
                TASK_COLUMNS[7]: str(r.iloc[7] or "").strip(),
                TASK_COLUMNS[8]: str(r.iloc[8] or "").strip(),
                TASK_COLUMNS[9]: str(r.iloc[9] or "").strip(),
                TASK_COLUMNS[10]: str(r.iloc[10] or "").strip(),
                TASK_COLUMNS[11]: str(r.iloc[11] or "").strip(),
                TASK_COLUMNS[12]: str(r.iloc[14] if len(r) > 14 else "").strip(),
            }
        )
    OUT_TASKS.parent.mkdir(parents=True, exist_ok=True)
    with OUT_TASKS.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=TASK_COLUMNS)
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def import_creators() -> int:
    df = pd.read_excel(XLSX, sheet_name="echotik达人邮箱", header=0)
    # 首行被当作列名：用位置取字段
    col_name, col_email, col_handle, col_niche, col_tt, col_followers = (
        0,
        1,
        2,
        3,
        12,
        13,
    )
    out_rows: list[dict[str, str]] = []
    email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    for _, r in df.iterrows():
        email = str(r.iloc[col_email] or "").strip()
        if not email_re.match(email):
            continue
        tt_url = str(r.iloc[col_tt] or "").strip()
        if "tiktok.com" not in tt_url:
            continue
        handle = str(r.iloc[col_handle] or "").strip()
        name = str(r.iloc[col_name] or "").strip()
        niche = str(r.iloc[col_niche] or "").strip().replace("nan", "")
        followers = r.iloc[col_followers]
        try:
            followers_i = int(float(followers))
        except (TypeError, ValueError):
            followers_i = 0
        notes = f"name={name};followers={followers_i}"
        out_rows.append(
            {
                "platform": "tiktok",
                "handle_or_url": tt_url,
                "email": email,
                "niche": niche,
                "notes": notes,
            }
        )
    with OUT_CREATORS.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["platform", "handle_or_url", "email", "niche", "notes"],
        )
        w.writeheader()
        w.writerows(out_rows)
    return len(out_rows)


def main() -> None:
    if not XLSX.exists():
        raise SystemExit(f"找不到: {XLSX}")
    n_tasks = import_tasks()
    n_creators = import_creators()
    print(f"✅ 任务清单: {OUT_TASKS} ({n_tasks} 条)")
    print(f"✅ 达人列表: {OUT_CREATORS} ({n_creators} 条，含邮箱)")
    print("\n生成邮件/文案:")
    print(f"  cd {ROOT} && ./run.sh -i creators_echotik.csv")


if __name__ == "__main__":
    main()
