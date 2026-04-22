class Pessoa:
    def __init__(self, nome: str, matricula: str, senha: str | None = None):
        self.id = None
        self.nome = nome
        self.matricula = matricula
        self.senha = senha
        self.ativo = True