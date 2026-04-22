# Biblioteca — Library Management System

A desktop Library Management System built with **Python**, **PySide6**, and **SQL Server**.

It provides role-based access, day-to-day circulation workflows, and a modern desktop UI for managing books, users, and loans.

## Features

- Role-based authentication and authorization
- Book catalog management (create, read, update, delete)
- User/member management (create, read, update, delete)
- Loan and return operations
- Search and filtering for faster operations
- Desktop-first responsive UI with PySide6
- SQL Server-backed persistence

## Architecture

The application follows a layered desktop architecture:

- **Presentation Layer (PySide6):** desktop windows, dialogs, forms, and event handling
- **Application/Domain Layer (Python):** business rules for users, books, and loan lifecycle
- **Data Access Layer:** SQL Server integration, query execution, and persistence concerns

Typical flow:

1. User action in UI
2. Validation and domain logic execution
3. Data read/write in SQL Server
4. UI refresh with updated state

## Tech Stack

- **Language:** Python 3.10+
- **UI Framework:** PySide6
- **Database:** Microsoft SQL Server
- **Driver:** ODBC (recommended via `pyodbc`)

## Setup

### 1) Prerequisites

- Python 3.10 or newer
- SQL Server instance (local or remote)
- ODBC Driver for SQL Server (v17 or v18)

### 2) Clone the repository

```bash
git clone https://github.com/RaphaelSch71/Biblioteca.git
cd Biblioteca
```

### 3) Create and activate a virtual environment

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

### 4) Install dependencies

> If your repository includes a requirements file:

```bash
pip install -r requirements.txt
```

> Otherwise, install the core stack manually:

```bash
pip install PySide6 pyodbc
```

### 5) Configure environment variables

Create a `.env` file (or configure OS environment variables) using the variables below.

### 6) Run the application

```bash
python main.py
```

> If your entry point differs, run the correct startup script for your project structure.

## Environment Variables

| Variable | Required | Description | Example |
| --- | --- | --- | --- |
| `DB_SERVER` | Yes | SQL Server host/address | `localhost` |
| `DB_PORT` | No | SQL Server port (default `1433`) | `1433` |
| `DB_NAME` | Yes | Database name | `Biblioteca` |
| `DB_USER` | Yes | SQL Server login user | `sa` |
| `DB_PASSWORD` | Yes | SQL Server login password | `StrongPassword!123` |
| `DB_DRIVER` | No | ODBC driver name | `ODBC Driver 18 for SQL Server` |
| `APP_ENV` | No | Environment label | `development` |

> Never commit real credentials. Use local environment configuration or secrets management.

## Screenshots

Add UI screenshots to `docs/screenshots/` and reference them here.

| Login | Dashboard |
| --- | --- |
| ![Login screen](docs/screenshots/login.png) | ![Dashboard](docs/screenshots/dashboard.png) |

| Book Management | Loan Management |
| --- | --- |
| ![Books screen](docs/screenshots/books.png) | ![Loans screen](docs/screenshots/loans.png) |

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening issues or pull requests.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
