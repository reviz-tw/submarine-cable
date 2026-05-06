#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import random
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import List

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait


ROOT = Path(__file__).resolve().parent
PROFILE = ROOT / ".selenium-profile-firefox-worker"
GECKO = "/usr/local/Cellar/geckodriver/0.36.0/bin/geckodriver"
FIREFOX = "/Applications/Firefox.app/Contents/MacOS/firefox"
SNAPSHOT_DIR = ROOT / "raw" / "threads-logged-in-html" / datetime.now().strftime("%Y-%m-%d-%H%M%S")
QUEUE_PATH = ROOT / "normalized" / "threads-current-queue-2026-04-29.json"
RUN_STATE_PATH = ROOT / "normalized" / "threads-current-run-state-2026-04-29.json"

SEARCH_URLS = [
    "https://www.threads.com/search?q=%E6%B5%B7%E5%BA%95%E9%9B%BB%E7%BA%9C",
    "https://www.threads.com/search?q=%E6%B5%B7%E7%BA%9C",
]
MAIN_POSTS_PATH = ROOT / "normalized" / "seacable-social-posts-2026-04-29.json"


@dataclass
class PostRecord:
    post_url: str
    source_name: str
    post_time_text: str
    post_text: str
    like_count_text: str
    comment_count_text: str
    repost_count_text: str
    share_count_text: str
    collection_method: str


@dataclass
class CommentRecord:
    parent_post_url: str
    author_name: str
    comment_time_text: str
    comment_text: str
    collection_method: str


def now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def load_existing_post_urls() -> set[str]:
    data = load_json(MAIN_POSTS_PATH)
    records = data.get("records", []) if isinstance(data, dict) else []
    return {r.get("post_url") for r in records if r.get("post_url")}


def load_queue_records() -> list[dict]:
    data = load_json(QUEUE_PATH)
    return data.get("records", []) if isinstance(data, dict) else []


def queue_urls_by_status(*statuses: str) -> set[str]:
    allowed = set(statuses)
    return {
        r.get("post_url")
        for r in load_queue_records()
        if r.get("post_url") and r.get("status") in allowed
    }


def slow_sleep(low: float, high: float) -> None:
    duration = random.uniform(low, high)
    time.sleep(duration)


def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ").strip()
    text = re.sub(r"\n+", "\n", text)
    return text


def has_seacable_keyword(text: str) -> bool:
    return any(keyword in text for keyword in ("海底", "海纜", "電纜"))


def should_skip_text(text: str) -> bool:
    lowered = text.lower()
    blocked_terms = [
        "pokemon",
        "pokémon",
        "寶可夢",
        "神奇寶貝",
    ]
    return any(term in lowered for term in blocked_terms)


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "page"


def save_html_snapshot(driver: webdriver.Firefox, label: str) -> str:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%H%M%S")
    path = SNAPSHOT_DIR / f"{timestamp}-{slugify(label)}.html"
    path.write_text(driver.page_source, encoding="utf-8")
    return str(path)


def upsert_queue_item(post: PostRecord, source_query: str) -> None:
    queue = load_json(QUEUE_PATH) or {"generated_at": now_iso(), "records": []}
    records = queue.setdefault("records", [])
    existing = next((r for r in records if r["post_url"] == post.post_url), None)
    payload = {
        "post_url": post.post_url,
        "source_name": post.source_name,
        "source_query": source_query,
        "status": "pending",
        "discovered_at": now_iso(),
        "last_attempted_at": None,
        "notes": "",
    }
    if existing is None:
        records.append(payload)
    else:
        existing.update({k: v for k, v in payload.items() if k not in {"discovered_at", "status"}})
        if existing.get("status") not in {"crawled", "skipped"}:
            existing["status"] = "pending"
    queue["updated_at"] = now_iso()
    write_json(QUEUE_PATH, queue)


def mark_queue_status(post_url: str, status: str, notes: str = "") -> None:
    queue = load_json(QUEUE_PATH)
    if not queue:
        return
    for record in queue.get("records", []):
        if record.get("post_url") == post_url:
            record["status"] = status
            record["last_attempted_at"] = now_iso()
            if notes:
                record["notes"] = notes
            break
    queue["updated_at"] = now_iso()
    write_json(QUEUE_PATH, queue)


