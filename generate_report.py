#!/usr/bin/env python3
"""Generate HTML analysis report from comments-labeled-v2.json."""

import json
import html as html_lib
import re
from collections import Counter, defaultdict
from itertools import count
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IN_FILE = ROOT / "normalized" / "comments-labeled-v2.json"
OUT_FILE = ROOT / "report.html"
THREADS_POSTS_FILE = ROOT / "normalized" / "threads-posts-156.json"

DIMS = ["topic_label", "belief_label", "misconception_type", "stance_label", "solution_label"]
COMMENT_DIMS = ["belief_label", "misconception_type", "stance_label", "solution_label"]
DIM_NAMES = {
    "topic_label": "主題",
    "belief_label": "認知",
    "misconception_type": "錯誤認知",
    "stance_label": "情緒/態度",
    "solution_label": "解方",
    "post_type": "貼文類型",
}

POST_TYPES = [
    "中國破壞事件", "意外/非蓄意斷纜事件", "海纜狀態更新",
    "政府政策與回應", "備援與韌性", "闢謠/查核", "國際案例", "其他",
]
tab_id_counter = count(1)


def get_th_post_id(r):
    m = re.search(r"\d{6}-post-([A-Za-z0-9_-]+)-round", r.get("source_file", ""))
    return m.group(1) if m else None


def pct(n, total):
    return f"{100*n/total:.1f}%" if total else "0%"


def bar(n, total, width=120):
    w = int(width * n / total) if total else 0
    return f'<div class="bar" style="width:{w}px"></div>'


def freq_table(counter, title="", show_pct=True):
    total = sum(counter.values())
    rows = ""
    for val, n in counter.most_common():
        rows += f"""<tr>
          <td class="label-cell">{val or "(空)"}</td>
          <td class="num">{n}</td>
          {"<td class='num'>" + pct(n,total) + "</td>" if show_pct else ""}
          <td>{bar(n, total)}</td>
        </tr>"""
    return f"""
    <div class="freq-table">
      {"<h4>" + title + "</h4>" if title else ""}
      <table>
        <tr><th>值</th><th>筆數</th>{"<th>%</th>" if show_pct else ""}<th></th></tr>
        {rows}
        <tr class="total-row"><td>合計</td><td class="num">{total}</td>{"<td></td>" if show_pct else ""}<td></td></tr>
      </table>
    </div>"""


def cross_table(records, row_field, col_field, row_vals=None, col_vals=None):
    counts = defaultdict(Counter)
    for r in records:
        rv = r.get(row_field, "(無)")
        cv = r.get(col_field, "(無)")
        counts[rv][cv] += 1

    if row_vals is None:
        row_totals = {rv: sum(c.values()) for rv, c in counts.items()}
        row_vals = sorted(row_totals, key=lambda x: -row_totals[x])
    if col_vals is None:
        all_cols = Counter()
        for c in counts.values():
            all_cols.update(c)
        col_vals = [v for v, _ in all_cols.most_common()]

    header = "<tr><th>" + DIM_NAMES.get(row_field, row_field) + " \\ " + DIM_NAMES.get(col_field, col_field) + "</th>"
    for cv in col_vals:
        header += f"<th>{cv}</th>"
    header += "<th>合計</th></tr>"

    rows = ""
    for rv in row_vals:
        row_total = sum(counts[rv].values())
        rows += f"<tr><td class='label-cell'><b>{rv}</b></td>"
        for cv in col_vals:
            n = counts[rv].get(cv, 0)
            p = pct(n, row_total)
            bg = f"rgba(59,130,246,{min(0.8, n/row_total*2) if row_total else 0:.2f})"
            rows += f"<td style='background:{bg};text-align:center'>{n}<br><small>{p}</small></td>"
        rows += f"<td class='num'><b>{row_total}</b></td></tr>"

    return f"""<div style="overflow-x:auto"><table class="cross-table">
      {header}{rows}
    </table></div>"""


def section(title, content, id=""):
    return f"""<section id="{id}">
      <h2>{title}</h2>
      {content}
    </section>"""


def slugify(text):
    slug = re.sub(r"[^0-9A-Za-z_-]+", "-", text.lower()).strip("-")
    return slug or "tab"


def tabs(items, key_prefix="tab"):
    nav = ""
    panes = ""
    key_prefix = slugify(key_prefix)
    for i, (label, content) in enumerate(items):
        active = "active" if i == 0 else ""
        tid = f"{key_prefix}-{next(tab_id_counter)}"
        nav += f'<button class="tab-btn {active}" onclick="showTab(\'{tid}\')">{label}</button>'
        panes += f'<div class="tab-pane {active}" id="{tid}">{content}</div>'
    return f'<div class="tab-nav">{nav}</div><div class="tab-content">{panes}</div>'


def filter_buttons(items, filter_group):
    buttons = [f"<button class=\"filter-btn active\" data-filter-group=\"{filter_group}\" data-filter-value=\"all\" onclick=\"filterPostsFromButton(this)\">全部</button>"]
    for label in items:
        safe_label = html_lib.escape(label)
        buttons.append(
            f"<button class=\"filter-btn\" data-filter-group=\"{filter_group}\" data-filter-value=\"{html_lib.escape(label, quote=True)}\" onclick=\"filterPostsFromButton(this)\">{safe_label}</button>"
        )
    return '<div class="filter-nav">' + "".join(buttons) + "</div>"


