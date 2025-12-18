# 🚀 Streamlit Cloud 部署指南

## 📋 完整部署步驟

### 步驟 1: 準備 GitHub Repository

#### 1.1 建立新的 GitHub Repository

1. 前往 https://github.com/new
2. 填寫 Repository 資訊:
   - Repository name: `gov-document-system-refactored`
   - Description: `政府公文追蹤系統 - 企業級架構重構版`
   - Visibility: **Private** (建議)
3. 點擊 **Create repository**

#### 1.2 上傳程式碼到 GitHub

```bash
# 在本地專案目錄執行
cd /path/to/gov-document-system-refactored

# 初始化 Git
git init

# 加入所有檔案
git add .

# 提交
git commit -m "Initial commit - 企業級重構版本"

# 連結遠端 Repository
git remote add origin https://github.com/YOUR_USERNAME/gov-document-system-refactored.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

---

### 步驟 2: 設定 Streamlit Secrets

#### 2.1 建立 `.streamlit/secrets.toml.example` (範例檔)

在專案根目錄建立 `.streamlit/secrets.toml.example`:

```toml
# Google Sheets 設定
[google_sheets]
sheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
docs_worksheet = "公文資料"
deleted_worksheet = "刪除紀錄"
users_worksheet = "使用者"

# Google Drive 設定
[google_drive]
folder_id = "YOUR_FOLDER_ID"
deleted_folder_id = "YOUR_DELETED_FOLDER_ID"

# GCP 服務帳號憑證
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"

# Gemini API Key (選填)
GOOGLE_GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

#### 2.2 建立 `.gitignore`

**重要**: 確保 secrets.toml 不會被上傳到 GitHub!

```gitignore
# Streamlit
.streamlit/secrets.toml

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

---

### 步驟 3: 部署到 Streamlit Cloud

#### 3.1 登入 Streamlit Cloud

1. 前往 https://share.streamlit.io/
2. 點擊 **Sign in** 並使用 GitHub 帳號登入
3. 授權 Streamlit 存取您的 GitHub

#### 3.2 建立新的 App

1. 點擊右上角的 **New app**
2. 填寫 App 資訊:
   - **Repository**: 選擇 `YOUR_USERNAME/gov-document-system-refactored`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: 自訂或使用預設
3. 點擊 **Advanced settings**

#### 3.3 設定 Secrets

在 **Secrets** 區域，貼上您的 secrets.toml 內容:

```toml
[google_sheets]
sheet_url = "https://docs.google.com/spreadsheets/d/YOUR_ACTUAL_SHEET_ID/edit"
docs_worksheet = "公文資料"
deleted_worksheet = "刪除紀錄"
users_worksheet = "使用者"

[google_drive]
folder_id = "YOUR_ACTUAL_FOLDER_ID"
deleted_folder_id = "YOUR_ACTUAL_DELETED_FOLDER_ID"

[gcp_service_account]
type = "service_account"
project_id = "your-actual-project-id"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."

GOOGLE_GEMINI_API_KEY = "YOUR_ACTUAL_GEMINI_API_KEY"
```

**注意事項**:
- ⚠️ **不要在 GitHub 上公開這些資訊!**
- ⚠️ 確保 private_key 包含完整的 `-----BEGIN PRIVATE KEY-----` 和 `-----END PRIVATE KEY-----`
- ⚠️ private_key 中的換行使用 `\n` 表示

#### 3.4 部署

1. 點擊 **Deploy!**
2. 等待 2-3 分鐘讓 Streamlit 安裝依賴和啟動 App
3. 部署完成後，您會看到 App 的 URL

---

### 步驟 4: 驗證部署

#### 4.1 檢查 App 狀態

1. 前往您的 App URL
2. 確認看到登入頁面
3. 使用測試帳號登入

#### 4.2 測試功能

測試清單:
- ✅ 登入功能
- ✅ 首頁顯示
- ✅ 統計數據正確
- ✅ 側邊欄導航
- ✅ 登出功能

#### 4.3 檢查 Logs

如果遇到問題:
1. 在 Streamlit Cloud 點擊 **Manage app**
2. 點擊 **Logs** 查看錯誤訊息
3. 點擊 **Resources** 查看資源使用狀況

---

### 步驟 5: 常見問題排除

#### 問題 1: `ModuleNotFoundError`

**原因**: requirements.txt 缺少套件

**解決方法**:
1. 檢查 requirements.txt 是否包含所有套件
2. 在 Streamlit Cloud 點擊 **Reboot app**

#### 問題 2: `KeyError: 'google_sheets'`

**原因**: Secrets 設定不正確

**解決方法**:
1. 前往 **Settings** → **Secrets**
2. 確認格式正確 (使用 TOML 格式)
3. 確認沒有多餘的空白或特殊字元

#### 問題 3: `DatabaseConnectionError`

**原因**: Google Sheets 或 Drive API 連線失敗

**解決方法**:
1. 確認 GCP Service Account 憑證正確
2. 確認 Service Account 有存取權限:
   - Google Sheets: Editor 權限
   - Google Drive: Content Manager 權限
3. 確認 Google Sheets API 和 Drive API 已啟用

#### 問題 4: `AuthenticationError`

**原因**: 找不到使用者或密碼錯誤

**解決方法**:
1. 檢查 Google Sheets 中的「使用者」工作表
2. 確認使用者名稱和密碼正確
3. 確認欄位名稱為: `Username`, `Password`, `Display_Name`, `Role`

---

### 步驟 6: 更新部署

當您需要更新程式碼時:

```bash
# 修改程式碼後
git add .
git commit -m "更新說明"
git push

# Streamlit Cloud 會自動偵測並重新部署
```

---

## 🔒 安全性建議

### 1. 不要公開 Secrets
- ✅ 使用 `.gitignore` 排除 secrets.toml
- ✅ 只在 Streamlit Cloud 設定 Secrets
- ❌ 不要在程式碼中硬編碼機密資訊

### 2. 限制 Service Account 權限
- ✅ 只給予必要的權限
- ✅ 定期檢查權限設定
- ✅ 使用專用的 Service Account

### 3. 定期更新
- ✅ 定期更新 Python 套件
- ✅ 關注安全性公告
- ✅ 定期變更密碼

---

## 📊 效能優化

### 1. Cache 設定

程式碼中已使用 `@st.cache_data`:
```python
@st.cache_data(ttl=3600)
def get_all_documents():
    ...
```

### 2. 連線池

Repository 使用連線池管理:
```python
class GoogleSheetsConnection:
    def __init__(self):
        self._client = None  # 重用連線
```

### 3. 分頁載入

對大量資料使用分頁:
```python
recent_docs = all_docs[:10]  # 只顯示前 10 筆
```

---

## 📞 技術支援

### 遇到問題?

1. **查看 Logs**
   - Streamlit Cloud → Manage app → Logs

2. **檢查文件**
   - README_REFACTORED.md
   - MIGRATION_GUIDE.md
   - IMPLEMENTATION_SUMMARY.md

3. **常見錯誤**
   - [Streamlit Community Forum](https://discuss.streamlit.io/)
   - [Streamlit Docs](https://docs.streamlit.io/)

---

## 🎉 部署完成!

恭喜您成功部署企業級架構的政府公文追蹤系統!

**接下來可以做什麼?**

1. ✅ 完成其他頁面 (新增、查詢、追蹤、OCR、管理)
2. ✅ 加入單元測試
3. ✅ 優化效能
4. ✅ 增加新功能

---

**部署成功後的 URL 範例**:
`https://YOUR-APP-NAME.streamlit.app`

**分享給使用者:**
只需分享 URL，使用者就能直接使用! 🚀
