<h3 style="color: #e74c3c;">第三階段：30–60 分鐘</h3>

## 剛剛還好好的，怎麼又壞了？

---

### 你感受到的

- Google Drive 剛剛可能還能開，現在卡住了 <!-- .element: class="fragment" -->
- 新聞網站可能文字有、圖片全消失 <!-- .element: class="fragment" -->
- LINE 可能閃退後重開，可能登不回去了 <!-- .element: class="fragment" -->
- 網銀 app 可能要你重新輸入密碼，然後愛的魔力轉圈圈 <!-- .element: class="fragment" -->

<p class="fragment fade-up" style="font-size: 1.3em; margin-top: 1em;">
  一次不會全壞<br>
  <strong style="color: #f39c12;">可能是一個一個壞掉</strong>，且看起來毫無規律
</p>


---

### 回到便利商店

<div class="fragment" style="margin-top: 0.8em;">
  <p style="font-size: 1.2em;">你家旁邊的 <strong>7-11</strong> 🏪</p>
  <p style="color: #aaa;">架上有飲料、便當、零食的「複製品」</p>
</div>

<div class="fragment" style="margin-top: 0.8em;">
  <p style="font-size: 1.2em;">這些商品從哪來？<strong>海外的倉庫</strong> 🚢</p>
  <p style="color: #aaa;">7-11 不生產東西，它從倉庫進貨、放在架上給你拿</p>
</div>

<p class="fragment fade-up" style="margin-top: 1em; font-size: 1.1em;">
  網路世界也一樣，<br>
  <strong style="color: #3498db;">CDN</strong> 就是你家旁邊的數位便利商店
</p>
 <p style="color: #aaa;">Content Delivery Network</p>

---

### 保存期限：TTL
 <p style="color: #aaa;">Time To Live</p>
<div class="fragment" style="margin-top: 0.8em;">
  <p>便利商店的便當有<strong>保存期限</strong></p>
  <p style="color: #aaa;">過期了就不能賣，要從倉庫補新的</p>
</div>

<div class="fragment" style="margin-top: 0.8em;">
  <p>CDN 快取也有類似保存期限，叫做 <strong style="color: #3498db;">TTL</strong></p>
  <p style="color: #aaa;">Time To Live：這份複製品可以用多久</p>
</div>

<div class="fragment" style="margin-top: 0.8em;">
  <p style="font-size: 1.1em;">TTL 可能是 <strong>5 分鐘</strong>，也可能是 <strong>24 小時</strong></p>
  <p style="color: #aaa;">每個網站、每個檔案的設定都不同</p>
</div>

<p class="fragment fade-up" style="margin-top: 0.8em; font-size: 1.1em; color: #f39c12;">
  前 30 分鐘大部分快取還沒到期，所以東西「還能用」<br>
  現在，保存期限開始一個一個到了
</p>

---

### 便利商店補不到貨了

<div class="fragment" style="margin-top: 0.8em;">
  <p style="font-size: 1.2em;">架上的便當過期了 → 要從倉庫補貨</p>
</div>

<div class="fragment" style="margin-top: 0.8em;">
  <p style="color: #e74c3c; font-size: 1.2em;">但通往倉庫的路塞爆了 🚛💨</p>
  <p style="color: #aaa;">（對外流量壅塞 = 國際連線極度緩慢）</p>
</div>

<div class="fragment" style="margin-top: 0.8em;">
  <p>補貨卡車出發了⋯⋯但塞在路上回不來</p>
  <p style="color: #aaa;">CDN 向海外原始伺服器要新資料 → 逾時 → 失敗</p>
</div>

<p class="fragment fade-up" style="margin-top: 1em; font-size: 1.3em; color: #e74c3c;">
  快取過期 + 補不到貨 = 架上空了
</p>

---

### 為什麼有些能看、有些不行？

