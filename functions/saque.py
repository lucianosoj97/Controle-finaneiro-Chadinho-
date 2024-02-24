import psycopg2

def realizar_saque(register_id, saque_amount):
    try:
        # Conexão com o banco de dados
        conexao = psycopg2.connect(user="seu_usuario", password="sua_senha", host="127.0.0.1", port="5432", database="seu_banco")
        cursor = conexao.cursor()
        
        # Buscar saldo atual (lead_value) baseado no register_id
        cursor.execute("SELECT lead_value FROM register WHERE id = %s", (register_id,))
        saldo_atual = cursor.fetchone()[0]

        # Calcular o novo saldo após o saque
        novo_saldo = saldo_atual - saque_amount

        if novo_saldo < 0:
            print("Saldo insuficiente para saque.")
            return

        # Atualizar o saldo na tabela register
        cursor.execute("UPDATE register SET lead_value = %s WHERE id = %s", (novo_saldo, register_id))

        # Inserir o registro de saque na tabela withdrawal_history
        cursor.execute("INSERT INTO withdrawal_history (register_id, withdrawn_amount, remaining_balance) VALUES (%s, %s, %s)",
                       (register_id, saque_amount, novo_saldo))
        
        conexao.commit()  # Confirmar as operações
        print("Saque realizado com sucesso.")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Erro ao realizar saque:", error)
    finally:
        if conexao is not None:
            conexao.close()

# Exemplo de uso
# realizar_saque('uuid-do-registro', 500.00)
