<h3 style="color: #e74c3c;">第一階段：0–5 分鐘</h3>

## 為什麼我的電話突然斷了？

---

### 你可能會感受到的

- LINE 語音通話 → 機器人聲音 → 斷線 ☎️❌ <!-- .element: class="fragment" -->
- Instagram → 白畫面 <!-- .element: class="fragment" -->
- Google Drive → 載入一半，卡住不動 <!-- .element: class="fragment" -->
- 看一眼右上角 <!-- .element: class="fragment" -->

<p class="fragment fade-up" style="font-size: 1.6em; margin-top: 0.8em;">
  Wi-Fi 訊號滿格 📶
</p>

---

### 「是 WiFi 機的問題，還是網路的問題？」

<div class="fragment" style="margin-top: 1em;">
  <p style="font-size: 1.1em;">Wi-Fi 訊號滿格 ≠ 網路正常</p>
</div>

<div class="fragment" style="margin-top: 1em; text-align: left; max-width: 80%; margin-left: auto; margin-right: auto;">
  <p>📱 → 📡 <strong>Wi-Fi</strong>：你的手機到你家路由器</p>
  <p style="color: #aaa;">這段完全正常 ✓</p>
</div>

<div class="fragment" style="text-align: left; max-width: 80%; margin-left: auto; margin-right: auto;">
  <p>📡 → 🌏 <strong>網路</strong>：你家路由器到全世界</p>
  <p style="color: #e74c3c;">這段出事了 ✗</p>
</div>

<p class="fragment fade-up" style="margin-top: 1em;">
  問題不在你家，在<strong>海底</strong>
</p>

---

### 當代的網路到底是什麼？

想像網路是一個由**幾千間郵局**組成的系統 <!-- .element: class="fragment" style="font-size: 1.1em;" -->

<div class="fragment" style="margin-top: 1em;">
  <p>🏣 每間郵局 = 一個網路機房（ISP、資料中心）</p>
</div>

<div class="fragment">
  <p>✉️ 你的資料 = 一封封信件（封包）</p>
</div>

<div class="fragment">
  <p>🛣️ 郵局之間有很多條路可以互相送信</p>
</div>

<p class="fragment fade-up" style="margin-top: 1em; font-size: 1.1em;">
  你在台北寄信到東京，信會經過好幾間郵局<br>一站一站轉送過去
</p>

---

### 郵局怎麼知道信要往哪送？

<div class="fragment" style="margin-top: 1em;">
  <p>每間郵局門口都有一塊<strong>路牌</strong> 🪧</p>
</div>

<div class="fragment" style="margin-top: 0.5em; background: rgba(255,255,255,0.05); padding: 0.8em; border-radius: 8px; max-width: 70%; margin-left: auto; margin-right: auto;">
  <p style="text-align: left;">「要去日本？→ 交給南邊那間郵局」</p>
  <p style="text-align: left;">「要去美國？→ 交給東邊那間郵局」</p>
  <p style="text-align: left;">「要去高雄？→ 交給隔壁那間郵局」</p>
</div>

<div class="fragment" style="margin-top: 1em;">
  <p>這塊路牌，在網路世界叫做<strong>路由表</strong></p>
</div>

<div class="fragment">
  <p>郵局之間互相更新路牌的方法，就叫 <strong>BGP</strong></p>
  <p style="color: #aaa; font-size: 0.8em;">Border Gateway Protocol 邊界閘道協定</p>
</div>

---

### 海纜斷了 = 路斷了

<div class="fragment" style="margin-top: 1em;">
  <p>光纖裡的光束<strong>直接消失</strong>（畢竟斷了）</p>
</div>

<div class="fragment" style="margin-top: 0.8em;">
  <p>離斷點最近的郵局第一個發現：</p>
  <p style="font-size: 1.3em; color: #e74c3c;">「這條路不通了！」</p>
</div>

<div class="fragment" style="margin-top: 0.8em;">
  <p>它立刻向鄰居廣播：</p>
  <p style="font-size: 1.2em;">「大家注意！往南的路斷了！<br>不要再把信往這邊送了！」</p>
</div>

<p class="fragment fade-up" style="margin-top: 0.8em; color: #f39c12;">
  這則消息開始一間接一間傳開⋯⋯
</p>

---

### 重新算路的混亂期

<p style="color: #aaa; font-size: 0.9em;">BGP Reconvergence</p>

<div class="fragment" style="margin-top: 0.8em;">
  <p>全球幾千間郵局同時收到消息</p>
  <p style="color: #e74c3c;">但不是<strong>同時</strong>收到</p>
</div>

<div class="fragment" style="margin-top: 0.8em; background: rgba(255,255,255,0.05); padding: 0.8em; border-radius: 8px; max-width: 80%; margin-left: auto; margin-right: auto;">
  <p style="text-align: left;">🏣 A 郵局已經改路牌了 ✓</p>
  <p style="text-align: left;">🏣 B 郵局還不知道路斷了 ✗</p>
  <p style="text-align: left;">🏣 C 郵局收到了，但還在算新路線 ⏳</p>
</div>

<div class="fragment" style="margin-top: 0.8em;">
  <p>你的信被⋯⋯</p>
  <ul>
    <li>送到已經斷掉的路 → <strong>丟失</strong></li>
    <li>在兩間郵局之間來回彈 → <strong>繞圈</strong></li>
    <li>沒有郵局願意收 → <strong>退回</strong></li>
  </ul>
</div>

<p class="fragment fade-up" style="margin-top: 0.5em; color: #f39c12;">
  這段混亂期：30 秒 ~ 數分鐘
</p>

---

### 對你來說，可能就是

<h2 class="fragment" style="color: #e74c3c;">全部斷了</h2>

<div class="fragment" style="margin-top: 1em; text-align: left; max-width: 75%; margin-left: auto; margin-right: auto;">
  <p>封包被丟掉 → 網頁可能載不出來</p>
  <p>封包繞遠路 → 延遲可能從 20ms 變 2000ms</p>
  <p>封包來回彈 → 可能根本到不了目的地</p>
</div>

<p class="fragment fade-up" style="margin-top: 1em; font-size: 1.1em;">
  實際上 50% 的對外網路流量還在<br>
  但在路由重算完成之前<br>
  對一般人來說可能就是<strong>卡爆</strong>
</p>

---

### 假設 LINE 語音掛了，<br>但文字可能還活著？

<div class="fragment" style="margin-top: 1em; display: flex; justify-content: center; gap: 2em; flex-wrap: wrap;">
  <div style="background: rgba(46,204,113,0.1); padding: 1em; border-radius: 8px; flex: 1; min-width: 250px; max-width: 350px;">
    <p style="font-size: 1.2em;">💬 文字訊息</p>
    <p>很小的封包（可能僅幾 KB）</p>
    <p>能鑽過混亂的空隙</p>
    <p>晚幾秒到也沒差</p>
  </div>
  <div style="background: rgba(231,76,60,0.1); padding: 1em; border-radius: 8px; flex: 1; min-width: 250px; max-width: 350px;">
    <p style="font-size: 1.2em;">🎙️ 語音通話</p>
    <p>持續的即時串流</p>
    <p>掉幾個封包 = 機器人聲</p>
    <p>延遲超過 300ms = 斷線</p>
  </div>
</div>

<div class="fragment" style="margin-top: 1.2em; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 0.8em;">
  <p>我們還不確定的是：</p>
  <p style="color: #e74c3c; font-size: 1.1em;">
    LINE 的通話伺服器<strong>可能在日本？</strong><br>
    台灣的語音通話<strong>可能必須出海</strong>才能接通？
  </p>
</div>
