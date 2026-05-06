#!/usr/bin/env python3
"""Label original Threads posts with 8-category post_type taxonomy using Batch API.

Usage:
    python3 label_posts.py submit
    python3 label_posts.py status [id...]
    python3 label_posts.py fetch  [id...]
    python3 label_posts.py merge          # write post_type into comments-labeled-v2.json
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

ROOT = Path(__file__).resolve().parent
POSTS_FILE      = ROOT / "normalized" / "threads-posts-156.json"
BATCH_STATE_FILE= ROOT / "normalized" / "label-posts-batch-state.json"
OUT_FILE        = ROOT / "normalized" / "threads-posts-labeled.json"
COMMENTS_FILE   = ROOT / "normalized" / "comments-labeled-v2.json"

MODEL = "claude-haiku-4-5"

SYSTEM_PROMPT = """你是台灣媒體研究助理，負責分類 Threads 上關於海底電纜的貼文。

對每篇貼文，輸出一個 JSON 物件，只包含一個欄位：

post_type（貼文主題類型，選一個）
  可能值：
  "中國破壞事件"       - 報導或討論中國切斷、破壞或疑似介入海纜事件的具體案例
  "意外/非蓄意斷纜事件" - 報導或討論錨害、地震、漁網等意外原因造成的斷纜
  "海纜狀態更新"       - 分享海纜修復進度、目前損壞狀況等動態
  "政府政策與回應"     - 討論政府、NCC、立法院對海纜問題的政策或回應
  "備援與韌性"         - 討論低軌衛星、備援方案、海纜韌性強化等
  "闢謠/查核"          - 針對海纜相關謠言或錯誤認知進行澄清
  "國際案例"           - 報導台灣以外（波羅的海、紅海等）的海纜斷裂事件
  "其他"               - 無法歸入以上類別

注意：
- 若貼文同時涉及多個主題，選最主要的一個。
- 若貼文提及中國但語氣是分析可能性（「懷疑」「可能是中國」），仍選「中國破壞事件」。
- 若貼文只是個人感嘆網路慢、與海纜無實質內容關聯，選「其他」。
- 只輸出純 JSON 物件，不要 markdown 代碼框、不要任何其他文字。

範例輸出：
{"post_type":"中國破壞事件"}"""

USER_TEMPLATE = "【貼文】{post_text}"


def cmd_submit() -> None:
    client = anthropic.Anthropic()
    posts = json.loads(POSTS_FILE.read_text(encoding="utf-8"))["posts"]
    print(f"Loaded {len(posts)} posts")

    requests = []
    for post_id, text in posts.items():
        requests.append({
            "custom_id": post_id,
            "params": {
                "model": MODEL,
                "max_tokens": 40,
                "system": [{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
                "messages": [{"role": "user", "content": USER_TEMPLATE.format(post_text=text[:400])}],
            },
        })

    print(f"Submitting {len(requests)} requests...")
    batch = client.messages.batches.create(requests=requests)
    print(f"  batch_id: {batch.id}  status: {batch.processing_status}")

    state = {
        "submitted_at": datetime.now().astimezone().isoformat(),
        "model": MODEL,
        "total_posts": len(posts),
        "batch_id": batch.id,
    }
    BATCH_STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"State saved -> {BATCH_STATE_FILE}")


def cmd_status(*batch_ids: str) -> None:
    client = anthropic.Anthropic()
    if not batch_ids:
        batch_ids = [json.loads(BATCH_STATE_FILE.read_text())["batch_id"]]
    for bid in batch_ids:
        batch = client.messages.batches.retrieve(bid)
        rc = batch.request_counts
        print(f"{bid}  status={batch.processing_status}  "
              f"processing={rc.processing}  succeeded={rc.succeeded}  "
              f"errored={rc.errored}  expired={rc.expired}")


def cmd_fetch(*batch_ids: str) -> None:
    client = anthropic.Anthropic()
    if not batch_ids:
        batch_ids = [json.loads(BATCH_STATE_FILE.read_text())["batch_id"]]

    results: dict[str, str] = {}
    for bid in batch_ids:
        batch = client.messages.batches.retrieve(bid)
        if batch.processing_status != "ended":
            print(f"Batch {bid} not done yet: {batch.processing_status}")
            continue
        print(f"Fetching results for {bid}...")
        for result in client.messages.batches.results(bid):
            if result.result.type == "succeeded":
                raw = result.result.message.content[0].text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                try:
                    results[result.custom_id] = json.loads(raw).get("post_type", "其他")
                except Exception:
                    results[result.custom_id] = "其他"
            else:
                results[result.custom_id] = "ERROR"

    OUT_FILE.write_text(json.dumps({
        "generated_at": datetime.now().astimezone().isoformat(),
        "count": len(results),
        "results": results,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(results)} post labels -> {OUT_FILE}")

    print("\n-- post_type distribution --")
    for val, n in Counter(results.values()).most_common():
        print(f"  {val}: {n} ({100*n/len(results):.1f}%)")


def cmd_merge() -> None:
    # Map post_id -> post_type
    labeled = json.loads(OUT_FILE.read_text(encoding="utf-8"))["results"]

    # Build post_url -> post_id mapping from snapshot filenames
    import re
    from pathlib import Path as P
    TH_SNAPSHOT_ROOT = ROOT / "raw" / "threads-logged-in-html"
    post_id_to_url: dict[str, str] = {}

    th_data = json.loads((ROOT / "normalized" / "threads-comments-from-snapshots-2026-04-29.json").read_text(encoding="utf-8"))
    # Build url -> post_id from snapshot filenames in records
    for r in th_data["records"]:
        src = r.get("source_file", "")
        m = re.search(r'\d{6}-post-([A-Za-z0-9_-]+)-round', src)
        if m:
            pid = m.group(1)
            # post_url is the comment permalink; we need to know which post this comment belongs to
            # We'll map by post_id from filename
            if pid not in post_id_to_url:
                post_id_to_url[pid] = []
            # Collect source files per post_id

    # Actually: map comment record -> post_id (from source_file) -> post_type
    data = json.loads(COMMENTS_FILE.read_text(encoding="utf-8"))
    changed = 0
    missing = 0
    for r in data["records"]:
        if r.get("platform") != "threads":
            continue
        src = r.get("source_file", "")
        m = re.search(r'\d{6}-post-([A-Za-z0-9_-]+)-round', src)
        if m:
            pid = m.group(1)
            pt = labeled.get(pid)
            if pt and pt != "ERROR":
                r["post_type"] = pt
                changed += 1
            else:
                missing += 1
        else:
            missing += 1

    data["labeled_post_type_at"] = datetime.now().astimezone().isoformat()
    COMMENTS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Merged: {changed} records updated, {missing} missing -> {COMMENTS_FILE}")

    print("\n-- post_type distribution in comments --")
    pt_counts = Counter(r.get("post_type", "(none)") for r in data["records"] if r.get("platform") == "threads")
    for val, n in pt_counts.most_common():
        print(f"  {val}: {n}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    args = sys.argv[2:]

    if cmd == "submit":
        cmd_submit()
    elif cmd == "status":
        cmd_status(*args)
    elif cmd == "fetch":
        cmd_fetch(*args)
    elif cmd == "merge":
        cmd_merge()
    else:
        print(__doc__)
