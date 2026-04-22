from models.bibliotecario import Bibliotecario

class BibliotecarioService:
    def __init__(self):
        self.bibliotecarios = []
        self.bibliotecario_logado = None

    def cadastrar_bibliotecario(self, nome, matricula, senha, *_, **__):
        bibliotecario = Bibliotecario(nome, matricula, senha)
        self.bibliotecarios.append(bibliotecario)
        return bibliotecario

    def login(self, matricula, senha):
        for b in self.bibliotecarios:
            if b.matricula == matricula and b.senha == senha:
                self.bibliotecario_logado = b
                return b
        return False
    
    def esta_logado(self):
        return self.bibliotecario_logado is not None

    def esta_loga(self):
        return self.esta_logado()