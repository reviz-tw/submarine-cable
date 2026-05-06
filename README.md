# 台灣海底電纜社群輿論研究

社群媒體（Facebook、Threads）上台灣海底電纜相關討論的爬取與分析。

## 資料蒐集

使用 Selenium + Firefox 登入後爬取，詳見 [`social-crawler/README.md`](social-crawler/README.md)。

## 標註流程

- `label_comments.py`：留言五向度批次標註（topic / belief / misconception / stance / solution）
- `label_posts.py`：貼文 post_type 分類

快速開始：

```bash
python3.12 label_comments.py sample
python3.12 label_comments.py submit
python3.12 label_comments.py fetch
python3.12 label_comments.py merge
```

## 分析報告

```bash
python3.12 generate_report.py
```

輸出 `report.html`，含整體分佈、平台比較、post_type × 各向度交叉分析、逐篇貼文向度分佈。

## 資料

- `normalized/comments-labeled-v2.json`：8332 筆留言（FB 3239 + Threads 5093），含平台、貼文、留言內容與五向度標註
