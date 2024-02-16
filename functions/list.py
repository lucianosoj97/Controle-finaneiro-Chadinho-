import psycopg2
from database.config import DatabaseConfig
import logging

# Configurando o registro
logging.basicConfig(level=logging.DEBUG)

def obter_cadastros():
    try:
        db_config = DatabaseConfig.get_db_config()
        conexao = psycopg2.connect(**db_config)
        cursor = conexao.cursor()

        # Consulta SQL para recuperar os cadastros com deletion_date vazio
        consulta_sql = """
            SELECT id, name, cpf,birth_date , address, value, percentage
            FROM register
            WHERE deletion_date IS NULL
        """

        cursor.execute(consulta_sql)
        cadastros = cursor.fetchall()  # Obtém todos os registros
        cursor.close()
        conexao.close()
        return cadastros

    except Exception as e:
        logging.error(f"Erro ao obter cadastros: {e}")
        return []
