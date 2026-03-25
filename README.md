# 台灣對外網路流量 degrade 模擬

This work is licensed under CC BY-SA 4.0 by [CHENG PENG (paulpengtw)](https://crcolab.art)

## 檔案結構

```
index.html                  ← 主框架，引用外部 Markdown 檔
slides/
  00-cold-open.md           ← Cold Open（2 張）
  01-phase1.md              ← 第一階段：0–5 分鐘（10 張）
  02-phase2.md              ← 第二階段：5–30 分鐘（20 張）
```

投影片內容以 Markdown 撰寫，透過 reveal.js `data-markdown` 屬性在執行時載入。每個 `.md` 檔內以 `---` 分隔各張投影片。
## 使用方式

```bash
npm install          # 安裝 reveal.js
npx serve            # 啟動於 localhost:3000
```

開啟瀏覽器後按 `S` 鍵可開啟講者備註視窗。
