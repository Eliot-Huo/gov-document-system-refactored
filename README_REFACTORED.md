# 政府公文追蹤系統 - 企業級重構版

## 📋 專案概述

本專案將原本的單體腳本重構為符合企業級標準的模組化架構，遵循 SOLID 原則和關注點分離。

## 🏗️ 架構設計

### 分層架構 (Layered Architecture)

```
┌─────────────────────────────────────┐
│         UI Layer (Presentation)      │  ← Streamlit Pages & Components
├─────────────────────────────────────┤
│      Service Layer (Business Logic)  │  ← DocumentService, TrackingService
├─────────────────────────────────────┤
│   Data Access Layer (Repository)     │  ← Google Sheets, Drive, Vision API
├─────────────────────────────────────┤
│     Models (Domain Objects)          │  ← Document, User
├─────────────────────────────────────┤
│    Config & Utils (Infrastructure)   │  ← Settings, Constants, Exceptions
└─────────────────────────────────────┘
```

## 📁 目錄結構

```
gov-document-system/
│
├── src/
│   ├── __init__.py
│   │
│   ├── config/                    # 設定層
│   │   ├── __init__.py
│   │   ├── constants.py          # 常數定義 (Enum, FieldNames, BusinessRules)
│   │   └── settings.py           # 設定載入 (GoogleSheetsConfig, DriveConfig)
│   │
│   ├── models/                    # 領域模型層
│   │   ├── __init__.py
│   │   ├── document.py           # Document 資料模型
│   │   └── user.py               # User 資料模型
│   │
│   ├── data_access/               # 資料存取層 (Repository Pattern)
│   │   ├── __init__.py
│   │   ├── base.py               # BaseRepository 抽象類別
│   │   ├── google_sheets.py      # DocumentRepository, UserRepository
│   │   ├── google_drive.py       # DriveRepository
│   │   └── google_vision.py      # VisionRepository (OCR)
│   │
│   ├── services/                  # 業務邏輯層 (Service Layer)
│   │   ├── __init__.py
│   │   ├── auth_service.py       # 驗證服務
│   │   ├── document_service.py   # 公文業務邏輯 (流水號生成、對話串)
│   │   ├── ocr_service.py        # OCR 業務邏輯
│   │   ├── tracking_service.py   # 追蹤回覆業務邏輯 (逾期判斷)
│   │   └── ai_service.py         # AI 摘要服務 (Gemini)
│   │
│   ├── ui/                        # UI 呈現層
│   │   ├── __init__.py
│   │   │
│   │   ├── components/            # 可重用 UI 元件
│   │   │   ├── __init__.py
│   │   │   ├── cards.py          # MetricCard, AlertCard
│   │   │   ├── forms.py          # DocumentForm
│   │   │   └── navigation.py     # Sidebar, Header
│   │   │
│   │   ├── pages/                 # 各個頁面
│   │   │   ├── __init__.py
│   │   │   ├── home.py           # 首頁 (儀表板)
│   │   │   ├── add_document.py   # 新增公文
│   │   │   ├── search.py         # 查詢公文
│   │   │   ├── tracking.py       # 追蹤回覆
│   │   │   ├── ocr.py            # OCR 處理
│   │   │   └── admin.py          # 系統管理
│   │   │
│   │   └── styles/
│   │       ├── __init__.py
│   │       └── theme.py          # CSS 樣式主題
│   │
│   └── utils/                     # 工具層
│       ├── __init__.py
│       ├── validators.py         # 資料驗證工具
│       ├── formatters.py         # 格式化工具
│       └── exceptions.py         # 自訂例外類別
│
├── tests/                         # 測試
│   ├── __init__.py
│   ├── test_services/
│   ├── test_data_access/
│   └── test_utils/
│
├── .streamlit/
│   └── secrets.toml.example      # 設定檔範例
│
├── app.py                         # 主程式進入點
├── requirements.txt
├── pytest.ini
└── README.md
```

## 🎯 架構改善重點

### 1. **關注點分離 (Separation of Concerns)**

**Before:**
```python
# 所有邏輯混在一起
def add_document():
    st.text_input(...)        # UI
    doc_id = generate_id()    # Logic
    sheet.append_row(...)     # Data Access
```

