class CommandState:
    """Komut durumları (Onay bekliyor, Zaman aşımı) (İskelet)"""
    def __init__(self):
        self.pending_commands = []
        self.executed_commands = []
