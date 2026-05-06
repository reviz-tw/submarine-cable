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
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait


ROOT = Path(__file__).resolve().parent
PROFILE = ROOT / ".selenium-profile-firefox-worker-fb-native"
GECKO = ROOT / "tools" / "geckodriver"
FIREFOX = "/Applications/Firefox.app/Contents/MacOS/firefox"
SNAPSHOT_DIR = ROOT / "raw" / "facebook-logged-in-html" / datetime.now().strftime("%Y-%m-%d-%H%M%S")
QUEUE_PATH = ROOT / "normalized" / "facebook-current-queue-2026-04-30.json"
RUN_STATE_PATH = ROOT / "normalized" / "facebook-current-run-state-2026-04-30.json"
RAW_OUTPUT_PATH = ROOT / "normalized" / "facebook-logged-in-crawl-2026-04-30.json"

SEARCH_URLS = [
    "https://www.facebook.com/search/top/?q=%E6%B5%B7%E5%BA%95%E9%9B%BB%E7%BA%9C",
    "https://www.facebook.com/search/top/?q=%E6%B5%B7%E7%BA%9C",
]


@dataclass
class PostRecord:
    post_url: str
    source_name: str
    post_time_text: str
    post_text: str
    like_count_text: str
    comment_count_text: str
    share_count_text: str
    collection_method: str
    source_query: str
    raw_text: str


@dataclass
class CommentRecord:
    parent_post_url: str
    author_name: str
    comment_time_text: str
    comment_text: str
    collection_method: str


@dataclass
class PostPageRecord:
    post_url: str
    page_title: str
    page_body_text: str
    comments_observed: int
    snapshot_before: str
    snapshot_after: str


def now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def slow_sleep(low: float, high: float) -> None:
    time.sleep(random.uniform(low, high))


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


def write_run_state(
    stage: str,
    current_query: str = "",
    current_post_url: str = "",
    posts_seen: int = 0,
    comments_seen: int = 0,
) -> None:
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
    service = Service(str(GECKO))
    driver = webdriver.Firefox(service=service, options=options)
    driver.set_window_position(120, 120)
    driver.set_window_size(1200, 900)
    return driver


def click_first_text(driver: webdriver.Firefox, labels: List[str]) -> str | None:
    script = """
    (labels) => {
      function visible(el) {
        const rect = el.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
      }

      function clickable(el) {
        return el.closest('a, button, div[role="button"], div[role="link"]') || el;
      }

      const els = [...document.querySelectorAll('a, button, div[role="link"], div[role="button"], span')];
      for (const label of labels) {
        const exact = els.find(el => {
          const text = ((el.innerText || el.textContent || '').trim());
          return text === label && visible(el);
        });
        if (exact) {
          try { exact.click(); } catch (err) { }
          return ((exact.innerText || exact.textContent || '').trim()) || label;
        }
        const fuzzy = els.find(el => {
          const text = ((el.innerText || el.textContent || '').trim());
          return text && text.includes(label) && visible(el);
        });
        if (fuzzy) {
          const node = clickable(fuzzy);
          try {
            node.click();
          } catch (err) {
            fuzzy.click();
          }
          return ((fuzzy.innerText || fuzzy.textContent || '').trim()) || label;
        }
      }
      return null;
    }
    """
    hit = driver.execute_script(script, labels)
    if hit:
        return hit
    for label in labels:
        xpath = (
            "//*[self::a or self::button or @role='button' or @role='link' or self::span]"
            f"[contains(normalize-space(.), '{label}')]"
        )
        try:
            el = driver.find_element(By.XPATH, xpath)
            driver.execute_script("arguments[0].click();", el)
            return label
        except Exception:
            continue
    return None


def get_comment_mode_labels(driver: webdriver.Firefox) -> list[str]:
    labels_script = """
    () => {
      const els = [...document.querySelectorAll('a, button, div[role="button"], span')];
      return els
        .map(el => ((el.innerText || el.textContent || '').trim()))
        .filter(Boolean)
        .filter(t => (
          t.includes('最相關') ||
          t.includes('相關性最高') ||
          t.includes('Most relevant') ||
          t.includes('所有留言') ||
          t.includes('全部留言') ||
          t.includes('All comments')
        ))
        .slice(0, 30);
    }
    """
    return driver.execute_script(f"return ({labels_script})();")