<div style="display: flex; justify-content: center; gap: 2em; flex-wrap: wrap; margin-top: 0.8em;">
  <div class="fragment" style="background: rgba(46,204,113,0.1); padding: 1em; border-radius: 8px; flex: 1; min-width: 250px; max-width: 350px;">
    <p style="font-size: 1.1em;">✅ 還能看</p>
    <p style="color: #aaa; font-size: 0.9em;">熱門 YouTube 影片<br>常用網站的 CSS/JS<br>大家都在看的新聞圖片</p>
    <p style="color: #2ecc71; font-size: 0.9em;">→ 快取剛補過、TTL 還沒到</p>
  </div>
  <div class="fragment" style="background: rgba(231,76,60,0.1); padding: 1em; border-radius: 8px; flex: 1; min-width: 250px; max-width: 350px;">
    <p style="font-size: 1.1em;">❌ 看不到了</p>
    <p style="color: #aaa; font-size: 0.9em;">冷門頁面、舊文章<br>你很久沒開的文件<br>TTL 短的即時內容</p>
    <p style="color: #e74c3c; font-size: 0.9em;">→ 快取已過期、補貨失敗</p>
  </div>
</div>

<p class="fragment fade-up" style="margin-top: 1em; font-size: 1.1em;">
  這就是為什麼<strong style="color: #f39c12;">同一個網站有些部分能看、有些不行</strong><br>
  <span style="color: #aaa;">結果以為是網站壞了，其實是快取到期的時間不同</span>
</p>

---

### 什麼是 Auth Token？

<p style="font-size: 1.2em; margin-top: 0.5em;">
  <br>
  假設我們去<strong style="color: #3498db;">遊樂園</strong>
</p>

<div class="fragment" style="margin-top: 1em;">
  <p style="font-size: 5em; margin: 0;">🎢</p>
</div>

<p class="fragment fade-up" style="font-size: 1.1em; margin-top: 0.5em;">
  去遊樂園<br>
  在入口<strong>買了票、驗了身分</strong><br>
  然後工作人員在你手上蓋了一個<strong style="color: #3498db;">章</strong>
</p>

---

### 手上的章 = Auth Token

<div class="fragment" style="margin-top: 0.8em;">
  <p style="font-size: 1.2em;">蓋了章之後，你可以：</p>
  <p>玩雲霄飛車 🎢 — 給工作人員看手上的章 ✓</p>
  <p>玩旋轉木馬 🎠 — 看章 ✓</p>
  <p>買園區餐點 🍔 — 看章 ✓</p>
</div>

<div class="fragment" style="margin-top: 0.8em;">
  <p style="color: #aaa;">每次不用重新排隊買票、重新驗身分</p>
  <p style="color: #aaa;">手上的章就代表「這個人已經驗證過了」</p>
</div>

<p class="fragment fade-up" style="margin-top: 1em; font-size: 1.1em; color: #3498db;">
  <strong>Auth Token 就是你手上的那個章</strong><br>
  <span style="font-size: 0.9em; color: #aaa;">你登入 Google 之後，瀏覽器拿到一個「章」<br>之後開 Gmail、Drive、YouTube 都不用重新登入</span>
</p>

---

### 但印章會褪色

<div class="fragment" style="margin-top: 0.8em;">
  <p style="font-size: 1.2em;">遊樂園的章用的是<strong style="color: #f39c12;">特殊墨水</strong></p>
  <p style="color: #aaa;">15 分鐘到 1 小時後，章就會褪色、看不到了</p>
</div>

<div class="fragment" style="margin-top: 1em;">
  <p style="font-size: 1.1em;">為什麼不用永久的墨水？</p>
</div>

<div class="fragment" style="background: rgba(231,76,60,0.1); padding: 0.8em; border-radius: 8px; margin-top: 0.5em; max-width: 80%; margin-left: auto; margin-right: auto;">
  <p style="text-align: left;">🔒 如果有人<strong>偷印了你的章</strong>（token 被盜）</p>
  <p style="text-align: left; color: #aaa;">用褪色墨水 → 小偷最多用 15 分鐘</p>
  <p style="text-align: left; color: #aaa;">用永久墨水 → 小偷可以<strong>永遠冒充你</strong></p>
