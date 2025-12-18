# 重構對照表 (Migration Guide)

本文件說明原始 `app.py` 中的每個函數/功能對應到新架構的哪個位置。

## 📋 函數遷移對照表

### 設定與初始化

| 舊函數/變數 | 新位置 | 說明 |
|------------|--------|------|
| Hardcoded CSS | `src/ui/styles/theme.py` | 抽離為 Theme 類別 |
| Google Sheets URL | `src/config/settings.py` → `GoogleSheetsConfig` | 從 secrets 載入 |
| Folder ID | `src/config/settings.py` → `GoogleDriveConfig` | 從 secrets 載入 |
| "ID", "Date" 等欄位名 | `src/config/constants.py` → `FieldNames` | 集中管理常數 |
| 7 天門檻 | `src/config/constants.py` → `BusinessRules.TRACKING_THRESHOLD_DAYS` | 業務規則常數 |

### 資料存取 (Google API)

| 舊函數 | 新位置 | 架構層級 |
|--------|--------|----------|
| `connect_to_google_sheets()` | `src/data_access/google_sheets.py` → `DocumentRepository.__init__()` | Data Access Layer |
| `get_all_documents(sheet)` | `src/data_access/google_sheets.py` → `DocumentRepository.get_all()` | Data Access Layer |
| `add_document_to_sheet(sheet, doc_data)` | `src/data_access/google_sheets.py` → `DocumentRepository.create()` | Data Access Layer |
| `soft_delete_document(...)` | `src/data_access/google_sheets.py` → `DocumentRepository.delete()` | Data Access Layer |
| `upload_to_drive(...)` | `src/data_access/google_drive.py` → `DriveRepository.upload_file()` | Data Access Layer |
| `download_from_drive(...)` | `src/data_access/google_drive.py` → `DriveRepository.download_file()` | Data Access Layer |
| `ocr_pdf_from_drive(...)` | `src/data_access/google_vision.py` → `VisionRepository.ocr_pdf()` | Data Access Layer |

### 業務邏輯

| 舊函數 | 新位置 | 架構層級 |
|--------|--------|----------|
| `generate_document_id(...)` | `src/services/document_service.py` → `DocumentService.generate_document_id()` | Service Layer |
| `build_conversation_tree(df)` | `src/services/document_service.py` → `DocumentService.get_conversation_thread()` | Service Layer |
| `filter_recent_documents(df, months)` | `src/services/document_service.py` → `DocumentService.get_recent_documents()` | Service Layer |
| `check_reply_status(...)` | `src/services/tracking_service.py` → `TrackingService.check_reply_status()` | Service Layer |
| `get_pending_replies(df)` | `src/services/tracking_service.py` → `TrackingService.get_pending_replies()` | Service Layer |
| `verify_user(...)` | `src/services/auth_service.py` → `AuthService.verify_user()` | Service Layer |
| `generate_conversation_summary_prompt(...)` | `src/services/ai_service.py` → `AIService._generate_prompt()` | Service Layer |
| `get_ai_summary(...)` | `src/services/ai_service.py` → `AIService.get_summary()` | Service Layer |

### UI 頁面

| 舊函數/Tab | 新位置 | 架構層級 |
|-----------|--------|----------|
| `show_home_page(...)` | `src/ui/pages/home.py` → `HomePage.render()` | UI Layer |
| `show_add_document_page(...)` | `src/ui/pages/add_document.py` → `AddDocumentPage.render()` | UI Layer |
| `show_search_page(...)` | `src/ui/pages/search.py` → `SearchPage.render()` | UI Layer |
| `show_tracking_page(...)` | `src/ui/pages/tracking.py` → `TrackingPage.render()` | UI Layer |
| `show_ocr_page(...)` | `src/ui/pages/ocr.py` → `OCRPage.render()` | UI Layer |
| `show_admin_page(...)` | `src/ui/pages/admin.py` → `AdminPage.render()` | UI Layer |
| `login_page()` | `src/services/auth_service.py` → `AuthService.render_login()` | Service Layer (UI 邏輯) |

### UI 元件

