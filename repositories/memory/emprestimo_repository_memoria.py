from repositories.emprestimo_repository import EmprestimoRepository

class EmprestimoRepositoryMemoria(EmprestimoRepository):
    def __init__(self):
        self.emprestimos = []
        self._proximo_id = 1

    def salvar(self, emprestimo):
        if getattr(emprestimo, "id", None) is None:
            emprestimo.id = self._proximo_id
            self._proximo_id += 1
        self.emprestimos.append(emprestimo)
        return emprestimo

    def listar(self):
        return self.emprestimos

    def listar_ativos(self):
        return [e for e in self.emprestimos if e.data_devolucao is None]

    def buscar_por_id(self, emprestimo_id):
        for emprestimo in self.emprestimos:
            if getattr(emprestimo, "id", None) == emprestimo_id:
                return emprestimo
        return None

    def atualizar(self, emprestimo):
        for i, existente in enumerate(self.emprestimos):
            if getattr(existente, "id", None) == getattr(emprestimo, "id", None):
                self.emprestimos[i] = emprestimo
                return emprestimo
        return None

    def remover(self, emprestimo_id):
        emprestimo = self.buscar_por_id(emprestimo_id)
        if emprestimo is None:
            return False
        self.emprestimos.remove(emprestimo)
        return True