def write_run_state(stage: str, current_query: str = "", current_post_url: str = "", posts_seen: int = 0, comments_seen: int = 0) -> None:
    write_json(
        RUN_STATE_PATH,
        {
            "updated_at": now_iso(),
            "stage": stage,
            "current_query": current_query,
            "current_post_url": current_post_url,
            "posts_seen": posts_seen,
            "comments_seen": comments_seen,
            "snapshot_dir": str(SNAPSHOT_DIR),
            "queue_path": str(QUEUE_PATH),
        },
    )


def build_driver() -> webdriver.Firefox:
    options = Options()
    options.binary_location = FIREFOX
    options.add_argument("-profile")
    options.add_argument(str(PROFILE))
    options.add_argument("-no-remote")
    service = Service(GECKO)
    driver = webdriver.Firefox(service=service, options=options)
    driver.set_window_position(120, 120)
    driver.set_window_size(1280, 900)
    return driver


def click_first_text(driver: webdriver.Firefox, labels: List[str]) -> bool:
    script = """
    (labels) => {
      const els = [...document.querySelectorAll('button, a, div[role="button"]')];
      for (const label of labels) {
        const target = els.find(el => ((el.innerText || '').trim() === label) || ((el.textContent || '').trim() === label));
        if (target) {
          target.click();
          return label;
        }
      }
      return null;
    }
    """
    clicked = driver.execute_script(script, labels)
    return bool(clicked)


def wait_for_search_cards(driver: webdriver.Firefox, timeout: int = 30) -> None:
    wait = WebDriverWait(driver, timeout)
    wait.until(lambda d: d.execute_script(
        "return document.querySelectorAll('a[href*=\"/post/\"]').length"
    ) > 0)


def wait_for_comments_to_appear(driver: webdriver.Firefox, timeout: int = 30) -> bool:
    wait = WebDriverWait(driver, timeout)
    try:
        wait.until(lambda d: d.execute_script("""
            return [...document.querySelectorAll('a[href*="threads.com/@"]')]
              .some(a => {
                const href = a.href || '';
                if (!href.includes('threads.com/@') || href.includes('/post/')) return false;
                let n = a;
                for (let i = 0; i < 8 && n; i++, n = n.parentElement) {
                  const t = (n.innerText || '').trim();
                  if (t.length >= 20 && t.includes('\\n')) return true;
                }
                return false;
              });
        """))
        return True
    except TimeoutException:
        return False


def slow_scroll(driver: webdriver.Firefox, rounds: int = 3, snapshot_prefix: str | None = None) -> None:
    for idx in range(rounds):
        delta = random.randint(500, 950)
        driver.execute_script("window.scrollBy({top: arguments[0], behavior: 'smooth'});", delta)
        slow_sleep(7, 14)
        if snapshot_prefix:
            save_html_snapshot(driver, f"{snapshot_prefix}-scroll-{idx+1}")


def extract_raw_search_cards(driver: webdriver.Firefox) -> List[dict]:
    script = """
    () => {
      const anchors = [...document.querySelectorAll('a[href*="/post/"]')]
        .filter(a => a.href.includes('threads.com/@') && !a.href.endsWith('/media'));
      const seen = new Set();
      const records = [];
      for (const a of anchors) {
        const href = a.href;
        if (seen.has(href)) continue;
        seen.add(href);
        let n = a;
        let text = '';
        for (let i = 0; i < 12 && n; i++, n = n.parentElement) {
          const t = (n.innerText || '').trim();
          if (t.length >= 40 && t.length <= 500 && t.includes('\\n')) {
            text = t;
            break;
          }
        }
        if (!text) continue;
        records.push({href, text});
      }
      return records;
    }
    """
    return driver.execute_script(f"return ({script})();")


