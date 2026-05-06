#!/usr/bin/env python3
"""Re-label misconception_type only, using Batch API.

Usage:
    python3.12 relabel_misconception.py submit
    python3.12 relabel_misconception.py status [id...]
    python3.12 relabel_misconception.py fetch  [id...]
    python3.12 relabel_misconception.py merge          # merge into comments-labeled-v2.json
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
IN_FILE    = ROOT / "normalized" / "comments-labeled-v2.json"
BATCH_STATE_FILE = ROOT / "normalized" / "relabel-misconception-batch-state.json"
OUT_FILE   = ROOT / "normalized" / "misconception-relabeled.json"

MODEL = "claude-haiku-4-5"
MAX_BATCH_SIZE = 10_000

SYSTEM_PROMPT = """你是台灣媒體研究助理，負責判斷社群媒體留言中是否有對海底電纜的錯誤認知。

對每則留言，輸出一個 JSON 物件，只包含一個欄位：

misconception_type（留言中是否有可辨識的錯誤認知，選一個）
  可能值：
  "把海底電纜想成可輕易切斷的一般電線"
  "認為斷一條就等於全面斷網"
  "認為修復應該很快完成"
  "把所有斷纜都直接推定為敵對攻擊"
  "混淆海纜與其他基礎設施概念"
  "認為網路慢一定跟海纜被破壞有關"
  "其他"
  "無"
  "無法判斷"

注意：
- misconception_type 只記錄留言者本人的錯誤認知，不是他在批評或糾正的對象的認知。若留言在指出他人的錯誤，填「無」。
- 「混淆海纜與其他基礎設施概念」僅限於誤解海纜的物理性質（如「海纜就是一般電線吧？」「衛星現在不就能完全替代了嗎？」）。推薦星鏈或衛星作為備援方案是正確的認知，填「無」。
- 「把所有斷纜都直接推定為敵對攻擊」：若留言語氣是直接斷定某次斷纜事件是中國或敵對勢力所為（不含「可能」「懷疑」「擔心」等保留語氣），填此值。單純對中國感到憤怒、或表達擔憂，填「無」。
- 「認為網路慢一定跟海纜被破壞有關」：若留言抱怨個人網路緩慢（家用WiFi、手機、串流、遊戲），並將其歸因於海纜斷裂，填此值。
- 只輸出純 JSON 物件，不要 markdown 代碼框、不要任何其他文字。

範例輸出：
{"misconception_type":"無"}"""

USER_TEMPLATE = "【貼文】{post_text}\n\n【留言】{comment_text}"


def load_records() -> list[dict]:
    return json.loads(IN_FILE.read_text(encoding="utf-8"))["records"]


def cmd_submit() -> None:
    client = anthropic.Anthropic()
    records = load_records()
    print(f"Loaded {len(records)} records")

    chunks = [records[i:i + MAX_BATCH_SIZE] for i in range(0, len(records), MAX_BATCH_SIZE)]
    batch_ids = []

    for chunk_idx, chunk in enumerate(chunks):
        requests = []
        for r in chunk:
            requests.append({
                "custom_id": r["id"],
                "params": {
                    "model": MODEL,
                    "max_tokens": 40,
                    "system": [{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
                    "messages": [{"role": "user", "content": USER_TEMPLATE.format(
                        post_text=r.get("post_text", "")[:200],
                        comment_text=r.get("comment_text", "")[:300],
                    )}],
                },
            })
        print(f"Submitting batch {chunk_idx + 1}/{len(chunks)} ({len(requests)} requests)...")
        batch = client.messages.batches.create(requests=requests)
        batch_ids.append(batch.id)
        print(f"  batch_id: {batch.id}  status: {batch.processing_status}")

    state = {
        "submitted_at": datetime.now().astimezone().isoformat(),
        "model": MODEL,
        "total_records": len(records),
        "batch_ids": batch_ids,
    }
    BATCH_STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nState saved -> {BATCH_STATE_FILE}")
    print(f"Run:  python3.12 relabel_misconception.py status {' '.join(batch_ids)}")


def cmd_status(*batch_ids: str) -> None:
    client = anthropic.Anthropic()
    if not batch_ids:
        batch_ids = json.loads(BATCH_STATE_FILE.read_text())["batch_ids"]
    for bid in batch_ids:
        batch = client.messages.batches.retrieve(bid)
        rc = batch.request_counts
        print(f"{bid}  status={batch.processing_status}  "
              f"processing={rc.processing}  succeeded={rc.succeeded}  "
              f"errored={rc.errored}  expired={rc.expired}")


def cmd_fetch(*batch_ids: str) -> None:
    client = anthropic.Anthropic()
    if not batch_ids:
        batch_ids = json.loads(BATCH_STATE_FILE.read_text())["batch_ids"]

    results: dict[str, str] = {}  # id -> misconception_type

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
                    results[result.custom_id] = json.loads(raw).get("misconception_type", "無")
                except Exception:
                    results[result.custom_id] = "無"
            else:
                results[result.custom_id] = "ERROR"

    OUT_FILE.write_text(json.dumps({
        "generated_at": datetime.now().astimezone().isoformat(),
        "count": len(results),
        "results": results,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(results)} misconception labels -> {OUT_FILE}")

    print("\n-- misconception_type (new) --")
    for val, n in Counter(results.values()).most_common():
        print(f"  {val}: {n} ({100*n/len(results):.1f}%)")


def cmd_merge() -> None:
    new_labels = json.loads(OUT_FILE.read_text(encoding="utf-8"))["results"]
    data = json.loads(IN_FILE.read_text(encoding="utf-8"))

    changed = 0
    for r in data["records"]:
        new_val = new_labels.get(r["id"])
        if new_val and new_val != "ERROR" and new_val != r.get("misconception_type"):
            r["misconception_type"] = new_val
            changed += 1

    data["merged_misconception_at"] = datetime.now().astimezone().isoformat()
    IN_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Merged: {changed} records updated -> {IN_FILE}")

    print("\n-- misconception_type (after merge) --")
    for val, n in Counter(r["misconception_type"] for r in data["records"]).most_common():
        print(f"  {val}: {n} ({100*n/len(data['records']):.1f}%)")


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
