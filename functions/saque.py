import psycopg2
from database.config import DatabaseConfig

def realizar_saque(register_id, saque_amount):
    try:
        # Conexão com o banco de dados
        db_config = DatabaseConfig.get_db_config()
        conexao = psycopg2.connect(**db_config)
        cursor = conexao.cursor()
        
        # Buscar saldo atual (register_id) baseado no register_id
        cursor.execute("""
            SELECT remaining_balance 
            FROM withdrawal_history 
            WHERE register_id = %s 
            ORDER BY timestamp DESC 
            LIMIT 1
        """, (register_id,))
        saldo_atual = cursor.fetchone()[0]

        saldo_atual = float(saldo_atual)

        # Calcular o novo saldo após o saque
        novo_saldo = saldo_atual - saque_amount

        if novo_saldo < 0:
            print("Saldo insuficiente para saque.")
            return

        # Inserir o registro de saque na tabela withdrawal_history
        cursor.execute("""
            INSERT INTO withdrawal_history
            (register_id, withdrawn_amount, initial_balance, remaining_balance)
            VALUES (%s, %s, %s, %s)
            """, (register_id, saque_amount, saldo_atual, novo_saldo))

        conexao.commit()  # Confirmar as operações
        print("Saque realizado com sucesso.")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Erro ao realizar saque:", error)
    finally:
        if conexao is not None:
            conexao.close()

# Exemplo de uso
# realizar_saque('uuid-do-registro', 500.00)