def insight_list(counter, total, max_items=5, skip_values=None):
    skip_values = set(skip_values or [])
    rows = []
    for label, n in counter.most_common():
        if label in skip_values:
            continue
        rows.append(f"<li><span>{label}</span><b>{n}（{pct(n, total)}）</b></li>")
        if len(rows) >= max_items:
            break
    return "<ul class='insight-list'>" + "".join(rows) + "</ul>"


def example_comments(records, field, value, limit=2):
    seen = set()
    items = []
    for r in records:
        if r.get(field) != value:
            continue
        text = " ".join((r.get("comment_text") or "").split())
        if not text or text in seen:
            continue
        seen.add(text)
        items.append(f"<li>{html_lib.escape(text[:120])}</li>")
        if len(items) >= limit:
            break
    if not items:
        return ""
    return "<div class='example-comments'><div class='example-title'>代表留言</div><ul>" + "".join(items) + "</ul></div>"


def insight_card(title, body, detail_html="", examples_html=""):
    return f"""<div class="insight-card">
      <h3>{title}</h3>
      <p class="insight-body">{body}</p>
      {detail_html}
      {examples_html}
    </div>"""


def unique_comment_records(records):
    seen = set()
    unique = []
    for r in records:
        text = " ".join((r.get("comment_text") or "").split())
        if not text or text in seen:
            continue
        seen.add(text)
        unique.append((r, text))
    return unique


def classify_solution_comment(text, mode):
    if mode == "提供解方":
        if any(k in text for k in ["槍斃", "擊斃", "掃射", "開槍", "殺", "處死", "關到死", "嚴辦", "制裁"]):
            return "懲罰／報復型"
        if any(k in text for k in ["修法", "政府", "政策", "立法", "管理", "保護措施", "硬起來", "反制"]):
            return "政策／治理型"
        if any(k.lower() in text.lower() for k in ["低軌衛星", "starlink", "備援", "電纜", "修復", "方案"]):
            return "技術／備援型"
        return "其他主張"
    if any(k.lower() in text.lower() for k in ["低軌衛星", "starlink", "備援", "保護措施", "修復", "防治方法"]):
        return "技術／備援詢問"
    if any(k in text for k in ["政府", "反制", "制裁", "作為", "動作", "政策"]):
        return "政策／反制詢問"
    if any(k in text for k in ["原因", "斷線率", "為什麼", "資訊", "限流", "怎麼報"]):
        return "資訊查證／原因詢問"
    return "其他提問"


def comment_list_table(records, title, mode, limit=80, per_category_limit=12):
    unique = unique_comment_records(records)
    total_unique = len(unique)
    grouped = defaultdict(list)
    counts = Counter()
    for r, text in unique:
        category = classify_solution_comment(text, mode)
        grouped[category].append((r, text))
        counts[category] += 1

    summary = "<ul class='insight-list'>" + "".join(
        f"<li><span>{cat}</span><b>{n}（{pct(n, total_unique)}）</b></li>"
        for cat, n in counts.most_common()
    ) + "</ul>"

    shown_total = 0
    sections = []
    for cat, n in counts.most_common():
        remaining = max(0, limit - shown_total)
        if remaining <= 0:
            break
        rows = []
        for r, text in grouped[cat][:min(per_category_limit, remaining)]:
            platform = "FB" if r.get("platform") == "facebook" else "Threads"
            post_type = r.get("post_type", "(無)")
            rows.append(
                f"<tr><td>{platform}</td><td><span class='tag'>{html_lib.escape(post_type)}</span></td><td class='label-cell'>{html_lib.escape(text[:220])}</td></tr>"
            )
        shown_total += len(rows)
        sections.append(
            f"<h4>{cat}</h4><p class='comment-table-note'>此類總數 {n} 則，列出 {len(rows)} 則。</p>"
            f"<table><tr><th>平台</th><th>post_type</th><th>留言</th></tr>{''.join(rows)}</table>"
        )

    return f"""<div class="comment-table-wrap">
      <p class="comment-table-note">{title}。原始總數 {len(records)} 則，去重後 {total_unique} 則，這裡實際列出 {shown_total} 則。</p>
      {summary}
      {''.join(sections)}
    </div>"""


def evidence_table(headers, rows):
    head = "".join(f"<th>{html_lib.escape(h)}</th>" for h in headers)
    body = ""
    for row in rows:
        body += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
    return f"<div class='evidence-table-wrap'><table><tr>{head}</tr>{body}</table></div>"


def method_card(title, body, table_html=""):
    return f"""<div class="method-card">
      <h3>{title}</h3>
      <p class="method-body">{body}</p>
      {table_html}
    </div>"""


def category_list_html(title, labels):
    items = "".join(f"<li>{html_lib.escape(label)}</li>" for label in labels)
    return f"<div class='method-list-block'><h4>{html_lib.escape(title)}</h4><ul class='method-list'>{items}</ul></div>"


def distribution_evidence_table(title, counter, total, highlight_labels):
    if isinstance(highlight_labels, str):
        highlight_labels = {highlight_labels}
    else:
        highlight_labels = set(highlight_labels)
    rows = []
    for label, n in counter.most_common():
        row_class = " class='highlight-row'" if label in highlight_labels else ""
        rows.append(
            f"<tr{row_class}><td>{html_lib.escape(label)}</td><td class='num'>{n}</td><td class='num'>{pct(n, total)}</td></tr>"
        )
    return (
        f"<div class='evidence-subtable'><h4>{title}</h4>"
        f"<div class='evidence-table-wrap'><table><tr><th>分類</th><th>數值</th><th>占比</th></tr>{''.join(rows)}</table></div></div>"
    )


