# 果然好味單頁式網站使用手冊

## 1. 簡介
「果然好味」為靜態單頁式水果商店網站，提供英雄橫幅、熱銷水果、服務特色以及聯絡資訊等區塊，適合用於宣傳或快速建立品牌曝光。此手冊將協助您快速了解檔案結構、內容修改方法與部署流程。

## 2. 系統需求
- 任一現代瀏覽器（Chrome、Safari、Firefox、Edge 等）
- 文字編輯器（建議使用 VS Code、Sublime Text 或其他支援語法高亮的編輯器）
- 若需進行本機預覽，建議安裝簡易靜態伺服器（如 VS Code Live Server、`python -m http.server`）。

## 3. 專案結構
```
Dennys/
├── index.html    # 網頁主體與區塊內容
├── styles.css    # 網頁樣式設定與響應式調整
└── 螢幕快照...   # 參考用的原始設計截圖
```

## 4. 修改內容
### 4.1 文字與連結
1. 開啟 `index.html`。
2. 依需求修改各區塊內文字，範例如下：
   - Hero 區塊的標題與副標題位於 `<header class="hero">` 中。
   - 商品資訊位於 `<section id="fruits">` 的 `<article class="card">` 裡，可調整名稱、描述與價格。
   - 聯絡資訊位於 `<section id="contact">` 中，可更改電話、Email 與地址。
3. 儲存後重新整理瀏覽器即可看到更新。

### 4.2 新增或移除商品卡片
1. 在 `index.html` 的「熱銷水果」區塊中複製或刪除整段 `<article class="card"> ... </article>`。
2. 若新增卡片，請確保圖片 URL 為公開可用的連結，並調整 `alt` 文字以符合無障礙需求。
3. 若需一次顯示超過四個商品，可持續新增卡片；版型會自動換行。

### 4.3 調整樣式
1. 開啟 `styles.css`。
2. 常見的調整位置：
   - 色彩與背景：`.hero`、`.cta`、`.card` 等選擇器中的 `background`、`color`。
   - 字型大小：`h1`、`h2`、`.card-body p` 等選擇器的 `font-size`。
   - 排版間距：`.section`、`.grid`、`.service-grid` 的 `padding` 與 `gap`。
3. 調整完畢後儲存並重新整理瀏覽器檢視效果。

## 5. 本機預覽
若要在本機測試頁面，可採用以下方法之一：

### 5.1 使用 VS Code Live Server
1. 安裝 VS Code 擴充套件「Live Server」。
2. 開啟專案資料夾，右下角點選「Go Live」。
3. 瀏覽器將自動開啟 http://127.0.0.1:5500/ ，並即時顯示修改結果。

### 5.2 使用 Python HTTP Server
1. 在終端機進入專案資料夾：`cd Dennys`。
2. 執行 `python3 -m http.server 8000`。
3. 開啟瀏覽器並輸入 http://localhost:8000/ 觀察頁面。
4. 按下 `Ctrl + C` 可停止伺服器。

## 6. 部署建議
此專案為純靜態網站，可快速部署至下列平台：
- GitHub Pages
- Netlify
- Vercel

部署流程概述：
1. 將專案推送至 Git 儲存庫。
2. 依據所選平台操作：
   - **GitHub Pages**：在儲存庫設定中啟用 Pages，來源選擇 `main` 分支與根目錄。
   - **Netlify**：登入後選擇「New site from Git」，連結儲存庫並指定建置指令為空、輸出資料夾為根目錄。
   - **Vercel**：導入儲存庫後，保持預設設定即可完成部署。
3. 平台建置完成後，即可取得公開網址分享。

## 7. 常見問題
- **圖片無法顯示**：確認圖片 URL 是否有效或是否支援跨域載入，必要時改用自行上傳的資源。
- **中文亂碼**：確保 HTML `<head>` 中的 `<meta charset="UTF-8">` 未被移除。
- **行動版顯示不佳**：檢查是否修改或刪除 `@media` 響應式設定，必要時調整 breakpoints。

## 8. 版本紀錄
- **v1.0**：建立初版單頁式版面與樣式，撰寫使用手冊。

如需進一步自訂或整合後端服務，建議先規劃 API 或 CMS 架構，再延伸此靜態版面。
