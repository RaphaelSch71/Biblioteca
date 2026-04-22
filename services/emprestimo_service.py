from models.emprestimo import Emprestimo
from datetime import date


class EmprestimoService:
    def __init__(self, emprestimo_repository=None):
        self.emprestimos = []
        self.emprestimo_repository = emprestimo_repository
        self.proximo_id = 1

    def emprestar_livro(self, usuario, livro):
        if not livro.disponivel:
            raise ValueError("Livro indisponível.")
        
        emprestimo = Emprestimo(self.proximo_id, usuario, livro)
        emprestimo.realizar()
        self.emprestimos.append(emprestimo)
        if self.emprestimo_repository is not None:
            self.emprestimo_repository.salvar(emprestimo)
        self.proximo_id += 1
        return emprestimo

    def devolver_livro(self, id_emprestimo):
        for emp in self.emprestimos:
            if emp.id == id_emprestimo and emp.ativo:
                emp.devolver()
                return emp
        
        raise ValueError("Empréstimo não encontrado ou já encerrado.")