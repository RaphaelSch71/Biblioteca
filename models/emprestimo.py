from datetime import date
from models.livro import Livro
from models.usuario import Usuario

class Emprestimo:
    def __init__(self, *args, **kwargs):
        self.id = kwargs.get("id")

        if kwargs:
            self.livro = kwargs["livro"]
            self.usuario = kwargs["usuario"]
        elif len(args) == 2:
            self.livro = args[0]
            self.usuario = args[1]
        elif len(args) == 3:
            self.id = args[0]
            self.usuario = args[1]
            self.livro = args[2]
        else:
            raise TypeError("Emprestimo espera (livro, usuario) ou (id, usuario, livro).")

        self.data_emprestimo = date.today()
        self.data_devolucao = None
        self.ativo = True
    
    def realizar(self):
        if self.ativo and self.data_devolucao is None and self.livro.disponivel is False:
            raise Exception("Empréstimo já realizado.")
        self.livro.emprestar()
        if hasattr(self.usuario, "emprestimos"):
            self.usuario.emprestimos.append(self)

    def devolver(self):
        if not self.ativo:
            raise Exception("Empréstimo já foi encerrado.")
        self.livro.devolver()
        self.data_devolucao = date.today()
        self.ativo = False