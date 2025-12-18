"""設定檔載入模組

此模組負責從 Streamlit Secrets 載入所有設定，
並提供型別安全的設定物件。
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
import streamlit as st


@dataclass
class GoogleSheetsConfig:
    """Google Sheets 設定"""
    sheet_url: str
    docs_worksheet: str
    deleted_worksheet: str
    users_worksheet: str


@dataclass
class GoogleDriveConfig:
    """Google Drive 設定"""
    folder_id: str
    deleted_folder_id: str


@dataclass
class APIConfig:
    """API 設定"""
    gemini_api_key: Optional[str] = None


@dataclass
class GCPCredentials:
    """GCP 服務帳號憑證"""
    credentials_dict: Dict[str, Any]


class Settings:
    """應用程式設定管理器"""
    
    @staticmethod
    def load_google_sheets_config() -> GoogleSheetsConfig:
        """載入 Google Sheets 設定
        
        Returns:
            GoogleSheetsConfig 物件
            
        Raises:
            KeyError: 當必要的設定遺失時
        """
        return GoogleSheetsConfig(
            sheet_url=st.secrets["google_sheets"]["sheet_url"],
            docs_worksheet=st.secrets["google_sheets"]["docs_worksheet"],
            deleted_worksheet=st.secrets["google_sheets"]["deleted_worksheet"],
            users_worksheet=st.secrets["google_sheets"]["users_worksheet"]
        )
    
    @staticmethod
    def load_google_drive_config() -> GoogleDriveConfig:
        """載入 Google Drive 設定
        
        Returns:
            GoogleDriveConfig 物件
            
        Raises:
            KeyError: 當必要的設定遺失時
        """
        return GoogleDriveConfig(
            folder_id=st.secrets["google_drive"]["folder_id"],
            deleted_folder_id=st.secrets["google_drive"]["deleted_folder_id"]
        )
    
    @staticmethod
    def load_api_config() -> APIConfig:
        """載入 API 設定
        
        Returns:
            APIConfig 物件
        """
        return APIConfig(
            gemini_api_key=st.secrets.get("GOOGLE_GEMINI_API_KEY")
        )
    
    @staticmethod
    def load_gcp_credentials() -> GCPCredentials:
        """載入 GCP 服務帳號憑證
        
        Returns:
            GCPCredentials 物件
            
        Raises:
            KeyError: 當必要的設定遺失時
        """
        return GCPCredentials(
            credentials_dict=dict(st.secrets["gcp_service_account"])
        )
