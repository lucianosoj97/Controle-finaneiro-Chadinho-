import psycopg2
from database.config import DatabaseConfig
from decimal import Decimal
from datetime import datetime
from flask import flash, redirect, url_for


def criar_registro(full_name, cpf, birth_date, address, deposit_amount, amount_received, positive_balance, payment_percentage, betting_house):
    try:
        db_config = DatabaseConfig.get_db_config()
        conexao = psycopg2.connect(**db_config)
        cursor = conexao.cursor()

        # Assegure-se de que 'deposit_amount' e 'payment_percentage' são passados como strings que se parecem com valores monetários, por exemplo 'R$ 1.000,50' e '10%', respectivamente.
        deposit_amount = Decimal(deposit_amount.replace('R$', '').replace('.', '').replace(',', '.'))
        amount_received = Decimal(amount_received.replace('R$', '').replace('.', '').replace(',', '.'))
        positive_balance = Decimal(positive_balance.replace('R$', '').replace('.', '').replace(',', '.'))
        payment_percentage = Decimal(payment_percentage.replace('R$', '').replace('.', '').replace(',', '.'))

        current_date = datetime.now().strftime('%Y-%m-%d')

        inserir_registro_query = """
            INSERT INTO register (name, cpf, birth_date, address, deposit_amount, amount_received, positive_balance, payment_percentage, creation_date, betting_house)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """

        cursor.execute(inserir_registro_query, (full_name, cpf, birth_date, address, deposit_amount, amount_received, positive_balance, payment_percentage, current_date, betting_house))
        register_id = cursor.fetchone()[0]

        conexao.commit()
        cursor.close()
        conexao.close()

    except Exception as e:
        conexao.rollback()
        print(f"Erro ao criar registro: {e}")
        return redirect(url_for('register'))
