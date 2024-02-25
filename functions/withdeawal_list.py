import psycopg2
from database.config import DatabaseConfig
import logging

# Configurando o registro
logging.basicConfig(level=logging.DEBUG)

def gerenciamento_de_contas():
    try:
        db_config = DatabaseConfig.get_db_config()
        conexao = psycopg2.connect(**db_config)
        cursor = conexao.cursor()

        # Consulta SQL para recuperar os cadastros com deletion_date vazio
        consulta_sql = """
            SELECT r.id,
                   r.name,
                   r.betting_house,
                   (SELECT wh.remaining_balance
                    FROM withdrawal_history wh
                    WHERE wh.register_id = r.id
                    ORDER BY wh.timestamp DESC
                    LIMIT 1) AS remaining_balance
            FROM register r;
        """

        cursor.execute(consulta_sql)
        cadastros = cursor.fetchall()  # Obtém todos os registros
        cursor.close()
        conexao.close()
        return cadastros

    except Exception as e:
        logging.error(f"Erro ao obter cadastros: {e}")
        return []