def ensure_all_comments_mode(driver: webdriver.Firefox, snapshot_prefix: str = "") -> dict:
    # Facebook comment sort labels vary slightly by locale/page state.
    before = get_comment_mode_labels(driver)
    if any(label in {"所有留言", "全部留言", "All comments"} for label in before):
        return {
            "before": before,
            "opened": None,
            "selected": "already_all_comments_visible",
            "after": before,
            "verified": True,
        }

    opened = None
    selected = None
    after: list[str] = []
    after_reopen: list[str] = []
    verified = False

    for _ in range(2):
        if not opened:
            opened = click_first_text(driver, ["最相關", "相關性最高", "Most relevant"])
            if opened:
                slow_sleep(4, 8)
                if snapshot_prefix:
                    save_html_snapshot(driver, f"{snapshot_prefix}-dropdown-open")
        selected = click_first_text(driver, ["所有留言", "全部留言", "All comments"]) or selected
        if selected:
            slow_sleep(5, 10)
            if snapshot_prefix:
                save_html_snapshot(driver, f"{snapshot_prefix}-after-select")
        after = get_comment_mode_labels(driver)
        verified = any(label in {"所有留言", "全部留言", "All comments"} for label in after)
        # 點「所有留言」後 sort button 可能改成「由新到舊」，通知消失即代表成功
        if not verified and selected in {"所有留言", "全部留言", "All comments"}:
            notification_gone = not any("可能已過濾" in l or "may have been filtered" in l for l in after)
            verified = notification_gone and not any("最相關" in l or "Most relevant" in l for l in after)
        if not verified and selected:
            reopened = click_first_text(driver, ["所有留言", "全部留言", "最相關", "相關性最高", "Most relevant", "All comments"])
            if reopened:
                slow_sleep(2, 4)
                after_reopen = get_comment_mode_labels(driver)
                verified = any(label in {"所有留言", "全部留言", "All comments"} for label in after_reopen)
                if not verified and reopened in {"所有留言", "全部留言", "All comments"}:
                    verified = not any("最相關" in l or "Most relevant" in l for l in after_reopen)
        if verified:
            break
        slow_sleep(2, 4)

    return {
        "before": before,
        "opened": opened,
        "selected": selected,
        "after": after,
        "after_reopen": after_reopen,
        "verified": verified,
    }


def has_no_comments_message(driver: webdriver.Firefox) -> str | None:
    script = """
    () => {
      const bodyText = ((document.body && document.body.innerText) || '').trim();
      if (bodyText.includes('尚無留言')) return '尚無留言';
      if (bodyText.includes('留言搶頭香')) return '留言搶頭香';
      return null;
    }
    """
    return driver.execute_script(f"return ({script})();")


def click_more_comment_controls(driver: webdriver.Firefox) -> list[str]:
    script = """
    () => {
      const labels = [
        '查看更多留言',
        '更多留言',
        'See more comments',
        'View more comments',
        'View previous comments',
        '查看更多回覆',
        '更多回覆',
        'See more replies',
        'View more replies',
      ];
      const clicked = [];
      const els = [...document.querySelectorAll('a, button, div[role="button"], span')];
      for (const el of els) {
        const text = ((el.innerText || el.textContent || '').trim());
        if (!text) continue;
        if (!labels.some(label => text.includes(label))) continue;
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) continue;
        try {
          el.click();
          clicked.push(text);
        } catch (err) {}
      }
      return clicked;
    }
    """
    return driver.execute_script(f"return ({script})();")


def scroll_comment_pane(driver: webdriver.Firefox) -> dict:
    script = """
    () => {
      function isVisible(el) {
        const rect = el.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
      }

      function pickAnchor() {
        const labels = ['所有留言', '全部留言', 'All comments', '最相關', '相關性最高', 'Most relevant', '留言'];
        const els = [...document.querySelectorAll('a, button, div[role="button"], span, div')];
        return els.find(el => {
          const text = ((el.innerText || el.textContent || '').trim());
          return text && labels.some(label => text.includes(label)) && isVisible(el);
        }) || null;
      }

      function candidateScore(el, anchor) {
        const rect = el.getBoundingClientRect();
        let score = 0;
        if (el.scrollHeight > el.clientHeight + 80) score += 5;
        if (rect.height > 250) score += 2;
        const text = (el.innerText || '').trim();
        if (text.includes('留言')) score += 3;
        if (text.includes('查看更多留言') || text.includes('更多留言')) score += 3;
        if (text.length > 200) score += 1;
        if (anchor && el.contains(anchor)) score += 8;
        return score;
      }

      const anchor = pickAnchor();
      const candidates = [];
      const all = [...document.querySelectorAll('div, section, article')];
      for (const el of all) {
        if (!(el instanceof HTMLElement) || !isVisible(el)) continue;
        const score = candidateScore(el, anchor);
        if (score >= 8) {
          candidates.push({
            el,
            score,
            scrollTop: el.scrollTop,
            scrollHeight: el.scrollHeight,
            clientHeight: el.clientHeight,
            overflow: el.scrollHeight - el.clientHeight,
            tag: el.tagName,
            containsAnchor: !!(anchor && el.contains(anchor)),
          });
        }
      }

      const best = candidates.sort((a, b) =>
        (b.overflow - a.overflow) ||
        (b.score - a.score)
      )[0];

      if (!best) {
        window.scrollBy({top: 900, behavior: 'smooth'});
        return {found: false, fallbackWindow: true};
      }

      const delta = Math.max(500, Math.floor(best.clientHeight * 0.85));
      const beforeTop = best.el.scrollTop;
      best.el.scrollTop = Math.min(best.el.scrollHeight, best.el.scrollTop + delta);
      const afterTop = best.el.scrollTop;
      return {
        found: true,
        fallbackWindow: false,
        tag: best.tag,
        delta,
        beforeTop,
        afterTop,
        clientHeight: best.clientHeight,
        scrollHeight: best.scrollHeight,
        overflow: best.overflow,
        score: best.score,
      };
    }
    """
    return driver.execute_script(f"return ({script})();")


