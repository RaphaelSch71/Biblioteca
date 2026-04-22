# BibliotecaBD (Python + PySide6 + SQL Server)

## Executar em outro computador

1. Instale Python 3.11+.
2. Instale **ODBC Driver 17 for SQL Server**.
3. Na pasta do projeto, instale dependências:
   - `pip install -r requirements.txt`
4. Copie `.env.example` para `.env` e ajuste conexão SQL.
5. Rode:
   - `python main.py`

## Modos de execução

- **SQL Server**: quando conexão estiver válida.
- **Memória**: fallback automático sem persistência no banco.
- Para forçar SQL e impedir fallback: `STRICT_SQL=true` no `.env`.

## Observações

- Banco esperado: `BibliotecaBD` com procedures/triggers do script `database/sql/01_create_biblioteca.sql`.
- Para o fluxo de pedidos de empréstimo (usuário solicita e bibliotecário aceita), execute também `database/sql/04_pedidos_emprestimo.sql`.
- Primeiro bibliotecário (bootstrap) só é criado se o banco estiver vazio.
- Código mestre padrão de bibliotecário: `BIB-2026` (alterável em `BIBLIOTECARIO_CODIGO_MASTER`).
