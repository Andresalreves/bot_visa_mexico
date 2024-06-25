from threading import Thread
from bot_playwright import bot

class Bot_visa_dating(Thread):
    def __init__(
            self,
            nombre_usuario,
            password,
            list_consulados,
            list_cas,
            rango
        ):
        super().__init__()

        self.nombre_usuario = nombre_usuario
        self.password = password
        self.result = {}
        self.list_consulados = list_consulados
        self.list_cas = list_cas
        self.rango = rango

    def run(self):
        self.result = bot(
                self.nombre_usuario,
                self.password,
                self.list_consulados,
                self.list_cas,
                self.rango
            )