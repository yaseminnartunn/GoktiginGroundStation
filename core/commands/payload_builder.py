class PayloadBuilder:
    """Rokete gidecek paketleri hazırlar (İskelet)"""
    def build_arm_command(self):
        return b"\xAA\x01\xBB"
        
    def build_parachute_deploy_command(self):
        return b"\xAA\x02\xBB"