def wait_for_search_results(driver: webdriver.Firefox, timeout: int = 30) -> None:
    wait = WebDriverWait(driver, timeout)
    wait.until(
        lambda d: d.execute_script(
            """
            return document.body && document.body.innerText && (
              document.body.innerText.includes('搜尋結果') ||
              document.body.innerText.includes('最新貼文')
            );
            """
        )
    )


def normalize_post_url(url: str) -> str:
    url = url.split("&__")[0]
    url = url.replace("&amp;", "&")
    return url


def extract_visible_post_candidates(driver: webdriver.Firefox) -> list[dict]:
    script = """
    () => {
      const anchors = [...document.querySelectorAll('a[href]')];
      const hits = [];
      const seen = new Set();
      for (const a of anchors) {
        const href = a.href || '';
        if (!href.includes('facebook.com')) continue;
        if (!(href.includes('/photo/?fbid=') || href.includes('permalink') || href.includes('/posts/') || href.includes('story.php'))) continue;
        if (seen.has(href)) continue;
        seen.add(href);
        let n = a;
        let text = '';
        for (let i = 0; i < 8 && n; i++, n = n.parentElement) {
          const t = (n.innerText || '').trim();
          if (t.length > 80) {
            text = t;
            break;
          }
        }
        hits.push({href, text});
      }
      return hits;
    }
    """
    return driver.execute_script(f"return ({script})();")


def has_keyword(text: str) -> bool:
    return "海底電纜" in text or "海纜" in text


def clean_lines(raw_text: str) -> list[str]:
    lines = []
    for line in raw_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line == "Facebook":
            continue
        if len(line) == 1 and re.match(r"[\da-zA-Z年月日時分秒上下午·]", line):
            continue
        lines.append(line)
    return lines


def parse_candidate(raw: dict, source_query: str) -> PostRecord | None:
    text = raw.get("text", "")
    if not text or not has_keyword(text):
        return None
    lines = clean_lines(text)
    if not lines:
        return None
    source_name = lines[0]
    time_text = ""
    for line in lines[1:10]:
        if any(token in line for token in ["分鐘", "小時", "年", "月", "日", "週"]):
            time_text = line
            break
    body_candidates = [line for line in lines if has_keyword(line) and "搜尋結果" not in line]
    post_text = body_candidates[0] if body_candidates else " ".join(lines[1:8])
    metrics = re.findall(r"\b\d[\d,]*\b", text)
    like_count = metrics[-3] if len(metrics) >= 3 else ""
    comment_count = metrics[-2] if len(metrics) >= 2 else ""
    share_count = metrics[-1] if len(metrics) >= 1 else ""
    return PostRecord(
        post_url=normalize_post_url(raw["href"]),
        source_name=source_name,
        post_time_text=time_text,
        post_text=post_text,
        like_count_text=like_count,
        comment_count_text=comment_count,
        share_count_text=share_count,
        collection_method="facebook_logged_in_search_top_latest_posts",
        source_query=source_query,
        raw_text=text,
    )


def upsert_queue_item(post: PostRecord) -> None:
    queue = load_json(QUEUE_PATH) or {"generated_at": now_iso(), "records": []}
    records = queue.setdefault("records", [])
    existing = next((r for r in records if r["post_url"] == post.post_url), None)
    payload = {
        "post_url": post.post_url,
        "source_name": post.source_name,
        "source_query": post.source_query,
        "status": "pending",
        "discovered_at": now_iso(),
        "last_attempted_at": None,
        "notes": "",
    }
    if existing is None:
        records.append(payload)
    queue["updated_at"] = now_iso()
    write_json(QUEUE_PATH, queue)


