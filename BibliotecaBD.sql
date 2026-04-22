-- Biblioteca - SQL Server 2022
-- Execute este script no SQL Server Management Studio 22.

USE master;
GO

IF DB_ID(N'BibliotecaBD') IS NULL
BEGIN
    CREATE DATABASE BibliotecaBD;
END
GO

USE BibliotecaBD;
GO

IF OBJECT_ID(N'dbo.Usuarios', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Usuarios
    (
        Id INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_Usuarios PRIMARY KEY,
        Nome NVARCHAR(120) NOT NULL,
        Matricula NVARCHAR(20) NOT NULL,
        Senha NVARCHAR(255) NOT NULL,
        Tipo NVARCHAR(20) NOT NULL CONSTRAINT DF_Usuarios_Tipo DEFAULT (N'usuario'),
        Ativo BIT NOT NULL CONSTRAINT DF_Usuarios_Ativo DEFAULT (1),
        DataCadastro DATETIME2(0) NOT NULL CONSTRAINT DF_Usuarios_DataCadastro DEFAULT (SYSDATETIME()),
        CONSTRAINT UQ_Usuarios_Matricula UNIQUE (Matricula),
        CONSTRAINT CK_Usuarios_Tipo CHECK (Tipo IN (N'usuario', N'bibliotecario'))
    );
END
GO

IF OBJECT_ID(N'dbo.Livros', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Livros
    (
        Id INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_Livros PRIMARY KEY,
        Titulo NVARCHAR(200) NOT NULL,
        Autor NVARCHAR(150) NOT NULL,
        ISBN NVARCHAR(20) NOT NULL,
        AnoPublicacao INT NULL,
        Disponivel BIT NOT NULL CONSTRAINT DF_Livros_Disponivel DEFAULT (1),
        DataCadastro DATETIME2(0) NOT NULL CONSTRAINT DF_Livros_DataCadastro DEFAULT (SYSDATETIME()),
        CONSTRAINT UQ_Livros_ISBN UNIQUE (ISBN),
        CONSTRAINT CK_Livros_AnoPublicacao CHECK (AnoPublicacao IS NULL OR (AnoPublicacao >= 1000 AND AnoPublicacao <= YEAR(GETDATE()) + 1))
    );
END
GO

IF OBJECT_ID(N'dbo.Emprestimos', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Emprestimos
    (
        Id INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_Emprestimos PRIMARY KEY,
        LivroId INT NOT NULL,
        UsuarioId INT NOT NULL,
        DataEmprestimo DATE NOT NULL CONSTRAINT DF_Emprestimos_DataEmprestimo DEFAULT (CAST(GETDATE() AS DATE)),
        DataDevolucao DATE NULL,
        Ativo BIT NOT NULL CONSTRAINT DF_Emprestimos_Ativo DEFAULT (1),
        CONSTRAINT FK_Emprestimos_Livros FOREIGN KEY (LivroId) REFERENCES dbo.Livros (Id),
        CONSTRAINT FK_Emprestimos_Usuarios FOREIGN KEY (UsuarioId) REFERENCES dbo.Usuarios (Id),
        CONSTRAINT CK_Emprestimos_Datas CHECK (DataDevolucao IS NULL OR DataDevolucao >= DataEmprestimo)
    );
END
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_Emprestimos_Ativo'
      AND object_id = OBJECT_ID(N'dbo.Emprestimos')
)
BEGIN
    CREATE INDEX IX_Emprestimos_Ativo
        ON dbo.Emprestimos (Ativo, LivroId, UsuarioId);
END
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_Emprestimos_Livro_Ativo'
      AND object_id = OBJECT_ID(N'dbo.Emprestimos')
)
BEGIN
    CREATE UNIQUE INDEX IX_Emprestimos_Livro_Ativo
        ON dbo.Emprestimos (LivroId)
        WHERE Ativo = 1;
END
GO

IF OBJECT_ID(N'dbo.LogEventos', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.LogEventos
    (
        Id INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_LogEventos PRIMARY KEY,
        Entidade NVARCHAR(50) NOT NULL,
        EntidadeId INT NULL,
        Acao NVARCHAR(30) NOT NULL,
        Detalhes NVARCHAR(4000) NULL,
        DataEvento DATETIME2(0) NOT NULL CONSTRAINT DF_LogEventos_DataEvento DEFAULT (SYSDATETIME())
    );
END
GO

CREATE OR ALTER VIEW dbo.vw_EmprestimosAtivos
AS
SELECT
    e.Id,
    e.LivroId,
    l.Titulo,
    l.ISBN,
    e.UsuarioId,
    u.Nome AS NomeUsuario,
    u.Matricula,
    e.DataEmprestimo
FROM dbo.Emprestimos e
INNER JOIN dbo.Livros l ON l.Id = e.LivroId
INNER JOIN dbo.Usuarios u ON u.Id = e.UsuarioId
WHERE e.Ativo = 1;
GO

CREATE OR ALTER PROCEDURE dbo.usp_CadastrarUsuario
    @Nome NVARCHAR(120),
    @Matricula NVARCHAR(20),
    @Senha NVARCHAR(255),
    @Tipo NVARCHAR(20) = N'usuario'
AS
BEGIN
    SET NOCOUNT ON;

    IF @Tipo NOT IN (N'usuario', N'bibliotecario')
        THROW 50010, 'Tipo de usuário inválido.', 1;

    IF EXISTS (SELECT 1 FROM dbo.Usuarios WHERE Matricula = @Matricula)
        THROW 50011, 'Matrícula já cadastrada.', 1;

    INSERT INTO dbo.Usuarios (Nome, Matricula, Senha, Tipo)
    VALUES (@Nome, @Matricula, @Senha, @Tipo);

    SELECT CAST(SCOPE_IDENTITY() AS INT) AS UsuarioId;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_CadastrarLivro
    @Titulo NVARCHAR(200),
    @Autor NVARCHAR(150),
    @ISBN NVARCHAR(20),
    @AnoPublicacao INT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (SELECT 1 FROM dbo.Livros WHERE ISBN = @ISBN)
        THROW 50020, 'ISBN já cadastrado.', 1;

    INSERT INTO dbo.Livros (Titulo, Autor, ISBN, AnoPublicacao, Disponivel)
    VALUES (@Titulo, @Autor, @ISBN, @AnoPublicacao, 1);

    SELECT CAST(SCOPE_IDENTITY() AS INT) AS LivroId;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_RealizarEmprestimo
    @LivroId INT,
    @UsuarioId INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRAN;

    IF NOT EXISTS (SELECT 1 FROM dbo.Usuarios WHERE Id = @UsuarioId AND Ativo = 1)
        THROW 50030, 'Usuário não encontrado ou inativo.', 1;

    IF NOT EXISTS (SELECT 1 FROM dbo.Livros WHERE Id = @LivroId)
        THROW 50031, 'Livro não encontrado.', 1;

    IF EXISTS (SELECT 1 FROM dbo.Emprestimos WHERE LivroId = @LivroId AND Ativo = 1)
        THROW 50032, 'Livro já possui empréstimo ativo.', 1;

    INSERT INTO dbo.Emprestimos (LivroId, UsuarioId, DataEmprestimo, DataDevolucao, Ativo)
    VALUES (@LivroId, @UsuarioId, CAST(GETDATE() AS DATE), NULL, 1);

    UPDATE dbo.Livros
       SET Disponivel = 0
     WHERE Id = @LivroId;

    COMMIT TRAN;

    SELECT CAST(SCOPE_IDENTITY() AS INT) AS EmprestimoId;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_DevolverLivro
    @EmprestimoId INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @LivroId INT;

    SELECT @LivroId = LivroId
    FROM dbo.Emprestimos
    WHERE Id = @EmprestimoId
      AND Ativo = 1;

    IF @LivroId IS NULL
        THROW 50040, 'Empréstimo não encontrado ou já encerrado.', 1;

    BEGIN TRAN;

    UPDATE dbo.Emprestimos
       SET Ativo = 0,
           DataDevolucao = CAST(GETDATE() AS DATE)
     WHERE Id = @EmprestimoId;

    UPDATE dbo.Livros
       SET Disponivel = CASE
                           WHEN EXISTS (SELECT 1 FROM dbo.Emprestimos WHERE LivroId = @LivroId AND Ativo = 1)
                                THEN 0
                           ELSE 1
                        END
     WHERE Id = @LivroId;

    COMMIT TRAN;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_ListarLivros
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        Id,
        Titulo,
        Autor,
        ISBN,
        AnoPublicacao,
        Disponivel,
        DataCadastro
    FROM dbo.Livros
    ORDER BY Titulo;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_ListarUsuarios
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        Id,
        Nome,
        Matricula,
        Tipo,
        Ativo,
        DataCadastro
    FROM dbo.Usuarios
    ORDER BY Nome;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_ObterUsuarioPorId
    @Id INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        Id,
        Nome,
        Matricula,
        Tipo,
        Ativo,
        DataCadastro
    FROM dbo.Usuarios
    WHERE Id = @Id;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_ObterUsuarioPorMatricula
    @Matricula NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        Id,
        Nome,
        Matricula,
        Senha,
        Tipo,
        Ativo,
        DataCadastro
    FROM dbo.Usuarios
    WHERE Matricula = @Matricula;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_AtualizarUsuario
    @Id INT,
    @Nome NVARCHAR(120),
    @Matricula NVARCHAR(20),
    @Senha NVARCHAR(255),
    @Tipo NVARCHAR(20),
    @Ativo BIT
AS
BEGIN
    SET NOCOUNT ON;

    IF @Tipo NOT IN (N'usuario', N'bibliotecario')
        THROW 50110, 'Tipo de usuário inválido.', 1;

    IF EXISTS (SELECT 1 FROM dbo.Usuarios WHERE Matricula = @Matricula AND Id <> @Id)
        THROW 50111, 'Matrícula já cadastrada para outro usuário.', 1;

    IF @Ativo = 0 AND EXISTS (SELECT 1 FROM dbo.Emprestimos WHERE UsuarioId = @Id AND Ativo = 1)
        THROW 50112, 'Não é possível inativar usuário com empréstimo ativo.', 1;

    UPDATE dbo.Usuarios
       SET Nome = @Nome,
           Matricula = @Matricula,
           Senha = @Senha,
           Tipo = @Tipo,
           Ativo = @Ativo
     WHERE Id = @Id;

    IF @@ROWCOUNT = 0
        THROW 50113, 'Usuário não encontrado.', 1;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_RemoverUsuario
    @Id INT
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (SELECT 1 FROM dbo.Emprestimos WHERE UsuarioId = @Id AND Ativo = 1)
        THROW 50120, 'Não é possível remover usuário com empréstimo ativo.', 1;

    DELETE FROM dbo.Usuarios
    WHERE Id = @Id;

    IF @@ROWCOUNT = 0
        THROW 50121, 'Usuário não encontrado.', 1;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_ObterLivroPorId
    @Id INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        Id,
        Titulo,
        Autor,
        ISBN,
        AnoPublicacao,
        Disponivel,
        DataCadastro
    FROM dbo.Livros
    WHERE Id = @Id;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_ObterLivroPorISBN
    @ISBN NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        Id,
        Titulo,
        Autor,
        ISBN,
        AnoPublicacao,
        Disponivel,
        DataCadastro
    FROM dbo.Livros
    WHERE ISBN = @ISBN;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_AtualizarLivro
    @Id INT,
    @Titulo NVARCHAR(200),
    @Autor NVARCHAR(150),
    @ISBN NVARCHAR(20),
    @AnoPublicacao INT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (SELECT 1 FROM dbo.Livros WHERE ISBN = @ISBN AND Id <> @Id)
        THROW 50210, 'ISBN já cadastrado para outro livro.', 1;

    UPDATE dbo.Livros
       SET Titulo = @Titulo,
           Autor = @Autor,
           ISBN = @ISBN,
           AnoPublicacao = @AnoPublicacao
     WHERE Id = @Id;

    IF @@ROWCOUNT = 0
        THROW 50211, 'Livro não encontrado.', 1;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_RemoverLivro
    @Id INT
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (SELECT 1 FROM dbo.Emprestimos WHERE LivroId = @Id AND Ativo = 1)
        THROW 50220, 'Não é possível remover livro com empréstimo ativo.', 1;

    IF EXISTS (SELECT 1 FROM dbo.Emprestimos WHERE LivroId = @Id)
        THROW 50221, 'Não é possível remover livro com histórico de empréstimos.', 1;

    DELETE FROM dbo.Livros
    WHERE Id = @Id;

    IF @@ROWCOUNT = 0
        THROW 50222, 'Livro não encontrado.', 1;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_ListarEmprestimos
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        e.Id,
        e.LivroId,
        l.Titulo,
        l.ISBN,
        e.UsuarioId,
        u.Nome AS NomeUsuario,
        u.Matricula,
        e.DataEmprestimo,
        e.DataDevolucao,
        e.Ativo
    FROM dbo.Emprestimos e
    INNER JOIN dbo.Livros l ON l.Id = e.LivroId
    INNER JOIN dbo.Usuarios u ON u.Id = e.UsuarioId
    ORDER BY e.Id DESC;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_ObterEmprestimoPorId
    @Id INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        e.Id,
        e.LivroId,
        l.Titulo,
        l.ISBN,
        e.UsuarioId,
        u.Nome AS NomeUsuario,
        u.Matricula,
        e.DataEmprestimo,
        e.DataDevolucao,
        e.Ativo
    FROM dbo.Emprestimos e
    INNER JOIN dbo.Livros l ON l.Id = e.LivroId
    INNER JOIN dbo.Usuarios u ON u.Id = e.UsuarioId
    WHERE e.Id = @Id;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_AtualizarEmprestimo
    @Id INT,
    @DataEmprestimo DATE,
    @DataDevolucao DATE = NULL,
    @Ativo BIT
AS
BEGIN
    SET NOCOUNT ON;

    IF @DataDevolucao IS NOT NULL AND @DataDevolucao < @DataEmprestimo
        THROW 50310, 'Data de devolução não pode ser menor que a data de empréstimo.', 1;

    IF @Ativo = 1 AND @DataDevolucao IS NOT NULL
        THROW 50311, 'Empréstimo ativo não pode ter data de devolução preenchida.', 1;

    IF @Ativo = 0 AND @DataDevolucao IS NULL
        SET @DataDevolucao = CAST(GETDATE() AS DATE);

    UPDATE dbo.Emprestimos
       SET DataEmprestimo = @DataEmprestimo,
           DataDevolucao = @DataDevolucao,
           Ativo = @Ativo
     WHERE Id = @Id;

    IF @@ROWCOUNT = 0
        THROW 50312, 'Empréstimo não encontrado.', 1;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_RemoverEmprestimo
    @Id INT
AS
BEGIN
    SET NOCOUNT ON;

    DELETE FROM dbo.Emprestimos
    WHERE Id = @Id;

    IF @@ROWCOUNT = 0
        THROW 50320, 'Empréstimo não encontrado.', 1;
END
GO

CREATE OR ALTER TRIGGER dbo.trg_Emprestimos_SincronizaDisponibilidade
ON dbo.Emprestimos
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    ;WITH LivrosAfetados AS
    (
        SELECT LivroId FROM inserted
        UNION
        SELECT LivroId FROM deleted
    )
    UPDATE l
       SET Disponivel = CASE
                           WHEN EXISTS (SELECT 1 FROM dbo.Emprestimos e WHERE e.LivroId = l.Id AND e.Ativo = 1)
                                THEN 0
                           ELSE 1
                        END
    FROM dbo.Livros l
    INNER JOIN LivrosAfetados a ON a.LivroId = l.Id;
END
GO

CREATE OR ALTER TRIGGER dbo.trg_Emprestimos_Log
ON dbo.Emprestimos
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO dbo.LogEventos (Entidade, EntidadeId, Acao, Detalhes)
    SELECT
        N'Emprestimos',
        i.Id,
        CASE
            WHEN d.Id IS NULL THEN N'INSERT'
            ELSE N'UPDATE'
        END,
        CASE
            WHEN d.Id IS NULL THEN CONCAT(N'LivroId=', i.LivroId, N'; UsuarioId=', i.UsuarioId, N'; Ativo=', i.Ativo)
            ELSE CONCAT(N'LivroId=', i.LivroId, N'; UsuarioId=', i.UsuarioId, N'; Ativo=', i.Ativo, N'; DataDevolucao=', COALESCE(CONVERT(NVARCHAR(30), i.DataDevolucao, 23), N'NULL'))
        END
    FROM inserted i
    LEFT JOIN deleted d ON d.Id = i.Id;
END
GO

CREATE OR ALTER TRIGGER dbo.trg_Usuarios_Log
ON dbo.Usuarios
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO dbo.LogEventos (Entidade, EntidadeId, Acao, Detalhes)
    SELECT
        N'Usuarios',
        COALESCE(i.Id, d.Id),
        CASE
            WHEN i.Id IS NOT NULL AND d.Id IS NULL THEN N'INSERT'
            WHEN i.Id IS NOT NULL AND d.Id IS NOT NULL THEN N'UPDATE'
            WHEN i.Id IS NULL AND d.Id IS NOT NULL THEN N'DELETE'
        END,
        CONCAT(
            N'Nome=', COALESCE(i.Nome, d.Nome),
            N'; Matricula=', COALESCE(i.Matricula, d.Matricula),
            N'; Tipo=', COALESCE(i.Tipo, d.Tipo),
            N'; Ativo=', COALESCE(CONVERT(NVARCHAR(10), i.Ativo), CONVERT(NVARCHAR(10), d.Ativo))
        )
    FROM inserted i
    FULL OUTER JOIN deleted d ON d.Id = i.Id;
END
GO

CREATE OR ALTER TRIGGER dbo.trg_Livros_Log
ON dbo.Livros
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO dbo.LogEventos (Entidade, EntidadeId, Acao, Detalhes)
    SELECT
        N'Livros',
        COALESCE(i.Id, d.Id),
        CASE
            WHEN i.Id IS NOT NULL AND d.Id IS NULL THEN N'INSERT'
            WHEN i.Id IS NOT NULL AND d.Id IS NOT NULL THEN N'UPDATE'
            WHEN i.Id IS NULL AND d.Id IS NOT NULL THEN N'DELETE'
        END,
        CONCAT(
            N'Titulo=', COALESCE(i.Titulo, d.Titulo),
            N'; ISBN=', COALESCE(i.ISBN, d.ISBN),
            N'; Disponivel=', COALESCE(CONVERT(NVARCHAR(10), i.Disponivel), CONVERT(NVARCHAR(10), d.Disponivel))
        )
    FROM inserted i
    FULL OUTER JOIN deleted d ON d.Id = i.Id;
END
GO

IF OBJECT_ID('dbo.PedidosEmprestimo', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.PedidosEmprestimo (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        UsuarioId INT NOT NULL,
        LivroId INT NOT NULL,
        Status NVARCHAR(20) NOT NULL CONSTRAINT DF_PedidosEmprestimo_Status DEFAULT(N'PENDENTE'),
        DataPedido DATETIME2(0) NOT NULL CONSTRAINT DF_PedidosEmprestimo_DataPedido DEFAULT(SYSDATETIME()),
        DataAtendimento DATETIME2(0) NULL,
        DataPrevistaDevolucao DATE NULL,
        BibliotecarioId INT NULL,
        EmprestimoId INT NULL,
        CONSTRAINT CK_PedidosEmprestimo_Status CHECK (Status IN (N'PENDENTE', N'ACEITO', N'RECUSADO', N'CANCELADO')),
        CONSTRAINT FK_PedidosEmprestimo_Usuario FOREIGN KEY (UsuarioId) REFERENCES dbo.Usuarios(Id),
        CONSTRAINT FK_PedidosEmprestimo_Livro FOREIGN KEY (LivroId) REFERENCES dbo.Livros(Id),
        CONSTRAINT FK_PedidosEmprestimo_Bibliotecario FOREIGN KEY (BibliotecarioId) REFERENCES dbo.Usuarios(Id),
        CONSTRAINT FK_PedidosEmprestimo_Emprestimo FOREIGN KEY (EmprestimoId) REFERENCES dbo.Emprestimos(Id)
    );

    CREATE INDEX IX_PedidosEmprestimo_Status ON dbo.PedidosEmprestimo(Status, DataPedido DESC);
    CREATE INDEX IX_PedidosEmprestimo_Usuario ON dbo.PedidosEmprestimo(UsuarioId, DataPedido DESC);
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_SolicitarPedidoEmprestimo
    @UsuarioId INT,
    @LivroId INT
AS
BEGIN
    SET NOCOUNT ON;

    IF NOT EXISTS (SELECT 1 FROM dbo.Usuarios WHERE Id = @UsuarioId AND Ativo = 1)
        THROW 51001, 'Usuário solicitante inválido.', 1;

    IF NOT EXISTS (SELECT 1 FROM dbo.Livros WHERE Id = @LivroId)
        THROW 51002, 'Livro não encontrado.', 1;

    IF EXISTS (SELECT 1 FROM dbo.Emprestimos WHERE LivroId = @LivroId AND Ativo = 1)
        THROW 51003, 'Livro indisponível para novo pedido.', 1;

    IF EXISTS (
        SELECT 1
        FROM dbo.PedidosEmprestimo
        WHERE UsuarioId = @UsuarioId
          AND LivroId = @LivroId
          AND Status = N'PENDENTE'
    )
        THROW 51004, 'Já existe pedido pendente para este livro.', 1;

    INSERT INTO dbo.PedidosEmprestimo (UsuarioId, LivroId)
    VALUES (@UsuarioId, @LivroId);

    SELECT CAST(SCOPE_IDENTITY() AS INT) AS PedidoId;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_ListarPedidosEmprestimoPendentes
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        p.Id,
        u.Id AS UsuarioId,
        u.Nome AS UsuarioNome,
        u.Matricula AS UsuarioMatricula,
        l.Id AS LivroId,
        l.Titulo AS LivroTitulo,
        l.ISBN AS LivroISBN,
        p.Status,
        p.DataPedido
    FROM dbo.PedidosEmprestimo p
    INNER JOIN dbo.Usuarios u ON u.Id = p.UsuarioId
    INNER JOIN dbo.Livros l ON l.Id = p.LivroId
    WHERE p.Status = N'PENDENTE'
    ORDER BY p.DataPedido ASC;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_ListarPedidosEmprestimoPorUsuario
    @UsuarioId INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        p.Id,
        l.Id AS LivroId,
        l.Titulo AS LivroTitulo,
        l.ISBN AS LivroISBN,
        p.Status,
        p.DataPedido,
        p.DataPrevistaDevolucao,
        b.Nome AS BibliotecarioNome,
        b.Matricula AS BibliotecarioMatricula,
        p.EmprestimoId
    FROM dbo.PedidosEmprestimo p
    INNER JOIN dbo.Livros l ON l.Id = p.LivroId
    LEFT JOIN dbo.Usuarios b ON b.Id = p.BibliotecarioId
    WHERE p.UsuarioId = @UsuarioId
    ORDER BY p.DataPedido DESC;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_AceitarPedidoEmprestimo
    @PedidoId INT,
    @BibliotecarioId INT,
    @DataPrevistaDevolucao DATE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @LivroId INT;
    DECLARE @UsuarioId INT;
    DECLARE @EmprestimoId INT;

    BEGIN TRAN;

    SELECT
        @LivroId = p.LivroId,
        @UsuarioId = p.UsuarioId
    FROM dbo.PedidosEmprestimo p WITH (UPDLOCK, HOLDLOCK)
    WHERE p.Id = @PedidoId
      AND p.Status = N'PENDENTE';

    IF @LivroId IS NULL
    BEGIN
        ROLLBACK TRAN;
        THROW 51005, 'Pedido não encontrado ou já processado.', 1;
    END

    IF EXISTS (SELECT 1 FROM dbo.Emprestimos WHERE LivroId = @LivroId AND Ativo = 1)
    BEGIN
        ROLLBACK TRAN;
        THROW 51006, 'Livro já está emprestado.', 1;
    END

    INSERT INTO dbo.Emprestimos (LivroId, UsuarioId, DataEmprestimo, DataDevolucao, Ativo)
    VALUES (@LivroId, @UsuarioId, CAST(GETDATE() AS DATE), NULL, 1);

    SET @EmprestimoId = CAST(SCOPE_IDENTITY() AS INT);

    UPDATE dbo.PedidosEmprestimo
       SET Status = N'ACEITO',
           DataAtendimento = SYSDATETIME(),
           DataPrevistaDevolucao = @DataPrevistaDevolucao,
           BibliotecarioId = @BibliotecarioId,
           EmprestimoId = @EmprestimoId
     WHERE Id = @PedidoId;

    COMMIT TRAN;

    SELECT @EmprestimoId AS EmprestimoId;
END
GO

PRINT 'Banco BibliotecaBD criado/verificado com sucesso (tabelas, view, procedures e triggers).';
GO

-- ==============================
SELECT * FROM dbo.Emprestimos
SELECT * FROM dbo.Livros
SELECT * FROM dbo.Usuarios
GO
-- ==============================

-- ==============================
-- EXEMPLOS DE REQUESTS (SSMS)
-- ==============================
-- EXEC dbo.usp_CadastrarUsuario @Nome = N'Ana', @Matricula = N'U100', @Senha = N'123', @Tipo = N'usuario';
-- EXEC dbo.usp_CadastrarLivro @Titulo = N'Domain-Driven Design', @Autor = N'Eric Evans', @ISBN = N'9780321125217', @AnoPublicacao = 2003;
-- EXEC dbo.usp_RealizarEmprestimo @LivroId = 1, @UsuarioId = 1;
-- EXEC dbo.usp_DevolverLivro @EmprestimoId = 1;
-- EXEC dbo.usp_ListarLivros;
-- EXEC dbo.usp_ListarUsuarios;
-- EXEC dbo.usp_ListarEmprestimos;
-- EXEC dbo.usp_ObterUsuarioPorId @Id = 1;
-- EXEC dbo.usp_ObterUsuarioPorMatricula @Matricula = N'U100';
-- EXEC dbo.usp_ObterLivroPorId @Id = 1;
-- EXEC dbo.usp_ObterLivroPorISBN @ISBN = N'9780321125217';
-- EXEC dbo.usp_ObterEmprestimoPorId @Id = 1;
-- EXEC dbo.usp_AtualizarUsuario @Id = 1, @Nome = N'Ana Silva', @Matricula = N'U100', @Senha = N'123', @Tipo = N'usuario', @Ativo = 1;
-- EXEC dbo.usp_AtualizarLivro @Id = 1, @Titulo = N'DDD', @Autor = N'Eric Evans', @ISBN = N'9780321125217', @AnoPublicacao = 2003;
-- EXEC dbo.usp_AtualizarEmprestimo @Id = 1, @DataEmprestimo = '2026-04-09', @DataDevolucao = NULL, @Ativo = 1;
-- EXEC dbo.usp_RemoverEmprestimo @Id = 99;
-- EXEC dbo.usp_RemoverLivro @Id = 99;
-- EXEC dbo.usp_RemoverUsuario @Id = 99;
-- SELECT * FROM dbo.vw_EmprestimosAtivos;
-- SELECT TOP (100) * FROM dbo.LogEventos ORDER BY Id DESC;