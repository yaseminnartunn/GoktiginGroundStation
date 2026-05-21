class PayloadBuilder:
    """
    BU DOSYA: Rokete gönderilecek 'emir' paketlerini hazırlar.
    Bilgisayardaki bir butona basıldığında, roketin anlayacağı byte (0-1) dizilerini burası oluşturur.
    """
    
    def build_arm_command(self):
        """Roketi uçuşa hazır hale getirme (ARM) komutu üretir."""
        # \xAA \x01 \xBB gibi ifadeler roketin 'Tamam, uçuşa hazır ol' dediği özel şifrelerdir.
        return b"\xAA\x01\xBB"
        
    def build_parachute_deploy_command(self):
        """Rokete 'Paraşütü Aç' emrini gönderecek paketi üretir."""
        # Roket bu 3 byte'lık veriyi aldığında paraşüt motorunu tetikler.
        return b"\xAA\x02\xBB"

