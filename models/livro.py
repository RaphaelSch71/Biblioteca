class Livro:
    def __init__(self, id, titulo, autor, isbn, ano_publicacao=None):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.isbn = isbn
        self.ano_publicacao = ano_publicacao
        self.disponivel = True

    def emprestar(self):
        if not self.disponivel:
            raise Exception("Livro já está emprestado.")
        self.disponivel = False

    def devolver(self):
        self.disponivel = True

    def __str__(self):
        status = "Disponível" if self.disponivel else "Emprestado"
        ano = f" ({self.ano_publicacao})" if self.ano_publicacao else ""
        return f"{self.titulo}{ano} - {self.autor} | {status}"
