# Social Crawler — Threads & Facebook

用 Selenium + Firefox 登入後爬取 Threads 和 Facebook 的貼文與留言。
目前主要用於台灣海底電纜相關討論的資料蒐集，但流程可通用於其他主題。

---

## 環境需求

- Python 3.12+
- Firefox（建議 121+）
- [geckodriver](https://github.com/mozilla/geckodriver/releases)（目前路徑設定在 `/usr/local/Cellar/geckodriver/0.36.0/bin/geckodriver`）
- 套件：`pip install selenium beautifulsoup4 lxml`

---

## 首次使用：手動登入與 Profile 建立

Threads 和 Facebook 都需要先登入，再把登入狀態的 Firefox Profile 複製給爬蟲使用。

```bash
# 開啟一個新的 Firefox 視窗讓你手動登入
python3 open_manual_login_firefox.py
```

登入後關閉視窗，Profile 會存在 `.selenium-profile-firefox/`（Threads）或 `.selenium-profile-meta/`（Facebook）。

**重要**：爬蟲使用的 Profile 路徑在各腳本頂部的 `PROFILE` 變數，確認路徑正確才能讀到登入狀態。

---

## Threads 爬取

### 用關鍵字搜尋建立貼文池

```bash
python3 crawl_threads_logged_in.py
```

預設搜尋 `海底電纜` 和 `海纜`，滾動收集貼文後逐一進入抓留言。

### 直接抓指定 URL 的留言（補抓模式）

```bash
python3 crawl_threads_logged_in.py --urls-file path/to/urls.txt
```

`urls.txt` 每行一個 Threads 貼文 URL，跳過搜尋階段直接進入各貼文抓留言。

### 停止條件

滾動時遇到以下任一條件即停止：

- 頁面出現「**部分回覆已隱藏。查看全部**」→ 已到底
- 連續 3 輪無新留言出現
- 達到最大輪數上限（預設 30 輪）

### 輸出

- 快照 HTML：`raw/threads-logged-in-html/YYYY-MM-DD-HHMMSS/`
- 結構化資料：`normalized/threads-logged-in-crawl-YYYY-MM-DD.json`

---

## Facebook 爬取

Facebook 爬取限制較多，請嚴格遵守以下規定，否則容易觸發 WindowServer watchdog timeout 或 Firefox hang。

### 執行

```bash
python3 crawl_facebook_logged_in.py
```

### 重要限制

- **禁止**開啟 `facebook.com/` 首頁或 `facebook.com/login`，只能開已知的貼文 URL 或搜尋頁
- **禁止**同時跑 Facebook 與 Threads 爬蟲
- **禁止**對整個頁面做 `body.text` 或 `page_source` 抽取；只用小範圍 DOM 查詢
- 每次只保留一個 active Selenium driver，用完立即 `.quit()`
- 如果機器出現高負載或視窗卡住，立刻中止並保留 queue

### 允許的入口

```
https://www.facebook.com/search/posts/?q=海底電纜
https://www.facebook.com/search/posts/?q=海纜
已知的粉專時間軸 URL
已知的貼文 URL
```

### 輸出

- 快照 HTML：`raw/facebook-logged-in-html/`
- 結構化資料：`normalized/facebook-logged-in-crawl-YYYY-MM-DD.json`

---

## 解析快照（parse_snapshots.py）

爬取完成後，把所有 HTML 快照解析成乾淨的留言記錄：

```bash
python3 parse_snapshots.py
```

輸出：

- `normalized/facebook-comments-from-snapshots-YYYY-MM-DD.json`
- `normalized/threads-comments-from-snapshots-YYYY-MM-DD.json`

**注意**：腳本只解析檔名含 `-post-` 的快照（即真正的貼文頁），搜尋頁快照（`-search-`）不會被處理，避免抓到留言 permalink 被誤判為貼文。

---

## 資料結構

各 JSON 輸出均包含：

| 欄位 | 說明 |
|---|---|
| `platform` | `facebook` / `threads` |
| `post_url` | 原始貼文 URL |
| `post_text` | 貼文內文（取自 meta description） |
| `author_name` | 留言者名稱 |
| `comment_time_text` | 留言時間文字（原始格式） |
| `comment_text` | 留言內容 |
| `source_file` | 來源快照檔名 |

---

## 常見問題

**Firefox 無法啟動（`Process unexpectedly closed`）**
通常是上一次沒有正常關閉，殘留 Firefox 程序佔住 Profile。
```bash
pkill firefox
```

**Threads 只滾幾下就停了**
確認 `extract_visible_comments()` 回傳的不是 `[:8]` 限制的舊版本（已修正），以及 `max_total_rounds` 是否夠大。

**搜尋頁留言混入資料**
`parse_snapshots.py` 的 glob pattern 已限定 `-post-` 檔名，如果仍有問題，檢查快照目錄的命名是否符合規則。
