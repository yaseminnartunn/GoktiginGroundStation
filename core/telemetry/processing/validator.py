class TelemetryValidator:
    """Veri doğruluğunu ve sınırları kontrol eder (İskelet)"""
    def validate(self, data: dict) -> bool:
        # Örnek: İrtifa negatif olamaz
        if data.get("altitude", 0) < -1000:
            return False
        return True