def load_queue_records() -> list[dict]:
    data = load_json(QUEUE_PATH)
    return data.get("records", []) if isinstance(data, dict) else []


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


def slow_scroll(driver: webdriver.Firefox, rounds: int = 5, snapshot_prefix: str | None = None) -> None:
    for idx in range(rounds):
        delta = random.randint(500, 900)
        driver.execute_script("window.scrollBy({top: arguments[0], behavior: 'smooth'});", delta)
        slow_sleep(7, 14)
        if snapshot_prefix:
            save_html_snapshot(driver, f"{snapshot_prefix}-scroll-{idx+1}")


def count_visible_comment_blocks(driver: webdriver.Firefox) -> int:
    script = """
    () => {
      const out = [];
      const els = [...document.querySelectorAll('div, article, ul > li')];
      for (const el of els) {
        const t = (el.innerText || '').trim();
        if (!t) continue;
        if (t.length < 12 || t.length > 900) continue;
        if (!t.includes('\\n')) continue;
        if (t.includes('留言……') || t.includes('留言...')) continue;
        if (t.includes('最相關') || t.includes('所有留言') || t.includes('全部留言')) continue;
        out.push(t);
      }
      return [...new Set(out)].length;
    }
    """
    return int(driver.execute_script(f"return ({script})();"))


def slow_comment_scroll(
    driver: webdriver.Firefox,
    max_rounds: int = 100,
    stable_round_limit: int = 3,
    snapshot_prefix: str | None = None,
) -> list[dict]:
    observations = []
    stable_rounds = 0
    last_visible_count = -1
    for idx in range(max_rounds):
        clicked = click_more_comment_controls(driver)
        slow_sleep(2, 4)
        scroll_info = scroll_comment_pane(driver)
        slow_sleep(7, 14)
        visible_count = count_visible_comment_blocks(driver)
        grew = visible_count > last_visible_count
        if grew:
            stable_rounds = 0
        else:
            stable_rounds += 1
        last_visible_count = visible_count
        observations.append(
            {
                "round": idx + 1,
                "clicked": clicked,
                "scroll_info": scroll_info,
                "visible_count": visible_count,
                "grew": grew,
                "stable_rounds": stable_rounds,
            }
        )
        if snapshot_prefix:
            save_html_snapshot(driver, f"{snapshot_prefix}-comment-scroll-{idx+1}")
        if stable_rounds >= stable_round_limit and not clicked and scroll_info.get("afterTop") == scroll_info.get("beforeTop"):
            break
    return observations


def collect_search_results(driver: webdriver.Firefox, source_query: str, max_idle_rounds: int = 4) -> list[PostRecord]:
    seen: dict[str, PostRecord] = {}
    idle_rounds = 0
    round_no = 0
    while idle_rounds < max_idle_rounds:
        round_no += 1
        before = len(seen)
        save_html_snapshot(driver, f"search-round-{round_no}-before")
        raw_hits = extract_visible_post_candidates(driver)
        keyword_hits = 0
        for raw in raw_hits:
            parsed = parse_candidate(raw, source_query)
            if not parsed:
                continue
            keyword_hits += 1
            seen.setdefault(parsed.post_url, parsed)
        after = len(seen)
        if raw_hits and keyword_hits == 0:
            save_html_snapshot(driver, f"search-round-{round_no}-no-keyword-stop")
            break
        if after == before:
            idle_rounds += 1
        else:
            idle_rounds = 0
        slow_scroll(driver, rounds=5, snapshot_prefix=f"search-round-{round_no}")
    return list(seen.values())