</div>

<p class="fragment fade-up" style="margin-top: 0.8em; color: #f39c12;">
  所以 token 故意設計成會過期：安全機制
</p>

---

### 章褪色了，回售票口重蓋

<div class="fragment" style="margin-top: 0.8em;">
  <p style="font-size: 1.2em;">章褪色了 → 走回入口售票處 🎫</p>
  <p style="color: #aaa;">出示你的年票卡，工作人員重新蓋章</p>
  <p style="color: #aaa;">整個過程只要幾秒鐘，你幾乎不會注意到</p>
</div>

<div class="fragment" style="margin-top: 1em;">
  <p style="font-size: 1.3em;">平常這完全不是問題</p>
  <p style="color: #aaa;">app 在背景自動幫你「重蓋章」，你根本感覺不到</p>
</div>

<p class="fragment fade-up" style="margin-top: 1em; font-size: 1.3em; color: #e74c3c;">
  但是⋯⋯如果售票處在<strong>海的另一邊</strong>呢？
</p>

---

### 售票處在海的另一邊

<div class="fragment" style="margin-top: 0.8em;">
  <p style="font-size: 1.1em;">Google 的認證伺服器 可能在 🇺🇸 美國</p>
  <p style="font-size: 1.1em;">LINE 的認證伺服器 可能在 🇯🇵 日本</p>
  <p style="font-size: 1.1em;">Microsoft 的認證伺服器 可能在 🇺🇸 美國</p>
</div>

<div class="fragment" style="margin-top: 1em;">
  <p>你的章褪色了 → 可能要跨海去重新蓋章</p>
  <p style="color: #e74c3c; font-size: 1.2em;">但對外流量雍塞 = 那條路大塞車 🚗🚗🚗</p>
</div>

<p class="fragment fade-up" style="margin-top: 0.8em; font-size: 1.1em;">
  重新蓋章的請求<strong>送出去了⋯⋯但回不來</strong><br>
  <span style="color: #aaa;">等了 30 秒 → 逾時 → 失敗</span>
</p>

<p class="fragment" style="margin-top: 0.5em; font-size: 1.2em; color: #e74c3c;">
  你被登出了。而且<strong>登不回去</strong>。
</p>

---

### 每個人在不同時間被登出

<div style="margin-top: 0.5em;">
  <div class="fragment" style="background: rgba(255,255,255,0.05); padding: 0.6em 1em; border-radius: 8px; margin-bottom: 0.5em; max-width: 85%; margin-left: auto; margin-right: auto;">
    <p style="text-align: left; margin: 0;">⏱️ 斷纜後 20 分鐘：<span style="color: #e74c3c;">Google Drive</span> 的章可能褪色了 → 可能被登出</p>
  </div>
  <div class="fragment" style="background: rgba(255,255,255,0.05); padding: 0.6em 1em; border-radius: 8px; margin-bottom: 0.5em; max-width: 85%; margin-left: auto; margin-right: auto;">
    <p style="text-align: left; margin: 0;">⏱️ 斷纜後 35 分鐘：<span style="color: #e74c3c;">LINE</span> 的章可能褪色了 → 可能閃退後登不回去</p>
  </div>
  <div class="fragment" style="background: rgba(255,255,255,0.05); padding: 0.6em 1em; border-radius: 8px; margin-bottom: 0.5em; max-width: 85%; margin-left: auto; margin-right: auto;">
    <p style="text-align: left; margin: 0;">⏱️ 斷纜後 45 分鐘：<span style="color: #e74c3c;">網路銀行</span> 的章褪色了 → 要求重新登入 → 失敗</p>
  </div>
  <div class="fragment" style="background: rgba(255,255,255,0.05); padding: 0.6em 1em; border-radius: 8px; margin-bottom: 0.5em; max-width: 85%; margin-left: auto; margin-right: auto;">
    <p style="text-align: left; margin: 0;">⏱️ 斷纜後 50 分鐘：<span style="color: #e74c3c;">公司 Slack</span> 的章可能褪色了 → 可能完全斷線</p>
  </div>
