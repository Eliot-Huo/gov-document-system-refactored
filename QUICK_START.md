# ⚡ 快速啟動指南 (5 分鐘完成部署)

## 🎯 前置需求

- ✅ GitHub 帳號
- ✅ Google Sheets (已建立公文資料表)
- ✅ GCP Service Account (已設定權限)

---

## 🚀 5 步驟快速部署

### 1️⃣ 上傳到 GitHub (1 分鐘)

```bash
cd gov-document-system-refactored
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2️⃣ 連結 Streamlit Cloud (1 分鐘)

1. 前往 https://share.streamlit.io/
2. 登入並點擊 **New app**
3. 選擇 Repository 和 `app.py`

### 3️⃣ 設定 Secrets (2 分鐘)

在 Streamlit Cloud 的 **Advanced settings** → **Secrets** 貼上:

```toml
[google_sheets]
sheet_url = "YOUR_SHEET_URL"
docs_worksheet = "公文資料"
deleted_worksheet = "刪除紀錄"
users_worksheet = "使用者"

[google_drive]
folder_id = "YOUR_FOLDER_ID"
deleted_folder_id = "YOUR_DELETED_FOLDER_ID"

[gcp_service_account]
type = "service_account"
project_id = "your-project"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "..."
# ... 其他 GCP 憑證欄位
```

### 4️⃣ 部署 (1 分鐘)

點擊 **Deploy!** 按鈕，等待 2-3 分鐘。

### 5️⃣ 測試 (1 分鐘)

1. 前往 App URL
2. 登入測試
3. 查看首頁

**完成! 🎉**

---

## 📝 檢查清單

部署前確認:

- [ ] GitHub Repository 已建立
- [ ] 程式碼已上傳
- [ ] `.gitignore` 包含 `secrets.toml`
- [ ] requirements.txt 存在
- [ ] Google Sheets 已建立並有資料
- [ ] GCP Service Account 有權限
- [ ] 已建立測試使用者

部署後確認:

- [ ] App 可正常開啟
- [ ] 登入功能正常
- [ ] 首頁顯示正確
- [ ] 統計數據正確
- [ ] 側邊欄功能正常

---

## ⚠️ 常見錯誤速查

| 錯誤訊息 | 原因 | 解決方法 |
|---------|------|----------|
| `ModuleNotFoundError` | 缺少套件 | 檢查 requirements.txt |
| `KeyError: 'google_sheets'` | Secrets 格式錯誤 | 檢查 TOML 格式 |
| `DatabaseConnectionError` | API 連線失敗 | 檢查 Service Account 權限 |
| `AuthenticationError` | 找不到使用者 | 檢查使用者工作表 |

---

## 🔗 相關文件

- 📖 [完整部署指南](DEPLOYMENT_GUIDE.md) - 詳細步驟說明
- 🏗️ [架構說明](README_REFACTORED.md) - 系統架構介紹
- 🔄 [遷移指南](MIGRATION_GUIDE.md) - 從舊版遷移
- 📋 [實作總結](IMPLEMENTATION_SUMMARY.md) - 已完成的模組

---

## 🆘 需要幫助?

遇到問題請查看:
1. Streamlit Cloud Logs
2. DEPLOYMENT_GUIDE.md 的「常見問題排除」
3. Streamlit Community Forum

---

**部署後的 URL**: `https://YOUR-APP-NAME.streamlit.app`

開始使用吧! 🚀