def collect_search_cards_with_scroll(driver: webdriver.Firefox, max_idle_rounds: int = 3) -> List[PostRecord]:
    seen = {}
    idle_rounds = 0
    round_no = 0
    while idle_rounds < max_idle_rounds:
        round_no += 1
        before = len(seen)
        save_html_snapshot(driver, f"search-round-{round_no}-before")
        raw_cards = extract_raw_search_cards(driver)
        keyword_hits_this_round = 0
        for card in extract_search_cards(driver):
            seen.setdefault(card.post_url, card)
            keyword_hits_this_round += 1
        after = len(seen)
        if raw_cards and keyword_hits_this_round == 0:
            save_html_snapshot(driver, f"search-round-{round_no}-no-keyword-stop")
            break
        if after == before:
            idle_rounds += 1
        else:
            idle_rounds = 0
        slow_scroll(driver, rounds=2, snapshot_prefix=f"search-round-{round_no}")
    return list(seen.values())


def extract_search_cards(driver: webdriver.Firefox) -> List[PostRecord]:
    raw = extract_raw_search_cards(driver)
    out: List[PostRecord] = []
    for item in raw:
      lines = [clean_text(x) for x in item["text"].split("\n") if clean_text(x)]
      if len(lines) < 6:
          continue
      source = lines[0]
      time_idx = 1
      if not re.search(r"\d{4}-\d{1,2}-\d{1,2}|^\d+天|^\d+小時|^\d+週|^\d+月", lines[1]):
          if len(lines) > 2 and re.search(r"\d{4}-\d{1,2}-\d{1,2}|^\d+天|^\d+小時|^\d+週|^\d+月", lines[2]):
              time_idx = 2
          else:
              continue
      time_text = lines[time_idx]
      metrics = lines[-4:]
      body_start = time_idx + 1
      body = " ".join(lines[body_start:-4]).replace("翻譯", "").strip()
      body = re.sub(r"\s+1 /$", "", body).strip()
      if not body or not has_seacable_keyword(body) or should_skip_text(body):
          continue
      out.append(
          PostRecord(
              post_url=item["href"],
              source_name=source,
              post_time_text=time_text,
              post_text=body,
              like_count_text=metrics[0],
              comment_count_text=metrics[1],
              repost_count_text=metrics[2],
              share_count_text=metrics[3],
              collection_method="threads_logged_in_search_results_page",
          )
      )
    return out


def extract_visible_comments(driver: webdriver.Firefox, parent_url: str) -> List[CommentRecord]:
    script = """
    () => {
      const anchors = [...document.querySelectorAll('a[href*="/@"]')];
      const rows = [];
      for (const a of anchors) {
        const href = a.href || '';
        if (!href.includes('threads.com/@') || href.includes('/post/')) continue;
        let n = a;
        let text = '';
        for (let i = 0; i < 10 && n; i++, n = n.parentElement) {
          const t = (n.innerText || '').trim();
          if (t.length >= 15 && t.length <= 500 && t.includes('\\n')) {
            text = t;
            break;
          }
        }
        if (text) rows.push(text);
      }
      return rows;
    }
    """
    raw_rows = driver.execute_script(f"return ({script})();")
    comments: List[CommentRecord] = []
    seen = set()
    for row in raw_rows:
        lines = [clean_text(x) for x in row.split("\n") if clean_text(x)]
        if len(lines) < 3:
            continue
        author = lines[0]
        time_text = lines[1]
        body = " ".join(lines[2:])
        key = (author, time_text, body)
        if key in seen:
            continue
        seen.add(key)
        if len(body) < 5 or body in {"翻譯", "更多"}:
            continue
        if author in {"訊息", "Threads", "Meta"}:
            continue
        if time_text in {"動態", "海底電纜", "海纜", "個人檔案"}:
            continue
        if body in {"個人檔案 洞察報告 已儲存", "2025-9-3", "2026-3-15"}:
            continue
        comments.append(
            CommentRecord(
                parent_post_url=parent_url,
                author_name=author,
                comment_time_text=time_text,
                comment_text=body,
                collection_method="threads_logged_in_post_page",
            )
        )
    return comments


