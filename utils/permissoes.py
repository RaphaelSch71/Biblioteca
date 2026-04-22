from enum import Enum

class Permissao(Enum):
    CADASTRAR_LIVRO = "cadastrar_livro"
    REMOVER_LIVRO = "remover_livro"
    REALIZAR_EMPRESTIMO = "realizar_emprestimo"
    DEVOLVER_LIVRO = "devolver_livro"
    LISTAR_LIVROS = "listar_livros"
    GERENCIAR_USUARIOS = "gerenciar_usuarios"
    GERENCIAR_EMPRESTIMOS = "gerenciar_emprestimos"