| 舊程式碼 | 新位置 | 說明 |
|---------|--------|------|
| `st.metric(...)` 重複程式碼 | `src/ui/components/cards.py` → `MetricCard` 類別 | 可重用元件 |
| 警示卡片 HTML | `src/ui/components/cards.py` → `AlertCard` 類別 | 可重用元件 |
| 側邊欄導航 | `src/ui/components/navigation.py` → `Sidebar` 類別 | 可重用元件 |
| Header | `src/ui/components/navigation.py` → `Header` 類別 | 可重用元件 |

### 主程式

| 舊程式碼 | 新位置 | 說明 |
|---------|--------|------|
| `main()` 函數 | `app.py` → `main()` | 簡化為路由邏輯 |
| `if __name__ == "__main__"` | `app.py` | 保持不變 |

## 🔄 重構範例

### 範例 1: 產生流水號

#### Before (舊版)
```python
def generate_document_id(docs_sheet, date_str, is_reply, parent_id):
    # 直接存取 Google Sheets
    df = pd.DataFrame(docs_sheet.get_all_records())
    
    # 業務邏輯混在一起
    if is_reply:
        # ...
    else:
        # ...
    
    return doc_id
```

#### After (新版)
```python
# Service Layer - 純業務邏輯
class DocumentService:
    def __init__(self, repository: DocumentRepository):
        self.repository = repository  # 依賴注入
    
    def generate_document_id(
        self,
        date: datetime,
        is_reply: bool,
        parent_id: Optional[str] = None
    ) -> str:
        """產生公文流水號
        
        Args:
            date: 公文日期
            is_reply: 是否為回覆案件
            parent_id: 父公文 ID
            
        Returns:
            公文流水號
            
        Raises:
            ValidationError: 驗證失敗
        """
        # 驗證
        if is_reply and not parent_id:
            raise ValidationError("回覆案件必須提供父公文 ID")
        
        # 透過 Repository 取得資料
        all_docs = self.repository.get_all()
        
        # 業務邏輯
        if is_reply:
            return self._generate_reply_id(all_docs, parent_id)
        else:
            return self._generate_general_id(all_docs, date)
```

### 範例 2: 查詢公文頁面

#### Before (舊版)
```python
def show_search_page(docs_sheet, drive_service, deleted_sheet, deleted_folder_id):
    # UI + 業務邏輯 + 資料存取混在一起
    df = pd.DataFrame(docs_sheet.get_all_records())  # 資料存取
    
    search_keyword = st.text_input("🔍 關鍵字")  # UI
    
    if st.button("🔎 搜尋"):
        # 業務邏輯
        filtered_df = df[df['Subject'].str.contains(search_keyword)]
        
        # UI
        for _, row in filtered_df.iterrows():
            st.markdown(f"**{row['ID']}**")
```

#### After (新版)
```python
# UI Layer - 只負責呈現
class SearchPage:
    def __init__(self, repository: DocumentRepository):
        self.service = DocumentService(repository)
    
    def render(self):
        """渲染查詢頁面"""
        # UI 輸入
        search_keyword = st.text_input("🔍 關鍵字")
        
        if st.button("🔎 搜尋"):
            try:
                # 呼叫 Service 執行業務邏輯
                results = self.service.search_documents(
                    keyword=search_keyword
                )
                
                # UI 呈現
                self._render_results(results)
                
            except ValidationError as e:
                st.error(f"❌ {str(e)}")
    
    def _render_results(self, results: List[Document]):
        """渲染搜尋結果"""
        for doc in results:
            st.markdown(f"**{doc.id}** | {doc.agency}")

# Service Layer - 業務邏輯
class DocumentService:
    def search_documents(
        self,
        keyword: Optional[str] = None,
        **criteria
    ) -> List[Document]:
        """搜尋公文
        
        Args:
            keyword: 關鍵字
            **criteria: 其他搜尋條件
            
        Returns:
            符合條件的公文列表
        """
        # 驗證
        if keyword and len(keyword) < 2:
            raise ValidationError("關鍵字至少需要 2 個字")
        
        # 透過 Repository 查詢
        all_docs = self.repository.get_all()
        
        # 業務邏輯: 篩選
        results = all_docs
        if keyword:
            results = [
                doc for doc in results
                if keyword in doc.subject
            ]
        
        return results
```

### 範例 3: 追蹤回覆邏輯

