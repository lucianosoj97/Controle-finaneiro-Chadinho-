import psycopg2
from database.config import DatabaseConfig

def buscar_historico_saques(account_id):
    try:
        db_config = DatabaseConfig.get_db_config()
        conexao = psycopg2.connect(**db_config)
        cursor = conexao.cursor()
        
        # Sua query SQL para buscar o histórico de saques
        query = """
            SELECT timestamp, withdrawn_amount, initial_balance, remaining_balance
            FROM withdrawal_history
            WHERE register_id = %s
            ORDER BY timestamp DESC;
        """
        cursor.execute(query, (account_id,))
        historico = cursor.fetchall()

        print('historico', historico)
        # Converter os dados do histórico em uma lista de dicionários
        lista_historico = []
        for data, valor_sacado, saldo_anterior, saldo_atual in historico:
            lista_historico.append({
                "data": data.strftime("%d/%m/%Y %H:%M:%S"),
                "valor_sacado": f"R$ {valor_sacado:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),  # Adaptação para formato brasileiro
                "saldo_anterior": f"R$ {saldo_anterior:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),  # Adaptação para formato brasileiro
                "saldo_atual": f"R$ {saldo_atual:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')  # Adaptação para formato brasileiro
            })

        conexao.close()
        return lista_historico
    except Exception as e:
        print(f"Erro ao buscar histórico de saques: {e}")
        return []
