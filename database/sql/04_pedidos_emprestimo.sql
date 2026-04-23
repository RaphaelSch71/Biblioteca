USE BibliotecaBD;
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

    IF @DataPrevistaDevolucao IS NULL
        THROW 51007, 'Informe a data prevista de devolução.', 1;

    IF @DataPrevistaDevolucao < CAST(GETDATE() AS DATE)
        THROW 51008, 'Data prevista de devolução não pode estar no passado.', 1;

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

    INSERT INTO dbo.Emprestimos (LivroId, UsuarioId, DataEmprestimo, DataPrevistaDevolucao, DataDevolucao, Ativo)
    VALUES (@LivroId, @UsuarioId, CAST(GETDATE() AS DATE), @DataPrevistaDevolucao, NULL, 1);

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