</div>

<p class="fragment fade-up" style="margin-top: 0.8em; font-size: 1.2em; color: #f39c12;">
  這就是為什麼看起來「毫無規律」<br>
  <span style="font-size: 0.9em; color: #aaa;">因為每個 app 的章在不同時間褪色</span>
</p>

---

### Token 的真面目

<div class="fragment" style="margin-top: 0.5em;">
  <p style="font-size: 1.1em;">技術上，Token 長這樣：</p>
</div>

<div class="fragment" style="background: rgba(255,255,255,0.05); padding: 0.8em; border-radius: 8px; max-width: 90%; margin: 0.5em auto; font-family: monospace; font-size: 0.7em; word-break: break-all; text-align: left;">
  eyJhbGciOiJSUzI1NiJ9.<span style="color: #3498db;">eyJ1c2VyIjoi5bCP5piOIiwic2NvcGUiOiJkcml2ZSIsImV4cCI6MTcxMTEyMzQ1Nn0</span>.SflKxwRJSMeKKF2QT4fw
</div>

<div class="fragment" style="margin-top: 0.8em;">
  <p>這叫 <strong style="color: #3498db;">JWT</strong>（JSON Web Token），裡面包含：</p>
</div>

<div class="fragment" style="display: flex; justify-content: center; gap: 1.5em; flex-wrap: wrap; margin-top: 0.5em;">
  <div style="background: rgba(52,152,219,0.1); padding: 0.6em 1em; border-radius: 8px;">
    <p style="margin: 0;">👤 你是誰</p>
    <p style="margin: 0; color: #aaa; font-size: 0.8em;">user: 小明</p>
  </div>
  <div style="background: rgba(52,152,219,0.1); padding: 0.6em 1em; border-radius: 8px;">
    <p style="margin: 0;">🔑 能做什麼</p>
    <p style="margin: 0; color: #aaa; font-size: 0.8em;">scope: drive</p>
  </div>
  <div style="background: rgba(52,152,219,0.1); padding: 0.6em 1em; border-radius: 8px;">
    <p style="margin: 0;">⏰ 何時到期</p>
    <p style="margin: 0; color: #aaa; font-size: 0.8em;">exp: 1 hr</p>
  </div>
</div>

<p class="fragment" style="margin-top: 0.5em; color: #aaa; font-size: 0.9em;">
  最後一段是<strong>數位簽章</strong>：防止偽造，只有伺服器能產生
</p>

---

### Token 的一生

<div style="margin-top: 0.5em; max-width: 90%; margin-left: auto; margin-right: auto;">
  <div class="fragment" style="background: rgba(46,204,113,0.1); padding: 0.6em 1em; border-radius: 8px; margin-bottom: 0.5em;">
    <p style="text-align: left; margin: 0;">1️⃣ <strong>登入</strong>：輸入帳號密碼 → 伺服器給你兩個東西</p>
    <p style="text-align: left; margin: 0; color: #aaa; font-size: 0.9em;">　　Access Token（通行章）有效 15 分鐘～1 小時</p>
    <p style="text-align: left; margin: 0; color: #aaa; font-size: 0.9em;">　　Refresh Token（年票卡）有效數天～數週</p>
  </div>
  <div class="fragment" style="background: rgba(52,152,219,0.1); padding: 0.6em 1em; border-radius: 8px; margin-bottom: 0.5em;">
    <p style="text-align: left; margin: 0;">2️⃣ <strong>使用中</strong>：每次操作都帶著 Access Token</p>
    <p style="text-align: left; margin: 0; color: #aaa; font-size: 0.9em;">　　伺服器看章就放行，不用每次都驗密碼</p>
  </div>
  <div class="fragment" style="background: rgba(243,156,18,0.1); padding: 0.6em 1em; border-radius: 8px; margin-bottom: 0.5em;">
    <p style="text-align: left; margin: 0;">3️⃣ <strong>章褪色</strong>：Access Token 到期 → 用 Refresh Token 自動換新章</p>
    <p style="text-align: left; margin: 0; color: #aaa; font-size: 0.9em;">　　背景自動完成，你完全不會發現</p>
  </div>
  <div class="fragment" style="background: rgba(231,76,60,0.1); padding: 0.6em 1em; border-radius: 8px;">
    <p style="text-align: left; margin: 0;">4️⃣ <strong>年票也到期</strong>：Refresh Token 也失效 → 必須重新輸入帳號密碼</p>
    <p style="text-align: left; margin: 0; color: #aaa; font-size: 0.9em;">　　這就是為什麼你偶爾會被要求「重新登入」</p>
  </div>