def extract_post_page_bundle(driver: webdriver.Firefox, parent_url: str) -> tuple[PostPageRecord, list[CommentRecord]]:
    body_text = driver.find_element("tag name", "body").text
    lines = [line.strip() for line in body_text.split("\n") if line.strip()]
    snapshot_before = save_html_snapshot(driver, f"post-{slugify(parent_url)}-before")
    comments: list[CommentRecord] = []

    comment_anchor = next((idx for idx, line in enumerate(lines) if line == "留言"), -1)
    if comment_anchor != -1:
        tail = lines[comment_anchor + 1 :]
        cleaned_tail = []
        for line in tail:
            if line in {"留言……", "留言...", "最相關", "最新", "Facebook", "分享", "讚"}:
                continue
            cleaned_tail.append(line)
        i = 0
        while i + 2 < len(cleaned_tail):
            author = cleaned_tail[i]
            time_text = cleaned_tail[i + 1]
            text = cleaned_tail[i + 2]
            if author in {"尚無留言", "留言搶頭香！"}:
                i += 1
                continue
            if len(text) < 2:
                i += 1
                continue
            comments.append(
                CommentRecord(
                    parent_post_url=parent_url,
                    author_name=author,
                    comment_time_text=time_text,
                    comment_text=text,
                    collection_method="facebook_logged_in_post_page_body_parse",
                )
            )
            i += 3

    snapshot_after = save_html_snapshot(driver, f"post-{slugify(parent_url)}-after")
    page = PostPageRecord(
        post_url=parent_url,
        page_title=driver.title,
        page_body_text=body_text,
        comments_observed=len(comments),
        snapshot_before=snapshot_before,
        snapshot_after=snapshot_after,
    )
    return page, comments


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--search-url", action="append", dest="search_urls")
    parser.add_argument("--skip-search", action="store_true")
    args = parser.parse_args()
    search_urls = args.search_urls or SEARCH_URLS

    random.seed()
    driver = build_driver()
    posts: list[PostRecord] = []
    post_pages: list[PostPageRecord] = []
    comments: list[CommentRecord] = []
    seen_urls = set()
    try:
        if not args.skip_search:
            for url in search_urls:
                write_run_state(stage="search", current_query=url, posts_seen=len(posts), comments_seen=len(comments))
                driver.get(url)
                slow_sleep(8, 14)
                wait_for_search_results(driver)
                click_first_text(driver, ["最新貼文", "貼文"])
                slow_sleep(5, 10)
                for post in collect_search_results(driver, url):
                    if post.post_url in seen_urls:
                        continue
                    seen_urls.add(post.post_url)
                    posts.append(post)
                    upsert_queue_item(post)
                write_run_state(stage="search_complete", current_query=url, posts_seen=len(posts), comments_seen=len(comments))

        for record in load_queue_records():
            if record.get("status") != "pending":
                continue
            post_url = record["post_url"]
            write_run_state(
                stage="post",
                current_post_url=post_url,
                posts_seen=len(posts),
                comments_seen=len(comments),
            )
            mark_queue_status(post_url, "crawling")
            driver.get(post_url)
            slow_sleep(9, 16)
            no_comments_reason = has_no_comments_message(driver)
            comments_mode = ""
            comments_mode_verified = False
            scroll_observations = []
            if not no_comments_reason:
                mode_result = ensure_all_comments_mode(driver, snapshot_prefix=f"post-{slugify(post_url)}")
                comments_mode = mode_result.get("selected") or ""
                comments_mode_verified = bool(mode_result.get("verified"))
                no_comments_reason = has_no_comments_message(driver)
                if not comments_mode_verified:
                    mode_note = (
                        f"failed_comment_mode_switch:"
                        f"before={mode_result.get('before')};"
                        f"opened={mode_result.get('opened')};"
                        f"selected={mode_result.get('selected')};"
                        f"after={mode_result.get('after')}"
                    )
                    mark_queue_status(post_url, "failed", notes=mode_note)
                    slow_sleep(3, 5)
                    continue
            if not no_comments_reason:
                scroll_observations = slow_comment_scroll(
                    driver,
                    max_rounds=100,
                    stable_round_limit=3,
                    snapshot_prefix=f"post-{slugify(post_url)}",
                )
            page, page_comments = extract_post_page_bundle(driver, post_url)
            post_pages.append(page)
            comments.extend(page_comments)
            note = f"comments_added={len(page_comments)}"
            if no_comments_reason:
                note += f";no_comments={no_comments_reason}"
            if comments_mode:
                note += f";comments_mode={comments_mode}"
            note += f";comments_mode_verified={comments_mode_verified}"
            note += f";comment_scroll_rounds={len(scroll_observations)}"
            mark_queue_status(post_url, "crawled", notes=note)
            slow_sleep(6, 10)
    finally:
        write_run_state(stage="finished", posts_seen=len(posts), comments_seen=len(comments))
        driver.quit()

    output = {
        "generated_at": now_iso(),
        "snapshot_dir": str(SNAPSHOT_DIR),
        "posts": [asdict(p) for p in posts],
        "post_pages": [asdict(p) for p in post_pages],
        "comments": [asdict(c) for c in comments],
    }
    write_json(RAW_OUTPUT_PATH, output)
    print(RAW_OUTPUT_PATH)
    print(f"posts={len(posts)} post_pages={len(post_pages)} comments={len(comments)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
