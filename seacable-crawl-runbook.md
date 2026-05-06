# 台灣海纜抓取 Runbook

## 目標

把目前的規劃文件轉成可以實際執行的抓取順序，讓後續用 `Chrome DevTools MCP` 操作時，不需要再重新決定：

- 先抓哪裡
- 先抓什麼欄位
- 什麼時候補留言
- 哪些來源先略過

## 事故後限制

2026-04-30 的 Facebook Selenium 測試曾引發 `firefox hang` 與 `WindowServer watchdog timeout`。後續所有 Meta 抓取都要遵守這些限制：

- 不要在 automation worker 裡打開 `facebook.com/login` 或 `facebook.com` 首頁。
- 先由使用者在一般可見瀏覽器登入，再複製 profile 給 worker。
- 不要同時跑 Facebook 與 Threads。
- 不要同時保留多個 Selenium browser / driver 測試實例。
- 不要在 Facebook 重頁面上做整頁 `body.text` 或整頁 `page_source` 抽取。
- 只用小範圍 DOM 查詢抽卡片、抽留言。
- 如果 driver 會讓瀏覽器跑在 Rosetta / translated 模式，先降級為單頁輕量測試，不直接開大跑。

## 瀏覽器策略

- `Threads`：現有流程可沿用，但仍維持單 worker、慢速、queue/checkpoint。
- `Facebook`：優先使用原生 Apple Silicon automation 路徑。
- 目前已確認：
  - `geckodriver` 是 `x86_64`
  - `chromedriver` 是 `x86_64`
  - `safaridriver` 是 universal，較適合當下一步候選
- 在未換 driver 前，Facebook 只能做最小化測試，不做長時間大規模 Selenium crawl。

## 會用到的種子檔

- [seacable-keywords.json](/Users/mac/oread/seacable/seacable-keywords.json)
- [seacable-sources.json](/Users/mac/oread/seacable/seacable-sources.json)
- [seacable-sources.csv](/Users/mac/oread/seacable/seacable-sources.csv)

## Round 1：Threads 搜尋建池

### 查詢

- `海底電纜`
- `海纜`

### 每個命中貼文至少要存

- `platform`
- `query`
- `post_url`
- `author_name`
- `author_handle`
- `post_time`
- `text_raw`
- `reply_count`
- `like_count`
- `repost_count`
- `crawl_time`

### Round 1 的目的

- 建立第一批命中貼文
- 抽出高頻台灣帳號
- 找出集中事件日期

### Round 1 的停止條件

- 搜尋結果開始重複
- 連續多次滾動沒有新增高相關貼文
- 已取得足夠數量的台灣相關作者與貼文 URL

## Round 2：Threads 帳號補深

從 Round 1 抽出的帳號裡，優先補深：

- 台灣媒體帳號
- 台灣政府帳號
- 馬祖 / 離島在地帳號
- 重複多次談 `海底電纜` / `海纜` 的公共評論帳號

### 每個帳號頁要做的事

- 自最新往回捲
- 遇到 `海底電纜` / `海纜` 命中貼文就存
- 如果是高價值貼文，再展開回覆

### 帳號頁停止條件

- 已無更多可載入貼文
- 已回補到帳號最早可見貼文
- 或到達自定時間下限

## Round 3：Facebook P1 來源回補

先抓這些來源：

- `fb_moda`
- `fb_cht_main`
- `fb_lienchiang`
- `fb_matsu_news`
- `fb_cna`
- `fb_twreporter`
- `fb_pnnpts`
- `fb_ettoday`
- `fb_tvbsfb`
- `fb_udnplus`

### Facebook 每個來源先做兩件事

1. 確認頁面主 URL 是否正確
2. 回捲時間軸並篩選 `海底電纜` / `海纜`

### Facebook 新流程

1. 先從搜尋頁建立候選池
2. 把候選貼文 URL 寫進 queue
3. 與既有 queue / 主表去重
4. 只讓新 URL 進單頁
5. 單頁先抓主文與前排可見留言
6. 必要時才繼續展開更深留言

### Facebook 入口限制

- 允許：
  - `https://www.facebook.com/search/posts/?q=海底電纜`
  - `https://www.facebook.com/search/posts/?q=海纜`
  - 已知可讀貼文 URL
  - 已知可讀粉專時間軸
- 禁止：
  - `https://www.facebook.com/`
  - `https://www.facebook.com/login`
  - 自動化登入流程