</div>

---

### 為什麼不能給永久通行證？

<div style="display: flex; justify-content: center; gap: 2em; flex-wrap: wrap; margin-top: 0.8em;">
  <div class="fragment" style="background: rgba(231,76,60,0.1); padding: 1em; border-radius: 8px; flex: 1; min-width: 250px; max-width: 350px;">
    <p style="font-size: 1.1em;">🔓 如果 Token 永久有效</p>
    <p style="color: #aaa; font-size: 0.9em;">被偷了 → 攻擊者永遠能冒充你</p>
    <p style="color: #aaa; font-size: 0.9em;">權限變了 → 舊 token 還有舊權限</p>
    <p style="color: #aaa; font-size: 0.9em;">離職了 → token 還能用</p>
  </div>
  <div class="fragment" style="background: rgba(46,204,113,0.1); padding: 1em; border-radius: 8px; flex: 1; min-width: 250px; max-width: 350px;">
    <p style="font-size: 1.1em;">🔒 Token 定期過期</p>
    <p style="color: #aaa; font-size: 0.9em;">被偷了 → 最多 15 分鐘就失效</p>
    <p style="color: #aaa; font-size: 0.9em;">權限變了 → 下次換發會更新</p>
    <p style="color: #aaa; font-size: 0.9em;">離職了 → token 自然失效</p>
  </div>
</div>

<p class="fragment fade-up" style="margin-top: 1em; font-size: 1.1em;">
  Token 過期不是設計缺陷——是<strong style="color: #2ecc71;">安全機制</strong><br>
  <span style="color: #aaa; font-size: 0.9em;">就像門鎖密碼定期更換：不方便，但更安全</span>
</p>

---

### 海纜斷裂時可能的連鎖反應

<div style="margin-top: 0.5em; max-width: 90%; margin-left: auto; margin-right: auto;">
  <div class="fragment" style="border-left: 3px solid #3498db; padding-left: 1em; margin-bottom: 0.5em;">
    <p style="margin: 0;">Access Token 到期</p>
    <p style="margin: 0; color: #aaa; font-size: 0.9em;">app 可能在背景嘗試用 Refresh Token 換新的</p>
  </div>
  <div class="fragment" style="border-left: 3px solid #f39c12; padding-left: 1em; margin-bottom: 0.5em;">
    <p style="margin: 0;">Refresh 可能請求送往海外認證伺服器</p>
    <p style="margin: 0; color: #aaa; font-size: 0.9em;">但國際連線壅塞⋯⋯等 10 秒、20 秒⋯⋯</p>
  </div>
  <div class="fragment" style="border-left: 3px solid #e74c3c; padding-left: 1em; margin-bottom: 0.5em;">
    <p style="margin: 0; color: #e74c3c;">逾時失敗 ✗</p>
    <p style="margin: 0; color: #aaa; font-size: 0.9em;">app 判定「認證失效」→ 可能強制登出</p>
  </div>
  <div class="fragment" style="border-left: 3px solid #e74c3c; padding-left: 1em; margin-bottom: 0.5em;">
    <p style="margin: 0;">跳出登入頁面 → 你輸入帳號密碼</p>
    <p style="margin: 0; color: #e74c3c; font-size: 0.9em;">但登入頁面本身可能也要連到海外伺服器 → 也逾時 ✗</p>
  </div>
