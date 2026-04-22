# BibliotecaBD (Python + PySide6 + SQL Server)

Desktop library management system built with Python (PySide6 + SQL Server), featuring role-based authentication, full CRUD for books/users/loans, and a modern responsive UI.

## Run on another machine

1. Install Python 3.11+.
2. Install **ODBC Driver 17 for SQL Server**.
3. In the project folder, install dependencies:
   - `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and adjust SQL connection settings.
5. Run:
   - `python main.py`

## Execution modes

- **SQL Server**: when database connection is available.
- **Memory**: automatic fallback when SQL is unavailable.
- To force SQL mode and disable fallback: set `STRICT_SQL=true` in `.env`.

## Notes

- Expected DB: `BibliotecaBD` with procedures/triggers from `database/sql/01_create_biblioteca.sql`.
- For loan-request workflow (user requests, librarian approves), also run `database/sql/04_pedidos_emprestimo.sql`.
- First librarian (bootstrap) is created only when the database is empty.
- Default librarian master code: `BIB-2026` (configurable via `BIBLIOTECARIO_CODIGO_MASTER`).
