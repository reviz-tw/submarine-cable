<h3 style="color: #e74c3c;">第四階段：1–6 小時</h3>

## 有些東西回來了，有些⋯⋯再也回不來

---

### 你感受到的

- LINE 文字訊息：可能又通了！ ✅ <!-- .element: class="fragment" -->
- 一些之前看過的網頁：可能可以開 <!-- .element: class="fragment" -->
- YouTube：可能能看，但畫質可能剩 144p 馬賽克 <!-- .element: class="fragment" -->
- Instagram：可能文字有，圖片全是灰框 🖼️❌ <!-- .element: class="fragment" -->
- 要登入任何 SaaS 工具：可能轉圈圈、失敗 <!-- .element: class="fragment" -->
- AWS / GCP 管理後台：可能完全打不開 <!-- .element: class="fragment" -->

<p class="fragment fade-up" style="font-size: 1.3em; margin-top: 1em;">
  出現了一條<strong style="color: #f39c12;">新的分水嶺</strong><br>
  <span style="font-size: 0.9em; color: #aaa;">能用 vs 不能用，取決於服務的「大腦」在哪裡</span>
</p>

---

### ISP 在幕後做了什麼？

<p style="font-size: 1.2em; margin-top: 0.5em;">
  <br>
  假設在<strong style="color: #e74c3c;">醫院急診室</strong>
</p>

<div class="fragment" style="margin-top: 1em;">
  <p style="font-size: 5em; margin: 0;">🏥</p>
</div>

<p class="fragment fade-up" style="font-size: 1.1em; margin-top: 0.5em;">
  如果有重大災難，<strong>大量傷患湧入急診室</strong><br>
  醫生人力有限，不可能同時救所有人<br>
  <span style="color: #aaa;">所以急診室有<strong style="color: #e74c3c;">檢傷分類</strong></span>
</p>

---

### 檢傷分類：誰先救？

<div style="display: flex; justify-content: center; gap: 1em; flex-wrap: wrap; margin-top: 0.8em;">
  <div class="fragment" style="background: rgba(231,76,60,0.15); padding: 0.8em; border-radius: 8px; flex: 1; min-width: 180px; max-width: 250px; border-left: 4px solid #e74c3c;">
    <p style="font-size: 1.1em; color: #e74c3c;">🔴 可能最優先</p>
    <p style="color: #aaa; font-size: 0.85em;">DNS 查詢<br>政府網站<br>即時訊息（LINE 文字）<br>金融交易</p>
  </div>
  <div class="fragment" style="background: rgba(243,156,18,0.15); padding: 0.8em; border-radius: 8px; flex: 1; min-width: 180px; max-width: 250px; border-left: 4px solid #f39c12;">
    <p style="font-size: 1.1em; color: #f39c12;">🟡 可能次優先</p>
    <p style="color: #aaa; font-size: 0.85em;">一般網頁瀏覽<br>Email 收發<br>低解析度串流</p>
  </div>
  <div class="fragment" style="background: rgba(46,204,113,0.15); padding: 0.8em; border-radius: 8px; flex: 1; min-width: 180px; max-width: 250px; border-left: 4px solid #2ecc71;">
    <p style="font-size: 1.1em; color: #2ecc71;">🟢 可能可延後</p>
    <p style="color: #aaa; font-size: 0.85em;">YouTube 高畫質<br>Instagram 圖片/影片<br>軟體更新下載<br>雲端備份</p>
  </div>
</div>

<p class="fragment fade-up" style="margin-top: 1em; font-size: 1.1em;">
  ISP 工程師<strong>可能會手動介入</strong>，可能會決定誰的封包優先通過<br>
  <span style="color: #aaa;">這就是為什麼有些東西「恢復了」、有些變更慢</span>
</p>

---

### 為什麼 LINE 文字可能恢復了？

<div class="fragment" style="margin-top: 0.8em;">
  <p style="font-size: 1.1em;">1️⃣ LINE 文字訊息 = <strong>相對小的封包</strong></p>
  <p style="color: #aaa;">一則文字訊息可能大約 1 KB</p>
  <p style="color: #aaa;">一張 Instagram 照片可能大約 2,000 KB</p>
  <p style="color: #aaa;">差 <strong style="color: #3498db;">2000 倍</strong></p>
</div>

<div class="fragment" style="margin-top: 1em;">
  <p style="font-size: 1.1em;">2️⃣ ISP 可能把訊息列為<strong style="color: #e74c3c;">高優先</strong></p>
  <p style="color: #aaa;">小封包 + 本地路由 + 高優先 = 可能擠得過去 ✅</p>