</div>

<p class="fragment fade-up" style="margin-top: 0.8em; font-size: 1.2em; color: #e74c3c;">
  登出了，而且<strong>可能登不回去</strong>
</p>

---

### 你的 App 可能正在一個一個登出

<div class="fragment" style="background: rgba(255,255,255,0.05); padding: 0.8em; border-radius: 8px; margin-top: 0.5em; max-width: 90%; margin-left: auto; margin-right: auto;">
  <p style="text-align: left; font-size: 1em;">
    <span style="color: #2ecc71;">t+0 min</span>　對外流量驟降：所有 Token 開始倒數<br>
    <span style="color: #2ecc71;">t+15 min</span>　<span style="color: #aaa;">網銀 token 到期 → 被登出</span><br>
    <span style="color: #f39c12;">t+25 min</span>　<span style="color: #aaa;">Slack token 到期 → 可能離線</span><br>
    <span style="color: #f39c12;">t+35 min</span>　<span style="color: #aaa;">LINE 需要重新驗證 → 可能失敗</span><br>
    <span style="color: #e74c3c;">t+45 min</span>　<span style="color: #aaa;">Google Drive token 到期 → 可能無法存取文件</span><br>
    <span style="color: #e74c3c;">t+60 min</span>　<span style="color: #aaa;">可能幾乎所有需要認證的服務都已失效</span>
  </p>
</div>

<p class="fragment fade-up" style="margin-top: 0.8em; font-size: 1.1em;">
  「一次斷線」不太可能發生<strong style="color: #e74c3c;">比較像慢動作的大規模登出</strong><br>
  <span style="color: #aaa; font-size: 0.9em;">每個人、每個 app、不同時間：看起來完全隨機</span>
</p>


---

### 接下來：DNS

<p style="font-size: 1.2em; margin-top: 1em;">
  CDN 快取到期 → 內容消失<br>
  Auth Token 到期 → 被登出
</p>

<p class="fragment fade-up" style="font-size: 1.3em; margin-top: 1em; color: #f39c12;">
  還有第三個東西也在倒數⋯⋯
</p>

<p class="fragment" style="font-size: 1.2em; margin-top: 0.5em;">
  而且這個東西壞掉的話<br>
  <strong style="color: #e74c3c;">連網站在哪都找不到</strong>
</p>

---

### 什麼是 DNS？網路的電話簿

<div class="fragment" style="margin-top: 0.8em;">
  <p style="font-size: 1.2em;">你在瀏覽器打 <strong style="color: #3498db;">google.com</strong></p>
  <p style="color: #aaa;">但電腦不懂「google.com」是什麼</p>
</div>

<div class="fragment" style="margin-top: 0.8em;">
  <p style="font-size: 1.2em;">電腦只懂<strong>數字地址</strong>：<span style="color: #3498db;">142.250.185.46</span></p>
  <p style="color: #aaa;">這叫 IP 位址：像電話號碼一樣，每台伺服器都有一組</p>
</div>

<p class="fragment fade-up" style="margin-top: 1em; font-size: 1.2em;">
  <strong style="color: #3498db;">DNS</strong> = 一本電話簿 📒<br>
  <span style="font-size: 0.9em; color: #aaa;">把「名字」翻譯成「電話號碼」</span><br>
  <span style="font-size: 0.9em; color: #aaa;">google.com → 142.250.185.46</span>
</p>

<p class="fragment" style="margin-top: 0.5em; font-size: 1.1em; color: #f39c12;">
  沒有這本電話簿，你就算知道對方的名字也打不了電話
</p>

---

### DNS 怎麼查？像打 104 查號台

<div class="fragment" style="margin-top: 0.5em;">
  <p>你的手機想找 <strong style="color: #3498db;">google.com</strong> 的電話號碼</p>
</div>

