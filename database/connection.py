import os

try:
    import pyodbc
except ImportError:  # pragma: no cover - dependência opcional durante a fase de memória
    pyodbc = None


class DatabaseConnection:
    _connection = None

    @classmethod
    def get_connection(cls):
        if cls._connection is None:
            if pyodbc is None:
                raise RuntimeError(
                    "pyodbc não está instalado. Use os repositórios em memória ou instale a dependência antes de acessar o banco de dados."
                )

            driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
            server = os.getenv("DB_SERVER", r"localhost\SQLEXPRESS")
            database = os.getenv("DB_NAME", "BibliotecaBD")
            uid = os.getenv("DB_UID", "")
            pwd = os.getenv("DB_PWD", "")
            timeout = int(os.getenv("DB_TIMEOUT", "5"))
            encrypt = os.getenv("DB_ENCRYPT", "no")
            trust_server_certificate = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")
            trusted_env = os.getenv("DB_TRUSTED")
            trusted = (trusted_env.lower() in {"1", "true", "yes"}) if trusted_env is not None else True

            if trusted:
                conn_str = (
                    f"DRIVER={{{driver}}};"
                    f"SERVER={server};"
                    f"DATABASE={database};"
                    "Trusted_Connection=yes;"
                    "MARS_Connection=yes;"
                    f"Encrypt={encrypt};"
                    f"TrustServerCertificate={trust_server_certificate};"
                )
            else:
                conn_str = (
                    f"DRIVER={{{driver}}};"
                    f"SERVER={server};"
                    f"DATABASE={database};"
                    f"UID={uid};"
                    f"PWD={pwd};"
                    "MARS_Connection=yes;"
                    f"Encrypt={encrypt};"
                    f"TrustServerCertificate={trust_server_certificate};"
                )

            cls._connection = pyodbc.connect(conn_str, timeout=timeout)
        return cls._connection