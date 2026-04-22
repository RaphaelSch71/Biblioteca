from database.connection import DatabaseConnection

class BaseRepository:
    def __init__(self):
        self.conn = DatabaseConnection.get_connection()
        self.cursor = self.conn.cursor()

    def _execute(self, sql, params=(), fetch=None, commit=False):
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, params)

            result = None
            if fetch == "one":
                result = cursor.fetchone()
            elif fetch == "all":
                result = cursor.fetchall()

            # Consome todos os result sets pendentes para evitar
            # HY000 "Conexão ocupada com resultados de outro comando".
            while cursor.nextset():
                pass

            if commit:
                self.conn.commit()

            return result
        finally:
            cursor.close()