def finding_block(title, summary, table_html):
    return f"""<div class="finding-block">
      <h3>{title}</h3>
      <p class="finding-body">{summary}</p>
      {table_html}
    </div>"""


def example_list_block(title, items):
    lis = "".join(f"<li>{html_lib.escape(item)}</li>" for item in items)
    return f"<div class='example-comments'><div class='example-title'>{title}</div><ul>{lis}</ul></div>"


def main():
    data = json.loads(IN_FILE.read_text(encoding="utf-8"))
    records = data["records"]
    threads_posts_data = json.loads(THREADS_POSTS_FILE.read_text(encoding="utf-8"))
    threads_posts = threads_posts_data.get("posts", {})

    fb_recs = [r for r in records if r.get("platform") == "facebook"]
    th_recs = [r for r in records if r.get("platform") == "threads"]

    # Build post groupings
    # Facebook: group by post_url
    fb_posts = defaultdict(list)
    for r in fb_recs:
        fb_posts[r["post_url"]].append(r)

    # Threads: group by post_id from source_file
    th_posts = defaultdict(list)
    for r in th_recs:
        pid = get_th_post_id(r)
        if pid:
            th_posts[pid].append(r)

    # Also build post_id -> post_text + post_type mapping
    th_post_meta = {}
    for r in th_recs:
        pid = get_th_post_id(r)
        if pid and pid not in th_post_meta:
            th_post_meta[pid] = {
                "post_text": threads_posts.get(pid) or r.get("post_text", ""),
                "post_type": r.get("post_type", "(無)"),
            }
    fb_post_meta = {}
    for r in fb_recs:
        url = r["post_url"]
        if url not in fb_post_meta:
            fb_post_meta[url] = {
                "post_text": r.get("post_text", ""),
                "post_type": r.get("post_type", "(無)"),
            }

    # ── 1. Cognition overview ─────────────────────────────────────────────────
    belief_counter = Counter(r.get("belief_label", "(無)") for r in records)
    misconception_counter = Counter(r.get("misconception_type", "(無)") for r in records)
    stance_counter = Counter(r.get("stance_label", "(無)") for r in records)
    solution_counter = Counter(r.get("solution_label", "(無)") for r in records)
    technical_signals = [
        "認為已有備援、不致全面斷網",
        "對修復時間有明確認知",
        "認為斷纜常見於船隻/拖網/錨具",
    ]
    technical_signal_count = sum(belief_counter.get(label, 0) for label in technical_signals)
    top_belief = belief_counter.most_common(1)[0]
    top_misconception = next((item for item in misconception_counter.most_common() if item[0] != "無"), ("無", 0))
    top_stance = stance_counter.most_common(1)[0]
    solution_signal_count = solution_counter.get("提供解方", 0) + solution_counter.get("想知道解方", 0)
    provide_solution_recs = [r for r in records if r.get("solution_label") == "提供解方"]
    ask_solution_recs = [r for r in records if r.get("solution_label") == "想知道解方"]
    provide_stance_counter = Counter(r.get("stance_label", "(無)") for r in provide_solution_recs)
    ask_stance_counter = Counter(r.get("stance_label", "(無)") for r in ask_solution_recs)
    method_category_lists = "".join([
        category_list_html("topic_label", [label for label, _ in Counter(r.get("topic_label", "(無)") for r in records).most_common()]),
        category_list_html("belief_label", [label for label, _ in belief_counter.most_common()]),
        category_list_html("misconception_type", [label for label, _ in misconception_counter.most_common()]),
        category_list_html("stance_label", [label for label, _ in stance_counter.most_common()]),
        category_list_html("solution_label", [label for label, _ in solution_counter.most_common()]),
    ])

    method_section = section(
        "研究方法",
        "<div class='method-grid'>"
        + method_card(
            "分析單位",
            "本報告以留言為主要分析單位，共整理 Facebook 與 Threads 的海纜相關留言 8525 則；同時保留每則留言所屬的平台、貼文與貼文分類，方便把留言認知放回原始貼文脈絡中理解。",
            evidence_table(
                ["資料層次", "說明"],
                [
                    ["留言層級", "每則留言都標記 5 個留言向度：主題、認知、錯誤認知、情緒/態度、解方"],
                    ["貼文層級", "每篇貼文另標記 1 個 post_type，用來判斷留言是被哪種貼文框架帶動"],
                    ["平台層級", "保留 Facebook / Threads 平台來源，可比較平台與貼文框架差異"],
                ],
            ),
        )
        + method_card(
            "貼文分類（post_type）",
            "貼文分類用來判斷留言是在什麼貼文框架下發生。Facebook 貼文直接沿用資料中的 post_type；Threads 則先以原始貼文文字做貼文級分類，再依 post_id 回填到該貼文底下的所有留言。",
            evidence_table(
                ["分類", "判斷重點"],
                [
                    ["中國破壞事件", "聚焦中國切斷、破壞或疑似介入海纜的具體案例"],
                    ["意外/非蓄意斷纜事件", "聚焦錨害、地震、漁網等非蓄意原因"],
                    ["海纜狀態更新", "聚焦斷纜現況、修復進度與最新狀態"],
                    ["政府政策與回應", "聚焦政府、主管機關、立法院等政策與回應"],
                    ["備援與韌性", "聚焦低軌衛星、備援路由、韌性強化等方案"],
                    ["闢謠/查核", "聚焦澄清謠言、錯誤資訊或不實傳言"],
                    ["國際案例", "聚焦台灣以外的海纜事件或比較案例"],
                    ["其他", "與以上類別關聯較弱或無法歸類的貼文"],
                ],
            ),
        )
        + method_card(
            "留言分類（5 個向度）",
            "每則留言都同時從五個角度閱讀。這些標記不是要判定留言真偽，而是用來辨識大家在討論海纜時，最常把焦點放在哪裡、如何理解事件，以及是否帶有明顯誤解或解方想像。",
            evidence_table(
                ["向度", "用途", "主要類別例子"],
                [
                    ["topic_label", "看留言主要在談什麼議題", "中國因素與敵意行動、斷纜原因、政府治理與政策、備援通訊與韌性"],
                    ["belief_label", "看留言如何理解事件與風險", "認為中國可能蓄意破壞、認為政府準備不足、將事件理解為政治操作/宣傳、無法判斷"],
                    ["misconception_type", "看留言是否反映常見誤解", "把所有斷纜都直接推定為敵對攻擊、認為網路慢一定跟海纜被破壞有關、認為斷一條就等於全面斷網"],
                    ["stance_label", "看留言情緒與表態方式", "憤怒/指責、嘲諷/反串、焦慮/恐慌、理性討論"],
                    ["solution_label", "看留言有沒有提出或追問解方", "提供解方、想知道解方、無"],
                ],
            ) + method_category_lists,
        )
        + method_card(
            "閱讀原則",
            "分析時區分三個層次：第一，看整體留言最常出現哪些認知與誤解；第二，看不同貼文分類如何帶出不同留言反應；第三，再比較 Facebook 與 Threads 是否存在平台差異。這樣可以避免把貼文 framing 效果誤當成單純的平台文化差異。",
            evidence_table(
                ["原則", "目的"],
                [
                    ["貼文與留言分開看", "避免把貼文主題錯當成留言本身的認知"],
                    ["完整分布優先", "每個發現都先看完整分布，再高亮重點類別"],
                    ["平台比較要控制 post_type", "降低不同平台貼文組成差異造成的誤判"],
                ],
            ),
        )
        + "</div>",
        id="method",
    )

    def collect_examples(recs, limit=4):
        seen = set()
        out = []
        for r in recs:
            text = " ".join((r.get("comment_text") or "").split())
            if not text or text in seen:
                continue
            seen.add(text)
            out.append(text[:140])
            if len(out) >= limit:
                break
        return out

    provide_examples = collect_examples(provide_solution_recs, limit=8)
    ask_examples = collect_examples(ask_solution_recs, limit=8)

    cognition_cards = [
        insight_card(
            "主要風險判斷",
            f"目前最強的認知軸線是「{top_belief[0]}」；其次才是「無法判斷」與「沒有可辨識認知」。",
            insight_list(belief_counter, len(records), max_items=5),
            example_comments(records, "belief_label", top_belief[0]),
        ),
        insight_card(
            "常見錯誤認知",
            f"最常見的誤解是「{top_misconception[0]}」。除了這類直接歸因，也可看到把網路變慢直接等同海纜受損的推論。",
            insight_list(misconception_counter, len(records), max_items=5, skip_values={"無"}),
            example_comments(records, "misconception_type", top_misconception[0]),
        ),
        insight_card(
            "技術理解訊號",
            f"較接近基礎事實的技術理解訊號共 {technical_signal_count} 筆，占 {pct(technical_signal_count, len(records))}。這表示有一部分留言知道備援、修復時間或常見斷纜原因，但比例仍不高。",
            "<ul class='insight-list'>"
            + "".join(f"<li><span>{label}</span><b>{belief_counter.get(label, 0)}（{pct(belief_counter.get(label, 0), len(records))}）</b></li>" for label in technical_signals)
            + "</ul>",
        ),
        insight_card(
            "情緒與解方",
            f"整體討論情緒以「{top_stance[0]}」最多；與此同時，明確提到解方或追問解方的留言只有 {solution_signal_count} 筆，占 {pct(solution_signal_count, len(records))}。",
            "<div class='insight-split'>"
            + insight_list(stance_counter, len(records), max_items=4)
            + insight_list(solution_counter, len(records), max_items=3)
            + "</div>",
            example_comments(records, "stance_label", top_stance[0]),
        ),
    ]
    cognition_section = section("大眾對海纜的認知輪廓", "<div class='insight-grid'>" + "".join(cognition_cards) + "</div>", id="cognition")
    post_type_counter = Counter(r.get("post_type", "(無)") for r in records)
    findings_section = section(
        "初步發現與佐證",
        "".join([
            finding_block(
                "1. 中國破壞是最強的理解框架",
                "整體討論最常把海纜事件放進中國威脅框架中，這同時反映在貼文分類與留言認知標籤上。",
                distribution_evidence_table("post_type 完整分布", post_type_counter, len(records), "中國破壞事件")
                + distribution_evidence_table("belief_label 完整分布", belief_counter, len(records), "認為中國可能蓄意破壞"),
            ),
            finding_block(
                "2. 情緒強，但很多人不知道具體怎麼辦",
                "留言中最常見的是憤怒與指責；而且即使進入「提供解方」或「想知道解方」的留言，情緒性表達仍然占很大比例，說明不少留言是在高情緒下尋找出口，而不是提出穩定、可操作的方案。",
                distribution_evidence_table("stance_label 完整分布", stance_counter, len(records), "憤怒/指責")
                + distribution_evidence_table("solution_label 完整分布", solution_counter, len(records), {"提供解方", "想知道解方"})
                + evidence_table(
                    ["解方類型內的 stance", "數值", "占該類留言比"],
                    [
                        ["提供解方：憤怒/指責", f"{provide_stance_counter['憤怒/指責']}", pct(provide_stance_counter["憤怒/指責"], len(provide_solution_recs))],
                        ["提供解方：支持強硬回應", f"{provide_stance_counter['支持強硬回應']}", pct(provide_stance_counter["支持強硬回應"], len(provide_solution_recs))],
                        ["提供解方：理性討論", f"{provide_stance_counter['理性討論']}", pct(provide_stance_counter["理性討論"], len(provide_solution_recs))],
                        ["想知道解方：憤怒/指責", f"{ask_stance_counter['憤怒/指責']}", pct(ask_stance_counter["憤怒/指責"], len(ask_solution_recs))],
                        ["想知道解方：理性討論", f"{ask_stance_counter['理性討論']}", pct(ask_stance_counter["理性討論"], len(ask_solution_recs))],
                        ["想知道解方：焦慮/恐慌", f"{ask_stance_counter['焦慮/恐慌']}", pct(ask_stance_counter["焦慮/恐慌"], len(ask_solution_recs))],
                    ],
                )
                + example_list_block("提供解方代表留言", provide_examples)
                + example_list_block("想知道解方代表留言", ask_examples),
            ),
            finding_block(
                "3. 討論中存在明顯的反向框架",
                "不是所有人都接受中國歸因。另一條重要敘事是：不要過早怪中國，或認為這些討論本身帶有政治操作成分。",
                distribution_evidence_table(
                    "belief_label 完整分布",
                    belief_counter,
                    len(records),
                    {"將事件理解為政治操作/宣傳", "認為斷纜情況被誇大或錯誤報導"},
                ),
            ),
            finding_block(
                "4. 闢謠貼文不一定會降低爭議",
                "在闢謠/查核類貼文下，『政治操作／宣傳』與『誇大／錯誤報導』的比例都偏高，表示澄清內容本身也會被部分受眾懷疑。",
                distribution_evidence_table(
                    "闢謠/查核類貼文的 belief_label 完整分布",
                    Counter(r.get("belief_label", "(無)") for r in records if r.get("post_type") == "闢謠/查核"),
                    sum(1 for r in records if r.get("post_type") == "闢謠/查核"),
                    {"將事件理解為政治操作/宣傳", "認為斷纜情況被誇大或錯誤報導"},
                ),
            ),
            finding_block(
                "5. 網路變慢常被直接連到海纜斷裂",
                "不少留言會把日常網速問題直接理解成海纜受損，顯示生活經驗很容易被帶入海纜事件框架。",
                distribution_evidence_table(
                    "belief_label 完整分布",
                    belief_counter,
                    len(records),
                    "認為網路慢一定跟海纜被破壞有關",
                )
                + distribution_evidence_table(
                    "misconception_type 完整分布",
                    misconception_counter,
                    len(records),
                    "認為網路慢一定跟海纜被破壞有關",
                ),
            ),
            finding_block(
                "6. 技術理解不足，討論容易回到既有政治立場",
                "真正貼近技術事實的理解訊號比例不高；相對地，直接把斷纜推定為敵對攻擊的留言很多，顯示資訊不一致時，大家更容易回到原本立場。",
                distribution_evidence_table(
                    "belief_label 完整分布",
                    belief_counter,
                    len(records),
                    {"認為已有備援、不致全面斷網", "認為斷纜常見於船隻/拖網/錨具", "對修復時間有明確認知"},
                )
                + distribution_evidence_table(
                    "misconception_type 完整分布",
                    misconception_counter,
                    len(records),
                    "把所有斷纜都直接推定為敵對攻擊",
                ),
            ),
        ]),
        id="findings",
    )
    solution_examples_section = section(
        "解方留言整理",
        tabs(
            [
                ("提供解方", comment_list_table([r for r in records if r.get("solution_label") == "提供解方"], "這些留言是在提供具體作法、懲罰主張或政策建議", "提供解方")),
                ("想知道解方", comment_list_table([r for r in records if r.get("solution_label") == "想知道解方"], "這些留言是在追問反制方法、備援方案或政府可以怎麼做", "想知道解方")),
            ],
            key_prefix="solution-examples",
        ),
        id="solutions",
    )

    # ── 2. Overall stats ──────────────────────────────────────────────────────
    overall_tabs = []
    for dim in DIMS:
        c = Counter(r.get(dim, "(無)") for r in records)
        overall_tabs.append((DIM_NAMES[dim], freq_table(c)))
    overall_section = section("各向度整體分佈", tabs(overall_tabs), id="overall")

    # Platform comparison
    platform_parts = []
    for dim in DIMS:
        fb_c = Counter(r.get(dim, "(無)") for r in fb_recs)
        th_c = Counter(r.get(dim, "(無)") for r in th_recs)
        all_vals = list(dict.fromkeys([v for v, _ in (fb_c + th_c).most_common()]))
        rows = ""
        for val in all_vals:
            fb_n = fb_c.get(val, 0)
            th_n = th_c.get(val, 0)
            rows += f"""<tr>
              <td class="label-cell">{val}</td>
              <td class="num">{fb_n}</td><td class="num">{pct(fb_n,len(fb_recs))}</td>
              <td class="num">{th_n}</td><td class="num">{pct(th_n,len(th_recs))}</td>
            </tr>"""
        platform_parts.append((DIM_NAMES[dim], f"""
          <table><tr><th>值</th><th>FB筆</th><th>FB%</th><th>TH筆</th><th>TH%</th></tr>
          {rows}</table>"""))
    platform_section = section("平台比較（FB vs Threads）", tabs(platform_parts), id="platform")

    def build_cross_platform_tab(platform_label, recs):
        cross_parts = []
        for dim in COMMENT_DIMS:
            ct = cross_table(recs, "post_type", dim)
            cross_parts.append((DIM_NAMES[dim], ct))
        return (platform_label, tabs(cross_parts, key_prefix=f"cross-{platform_label.lower()}"))

    # ── 3. post_type × belief/misconception ───────────────────────────────────
    cross_section = section(
        "post_type × 留言向度交叉分析",
        tabs(
            [
                build_cross_platform_tab("一起看", records),
                build_cross_platform_tab("Facebook", fb_recs),
                build_cross_platform_tab("Threads", th_recs),
            ],
            key_prefix="cross-platform",
        ),
        id="cross",
    )

    def build_post_type_platform_tab(platform_label, recs):
        pt_parts = []
        present_post_types = list(dict.fromkeys(
            POST_TYPES + sorted({r.get("post_type", "(無)") for r in recs if r.get("post_type") not in POST_TYPES})
        ))
        if any((r.get("post_type") or "(無)") == "(無)" for r in recs):
            present_post_types.append("(無)")
        for pt in present_post_types:
            pt_recs = [r for r in recs if (r.get("post_type") or "(無)") == pt]
            if not pt_recs:
                continue
            inner = f"<p><b>{len(pt_recs)} 筆留言</b></p>"
            dim_tabs = []
            for dim in COMMENT_DIMS:
                c = Counter(r.get(dim, "(無)") for r in pt_recs)
                dim_tabs.append((DIM_NAMES[dim], freq_table(c)))
            inner += tabs(dim_tabs, key_prefix=f"posttype-{platform_label.lower()}-{pt}")
            pt_parts.append((pt, inner))
        return (platform_label, tabs(pt_parts, key_prefix=f"posttype-platform-{platform_label.lower()}"))

    # ── 4. Per post_type stats ────────────────────────────────────────────────
    pt_section = section(
        "各 post_type 留言向度分佈",
        tabs(
            [
                build_post_type_platform_tab("一起看", records),
                build_post_type_platform_tab("Facebook", fb_recs),
                build_post_type_platform_tab("Threads", th_recs),
            ],
            key_prefix="posttype-root",
        ),
        id="by-posttype",
    )

    # ── 5. Per post stats ─────────────────────────────────────────────────────
    # Facebook posts
    fb_rows = ""
    for url, recs in sorted(fb_posts.items(), key=lambda x: -len(x[1])):
        meta = fb_post_meta.get(url, {})
        text = (meta.get("post_text", "") or "")
        pt = meta.get("post_type", "(無)")
        detail_id = f"fb-{abs(hash(url)) % 99999}"
        dim_html = f"""<div class="post-header">
          <span class="tag tag-lg">{pt}</span>
          <div class="post-text">{text[:300] or "(無貼文內容)"}</div>
        </div>"""
        for dim in DIMS:
            c = Counter(r.get(dim, "(無)") for r in recs)
            dim_html += freq_table(c, DIM_NAMES[dim], show_pct=False)
        fb_rows += f"""<tr class="post-summary-row" data-filter-group="per-post" data-post-type="{html_lib.escape(pt, quote=True)}">
          <td class="num">{len(recs)}</td>
          <td><span class="tag">{pt}</span></td>
          <td class="label-cell"><small>{text[:80] or "(無內容)"}</small></td>
          <td><button class="toggle-btn" onclick="toggleDetail('{detail_id}')">展開</button></td>
        </tr>
        <tr id="{detail_id}" class="post-detail-row" data-filter-group="per-post" data-post-type="{html_lib.escape(pt, quote=True)}" style="display:none"><td colspan="4">
          <div class="post-detail">{dim_html}</div>
        </td></tr>"""

    # Threads posts
    th_rows = ""
    for pid, recs in sorted(th_posts.items(), key=lambda x: -len(x[1])):
        meta = th_post_meta.get(pid, {})
        text = (meta.get("post_text", "") or "")
        pt = meta.get("post_type", "(無)")
        detail_id = f"th-{abs(hash(pid)) % 99999}"
        dim_html = f"""<div class="post-header">
          <span class="tag tag-lg">{pt}</span>
          <div class="post-text">{text[:300] or "(無貼文內容)"}</div>
        </div>"""
        for dim in DIMS:
            c = Counter(r.get(dim, "(無)") for r in recs)
            dim_html += freq_table(c, DIM_NAMES[dim], show_pct=False)
        th_rows += f"""<tr class="post-summary-row" data-filter-group="per-post" data-post-type="{html_lib.escape(pt, quote=True)}">
          <td class="num">{len(recs)}</td>
          <td><span class="tag">{pt}</span></td>
          <td class="label-cell"><small>{text[:80] or "(無內容)"}</small></td>
          <td><button class="toggle-btn" onclick="toggleDetail('{detail_id}')">展開</button></td>
        </tr>
        <tr id="{detail_id}" class="post-detail-row" data-filter-group="per-post" data-post-type="{html_lib.escape(pt, quote=True)}" style="display:none"><td colspan="4">
          <div class="post-detail">{dim_html}</div>
        </td></tr>"""

    per_post_types = list(dict.fromkeys(
        POST_TYPES + sorted({(r.get("post_type") or "(無)") for r in records if (r.get("post_type") or "(無)") not in POST_TYPES})
    ))
    per_post_section = section("每篇貼文向度分佈", f"""
      {filter_buttons(per_post_types, "per-post")}
      <h3>Facebook（{len(fb_posts)} 篇）</h3>
      <table><tr><th>留言數</th><th>post_type</th><th>貼文</th><th></th></tr>{fb_rows}</table>
      <h3 style="margin-top:2rem">Threads（{len(th_posts)} 篇）</h3>
      <table><tr><th>留言數</th><th>post_type</th><th>貼文</th><th></th></tr>{th_rows}</table>
    """, id="per-post")

    # ── Assemble HTML ─────────────────────────────────────────────────────────
    toc = """<nav id="toc">
      <a href="#method">研究方法</a>
      <a href="#cognition">認知輪廓</a>
      <a href="#findings">初步發現</a>
      <a href="#solutions">解方留言</a>
      <a href="#overall">整體分佈</a>
      <a href="#platform">平台比較</a>
      <a href="#cross">交叉分析</a>
      <a href="#by-posttype">per post_type</a>
      <a href="#per-post">per 貼文</a>
    </nav>"""

    summary = f"""<div class="summary-cards">
      <div class="card"><div class="num">{len(records)}</div><div>總留言數</div></div>
      <div class="card"><div class="num">{len(fb_recs)}</div><div>Facebook</div></div>
      <div class="card"><div class="num">{len(th_recs)}</div><div>Threads</div></div>
      <div class="card"><div class="num">{len(fb_posts)}</div><div>FB 貼文</div></div>
      <div class="card"><div class="num">{len(th_posts)}</div><div>Threads 貼文</div></div>
    </div>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<title>海纜留言分析報告</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, sans-serif; margin: 0; background: #f8fafc; color: #1e293b; }}
  #toc {{ position: sticky; top: 0; background: #1e3a5f; padding: .6rem 1.5rem; display: flex; gap: 1.5rem; z-index: 100; }}
  #toc a {{ color: #93c5fd; text-decoration: none; font-size: .9rem; }}
  #toc a:hover {{ color: white; }}
  .container {{ max-width: 1400px; margin: 0 auto; padding: 1.5rem; }}
  h1 {{ font-size: 1.6rem; margin-bottom: 1rem; }}
  h2 {{ font-size: 1.2rem; border-left: 4px solid #3b82f6; padding-left: .75rem; margin: 2rem 0 1rem; }}
  h3 {{ font-size: 1rem; color: #475569; }}
  h4 {{ font-size: .9rem; color: #64748b; margin: .5rem 0 .25rem; }}
  section {{ background: white; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,.08); }}
  .summary-cards {{ display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }}
  .card {{ background: white; border-radius: 8px; padding: 1rem 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,.08); text-align: center; }}
  .card .num {{ font-size: 2rem; font-weight: bold; color: #1e3a5f; }}
  .method-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }}
  .method-card {{ border: 1px solid #dbeafe; border-radius: 10px; padding: 1rem; background: #fcfdff; }}
  .method-body {{ color: #334155; font-size: .9rem; line-height: 1.6; margin-bottom: .75rem; }}
  .method-list-block {{ margin-top: .9rem; }}
  .method-list {{ margin: .25rem 0 0; padding-left: 1.1rem; color: #475569; font-size: .84rem; line-height: 1.5; }}
  .method-list li {{ margin-bottom: .18rem; }}
  .finding-block {{ border-top: 1px solid #e2e8f0; padding-top: 1rem; margin-top: 1rem; }}
  .finding-block:first-child {{ border-top: 0; padding-top: 0; margin-top: 0; }}
  .finding-body {{ color: #334155; font-size: .9rem; line-height: 1.6; margin-bottom: .75rem; }}
  .evidence-subtable {{ margin-top: .75rem; }}
  .evidence-subtable h4 {{ margin: 0 0 .4rem; color: #334155; }}
  .evidence-table-wrap {{ overflow-x: auto; }}
  .highlight-row td {{ background: #dbeafe; font-weight: 700; }}
  .insight-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }}
  .insight-card {{ border: 1px solid #dbeafe; border-radius: 10px; padding: 1rem; background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%); }}
  .insight-body {{ color: #334155; font-size: .9rem; line-height: 1.5; margin-bottom: .8rem; }}
  .insight-list {{ list-style: none; padding: 0; margin: 0; }}
  .insight-list li {{ display: flex; justify-content: space-between; gap: 1rem; padding: .3rem 0; border-top: 1px solid #e2e8f0; font-size: .84rem; }}
  .insight-list li:first-child {{ border-top: 0; padding-top: 0; }}
  .insight-list b {{ white-space: nowrap; color: #0f172a; }}
  .insight-split {{ display: grid; grid-template-columns: 1fr 1fr; gap: .8rem; }}
  .example-comments {{ margin-top: .8rem; padding-top: .8rem; border-top: 1px dashed #cbd5e1; }}
  .example-title {{ font-size: .8rem; color: #64748b; margin-bottom: .3rem; }}
  .example-comments ul {{ margin: 0; padding-left: 1rem; }}
  .example-comments li {{ font-size: .82rem; color: #475569; margin-bottom: .3rem; }}
  .comment-table-wrap {{ margin-top: .5rem; }}
  .comment-table-note {{ color: #64748b; font-size: .84rem; margin: 0 0 .75rem; }}
  table {{ border-collapse: collapse; font-size: .85rem; }}
  th {{ background: #f1f5f9; padding: .4rem .75rem; text-align: left; border-bottom: 2px solid #e2e8f0; white-space: nowrap; }}
  td {{ padding: .35rem .75rem; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }}
  tr:hover td {{ background: #f8fafc; }}
  .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .label-cell {{ max-width: 320px; }}
  .total-row td {{ font-weight: bold; border-top: 2px solid #e2e8f0; }}
  .bar {{ height: 12px; background: #3b82f6; border-radius: 2px; min-width: 2px; }}
  .freq-table {{ display: inline-block; vertical-align: top; margin-right: 1.5rem; margin-bottom: 1rem; }}
  .cross-table th, .cross-table td {{ border: 1px solid #e2e8f0; padding: .3rem .5rem; font-size: .8rem; }}
  .cross-table th {{ background: #f1f5f9; }}
  .tab-nav {{ display: flex; flex-wrap: wrap; gap: .4rem; margin-bottom: 1rem; border-bottom: 2px solid #e2e8f0; padding-bottom: .5rem; }}
  .tab-btn {{ padding: .35rem .8rem; border: 1px solid #e2e8f0; border-radius: 4px; background: white; cursor: pointer; font-size: .82rem; }}
  .tab-btn.active {{ background: #1e3a5f; color: white; border-color: #1e3a5f; }}
  .filter-nav {{ display: flex; flex-wrap: wrap; gap: .4rem; margin-bottom: 1rem; }}
  .filter-btn {{ padding: .35rem .8rem; border: 1px solid #cbd5e1; border-radius: 999px; background: #fff; cursor: pointer; font-size: .82rem; color: #334155; }}
  .filter-btn.active {{ background: #0f766e; color: #fff; border-color: #0f766e; }}
  .tab-pane {{ display: none; }}
  .tab-pane.active {{ display: block; }}
  .tag {{ background: #dbeafe; color: #1e40af; padding: .15rem .5rem; border-radius: 4px; font-size: .78rem; white-space: nowrap; }}
  .toggle-btn {{ padding: .2rem .6rem; border: 1px solid #cbd5e1; border-radius: 4px; background: white; cursor: pointer; font-size: .8rem; }}
  .post-detail {{ display: flex; flex-wrap: wrap; padding: .75rem; background: #f8fafc; border-radius: 4px; }}
  .post-header {{ width: 100%; margin-bottom: .75rem; padding-bottom: .75rem; border-bottom: 1px solid #e2e8f0; }}
  .post-text {{ margin-top: .4rem; font-size: .85rem; color: #475569; white-space: pre-wrap; }}
  .tag-lg {{ font-size: .88rem; padding: .25rem .75rem; }}
</style>
</head>
<body>
{toc}
<div class="container">
<h1>海纜留言分析報告</h1>
{summary}
{method_section}
{cognition_section}
{findings_section}
{solution_examples_section}
{overall_section}
{platform_section}
{cross_section}
{pt_section}
{per_post_section}
</div>
<script>
function showTab(id) {{
  const pane = document.getElementById(id);
  if (!pane) return;
  const content = pane.closest('.tab-content');
  const panes = Array.from(content.children).filter(el => el.classList.contains('tab-pane'));
  panes.forEach(p => p.classList.remove('active'));
  pane.classList.add('active');
  const nav = content.previousElementSibling;
  const buttons = Array.from(nav.children).filter(el => el.classList.contains('tab-btn'));
  buttons.forEach(b => b.classList.remove('active'));
  const idx = panes.indexOf(pane);
  if (idx >= 0 && buttons[idx]) {{
    buttons[idx].classList.add('active');
  }}
}}
function toggleDetail(id) {{
  const el = document.getElementById(id);
  if (!el || el.style.display === 'none' && el.classList.contains('is-filter-hidden')) return;
  const btn = el.previousElementSibling.querySelector('.toggle-btn');
  if (el.style.display === 'none') {{ el.style.display = ''; btn.textContent = '收起'; }}
  else {{ el.style.display = 'none'; btn.textContent = '展開'; }}
}}
function filterPostsFromButton(buttonEl) {{
  if (!buttonEl) return;
  filterPosts(buttonEl.dataset.filterGroup, buttonEl.dataset.filterValue, buttonEl);
}}
function filterPosts(group, postType, buttonEl) {{
  document.querySelectorAll(`.filter-btn[data-filter-group="${{group}}"]`).forEach(btn => btn.classList.remove('active'));
  if (buttonEl) buttonEl.classList.add('active');
  const summaryRows = document.querySelectorAll(`.post-summary-row[data-filter-group="${{group}}"]`);
  summaryRows.forEach(row => {{
    const matches = postType === 'all' || row.dataset.postType === postType;
    row.style.display = matches ? '' : 'none';
    const detail = row.nextElementSibling;
    if (detail && detail.classList.contains('post-detail-row')) {{
      detail.classList.toggle('is-filter-hidden', !matches);
      if (!matches) {{
        detail.style.display = 'none';
        const btn = row.querySelector('.toggle-btn');
        if (btn) btn.textContent = '展開';
      }}
    }}
  }});
}}
</script>
</body>
</html>"""

    OUT_FILE.write_text(html, encoding="utf-8")
    print(f"Saved -> {OUT_FILE}")
    print(f"FB posts: {len(fb_posts)}, Threads posts: {len(th_posts)}")


if __name__ == "__main__":
    main()