<div style="margin-top: 0.5em; max-width: 90%; margin-left: auto; margin-right: auto;">
  <div class="fragment" style="border-left: 3px solid #3498db; padding-left: 1em; margin-bottom: 0.4em;">
    <p style="margin: 0;">1️⃣ 先翻自己的通訊錄（本機快取）</p>
    <p style="margin: 0; color: #aaa; font-size: 0.85em;">之前查過就直接用，不用再問別人</p>
  </div>
  <div class="fragment" style="border-left: 3px solid #3498db; padding-left: 1em; margin-bottom: 0.4em;">
    <p style="margin: 0;">2️⃣ 沒有 → 打給 ISP 的查號台（DNS 解析器）</p>
    <p style="margin: 0; color: #aaa; font-size: 0.85em;">你的中華電信 / 台灣大 有一台專門幫你查號碼的伺服器</p>
  </div>
  <div class="fragment" style="border-left: 3px solid #3498db; padding-left: 1em; margin-bottom: 0.4em;">
    <p style="margin: 0;">3️⃣ ISP 也沒有 → 一路往上問到「總機」</p>
    <p style="margin: 0; color: #aaa; font-size: 0.85em;">Root Server → .com 管理者 → google.com 的權威伺服器</p>
  </div>
  <div class="fragment" style="border-left: 3px solid #2ecc71; padding-left: 1em;">
    <p style="margin: 0; color: #2ecc71;">4️⃣ 查到了！把結果記在通訊錄裡下次用</p>
    <p style="margin: 0; color: #aaa; font-size: 0.85em;">這就是「DNS 快取」：記住查到的結果，省得每次都打電話問</p>
  </div>
</div>

---

### DNS 快取也有保存期限

<div class="fragment" style="margin-top: 0.8em;">
  <p style="font-size: 1.1em;">通訊錄裡的電話號碼也會「過期」</p>
  <p style="color: #aaa;">google.com 的 TTL 可能設 300 秒（5 分鐘）</p>
  <p style="color: #aaa;">某些 .tw 網站可能設 3600 秒（1 小時）</p>
</div>

<div class="fragment" style="margin-top: 1em;">
  <p style="font-size: 1.1em;">為什麼不永久記住？</p>
  <p style="color: #aaa;">因為伺服器可能搬家（換 IP）、做負載平衡、或做故障切換</p>
  <p style="color: #aaa;">如果永遠用舊號碼，可能打到空號</p>
</div>

<p class="fragment fade-up" style="margin-top: 1em; font-size: 1.1em; color: #f39c12;">
  所以 DNS 快取也有 TTL：過期就要<strong>重新查號</strong><br>
  <span style="color: #aaa; font-size: 0.9em;">平常幾十毫秒搞定，你完全不會發現</span>
</p>

---

### DNS 快取過期 = 找不到門牌號碼

<div class="fragment" style="margin-top: 0.5em;">
  <p style="font-size: 1.1em;">假設有一個網站 <strong style="color: #3498db;">service.gov.tw</strong></p>
  <p style="color: #aaa;">伺服器就在台北市內 🏢</p>
</div>

<div class="fragment" style="margin-top: 0.8em;">
  <p>你的裝置之前查過，通訊錄裡有它的 IP</p>
  <p style="color: #2ecc71;">→ 連線正常、速度快 ✓</p>
</div>

<div class="fragment" style="margin-top: 0.8em;">
  <p>但 DNS 快取到期了：需要重新查號</p>
  <p style="color: #aaa;">權威 DNS 伺服器在哪？<span style="color: #e74c3c;">可能在美國（e.g. AWS Route 53）</span></p>
</div>

<p class="fragment fade-up" style="margin-top: 0.8em; font-size: 1.2em; color: #e74c3c;">
  查號的電話打不通 → 你<strong>查不到門牌號碼</strong><br>
  <span style="font-size: 0.9em;">伺服器就在 10 公里外：但你找不到它</span>
</p>

<p class="fragment" style="margin-top: 0.5em; color: #aaa; font-size: 0.9em;">
  不是伺服器掛了，不是網路斷了<br>
  <strong style="color: #f39c12;">是你忘了地址，而且問不到</strong>
</p>
