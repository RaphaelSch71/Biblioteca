USE BibliotecaBD;
GO

-- Remove dados respeitando dependências
DELETE FROM dbo.Emprestimos;
DELETE FROM dbo.Livros;
DELETE FROM dbo.Usuarios;
GO

-- Reinicia IDs para 1 no próximo insert
DBCC CHECKIDENT ('dbo.Emprestimos', RESEED, 0);
DBCC CHECKIDENT ('dbo.Livros', RESEED, 0);
DBCC CHECKIDENT ('dbo.Usuarios', RESEED, 0);
GO

SELECT
    (SELECT COUNT(*) FROM dbo.Usuarios) AS TotalUsuarios,
    (SELECT COUNT(*) FROM dbo.Livros) AS TotalLivros,
    (SELECT COUNT(*) FROM dbo.Emprestimos) AS TotalEmprestimos;
GO
