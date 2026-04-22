from models.livro import Livro
from utils.permissoes import Permissao


class Menu:
    def __init__(self, biblioteca_service, usuario_logado, bibliotecario=None):
        self.biblioteca_service = biblioteca_service
        self.usuario_logado = usuario_logado
        self.bibliotecario = bibliotecario or usuario_logado

    def _tem_permissao(self, permissao):
        if self.bibliotecario and hasattr(self.bibliotecario, "tem_permissao"):
            return self.bibliotecario.tem_permissao(permissao)
        if hasattr(self.usuario_logado, "tem_permissao"):
            return self.usuario_logado.tem_permissao(permissao)
        return False

    def _buscar_livro_por_isbn(self, isbn):
        repo = getattr(self.biblioteca_service, "livro_repository", None)
        if repo is not None and hasattr(repo, "buscar_por_isbn"):
            return repo.buscar_por_isbn(isbn)

        for livro in self.biblioteca_service.listar_livros(self.usuario_logado):
            if livro.isbn == isbn:
                return livro
        return None

    def exibir(self):
        while True:
            print("\n=== Biblioteca ===")
            print("1 - Listar livros")

            if self._tem_permissao(Permissao.CADASTRAR_LIVRO):
                print("2 - Cadastrar livro")
            if self._tem_permissao(Permissao.REALIZAR_EMPRESTIMO):
                print("3 - Realizar empréstimo")
            if self._tem_permissao(Permissao.DEVOLVER_LIVRO):
                print("4 - Devolver livro")

            print("0 - Sair")

            opcao = input("Escolha uma opção: ").strip()

            if opcao == "0":
                print("Saindo...")
                break

            if opcao == "1":
                livros = self.biblioteca_service.listar_livros(self.usuario_logado)
                if not livros:
                    print("Nenhum livro cadastrado.")
                else:
                    for livro in livros:
                        print(livro)

            elif opcao == "2" and self._tem_permissao(Permissao.CADASTRAR_LIVRO):
                titulo = input("Título: ").strip()
                autor = input("Autor: ").strip()
                isbn = input("ISBN: ").strip()
                ano = input("Ano de publicação (opcional): ").strip() or None
                if ano is not None:
                    try:
                        ano = int(ano)
                    except ValueError:
                        print("Ano inválido. Usando valor vazio.")
                        ano = None
                livro = Livro(None, titulo, autor, isbn, ano)
                self.biblioteca_service.cadastrar_livro(self.bibliotecario, livro)
                print("Livro cadastrado com sucesso.")

            elif opcao == "3" and self._tem_permissao(Permissao.REALIZAR_EMPRESTIMO):
                isbn = input("ISBN do livro: ").strip()
                matricula = input("Matrícula do usuário: ").strip()
                livro = self._buscar_livro_por_isbn(isbn)
                usuario = None

                repo_usuario = getattr(self.biblioteca_service, "usuario_repository", None)
                if repo_usuario is not None and hasattr(repo_usuario, "buscar_por_matricula"):
                    usuario = repo_usuario.buscar_por_matricula(matricula)

                if livro is None or usuario is None:
                    print("Livro ou usuário não encontrado.")
                else:
                    self.biblioteca_service.realizar_emprestimo(self.bibliotecario, livro, usuario)
                    print("Empréstimo realizado com sucesso.")

            elif opcao == "4" and self._tem_permissao(Permissao.DEVOLVER_LIVRO):
                isbn = input("ISBN do livro emprestado: ").strip()
                livro = self._buscar_livro_por_isbn(isbn)
                if livro is None:
                    print("Livro não encontrado.")
                    continue

                emprestimos = getattr(self.biblioteca_service, "emprestimo_repository", None)
                emprestimo_encontrado = None
                if emprestimos is not None and hasattr(emprestimos, "listar_ativos"):
                    for emprestimo in emprestimos.listar_ativos():
                        if emprestimo.livro.isbn == isbn:
                            emprestimo_encontrado = emprestimo
                            break

                if emprestimo_encontrado is None:
                    print("Empréstimo ativo não encontrado.")
                else:
                    self.biblioteca_service.devolver_livro(self.bibliotecario, emprestimo_encontrado)
                    print("Livro devolvido com sucesso.")

            else:
                print("Opção inválida ou sem permissão.")