**After:**
```python
# UI Layer
class AddDocumentPage:
    def render(self):
        form_data = self._render_form()
        if st.button("新增"):
            self.service.create_document(form_data)

# Service Layer
class DocumentService:
    def create_document(self, data):
        doc = self._build_document(data)
        return self.repository.create(doc)

# Data Access Layer
class DocumentRepository:
    def create(self, document):
        return self._worksheet.append_row(...)
```

### 2. **依賴注入 (Dependency Injection)**

```python
# 透過建構子注入依賴
class DocumentService:
    def __init__(self, repository: DocumentRepository):
        self.repository = repository

# 易於測試 (可注入 Mock)
mock_repo = Mock(DocumentRepository)
service = DocumentService(mock_repo)
```

### 3. **Type Hinting (型別提示)**

```python
def generate_document_id(
    self,
    date: datetime,
    is_reply: bool,
    parent_id: Optional[str] = None
) -> str:
    """產生公文流水號"""
    ...
```

### 4. **常數集中管理**

```python
# Before: Magic Numbers & Hardcoded Strings
if days > 7:
    ...
if col == "ID":
    ...

# After: 使用常數
if days > BusinessRules.TRACKING_THRESHOLD_DAYS:
    ...
if col == FieldNames.ID:
    ...
```

### 5. **領域模型 (Domain Model)**

```python
@dataclass
class Document:
    id: str
    date: datetime
    type: DocumentType
    ...
    
    @classmethod
    def from_sheet_row(cls, row: dict) -> 'Document':
        """封裝轉換邏輯"""
        ...
    
    def is_reply(self) -> bool:
        """封裝業務邏輯"""
        return self.parent_id is not None
```

### 6. **錯誤處理機制**

```python
# Service Layer
def create_document(...):
    if not agency:
        raise ValidationError("機關單位為必填")

# UI Layer
try:
    service.create_document(...)
except ValidationError as e:
    st.error(f"❌ {str(e)}")
except BusinessLogicError as e:
    st.error(f"❌ {str(e)}")
```

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設定 Streamlit Secrets

複製 `.streamlit/secrets.toml.example` 為 `.streamlit/secrets.toml`，並填入您的設定。

### 3. 執行應用程式

```bash
streamlit run app.py
```

## 🧪 測試

```bash
# 執行所有測試
pytest

# 執行特定測試
pytest tests/test_services/test_document_service.py

# 產生覆蓋率報告
pytest --cov=src tests/
```

## 📝 開發指南

### 新增一個頁面

1. 在 `src/ui/pages/` 建立新頁面檔案
2. 繼承基礎 Page 類別
3. 實作 `render()` 方法
4. 在 `app.py` 中註冊路由

```python
# src/ui/pages/my_page.py
class MyPage:
    def __init__(self, repository):
        self.service = MyService(repository)
    
    def render(self):
        st.markdown("## My Page")
        # ... UI 邏輯
```

### 新增一個服務

1. 在 `src/services/` 建立服務檔案
2. 注入所需的 Repository
3. 只包含業務邏輯，不包含 UI 程式碼

```python
# src/services/my_service.py
class MyService:
    def __init__(self, repository: DocumentRepository):
        self.repository = repository
    
    def my_business_logic(self, param: str) -> Result:
        # 純業務邏輯
        ...
```

## 📦 部署

### Streamlit Cloud

1. 將程式碼推送到 GitHub
2. 在 Streamlit Cloud 連結 repository
3. 在 Settings → Secrets 設定環境變數
4. 部署完成！

## 🔧 設定說明

### secrets.toml 範例

```toml
[google_sheets]
sheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID"
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
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
# ... 其他 GCP 憑證

GOOGLE_GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

## 🎓 學習資源

- [SOLID 原則](https://en.wikipedia.org/wiki/SOLID)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Dependency Injection](https://en.wikipedia.org/wiki/Dependency_injection)
- [Domain-Driven Design](https://en.wikipedia.org/wiki/Domain-driven_design)

## 📄 授權

MIT License

## 👥 貢獻者

- 您的名字

## 📞 聯絡方式

如有問題請聯繫...