</div>

<p class="fragment fade-up" style="margin-top: 0.8em; font-size: 1.1em; color: #f39c12;">
  Instagram 圖片？大封包 + 海外來源 + 可能被降級 = 可能轉圈圈 🖼️
</p>

---

### 你的網路可能不是壞了：可能是被「管」了

<div class="fragment" style="margin-top: 0.8em;">
  <p style="font-size: 1.2em;">🚦 ISP 工程師 = <strong>十字路口的交通警察</strong></p>
</div>

<div class="fragment" style="margin-top: 0.8em;">
  <p>正常時候：綠燈，所有車都能過</p>
  <p style="color: #aaa;">你感覺不到交通警察的存在</p>
</div>

<div class="fragment" style="margin-top: 0.8em;">
  <p>危機時候：警察出來指揮 🖐️</p>
  <p style="color: #aaa;">「救護車先走！公車可以過！私家車等一下！」</p>
</div>

<p class="fragment fade-up" style="margin-top: 1em; font-size: 1.2em;">
  你的 YouTube 可能不是「斷了」<br>
  是被<strong style="color: #f39c12;">可能讓道</strong>給更重要的東西了
</p>

---

### 這代表什麼？一件你該知道的事

<div class="fragment" style="background: rgba(52,152,219,0.1); padding: 1em; border-radius: 8px; margin-top: 0.8em; max-width: 85%; margin-left: auto; margin-right: auto; text-align: left;">
  <p style="font-size: 1.1em;">ISP <strong>有能力</strong>做流量分類和管理</p>
  <p style="color: #aaa;">他們知道哪些封包去哪裡、是什麼類型</p>
</div>

<div class="fragment" style="background: rgba(243,156,18,0.1); padding: 1em; border-radius: 8px; margin-top: 0.8em; max-width: 85%; margin-left: auto; margin-right: auto; text-align: left;">
  <p style="font-size: 1.1em;">這代表 ISP <strong>平時的路由決策</strong>也是「選擇」</p>
  <p style="color: #aaa;">可能把你的流量繞去國外再繞回來</p>
  <p style="color: #aaa;">不在本土做對等連線</p>
</div>

<p class="fragment fade-up" style="margin-top: 1em; font-size: 1.3em; color: #e74c3c;">
  <strong>危機時 ISP 能選擇救誰<br>
  代表平時 ISP 也在選擇犧牲誰</strong>
</p>

---

### 接下來：雲端的問題

<p style="font-size: 1.1em; margin-top: 0.5em; color: #aaa;">
  LINE 文字可能恢復了、可能一些網頁能看了：<br>
  但 SaaS 工具和雲端服務<strong style="color: #e74c3c;">可能完全死掉</strong>
</p>

<p class="fragment" style="font-size: 1.2em; margin-top: 1em;">
  要理解為什麼，我們需要先搞懂一件事：
</p>

<p class="fragment fade-up" style="font-size: 1.5em; margin-top: 1em;">
  <strong style="color: #3498db;">「雲端」到底是什麼？</strong>
</p>

<div class="fragment" style="margin-top: 1em;">
  <p style="font-size: 5em; margin: 0;">☁️🤔</p>
</div>

---

### 「雲端」其實是⋯⋯別人的電腦

<div class="fragment" style="margin-top: 0.8em;">
  <p style="font-size: 1.2em;">你聽過「資料存在雲端」☁️</p>
  <p style="color: #aaa;">聽起來很輕盈、很抽象、飄在天上</p>
</div>

<div class="fragment" style="margin-top: 1em;">
  <p style="font-size: 1.2em;">真相：</p>
  <p style="font-size: 1.3em; color: #3498db;"><strong>你的資料存在別人的電腦裡</strong></p>
  <p style="color: #aaa;">那台電腦放在一棟巨大的建築物裡，有空調、有保全、有備用發電機</p>
  <p style="color: #aaa;">這棟建築叫做<strong>「資料中心」（Data Center）</strong></p>
</div>

<p class="fragment fade-up" style="margin-top: 1em; font-size: 1.1em;">
  台灣有這樣的建築物 🏢<br>
  <span style="color: #2ecc71;">AWS、GCP 都有台灣機房</span><br>
  <span style="color: #aaa; font-size: 0.9em;">你的資料<strong>確實</strong>存在台灣的土地上 ✓</span>
</p>

---

