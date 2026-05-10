class SystemLogger:
    """Yazılım hatalarını ve olayları loglar (İskelet)"""
    def log_info(self, message: str):
        print(f"[INFO] {message}")
        
    def log_error(self, message: str):
        print(f"[ERROR] {message}")
