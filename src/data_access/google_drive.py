"""Google Drive 資料存取層

此模組實作與 Google Drive 的所有互動邏輯。
"""
from typing import Optional, Dict, Any
from io import BytesIO
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from google.oauth2.service_account import Credentials

from src.config.settings import GoogleDriveConfig
from src.utils.exceptions import DatabaseConnectionError, FileUploadError


class DriveRepository:
    """Google Drive 資料倉儲
    
    負責檔案的上傳、下載、移動等操作。
    """
    
    def __init__(self, config: GoogleDriveConfig, credentials: Dict[str, Any]):
        """初始化
        
        Args:
            config: Google Drive 設定
            credentials: GCP 服務帳號憑證
        """
        self.config = config
        self._service = None
        self._connect(credentials)
    
    def _connect(self, credentials: Dict[str, Any]) -> None:
        """連接到 Google Drive API
        
        Args:
            credentials: GCP 服務帳號憑證
            
        Raises:
            DatabaseConnectionError: 連線失敗
        """
        try:
            creds = Credentials.from_service_account_info(
                credentials,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            
            self._service = build(
                'drive',
                'v3',
                credentials=creds,
                cache_discovery=False
            )
            
        except Exception as e:
            raise DatabaseConnectionError(f"無法連接到 Google Drive: {str(e)}")
    
    def upload_file(
        self,
        file_bytes: bytes,
        filename: str,
        folder_id: Optional[str] = None,
        mime_type: str = 'application/pdf'
    ) -> str:
        """上傳檔案到 Google Drive
        
        Args:
            file_bytes: 檔案內容 (bytes)
            filename: 檔案名稱
            folder_id: 目標資料夾 ID (選填，預設使用設定檔中的 folder_id)
            mime_type: MIME 類型
            
        Returns:
            上傳後的檔案 ID
            
        Raises:
            FileUploadError: 上傳失敗
        """
        try:
            if folder_id is None:
                folder_id = self.config.folder_id
            
            # 準備檔案 metadata
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            # 準備檔案內容
            media = MediaIoBaseUpload(
                BytesIO(file_bytes),
                mimetype=mime_type,
                resumable=True
            )
            
            # 上傳檔案
            file = self._service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id',
                supportsAllDrives=True
            ).execute()
            
            return file.get('id')
            
        except Exception as e:
            raise FileUploadError(f"上傳檔案失敗: {str(e)}")
    
    def download_file(self, file_id: str) -> Optional[bytes]:
        """從 Google Drive 下載檔案
        
        Args:
            file_id: 檔案 ID
            
        Returns:
            檔案內容 (bytes)，如果失敗則回傳 None
        """
        try:
            request = self._service.files().get_media(
                fileId=file_id,
                supportsAllDrives=True
            )
            
            file_stream = BytesIO()
            downloader = MediaIoBaseDownload(file_stream, request)
            
            done = False
            while not done:
                _, done = downloader.next_chunk()
            
            file_stream.seek(0)
            return file_stream.read()
            
        except Exception as e:
            print(f"下載檔案失敗: {str(e)}")
            return None
    
    def move_file(
        self,
        file_id: str,
        target_folder_id: str,
        source_folder_id: Optional[str] = None
    ) -> bool:
        """移動檔案到另一個資料夾
        
        Args:
            file_id: 檔案 ID
            target_folder_id: 目標資料夾 ID
            source_folder_id: 來源資料夾 ID (選填)
            
        Returns:
            True 如果成功
        """
        try:
            # 準備參數
            update_params = {
                'fileId': file_id,
                'addParents': target_folder_id,
                'fields': 'id, parents',
                'supportsAllDrives': True
            }
            
            # 如果指定了來源資料夾，則從中移除
            if source_folder_id:
                update_params['removeParents'] = source_folder_id
            
            # 執行移動
            self._service.files().update(**update_params).execute()
            
            return True
            
        except Exception as e:
            print(f"移動檔案失敗: {str(e)}")
            return False
    
    def delete_file(self, file_id: str) -> bool:
        """刪除檔案
        
        Args:
            file_id: 檔案 ID
            
        Returns:
            True 如果成功
        """
        try:
            self._service.files().delete(
                fileId=file_id,
                supportsAllDrives=True
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"刪除檔案失敗: {str(e)}")
            return False
    
    def get_or_create_subfolder(
        self,
        parent_folder_id: str,
        folder_name: str
    ) -> Optional[str]:
        """取得或建立子資料夾
        
        Args:
            parent_folder_id: 父資料夾 ID
            folder_name: 子資料夾名稱
            
        Returns:
            子資料夾 ID，如果失敗則回傳 None
        """
        try:
            # 先搜尋是否已存在
            query = (
                f"name='{folder_name}' and "
                f"'{parent_folder_id}' in parents and "
                f"mimeType='application/vnd.google-apps.folder' and "
                f"trashed=false"
            )
            
            results = self._service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                # 已存在，回傳 ID
                return files[0]['id']
            
            # 不存在，建立新資料夾
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id]
            }
            
            folder = self._service.files().create(
                body=folder_metadata,
                fields='id',
                supportsAllDrives=True
            ).execute()
            
            return folder.get('id')
            
        except Exception as e:
            print(f"取得或建立資料夾失敗: {str(e)}")
            return None
    
    def get_service(self):
        """取得 Drive Service (用於向下相容)
        
        Returns:
            Google Drive API service
        """
        return self._service
