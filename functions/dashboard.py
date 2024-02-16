import psycopg2
from database.config import DATABASE_CONFIG
from datetime import date

def get_dashboard_data():
    try:
        conexao = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conexao.cursor()

        # Obter a data do mês atual
        data_atual = date.today()
        primeiro_dia_do_mes_atual = data_atual.replace(day=1)

        # Consultar o valor limpo
        cursor.execute("""
            SELECT SUM(owner_value)
            FROM register
            WHERE (creation_date >= %s OR update_date >= %s)
            AND deletion_date IS NULL
        """, (primeiro_dia_do_mes_atual, primeiro_dia_do_mes_atual))
        valor_limpo = cursor.fetchone()[0] or 0

        # Consultar o valor pago
        cursor.execute("""
            SELECT SUM(value)
            FROM register
            WHERE (creation_date >= %s OR update_date >= %s)
            AND deletion_date IS NULL
        """, (primeiro_dia_do_mes_atual, primeiro_dia_do_mes_atual))
        valor_arrecadado = cursor.fetchone()[0] or 0

        # Consultar a porcentagem de leads
        cursor.execute("""
            SELECT SUM(lead_value)
            FROM register
            WHERE (creation_date >= %s OR update_date >= %s)
            AND deletion_date IS NULL
        """, (primeiro_dia_do_mes_atual, primeiro_dia_do_mes_atual))
        porcentagem_leads = cursor.fetchone()[0] or 0

        conexao.close()

        return valor_limpo, valor_arrecadado, porcentagem_leads

    except Exception as e:
        print(f"Erro ao obter dados do dashboard: {e}")
        return None, None, None
