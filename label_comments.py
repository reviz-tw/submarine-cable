#!/usr/bin/env python3
"""Label sea-cable comments with multi-dimensional taxonomy using Claude Batch API.

Usage:
    python3.12 label_comments.py test            # label 50 comments directly, print results
    python3.12 label_comments.py submit          # submit full batch job
    python3.12 label_comments.py status [id...]  # check batch status
    python3.12 label_comments.py fetch  [id...]  # download results -> comments-labeled.json
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

ROOT = Path(__file__).resolve().parent
FB_FILE = ROOT / "normalized" / "facebook-comments-from-snapshots-2026-04-30.json"
TH_FILE = ROOT / "normalized" / "threads-comments-from-snapshots-2026-04-29.json"
BATCH_STATE_FILE = ROOT / "normalized" / "label-batch-state-v2.json"
OUT_FILE = ROOT / "normalized" / "comments-labeled-v2.json"

MODEL = "claude-haiku-4-5"

SYSTEM_PROMPT = """你是台灣媒體研究助理，負責分析社群媒體留言對海底電纜議題的認知。

對每則留言，輸出一個 JSON 物件，包含以下四個欄位：

────────────────────────────────────────
topic_label（留言談論的主題）
  可能值（選一個）：
  "海底電纜的功能與重要性"
  "斷纜原因"
  "修復方式與難度"
  "備援通訊與韌性"
  "國安/灰色地帶衝突"
  "中國因素與敵意行動"
  "政府治理與政策"
  "媒體報導與資訊判讀"
  "其他"
  "無法判斷"

────────────────────────────────────────
belief_label（留言者對海底電纜的認知或信念，選一個最貼切的）
  可能值：
  "認為海底電纜很脆弱、容易被破壞"
  "認為斷纜多半是人為破壞"
  "認為斷纜常見於船隻/拖網/錨具"
  "認為中國可能蓄意破壞"
  "認為政府準備不足"
  "認為已有備援、不致全面斷網"
  "認為斷纜會直接導致全面通訊癱瘓"
  "對修復時間有明確認知"
  "對修復時間有錯誤期待"
  "將事件理解為政治操作/宣傳"
  "認為斷纜情況被誇大或錯誤報導"
  "沒有可辨識認知"
  "其他"
  "無法判斷"

────────────────────────────────────────
misconception_type（留言中是否有可辨識的錯誤認知，選一個或"無"）
  可能值：
  "把海底電纜想成可輕易切斷的一般電線"
  "認為斷一條就等於全面斷網"
  "認為修復應該很快完成"
  "把所有斷纜都直接推定為敵對攻擊"
  "混淆海纜與其他基礎設施概念（如誤以為海纜是輸電線、誤以為衛星已能完全取代海纜）"
  "認為網路慢一定跟海纜被破壞有關"
  "其他"
  "無"
  "無法判斷"

────────────────────────────────────────
stance_label（留言的情緒或態度傾向，選一個）
  可能值：
  "焦慮/恐慌"
  "憤怒/指責"
  "嘲諷/反串"
  "陰謀論傾向"
  "理性討論"
  "支持強硬回應"
  "無明顯態度"
  "其他"
  "無法判斷"

────────────────────────────────────────
solution_label（留言者是否涉及因應方式，選一個）
  可能值：
  "提供解方"
  "想知道解方"
  "無"

  注意：
  - 嘲諷或不切實際的建議（如「乾脆炸了算了」「直接槍斃」）仍算「提供解方」。
  - 純發洩憤怒填「無」；但帶有「為什麼沒有辦法？」「只能這樣嗎？」的問句，即使語氣是抱怨，仍算「想知道解方」。
  - 分享新聞連結或政策說明而沒有表達個人立場，填「無」。

────────────────────────────────────────