### 工廠和總部

<p style="font-size: 1.1em; margin-top: 0.5em;">
  想像一家<strong style="color: #3498db;">跨國企業</strong>在台灣設了一座<strong>工廠</strong>
</p>

<div style="display: flex; justify-content: center; gap: 2em; flex-wrap: wrap; margin-top: 1em;">
  <div class="fragment" style="background: rgba(46,204,113,0.1); padding: 1em; border-radius: 8px; flex: 1; min-width: 240px; max-width: 320px;">
    <p style="font-size: 1.1em;">🏭 台灣工廠</p>
    <p style="color: #aaa; font-size: 0.9em;">生產產品（存你的檔案）</p>
    <p style="color: #aaa; font-size: 0.9em;">出貨給客戶（回應你的請求）</p>
    <p style="color: #aaa; font-size: 0.9em;">倉庫裡有原料（你的資料）</p>
    <p style="color: #2ecc71; font-size: 0.85em;">→ 這叫「資料平面」<br>Data Plane</p>
  </div>
  <div class="fragment" style="background: rgba(231,76,60,0.1); padding: 1em; border-radius: 8px; flex: 1; min-width: 240px; max-width: 320px;">
    <p style="font-size: 1.1em;">🏢 美國總部</p>
    <p style="color: #aaa; font-size: 0.9em;">核發員工證（身分驗證 IAM）</p>
    <p style="color: #aaa; font-size: 0.9em;">核准預算（配置資源）</p>
    <p style="color: #aaa; font-size: 0.9em;">簽發合約（SSL 憑證）</p>
    <p style="color: #e74c3c; font-size: 0.85em;">→ 這叫「控制平面」<br>Control Plane</p>
  </div>
</div>

<p class="fragment fade-up" style="margin-top: 1em; font-size: 1.1em; color: #f39c12;">
  工廠在台灣 ✓　但做任何重要決定都要<strong>打電話回總部</strong>
</p>


---

### 工廠在台灣，但鑰匙可能在美國

<div class="fragment" style="margin-top: 0.5em;">
  <p style="font-size: 1.1em;">🔑 <strong>員工要進工廠</strong>（你要登入 AWS）</p>
  <p style="color: #aaa;">→ 可能要跟美國總部確認身分（IAM 驗證）</p>
  <p style="color: #aaa;">→ 可能請求走海纜到維吉尼亞 → <span style="color: #e74c3c;">逾時</span></p>
</div>

<div class="fragment" style="margin-top: 0.8em;">
  <p style="font-size: 1.1em;">📋 <strong>工廠要出貨</strong>（網站要更新安全憑證）</p>
  <p style="color: #aaa;">→ 可能要跟美國總部簽發合約（SSL 憑證驗證）</p>
  <p style="color: #aaa;">→ 請求走海纜 → <span style="color: #e74c3c;">逾時</span> → HTTPS 連線失敗</p>
</div>

<div class="fragment" style="margin-top: 0.8em;">
  <p style="font-size: 1.1em;">📞 <strong>客戶要查工廠地址</strong>（DNS 解析）</p>
  <p style="color: #aaa;">→ 地址簿可能在美國（Route 53 在 us-east-1）</p>
  <p style="color: #aaa;">→ 查詢走海纜 → <span style="color: #e74c3c;">逾時</span> → 找不到工廠</p>
</div>

<p class="fragment fade-up" style="margin-top: 0.8em; font-size: 1.2em; color: #e74c3c;">
  工廠完好、原料充足、機器正常<br>
  但就是<strong>開不了門</strong>
</p>

---

### 你的資料就在這裡——但你沒有「授權」打開它

<div style="background: rgba(231,76,60,0.1); padding: 1em; border-radius: 8px; margin-top: 0.5em; max-width: 85%; margin-left: auto; margin-right: auto;">
  <p style="font-size: 1.3em;">🔐</p>
  <p style="font-size: 1.1em;">你的 Google Drive 檔案<br>可能物理上存在彰化的 GCP 機房</p>
  <p style="font-size: 1.2em; margin-top: 0.8em; color: #e74c3c;">
    <strong>但你可能就是打不開</strong>
  </p>
  <p style="color: #aaa; font-size: 0.9em;">因為你<br>可能需要美國的伺服器來確認</p>
</div>

<p class="fragment fade-up" style="margin-top: 1em; font-size: 1.2em;">
  這就像把<strong style="color: #f39c12;">保險箱放在家裡</strong><br>
  但把鑰匙寄放在<strong style="color: #f39c12;">國外的銀行</strong> 🏦
