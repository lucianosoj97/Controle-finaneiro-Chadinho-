import psycopg2
from database.config import DatabaseConfig
from datetime import date

def get_dashboard_data():
    try:
        db_config = DatabaseConfig.get_db_config()
        conexao = psycopg2.connect(**db_config)
        cursor = conexao.cursor()

        # Obter a data do mês atual
        data_atual = date.today()
        primeiro_dia_do_mes_atual = data_atual.replace(day=1)

        # Consultar o valor limpo
        cursor.execute("""
            SELECT SUM(deposit_amount::numeric)
            FROM register
            WHERE (creation_date >= %s OR update_date >= %s)
            AND deletion_date IS NULL
        """, (primeiro_dia_do_mes_atual, primeiro_dia_do_mes_atual))
        deposit_amount = cursor.fetchone()[0] or 0

        # Consultar o valor pago
        cursor.execute("""
            SELECT SUM(amount_received::numeric)
            FROM register
            WHERE (creation_date >= %s OR update_date >= %s)
            AND deletion_date IS NULL
        """, (primeiro_dia_do_mes_atual, primeiro_dia_do_mes_atual))
        amount_received = cursor.fetchone()[0] or 0

        # Consultar a porcentagem de leads
        cursor.execute("""
            SELECT SUM(positive_balance::numeric)
            FROM register
            WHERE (creation_date >= %s OR update_date >= %s)
            AND deletion_date IS NULL
        """, (primeiro_dia_do_mes_atual, primeiro_dia_do_mes_atual))
        positive_balance = cursor.fetchone()[0] or 0


        cursor.execute("""
            SELECT SUM(payment_percentage::numeric)
            FROM register
            WHERE (creation_date >= %s OR update_date >= %s)
            AND deletion_date IS NULL
        """, (primeiro_dia_do_mes_atual, primeiro_dia_do_mes_atual))
        payment_percentage = cursor.fetchone()[0] or 0

        conexao.close()

        return deposit_amount, amount_received, positive_balance, payment_percentage

    except Exception as e:
        print(f"Erro ao obter dados do dashboard: {e}")
        return None, None, None
