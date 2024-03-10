import psycopg2
from flask import redirect, url_for, render_template, flash
from database.config import DatabaseConfig
from datetime import datetime
from decimal import Decimal
import logging
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
logging.basicConfig(filename='update_person_log.log', level=logging.INFO)

def edit_person(id):
    try:
        db_config = DatabaseConfig.get_db_config()
        conexao = psycopg2.connect(**db_config)
        cursor = conexao.cursor()

        buscar_pessoa_query = """
            SELECT id, name, cpf, birth_date , address, deposit_amount, amount_received, positive_balance, payment_percentage, betting_house FROM register
            WHERE id = %s
        """
        cursor.execute(buscar_pessoa_query, (id,))
        pessoa = cursor.fetchone()

        conexao.close()

        if pessoa is None:
            return redirect(url_for('list_people'))

        # Converta os valores da pessoa em um dicionário para facilitar o acesso aos dados no template
        pessoa_dict = {
            'id': pessoa[0],
            'name': pessoa[1],
            'cpf': pessoa[2],
            'birth_date': pessoa[3],
            'address': pessoa[4],
            'deposit_amount': locale.currency(pessoa[5], grouping=True),
            'amount_received': locale.currency(pessoa[6], grouping=True),
            'positive_balance': locale.currency(pessoa[7], grouping=True),
            'payment_percentage': locale.currency(pessoa[8], grouping=True),
            'betting_house': pessoa[9],
        }

        return render_template('edit.html', person=pessoa_dict)

    except Exception as e:
        print(f"Erro ao editar pessoa: {e}")
        return redirect(url_for('list_people'))

def update_person(id, name, cpf, birth_date, address, deposit_amount,amount_received, positive_balance, payment_percentage, betting_house):
    try:
        db_config = DatabaseConfig.get_db_config()
        conexao = psycopg2.connect(**db_config)
        cursor = conexao.cursor()

        # Obtenha a data atual
        current_date = datetime.now().strftime('%Y-%m-%d')

        deposit_amount = Decimal(deposit_amount.replace('R$', '').replace('.', '').replace(',', '.'))
        amount_received = Decimal(amount_received.replace('R$', '').replace('.', '').replace(',', '.'))
        positive_balance = Decimal(positive_balance.replace('R$', '').replace('.', '').replace(',', '.'))
        payment_percentage = Decimal(payment_percentage.replace('R$', '').replace('.', '').replace(',', '.'))

        # Atualize os dados da pessoa no banco de dados
        atualizar_pessoa_query = """
            UPDATE register
            SET name = %s, cpf = %s, birth_date = %s, address = %s, deposit_amount = %s, amount_received = %s, positive_balance = %s, payment_percentage = %s, betting_house = %s, update_date = %s
            WHERE id = %s
        """
        cursor.execute(atualizar_pessoa_query, (name, cpf, birth_date, address, deposit_amount, amount_received, positive_balance, payment_percentage, betting_house, current_date, id))
        conexao.commit()
        cursor.close()
        conexao.close()

        flash('Cadastro realizado com sucesso!', 'success')
        return True

    except Exception as e:
        logging.error(f"Erro ao atualizar pessoa: {e}")
        return False  # Indica que ocorreu um erro na atualização