def collect_comments_with_scroll(
    driver: webdriver.Firefox, parent_url: str, max_idle_rounds: int = 3, max_total_rounds: int = 30
) -> List[CommentRecord]:
    seen = {}
    idle_rounds = 0
    rounds = 0
    post_slug = slugify(parent_url.rsplit("/", 1)[-1])
    def reached_end(d) -> bool:
        return d.execute_script(
            "return document.body.innerText.includes('部分回覆已隱藏') || document.body.innerText.includes('查看全部回覆');"
        )

    while idle_rounds < max_idle_rounds and rounds < max_total_rounds:
        rounds += 1
        before = len(seen)
        save_html_snapshot(driver, f"post-{post_slug}-round-{rounds}-before")
        for comment in extract_visible_comments(driver, parent_url):
            key = (comment.author_name, comment.comment_time_text, comment.comment_text)
            seen.setdefault(key, comment)
        after = len(seen)
        if reached_end(driver):
            save_html_snapshot(driver, f"post-{post_slug}-round-{rounds}-end")
            break
        if after == before:
            idle_rounds += 1
        else:
            idle_rounds = 0
        slow_scroll(driver, rounds=2, snapshot_prefix=f"post-{post_slug}-round-{rounds}")
    return list(seen.values())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--search-url", action="append", dest="search_urls")
    parser.add_argument("--urls-file", dest="urls_file", help="Text file with one post URL per line; skips search phase")
    args = parser.parse_args()

    random.seed()
    driver = build_driver()
    posts: List[PostRecord] = []
    comments: List[CommentRecord] = []
    seen_urls = set()
    existing_urls = load_existing_post_urls()

    try:
        if args.urls_file:
            direct_urls = [u.strip() for u in Path(args.urls_file).read_text().splitlines() if u.strip() and not u.startswith("#")]
            for url in direct_urls:
                stub = PostRecord(post_url=url, source_name="", post_time_text="", post_text="",
                                  like_count_text="", comment_count_text="", repost_count_text="",
                                  share_count_text="", collection_method="direct_url")
                posts.append(stub)
                seen_urls.add(url)
            crawl_posts = posts
        else:
            search_urls = args.search_urls or SEARCH_URLS
            for url in search_urls:
                write_run_state(stage="search", current_query=url, posts_seen=len(posts), comments_seen=len(comments))
                driver.get(url)
                slow_sleep(8, 14)
                wait_for_search_cards(driver)
                click_first_text(driver, ["最新", "最近"])
                slow_sleep(6, 12)
                cards = collect_search_cards_with_scroll(driver, max_idle_rounds=3)
                for card in cards:
                    if card.post_url in seen_urls:
                        continue
                    seen_urls.add(card.post_url)
                    posts.append(card)
                    upsert_queue_item(card, url)
                write_run_state(stage="search_complete", current_query=url, posts_seen=len(posts), comments_seen=len(comments))

            pending_or_retry_urls = queue_urls_by_status("pending", "failed", "crawling")
            crawl_posts = [post for post in posts if post.post_url in pending_or_retry_urls]

        for post in crawl_posts:
            write_run_state(
                stage="post",
                current_post_url=post.post_url,
                posts_seen=len(crawl_posts),
                comments_seen=len(comments),
            )
            if post.post_url in existing_urls:
                mark_queue_status(post.post_url, "skipped", notes="already_in_main_dataset")
                continue
            mark_queue_status(post.post_url, "crawling")
            driver.get(post.post_url)
            slow_sleep(9, 16)
            click_first_text(driver, ["最相關", "最新"])
            slow_sleep(5, 11)
            wait_for_comments_to_appear(driver, timeout=10)
            before_comments = len(comments)
            comments.extend(collect_comments_with_scroll(driver, post.post_url))
            note = f"comments_added={len(comments) - before_comments}"
            mark_queue_status(post.post_url, "crawled", notes=note)
            slow_sleep(6, 10)
    finally:
        write_run_state(stage="finished", posts_seen=len(posts), comments_seen=len(comments))
        driver.quit()

    output = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "snapshot_dir": str(SNAPSHOT_DIR),
        "posts": [asdict(p) for p in posts],
        "comments": [asdict(c) for c in comments],
    }
    out_path = ROOT / "normalized" / "threads-logged-in-crawl-2026-04-29.json"
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(out_path)
    print(f"posts={len(posts)} comments={len(comments)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