注意：
- 判斷依據以**留言內容為主**，貼文只是輔助脈絡參考。
- 每個欄位只選一個值，必須與上列完全一致。
- **不要強迫分類**：若留言內容不足以判斷某欄位，請填「無法判斷」（topic/belief/stance）或「無」（misconception）；尤其短留言、純日期、明顯離題的留言，寧可填「無法判斷」也不要硬套。
- **純日期或純數字**（如「2025-12-4」、「3」）沒有任何語意，四個欄位一律填「無法判斷」或「無」，不要根據貼文推測。
- **misconception_type 只記錄留言者本人的錯誤認知**，不是他在批評或糾正的對象的認知。若留言在指出他人的錯誤，此欄填「無」。「認為網路慢一定跟海纜被破壞有關」僅限於明顯無關的情況（如家用 WiFi、4G 個人熱點），若有可能成立則填「無」。
- **若 stance 為「嘲諷/反串」，belief_label 應反映留言者本人的立場**，而非其嘲諷對象的立場。例如「趕快甩鍋大陸」是在諷刺歸因中國的人，留言者本人的 belief 應是「將事件理解為政治操作/宣傳」而非「認為中國可能蓄意破壞」。
- **隱含的網路體驗留言**：若留言是抱怨網路緩慢、YT 卡頓、遊戲 ping 高等連線問題，且【貼文】明確是關於海纜斷裂，即使留言沒有明說兩者關聯，belief 可標記為「認為網路慢一定跟海纜被破壞有關」，topic 標記為「斷纜原因」。
- **「混淆海纜與其他基礎設施概念」僅限於誤解海纜的物理性質**（如「海纜就是一般電線吧？」「衛星現在不就能完全替代了嗎？」）。推薦星鏈或衛星作為備援方案是正確的認知，填「無」。
- **質疑本身就是一種認知立場**，不應填「無法判斷」或「沒有可辨識認知」。若留言對事件的歸因、規模或媒體說法表達了懷疑或不信任，即使是問句或否定句，仍應找對應的 belief 標記。「無法判斷」僅限於：留言完全無法推斷留言者對海纜議題的看法（純情緒抒發、完全離題、純數字）。「沒有可辨識認知」僅限於：留言有在談海纜，但沒有表達任何具體立場。
- **「認為斷纜情況被誇大或錯誤報導」vs「將事件理解為政治操作/宣傳」**：前者適用於留言者要求驗證、對說法存疑、或認為消息不可靠（如「怎麼證明？」「先確認是不是人為再說」「來源？」）；後者僅適用於留言者明確認為整件事被政治力量刻意操弄或用來宣傳（如「又在炒議題」「選舉到了就有事」）。單純的質疑或存疑不等於認為有政治操作。
- 只輸出純 JSON 物件，不要 markdown 代碼框、不要任何其他文字。

