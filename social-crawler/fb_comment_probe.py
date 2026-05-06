#!/usr/bin/env python3

from __future__ import annotations

import json
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


URL = "https://www.facebook.com/photo/?fbid=1496569192127944&set=a.740746141043590"
OUT = Path("/Users/mac/oread/seacable/raw/facebook-debug-single/ntd-comment-probe.json")


def build_driver() -> webdriver.Firefox:
    opts = Options()
    opts.binary_location = "/Applications/Firefox.app/Contents/MacOS/firefox"
    opts.add_argument("-profile")
    opts.add_argument("/Users/mac/oread/seacable/.selenium-profile-firefox-worker-fb-debug")
    opts.add_argument("-no-remote")
    service = Service("/Users/mac/oread/seacable/tools/geckodriver")
    driver = webdriver.Firefox(service=service, options=opts)
    driver.set_window_position(120, 120)
    driver.set_window_size(1200, 900)
    return driver


def click_text(driver: webdriver.Firefox, labels: list[str]) -> str | None:
    return driver.execute_script(
        """
        const labels = arguments[0];
        const els = [...document.querySelectorAll('a, button, div[role="button"], span')];
        for (const label of labels) {
          const el = els.find(e => ((e.innerText || '').trim() === label) || ((e.textContent || '').trim() === label));
          if (el) {
            el.click();
            return label;
          }
        }
        return null;
        """,
        labels,
    )


def get_comment_mode_labels(driver: webdriver.Firefox) -> list[str]:
    return driver.execute_script(
        """
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
        """
    )


def ensure_all_comments_mode(driver: webdriver.Firefox) -> dict:
    before = get_comment_mode_labels(driver)
    if any(label in {"所有留言", "全部留言", "All comments"} for label in before):
        return {
            "before": before,
            "opened": None,
            "selected": "already_all_comments_visible",
            "after": before,
        }
    opened = click_text(driver, ["最相關", "相關性最高", "Most relevant"])
    if opened:
        time.sleep(4)
    selected = click_text(driver, ["所有留言", "全部留言", "All comments"])
    if selected:
        time.sleep(5)
    after = get_comment_mode_labels(driver)
    return {
        "before": before,
        "opened": opened,
        "selected": selected,
        "after": after,
    }


def click_more_controls(driver: webdriver.Firefox) -> list[str]:
    return driver.execute_script(
        """
        const labels = [
          '查看更多留言',
          '更多留言',
          '查看更多留言',
          'See more comments',
          'View more comments',
          'View previous comments',
          '查看更多回覆',
          '更多回覆',
          '查看更多回覆',
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
        """
    )


def scroll_comment_pane(driver: webdriver.Firefox) -> dict:
    return driver.execute_script(
        """
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
              className: el.className || '',
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
          className: best.className,
          delta,
          beforeTop,
          afterTop,
          clientHeight: best.clientHeight,
          scrollHeight: best.scrollHeight,
          overflow: best.overflow,
          score: best.score,
        };
        """
    )


def dump_scrollable_candidates(driver: webdriver.Firefox) -> list[dict]:
    return driver.execute_script(
        """
        function isVisible(el) {
          const rect = el.getBoundingClientRect();
          return rect.width > 0 && rect.height > 0;
        }

        const items = [];
        for (const el of document.querySelectorAll('div, section, article')) {
          if (!(el instanceof HTMLElement) || !isVisible(el)) continue;
          if (el.scrollHeight <= el.clientHeight + 20) continue;
          const text = (el.innerText || '').trim();
          items.push({
            tag: el.tagName,
            className: el.className || '',
            clientHeight: el.clientHeight,
            scrollHeight: el.scrollHeight,
            scrollTop: el.scrollTop,
            snippet: text.slice(0, 180),
          });
        }
        items.sort((a, b) => (b.scrollHeight - b.clientHeight) - (a.scrollHeight - a.clientHeight));
        return items.slice(0, 12);
        """
    )


def collect_blocks(driver: webdriver.Firefox) -> list[str]:
    return driver.execute_script(
        """
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
        const uniq = [];
        const seen = new Set();
        for (const t of out) {
          if (seen.has(t)) continue;
          seen.add(t);
          uniq.push(t);
          if (uniq.length >= 120) break;
        }
        return uniq;
        """
    )


def count_visible_blocks(driver: webdriver.Firefox) -> int:
    return len(collect_blocks(driver))


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    driver = build_driver()
    try:
        driver.get(URL)
        time.sleep(8)
        before_buttons = driver.execute_script(
            """
            const els = [...document.querySelectorAll('a, button, div[role="button"], span')];
            return els
              .map(e => ((e.innerText || e.textContent || '').trim()))
              .filter(Boolean)
              .filter(t => t.includes('留言') || t.includes('最相關') || t.includes('所有留言') || t.includes('全部留言') || t.includes('回覆'))
              .slice(0, 80);
            """
        )
        mode = ensure_all_comments_mode(driver)
        scrollable_candidates = dump_scrollable_candidates(driver)

        blocks_by_round = []
        stable_rounds = 0
        last_count = -1
        for i in range(100):
            clicked_more = click_more_controls(driver)
            time.sleep(2)
            blocks = collect_blocks(driver)
            scroll_info = scroll_comment_pane(driver)
            time.sleep(6)
            visible_count = count_visible_blocks(driver)
            grew = visible_count > last_count
            if grew:
                stable_rounds = 0
            else:
                stable_rounds += 1
            last_count = visible_count
            blocks_by_round.append(
                {
                    "round": i,
                    "count": len(blocks),
                    "visible_count": visible_count,
                    "grew": grew,
                    "stable_rounds": stable_rounds,
                    "head_sample": blocks[:6],
                    "tail_sample": blocks[-6:],
                    "clicked_more": clicked_more,
                    "scroll_info": scroll_info,
                }
            )
            if stable_rounds >= 3 and not clicked_more and scroll_info.get("afterTop") == scroll_info.get("beforeTop"):
                break

        body = driver.find_element(By.TAG_NAME, "body").text
        idx = body.find("留言")
        result = {
            "title": driver.title,
            "mode": mode,
            "before_buttons": before_buttons,
            "scrollable_candidates": scrollable_candidates,
            "comment_anchor_found": idx != -1,
            "comment_snippet": body[idx : idx + 800] if idx != -1 else body[:800],
            "blocks_by_round": blocks_by_round,
        }
        OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(OUT)
        return 0
    finally:
        driver.quit()


if __name__ == "__main__":
    raise SystemExit(main())