### Facebook 抓取保護

- 搜尋頁只抽可見卡片，不做整頁文字抓取。
- 單頁只抽留言區附近 DOM，不做整頁文字抓取。
- 每一輪搜尋只保留一個 active query。
- 如果機器出現高負載、視窗明顯卡住、或 WindowServer 異常，再中止該輪並保留 queue。

### 每個命中貼文至少要存

- `platform`
- `source_id`
- `source_name`
- `post_url`
- `author_name`
- `post_time`
- `text_raw`
- `comment_count`
- `share_count`
- `like_count`
- `crawl_time`

## Round 4：留言補抓

優先補留言的貼文：

- 官方說明文
- 媒體高互動文
- 馬祖地方生活影響文
- 明顯引發政治 / 國安解讀的貼文

### 留言層級

- 先抓第一層留言
- 若回覆量大或有明顯討論串，再往下展開

### 留言停止條件

- 介面已沒有更多可展開留言
- 開始大量重複
- 貼文價值不足以支撐更深展開

## Round 5：第二批來源

第二批再補：

- `fb_setn`
- `fb_ltn`
- `fb_inside`
- `fb_ithome`
- `fb_techorange`

這批來源若 URL 未確認，先完成頁面確認，再納入固定清單。

## Round G：Google Site Search 種子發現

當 Threads / Facebook 站內搜尋受到未登入限制，或需要明確設定時間區間時，先用 Google site search 產生候選 URL，再用 `Chrome DevTools MCP` 開頁抽取。

### 產生查詢種子

預設時間區間是 `2025-01-01` 到 `2026-04-24`。這裡採用 `before` 作為排他上界，因此涵蓋到 `2026-04-23`。

```bash
npm run generate:google-seeds
```

自訂時間區間：

```bash
node generate-google-site-search-seeds.js --after 2025-01-01 --before 2025-03-01
```

### 查詢模板來源

- [google-site-search-queries.json](/Users/mac/oread/seacable/google-site-search-queries.json)

### 每個 Google 搜尋結果至少要存

- `collection_method`: `google_site_search`
- `search_engine`: `google`
- `search_query`
- `search_after`
- `search_before`
- `search_rank`
- `search_result_title`
- `search_result_snippet`
- `search_result_url`
- `discovered_at`

### 後續開頁抽取至少要存

- `platform`
- `post_url`
- `post_time_text`
- `post_time_normalized`（若可判斷）
- `author_name`
- `author_handle`
- `text_raw`
- `like_count`
- `comment_count`
- `share_count`
- `reply_count`
- `crawl_time`

### 時間區間注意事項

Google 的 `after:` / `before:` 是搜尋發現階段的過濾條件，不保證等於貼文真實發布時間。所有候選 URL 都必須再打開頁面，讀取可見的 `post_time_text`，才能納入正式時間分析。

### 去重規則

- 以 canonical `post_url` 去重。
- Facebook 需排除明顯非貼文頁，例如 `photo/`、`watch/`、`reel/`、登入頁與錯誤頁。
- Threads 需排除 `/media` URL，優先保留 `/@handle/post/id`。

## 儲存建議

### 檔案分層

- `raw/`
  - 每次抓下來的原始 HTML、JSON、截圖
- `normalized/`
  - 清洗後的 posts / comments / crawl_runs
- `logs/`
  - 每一輪抓取摘要

### 命名方式

- `platform_sourceid_yyyymmdd_hhmmss.json`
- `platform_sourceid_yyyymmdd_hhmmss.html`

## 建議的執行節奏

- 初次回補：
  - 先做完 Threads Round 1-2
  - 再做 Facebook Round 3
- 之後增量：
  - 每日：Threads 關鍵字搜尋
  - 每 2-3 日：Facebook P1 來源新貼文
  - 每週：高價值貼文留言回訪

## 明確不要做的事

- 不要把 Facebook 全站搜尋當成完整歷史庫
- 不要先掃整站留言
- 不要在 URL 未確認的來源上直接做大量回補
- 不要把 `台馬`、`馬祖`、`斷裂` 之類詞當成第一層搜尋入口

## 實作完成的最低標準

做到以下就算第一輪完成：

1. Threads 兩個關鍵字各完成一輪搜尋
2. 至少整理出一批台灣高頻帳號
3. Facebook P1 來源完成第一輪命中文章檢查
4. 至少對一批高價值貼文補抓留言
