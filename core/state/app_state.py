from dataclasses import dataclass

@dataclass
class AppState:
    """MERKEZİ VERİ KAYNAĞI: UI durumu ve sistem bağlantı bilgileri"""
    is_logged_in: bool = False
    active_page: str = "login"
    is_armed: bool = False
    connection_status: str = "DISCONNECTED"
