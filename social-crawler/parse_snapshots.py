#!/usr/bin/env python3
"""Parse Facebook and Threads HTML snapshots into clean comment records."""

from __future__ import annotations

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
FB_SNAPSHOT_ROOT = ROOT / "raw" / "facebook-logged-in-html"
TH_SNAPSHOT_ROOT = ROOT / "raw" / "threads-logged-in-html"
OUT_FB = ROOT / "normalized" / "facebook-comments-from-snapshots-2026-04-30.json"
OUT_TH = ROOT / "normalized" / "threads-comments-from-snapshots-2026-04-29.json"


def post_url_from_filename(filename: str) -> str:
    """Extract post URL from snapshot filename like:
    203304-post-https-www-facebook-com-photo-fbid-1496...-comment-scroll-1.html
    """
    m = re.search(r"-post-(https-www-facebook-com[^.]+?)(?:-dropdown|-after|-comment|-before)", filename)
    if not m:
        return ""
    slug = m.group(1)
    url = slug.replace("https-www-facebook-com", "https://www.facebook.com/")
    # restore ?fbid= and &set=
    url = re.sub(r"photo-fbid-(\d+)-set-([a-z0-9.-]+)", r"photo/?fbid=\1&set=\2", url)
    url = re.sub(r"/photo/\?", "/photo/?", url)
    return url


def post_text_from_soup(soup: BeautifulSoup) -> str:
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        return meta["content"].strip()
    return ""


def parse_facebook_snapshots() -> list[dict]:
    seen: set[tuple] = set()
    records: list[dict] = []
    post_texts: dict[str, str] = {}  # post_url -> text (from first snapshot seen)

    for snap_dir in sorted(FB_SNAPSHOT_ROOT.iterdir()):
        if not snap_dir.is_dir():
            continue
        for html_file in sorted(snap_dir.glob("*-comment-scroll-*.html")):
            post_url = post_url_from_filename(html_file.name)
            if not post_url:
                continue
            soup = BeautifulSoup(html_file.read_text(encoding="utf-8", errors="replace"), "lxml")
            if post_url not in post_texts:
                post_texts[post_url] = post_text_from_soup(soup)
            for article in soup.find_all("div", attrs={"role": "article"}):
                aria = article.get("aria-label", "")
                # aria-label format: "AuthorName的留言TimeAgo" or "AuthorName回覆TimeAgo"
                m = re.match(r"^(.+?)(?:的留言|回覆)(.+)$", aria)
                if not m:
                    continue
                author = m.group(1).strip()
                time_text = m.group(2).strip()

                # Comment text: innermost div[dir="auto"] that has real text
                text = ""
                for d in article.find_all("div", attrs={"dir": "auto"}):
                    t = d.get_text(" ", strip=True)
                    if t and len(t) > 1 and t not in (author,):
                        # prefer the deepest non-empty block
                        if len(t) > len(text):
                            text = t

                if not text:
                    continue

                key = (post_url, author, text[:80])
                if key in seen:
                    continue
                seen.add(key)
                records.append({
                    "platform": "facebook",
                    "post_url": post_url,
                    "post_text": post_texts.get(post_url, ""),
                    "author_name": author,
                    "comment_time_text": time_text,
                    "comment_text": text,
                    "source_file": html_file.name,
                })

    return records


def parse_threads_snapshots() -> list[dict]:
    seen: set[tuple] = set()
    records: list[dict] = []
    snap_post_texts: dict[str, str] = {}  # snap_dir name -> post text from first file with content

    for snap_dir in sorted(TH_SNAPSHOT_ROOT.iterdir()):
        if not snap_dir.is_dir():
            continue
        for html_file in sorted(snap_dir.glob("*.html")):
            soup = BeautifulSoup(html_file.read_text(encoding="utf-8", errors="replace"), "lxml")
            snap_key = html_file.name
            snap_post_texts[snap_key] = post_text_from_soup(soup)
            for container in soup.find_all("div", attrs={"data-pressable-container": "true"}):
                # Username from img alt
                img = container.find("img", alt=re.compile(r"的大頭貼照$"))
                if img:
                    username = re.sub(r"的大頭貼照$", "", img["alt"]).strip()
                else:
                    a = container.find("a", href=re.compile(r"^/@"))
                    username = a["href"].lstrip("/@") if a else ""

                if not username:
                    continue

                # Post URL from permalink link
                post_url = ""
                for a in container.find_all("a", href=True):
                    if re.search(r"/@[^/]+/post/", a["href"]):
                        post_url = a["href"]
                        if post_url.startswith("/"):
                            post_url = "https://www.threads.net" + post_url
                        break

                skip = {"追蹤", "更多", "讚", "回覆", "轉發", "分享", ""}

                # Timestamp and text from spans
                time_text = ""
                text = ""
                for span in container.find_all("span"):
                    t = span.get_text(strip=True)
                    if not t or t in skip or t.isdigit():
                        continue
                    if re.match(r"^\d{4}-\d{2}-\d{2}$", t) or re.match(r"^\d+\s*(秒|分|小時|天|週|h|m|s|d|w)", t):
                        if not time_text:
                            time_text = t
                    elif t != username and len(t) > len(text):
                        text = t

                if not text or len(text) < 2:
                    continue

                key = (username, text[:80])
                if key in seen:
                    continue
                seen.add(key)
                records.append({
                    "platform": "threads",
                    "post_url": post_url,
                    "post_text": snap_post_texts.get(html_file.name, ""),
                    "author_name": username,
                    "comment_time_text": time_text,
                    "comment_text": text,
                    "source_file": html_file.name,
                })

    return records


def main() -> None:
    print("Parsing Facebook snapshots...")
    fb_records = parse_facebook_snapshots()
    print(f"  → {len(fb_records)} comments")
    OUT_FB.write_text(json.dumps({
        "generated_at": __import__("datetime").datetime.now().astimezone().isoformat(),
        "count": len(fb_records),
        "records": fb_records,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  saved: {OUT_FB}")

    print("Parsing Threads snapshots...")
    th_records = parse_threads_snapshots()
    print(f"  → {len(th_records)} records")
    OUT_TH.write_text(json.dumps({
        "generated_at": __import__("datetime").datetime.now().astimezone().isoformat(),
        "count": len(th_records),
        "records": th_records,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  saved: {OUT_TH}")


if __name__ == "__main__":
    main()