範例輸出：
{"topic_label":"中國因素與敵意行動","belief_label":"認為中國可能蓄意破壞","misconception_type":"無","stance_label":"憤怒/指責","solution_label":"無"}"""

USER_TEMPLATE = "【貼文】{post_text}\n\n【留言】{comment_text}"

MAX_BATCH_SIZE = 10_000


def load_comments() -> list[dict]:
    records = []
    for platform_file, platform in [(FB_FILE, "facebook"), (TH_FILE, "threads")]:
        data = json.loads(platform_file.read_text(encoding="utf-8"))
        for i, r in enumerate(data["records"]):
            records.append({
                "id": f"{platform}_{i}",
                "platform": platform,
                "post_url": r.get("post_url", ""),
                "post_text": r.get("post_text", ""),
                "author_name": r.get("author_name", ""),
                "comment_time_text": r.get("comment_time_text", ""),
                "comment_text": r.get("comment_text", ""),
                "source_file": r.get("source_file", ""),
            })
    return records


def build_batch_requests(records: list[dict]) -> list[dict]:
    requests = []
    for r in records:
        user_content = USER_TEMPLATE.format(
            post_text=r.get("post_text", "")[:300],
            comment_text=r["comment_text"][:300],
        )
        requests.append({
            "custom_id": r["id"],
            "params": {
                "model": MODEL,
                "max_tokens": 160,
                "system": [
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                "messages": [
                    {"role": "user", "content": user_content}
                ],
            },
        })
    return requests


# Haiku rate limit: 2000 RPM / 200K TPM. Each request ~600 tokens.
# 1 req/sec → well within limits for a small test.
_MIN_INTERVAL = 1.0  # seconds between requests


def cmd_test(n: int = 50) -> None:
    import random
    client = anthropic.Anthropic()
    comments = load_comments()
    sample = random.sample(comments, min(n, len(comments)))
    print(f"Testing {len(sample)} comments with {MODEL}...\n")

    results = []
    last_call = 0.0
    for i, r in enumerate(sample):
        elapsed = time.monotonic() - last_call
        if elapsed < _MIN_INTERVAL:
            time.sleep(_MIN_INTERVAL - elapsed)

        user_content = USER_TEMPLATE.format(
            post_text=r.get("post_text", "")[:300],
            comment_text=r["comment_text"][:300],
        )
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=128,
                system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": user_content}],
            )
            last_call = time.monotonic()
            raw = resp.content[0].text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            parsed = json.loads(raw)
        except Exception as e:
            parsed = {"error": str(e)}

        print(f"[{i+1:02d}] {r['comment_text']!r}")
        print(f"      → {parsed}")
        print()
        results.append({**r, **parsed})

    out = Path("normalized/comments-labeled-test.json")
    out.write_text(json.dumps({"count": len(results), "records": results},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(results)} test results → {out}")


def cmd_submit() -> None:
    client = anthropic.Anthropic()
    comments = load_comments()
    print(f"Loaded {len(comments)} comments")

    chunks = [comments[i:i + MAX_BATCH_SIZE] for i in range(0, len(comments), MAX_BATCH_SIZE)]
    batch_ids = []

    for chunk_idx, chunk in enumerate(chunks):
        requests = build_batch_requests(chunk)
        print(f"Submitting batch {chunk_idx + 1}/{len(chunks)} ({len(requests)} requests)...")
        batch = client.messages.batches.create(requests=requests)
        batch_ids.append(batch.id)
        print(f"  batch_id: {batch.id}  status: {batch.processing_status}")

    state = {
        "submitted_at": datetime.now().astimezone().isoformat(),
        "model": MODEL,
        "total_comments": len(comments),
        "batch_ids": batch_ids,
    }
    BATCH_STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nState saved -> {BATCH_STATE_FILE}")
    print(f"Run:  python3.12 label_comments.py status {' '.join(batch_ids)}")


def cmd_status(*batch_ids: str) -> None:
    client = anthropic.Anthropic()
    if not batch_ids:
        state = json.loads(BATCH_STATE_FILE.read_text())
        batch_ids = state["batch_ids"]
    for bid in batch_ids:
        batch = client.messages.batches.retrieve(bid)
        rc = batch.request_counts
        print(f"{bid}  status={batch.processing_status}  "
              f"processing={rc.processing}  succeeded={rc.succeeded}  "
              f"errored={rc.errored}  expired={rc.expired}")


def cmd_fetch(*batch_ids: str) -> None:
    client = anthropic.Anthropic()
    if not batch_ids:
        state = json.loads(BATCH_STATE_FILE.read_text())
        batch_ids = state["batch_ids"]

    comments_by_id = {r["id"]: r for r in load_comments()}
    results: list[dict] = []

    for bid in batch_ids:
        batch = client.messages.batches.retrieve(bid)
        if batch.processing_status != "ended":
            print(f"Batch {bid} not done yet: {batch.processing_status}")
            continue
        print(f"Fetching results for {bid}...")
        for result in client.messages.batches.results(bid):
            cid = result.custom_id
            comment = comments_by_id.get(cid, {})
            if result.result.type == "succeeded":
                raw = result.result.message.content[0].text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                try:
                    parsed = json.loads(raw)
                    label = {
                        "topic_label": parsed.get("topic_label", "無法判斷"),
                        "belief_label": parsed.get("belief_label", "沒有可辨識認知"),
                        "misconception_type": parsed.get("misconception_type", "無"),
                        "stance_label": parsed.get("stance_label", "無明顯態度"),
                        "solution_label": parsed.get("solution_label", "無"),
                    }
                except Exception:
                    label = {
                        "topic_label": "無法判斷",
                        "belief_label": "沒有可辨識認知",
                        "misconception_type": "無",
                        "stance_label": "無明顯態度",
                    }
            else:
                label = {
                    "topic_label": "ERROR",
                    "belief_label": "ERROR",
                    "misconception_type": "ERROR",
                    "stance_label": "ERROR",
                    "solution_label": "ERROR",
                }
            results.append({**comment, **label})

    results.sort(key=lambda r: r.get("id", ""))
    OUT_FILE.write_text(json.dumps({
        "generated_at": datetime.now().astimezone().isoformat(),
        "count": len(results),
        "records": results,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(results)} labeled records -> {OUT_FILE}")

    print("\n-- topic_label --")
    for val, n in Counter(r["topic_label"] for r in results).most_common():
        print(f"  {val}: {n} ({100*n/len(results):.1f}%)")
    print("\n-- belief_label --")
    for val, n in Counter(r["belief_label"] for r in results).most_common():
        print(f"  {val}: {n} ({100*n/len(results):.1f}%)")
    print("\n-- misconception_type --")
    for val, n in Counter(r["misconception_type"] for r in results).most_common():
        print(f"  {val}: {n} ({100*n/len(results):.1f}%)")
    print("\n-- stance_label --")
    for val, n in Counter(r["stance_label"] for r in results).most_common():
        print(f"  {val}: {n} ({100*n/len(results):.1f}%)")
    print("\n-- solution_label --")
    for val, n in Counter(r.get("solution_label", "無") for r in results).most_common():
        print(f"  {val}: {n} ({100*n/len(results):.1f}%)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    args = sys.argv[2:]

    if cmd == "test":
        cmd_test(int(args[0]) if args else 50)
    elif cmd == "submit":
        cmd_submit()
    elif cmd == "status":
        cmd_status(*args)
    elif cmd == "fetch":
        cmd_fetch(*args)
    else:
        print(__doc__)