#### Before (舊版)
```python
def check_reply_status(df, doc_id, doc_type, doc_date):
    # 業務邏輯直接操作 DataFrame
    if doc_type not in ['發文', '函']:
        return {...}
    
    replies = df[df['Parent_ID'] == doc_id]
    days_waiting = (datetime.now() - pd.to_datetime(doc_date)).days
    need_tracking = len(replies) == 0 and days_waiting > 7  # Magic Number
    
    return {...}
```

#### After (新版)
```python
# Service Layer
@dataclass
class TrackingStatus:
    """追蹤狀態 - 使用資料類別"""
    has_reply: bool
    days_waiting: int
    need_tracking: bool
    reply_count: int
    latest_reply_date: Optional[datetime] = None

class TrackingService:
    def check_reply_status(
        self,
        doc_id: str,
        doc_type: DocumentType,
        doc_date: datetime
    ) -> TrackingStatus:
        """檢查公文回覆狀態
        
        Args:
            doc_id: 公文 ID
            doc_type: 公文類型
            doc_date: 公文日期
            
        Returns:
            TrackingStatus 物件
        """
        # 業務邏輯: 只追蹤我方發文
        if doc_type not in [DocumentType.OUTGOING, DocumentType.LETTER]:
            return TrackingStatus(
                has_reply=False,
                days_waiting=0,
                need_tracking=False,
                reply_count=0
            )
        
        # 透過 Repository 查詢回覆
        all_docs = self.repository.get_all()
        replies = [doc for doc in all_docs if doc.parent_id == doc_id]
        
        # 計算等待天數
        days_waiting = (datetime.now() - doc_date).days
        
        # 使用常數判斷是否需要追蹤
        need_tracking = (
            len(replies) == 0 and 
            days_waiting > BusinessRules.TRACKING_THRESHOLD_DAYS
        )
        
        return TrackingStatus(
            has_reply=len(replies) > 0,
            days_waiting=days_waiting,
            need_tracking=need_tracking,
            reply_count=len(replies),
            latest_reply_date=max(r.date for r in replies) if replies else None
        )
```

## 📊 架構優勢對比

| 面向 | 舊架構 | 新架構 |
|------|--------|--------|
| **可測試性** | ❌ 困難 (UI 混在邏輯中) | ✅ 容易 (可單獨測試 Service) |
| **可維護性** | ❌ 低 (2300+ 行單檔) | ✅ 高 (模組化,單一職責) |
| **可擴展性** | ❌ 困難 (耦合度高) | ✅ 容易 (依賴注入,介面抽象) |
| **可讀性** | ❌ 差 (函數過長,邏輯混雜) | ✅ 好 (清晰的層級,型別提示) |
| **錯誤處理** | ❌ 不一致 | ✅ 統一的例外機制 |
| **重用性** | ❌ 低 (程式碼重複) | ✅ 高 (UI 元件可重用) |

## 🎓 學習重點

### 1. 單一職責原則 (Single Responsibility Principle)

每個類別/函數只做一件事:
- `DocumentRepository` 只負責資料存取
- `DocumentService` 只負責業務邏輯
- `SearchPage` 只負責 UI 呈現

### 2. 依賴反轉原則 (Dependency Inversion Principle)

高層模組不依賴低層模組,都依賴抽象:
- `DocumentService` 依賴 `BaseRepository` (抽象)
- 不直接依賴 `GoogleSheetsRepository` (具體實作)

### 3. 開放封閉原則 (Open/Closed Principle)

對擴展開放,對修改封閉:
- 要新增資料來源? 實作 `BaseRepository` 介面即可
- 不需修改 `DocumentService` 的程式碼

## 🚀 遷移檢查清單

- [ ] 複製目錄結構
- [ ] 遷移常數定義到 `constants.py`
- [ ] 建立資料模型 (`Document`, `User`)
- [ ] 實作 Repository 層
- [ ] 實作 Service 層
- [ ] 實作 UI 元件
- [ ] 遷移各個頁面
- [ ] 撰寫單元測試
- [ ] 整合測試
- [ ] 文件更新
- [ ] 部署

## 📞 需要協助?

遇到問題請參考:
1. `README_REFACTORED.md` - 專案說明
2. 程式碼註解 - 每個類別/函數都有完整文件字串
3. 測試檔案 - 看測試了解如何使用
