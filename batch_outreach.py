#!/usr/bin/env python3
"""批量：TikHub 拉 IG 达人数据 → 生成可直接复制的 DM / 邮件 → 导出飞书 CSV。"""

from __future__ import annotations

import argparse
import csv
import os
import re
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from template_render import render_dm_v2, render_email_v2

ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT / "creators.csv"
DEFAULT_OUT = ROOT / "output"
BETA_FORM_URL = os.environ.get(
    "MENTORLY_BETA_FORM_URL", "https://tally.so/r/REPLACE_ME"
)


def load_dotenv() -> None:
    for path in (
        ROOT / ".env",
        ROOT.parent.parent / ".env.local",
        ROOT.parent.parent / ".env",
    ):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip('"').strip("'")
            os.environ.setdefault(key, val)


def ig_username(value: str) -> str:
    value = value.strip()
    m = re.search(r"instagram\.com/([^/?#]+)", value, re.I)
    if m:
        return m.group(1).lstrip("@")
    return value.lstrip("@").split("/")[0]


def tiktok_username(value: str) -> str:
    value = value.strip()
    m = re.search(r"tiktok\.com/@([^/?#]+)", value, re.I)
    if m:
        return m.group(1)
    return value.lstrip("@").split("/")[0]


def parse_notes_field(notes: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in (notes or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
    return out


EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", re.I
)


def extract_email(bio: str | None, override: str | None) -> str:
    if override and override.strip():
        return override.strip()
    if not bio:
        return ""
    found = EMAIL_RE.findall(bio)
    return found[0] if found else ""


def extract_post_codes(payload: Any) -> list[str]:
    codes: list[str] = []
    seen: set[str] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            code = value.get("code") or value.get("shortcode")
            if isinstance(code, str) and code and code not in seen:
                seen.add(code)
                codes.append(code)
            for nested in value.values():
                visit(nested)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(payload)
    return codes


def post_metrics(item: dict[str, Any]) -> tuple[int, int]:
    likes = int(item.get("like_count") or 0)
    comments = int(item.get("comment_count") or 0)
    return likes, comments


def caption_snippet(item: dict[str, Any], max_len: int = 80) -> str:
    cap = item.get("caption") or {}
    text = cap.get("text") if isinstance(cap, dict) else None
    if not text:
        text = item.get("text") or item.get("author_text") or ""
    text = re.sub(r"\s+", " ", str(text)).strip()
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text or "your recent content"


def calc_engagement_rate(
    followers: int, posts: list[dict[str, Any]]
) -> float | None:
    if not followers or not posts:
        return None
    rates: list[float] = []
    for item in posts:
        likes, comments = post_metrics(item)
        if (likes + comments) > followers * 5:
            continue
        rates.append((likes + comments) / followers * 100)
    if rates:
        return round(sum(rates) / len(rates), 2)
    # 全是爆款帖时，用未过滤的中位数兜底
    raw = [
        (post_metrics(item)[0] + post_metrics(item)[1]) / followers * 100
        for item in posts
    ]
    raw.sort()
    mid = raw[len(raw) // 2]
    return round(mid, 2)


def display_first_name(full_name: str, username: str) -> str:
    for part in re.split(r"[\s—\-]+", full_name or ""):
        word = re.sub(r"[^A-Za-z]", "", part)
        if len(word) >= 2:
            return word.capitalize()
    return username


@dataclass
class CreatorRow:
    platform: str
    handle: str
    profile_url: str
    full_name: str
    followers: int
    engagement_rate_pct: float | None
    email: str
    niche: str
    hook_data_point: str
    latest_post_snippet: str
    dm_message: str
    email_subject: str
    email_body: str
    status: str = "待触达"


def build_hook(
    followers: int,
    engagement: float | None,
    niche: str,
    latest_snippet: str,
) -> str:
    niche_label = niche or "your niche"
    if engagement is not None and engagement > 20:
        return (
            f"At ~{followers:,} followers, your recent content is punching well above "
            f"typical {niche_label} accounts — strong signal for brands."
        )
    if engagement is not None:
        bench = 3.0
        comp = "above" if engagement >= bench else "below"
        return (
            f'Your recent posts average ~{engagement}% engagement at ~{followers:,} followers '
            f"— that's {comp} what we typically see for {niche_label} creators."
        )
    return (
        f"At ~{followers:,} followers, your recent post on "
        f'"{latest_snippet}" stood out in {niche_label}.'
    )


def render_dm(name: str, hook: str, form_url: str, platform: str = "instagram") -> str:
    who = name or "there"
    return render_dm_v2(who)


def render_email(name: str, hook: str, form_url: str) -> tuple[str, str]:
    who = name or "there"
    return render_email_v2(who)


def reel_edges_to_items(reels_resp: dict[str, Any]) -> list[dict[str, Any]]:
    """把 get_user_reels 响应转成与帖子类似的 item 结构（兼容 edges 与 items）。"""
    data = reels_resp.get("data", {}) or {}
    raw = data.get("edges") or data.get("items") or []
    items: list[dict[str, Any]] = []
    for edge in raw:
        if not isinstance(edge, dict):
            continue
        # 新 API：items[] 即媒体本身
        if edge.get("like_count") is not None or edge.get("caption_text"):
            media = edge
        else:
            node = edge.get("node") if isinstance(edge.get("node"), dict) else edge
            media = (
                node.get("media")
                if isinstance(node.get("media"), dict)
                else node
            )
        cap = media.get("caption") or {}
        text = media.get("caption_text")
        if not text and isinstance(cap, dict):
            text = cap.get("text")
        items.append(
            {
                "like_count": media.get("like_count"),
                "comment_count": media.get("comment_count"),
                "caption": {"text": text} if text else {},
                "text": text,
                "code": media.get("code") or media.get("shortcode"),
            }
        )
    return items


def fetch_recent_media(
    client: Any, username: str, post_count: int, sleep_s: float
) -> list[dict[str, Any]]:
    """优先帖子列表；若 TikHub 返回 400 则改用 Reels（当前 Key 下 posts 常不可用）。"""
    try:
        posts_resp = client.instagram_v3.get_user_posts(
            username=username, first=post_count, count=post_count
        )
        codes = extract_post_codes(posts_resp)[:post_count]
        items: list[dict[str, Any]] = []
        for code in codes:
            time.sleep(sleep_s)
            detail = client.instagram_v3.get_post_info_by_code(code=code)
            item_list = detail.get("data", {}).get("items") or []
            if item_list:
                items.append(item_list[0])
        if items:
            return items
    except Exception:
        pass

    reels_resp = client.instagram_v3.get_user_reels(
        username=username, first=post_count, page_size=post_count
    )
    return reel_edges_to_items(reels_resp)[:post_count]


def parse_profile_user(profile: dict[str, Any]) -> dict[str, Any]:
    data = profile.get("data", {}) or {}
    if isinstance(data.get("user"), dict):
        return data["user"]
    if isinstance(data, dict) and data.get("username"):
        return data
    return {}


def fetch_instagram(
    client: Any, username: str, post_count: int, sleep_s: float
) -> dict[str, Any]:
    profile = client.instagram_v3.get_user_profile(username=username)
    user = parse_profile_user(profile)
    items = fetch_recent_media(client, username, post_count, sleep_s)
    return {"user": user, "posts": items}


def process_tiktok_row(
    row: dict[str, str], form_url: str, dry_run: bool
) -> CreatorRow:
    raw = (row.get("handle_or_url") or "").strip()
    niche = (row.get("niche") or "").strip()
    email = (row.get("email") or "").strip()
    meta = parse_notes_field(row.get("notes") or "")
    username = tiktok_username(raw)
    profile_url = raw if "tiktok.com" in raw else f"https://www.tiktok.com/@{username}"
    full_name = meta.get("name", username)
    try:
        followers = int(meta.get("followers") or 0)
    except ValueError:
        followers = 0
    first = display_first_name(full_name, username)
    hook = build_hook(followers, None, niche, "your recent TikTok content")
    dm = render_dm(first, hook, form_url, platform="tiktok")
    subject, body = render_email(first, hook, form_url)
    return CreatorRow(
        platform="tiktok",
        handle=username,
        profile_url=profile_url,
        full_name=full_name,
        followers=followers,
        engagement_rate_pct=None,
        email=email,
        niche=niche,
        hook_data_point=hook,
        latest_post_snippet="your recent TikTok content",
        dm_message=dm,
        email_subject=subject,
        email_body=body,
    )


def process_row(
    client: Any | None,
    row: dict[str, str],
    post_count: int,
    sleep_s: float,
    form_url: str,
    dry_run: bool,
) -> CreatorRow:
    platform = (row.get("platform") or "instagram").strip().lower()
    raw = (row.get("handle_or_url") or "").strip()
    niche = (row.get("niche") or "").strip()
    email_override = (row.get("email") or "").strip()

    if platform == "tiktok":
        return process_tiktok_row(row, form_url, dry_run)

    if platform != "instagram":
        raise ValueError(f"不支持的平台: {platform}")

    username = ig_username(raw)
    profile_url = f"https://www.instagram.com/{username}/"

    if dry_run or client is None:
        return CreatorRow(
            platform=platform,
            handle=username,
            profile_url=profile_url,
            full_name="",
            followers=0,
            engagement_rate_pct=None,
            email=email_override,
            niche=niche,
            hook_data_point="[dry-run] set TIKHUB_API_KEY to fetch real stats",
            latest_post_snippet="your recent content",
            dm_message=render_dm(
                username, "[dry-run hook]", form_url
            ),
            email_subject=f"Free creator stats — @{username}",
            email_body=render_email(username, "[dry-run hook]", form_url)[1],
        )

    data = fetch_instagram(client, username, post_count, sleep_s)
    user = data["user"]
    posts = data["posts"]
    followers = int(user.get("follower_count") or 0)
    full_name = (user.get("full_name") or username).strip()
    bio = user.get("biography") or ""
    email = extract_email(bio, email_override)
    engagement = calc_engagement_rate(followers, posts)
    latest = caption_snippet(posts[0]) if posts else "your recent Reel"
    hook = build_hook(followers, engagement, niche, latest)
    first = display_first_name(full_name, username)
    dm = render_dm(first, hook, form_url, platform="instagram")
    subject, body = render_email(first, hook, form_url)

    return CreatorRow(
        platform=platform,
        handle=username,
        profile_url=profile_url,
        full_name=full_name,
        followers=followers,
        engagement_rate_pct=engagement,
        email=email,
        niche=niche,
        hook_data_point=hook,
        latest_post_snippet=latest,
        dm_message=dm,
        email_subject=subject,
        email_body=body,
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_outputs(rows: list[CreatorRow], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    csv_path = out_dir / f"outreach_ready_{ts}.csv"
    copy_path = out_dir / f"COPY_PASTE_{ts}.txt"
    dm_dir = out_dir / "dm"
    mail_dir = out_dir / "email"
    dm_dir.mkdir(exist_ok=True)
    mail_dir.mkdir(exist_ok=True)

    fieldnames = list(asdict(rows[0]).keys()) if rows else []
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(asdict(r))

    blocks: list[str] = []
    for r in rows:
        dm_file = dm_dir / f"{r.handle}_dm.txt"
        dm_file.write_text(r.dm_message, encoding="utf-8")
        if r.email:
            mail_file = mail_dir / f"{r.handle}_email.txt"
            mail_file.write_text(
                f"To: {r.email}\nSubject: {r.email_subject}\n\n{r.email_body}",
                encoding="utf-8",
            )
        blocks.append(
            f"\n{'='*60}\n@{r.handle} | {r.profile_url}\n"
            f"粉丝: {r.followers:,} | 互动率: {r.engagement_rate_pct}%\n"
            f"邮箱: {r.email or '(bio 未找到，请手补)'}\n"
            f"--- DM (复制到 IG) ---\n{r.dm_message}\n"
        )
        if r.email:
            blocks.append(
                f"--- Email ---\nSubject: {r.email_subject}\n\n{r.email_body}\n"
            )

    copy_path.write_text("\n".join(blocks), encoding="utf-8")
    print(f"\n✅ 飞书导入: {csv_path}")
    print(f"✅ 一键复制: {copy_path}")
    print(f"✅ 分人 DM:   {dm_dir}/")
    print(f"✅ 分人邮件: {mail_dir}/")


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Mentorly 达人触达批量生成")
    parser.add_argument("-i", "--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--posts", type=int, default=3, help="分析最近 N 条帖子")
    parser.add_argument("--sleep", type=float, default=0.6, help="API 请求间隔秒")
    parser.add_argument(
        "--form-url",
        default=BETA_FORM_URL,
        help="Beta 表单链接（或设 MENTORLY_BETA_FORM_URL）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="不调用 TikHub，只生成模板结构",
    )
    args = parser.parse_args()

    api_key = os.environ.get("TIKHUB_API_KEY", "").strip()
    if not api_key and not args.dry_run:
        print("⚠️  未设置 TIKHUB_API_KEY，使用 --dry-run 预览，或在 scripts/outreach/.env 配置")
        args.dry_run = True

    raw_rows = read_csv(args.input)
    raw_rows = [r for r in raw_rows if (r.get("handle_or_url") or "").strip()]

    client = None
    if not args.dry_run:
        from tikhub import TikHub

        client = TikHub(api_key=api_key)

    results: list[CreatorRow] = []

    def run_batch(active_client: Any | None) -> None:
        for i, row in enumerate(raw_rows, 1):
            print(f"[{i}/{len(raw_rows)}] {row.get('handle_or_url')} ...")
            try:
                cr = process_row(
                    active_client,
                    row,
                    args.posts,
                    args.sleep,
                    args.form_url,
                    active_client is None,
                )
                results.append(cr)
            except Exception as e:
                print(f"  ❌ 跳过: {e}")

    if client:
        with client:
            run_batch(client)
    else:
        run_batch(None)

    if not results:
        print("没有成功处理的达人")
        return

    write_outputs(results, args.output)


if __name__ == "__main__":
    main()