</p>

<p class="fragment" style="color: #aaa; font-size: 0.9em; margin-top: 0.5em;">
  銀行正常營業，但你打不了國際電話了
</p>


---

### 「雲端在台灣」≠ 安全

<div style="display: flex; justify-content: center; gap: 1.5em; flex-wrap: wrap; margin-top: 0.8em;">
  <div class="fragment" style="flex: 1; min-width: 140px; max-width: 200px; text-align: center;">
    <p style="font-size: 2.5em; margin: 0;">🏭</p>
    <p style="font-size: 0.9em;">工廠在台灣</p>
    <p style="color: #2ecc71;">✓</p>
  </div>
  <div class="fragment" style="flex: 1; min-width: 140px; max-width: 200px; text-align: center;">
    <p style="font-size: 2.5em; margin: 0;">🔑</p>
    <p style="font-size: 0.9em;">鑰匙在美國</p>
    <p style="color: #e74c3c;">✗</p>
  </div>
  <div class="fragment" style="flex: 1; min-width: 140px; max-width: 200px; text-align: center;">
    <p style="font-size: 2.5em; margin: 0;">📞</p>
    <p style="font-size: 0.9em;">電話線塞爆了</p>
    <p style="color: #e74c3c;">✗</p>
  </div>
</div>

<div class="fragment" style="margin-top: 1.2em;">
  <p style="font-size: 1.3em;">所以⋯⋯</p>
</div>

<p class="fragment fade-up" style="font-size: 1.4em; margin-top: 0.5em; color: #f39c12;">
  <strong>「我們用台灣的 AWS/GCP」<br>
  可能 ≠<br>
  「我們的服務在對外流量大量降低時還能用」</strong>
</p>

---

### 贏家：真正的純國內服務

<p style="font-size: 1.1em; margin-top: 0.5em; color: #aaa;">
  在這場模擬中，可能有些服務完全不受影響，
</p>

<div class="fragment" style="background: rgba(46,204,113,0.12); padding: 1em; border-radius: 8px; margin-top: 0.8em; max-width: 85%; margin-left: auto; margin-right: auto; text-align: left; border: 1px solid rgba(46,204,113,0.3);">
  <p style="font-size: 1.1em; color: #2ecc71;"><strong>✅ 活下來的服務長這樣：</strong></p>
  <p>伺服器在台灣 <!-- .element: class="fragment" --></p>
  <p>認證（Auth）在台灣 <!-- .element: class="fragment" --></p>
  <p>DNS 權威伺服器在台灣 <!-- .element: class="fragment" --></p>
  <p>CDN 來源站在台灣 <!-- .element: class="fragment" --></p>
</div>

<p class="fragment fade-up" style="margin-top: 1em; font-size: 1.2em; color: #2ecc71;">
  <strong>整條鏈都在島內 → 海纜斷不斷，跟它無關</strong>
</p>

---

### 差別在哪？一張表

<div style="font-size: 0.85em; margin-top: 0.5em;">

| | 伺服器 | 認證 | DNS | CDN 來源 | 海纜斷裂時可能情境 |
|---|:---:|:---:|:---:|:---:|---|
| **純國內 stack** | 🟢 台灣 | 🟢 台灣 | 🟢 台灣 | 🟢 台灣 | ✅ 正常運作 |
| **台灣雲端** | 🟢 台灣 | 🔴 美國 | 🔴 美國 | 🟢 台灣 | ⚠️ 能跑但登不進去 |
| **完全海外** | 🔴 海外 | 🔴 海外 | 🔴 海外 | 🔴 海外 | ❌ 完全掛掉 |

</div>

<p class="fragment fade-up" style="margin-top: 1em; font-size: 1.1em;">
  大多數台灣企業的服務落在<strong style="color: #f39c12;">中間那一列</strong><br>
  <span style="color: #aaa;">看起來在台灣，但 dependency 在海外</span>
</p>

---

### 是技術限制嗎？

<div class="fragment" style="margin-top: 0.8em;">
  <p style="font-size: 1.1em;">那些活下來的服務，不是運氣好</p>
  <p style="color: #aaa;">是有人<strong>選擇</strong>多花時間、多花錢、把每一層都做到國內自主</p>
</div>


<p class="fragment" style="font-size: 1.4em; margin-top: 0.5em; color: #f39c12;">
  「如果海纜斷了，我們的服務還能用嗎？」
</p>
