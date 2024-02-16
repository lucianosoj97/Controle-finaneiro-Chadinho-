import psycopg2
from flask import redirect, url_for, render_template
from database.config import DatabaseConfig
from datetime import datetime
from decimal import Decimal
import logging

# Configurar o registro
logging.basicConfig(filename='update_person_log.log', level=logging.INFO)

def edit_person(id):
    try:
        db_config = DatabaseConfig.get_db_config()
        conexao = psycopg2.connect(**db_config)
        cursor = conexao.cursor()

        buscar_pessoa_query = """
            SELECT id, name, cpf, birth_date, address, value, percentage FROM register
            WHERE id = %s
        """
        cursor.execute(buscar_pessoa_query, (id,))
        pessoa = cursor.fetchone()

        conexao.close()

        if pessoa is None:
            # Se não encontrar a pessoa pelo ID, redirecione para a página de listagem
            return redirect(url_for('list_people'))

        # Converta os valores da pessoa em um dicionário para facilitar o acesso aos dados no template
        pessoa_dict = {
            'id': pessoa[0],
            'name': pessoa[1],
            'cpf': pessoa[2],
            'birth_date': pessoa[3],
            'address': pessoa[4],
            'value': pessoa[5],
            'percentage': pessoa[6]
        }

        return render_template('edit.html', person=pessoa_dict)

    except Exception as e:
        print(f"Erro ao editar pessoa: {e}")
        return redirect(url_for('list_people'))

def update_person(id, name, cpf, birth_date, address, value, percentage):
    try:
        db_config = DatabaseConfig.get_db_config()
        conexao = psycopg2.connect(**db_config)
        cursor = conexao.cursor()

        # Obtenha a data atual
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Calcula os valores de owner_value e lead_value
        value = Decimal(value.replace('R$', '').replace('.', '').replace(',', ''))
        percentage = Decimal(percentage.replace('%', ''))
        valor_total, valor_descontado = calcular_valor_descontado(value, percentage)

        # Atualize os dados da pessoa no banco de dados
        atualizar_pessoa_query = """
            UPDATE register
            SET name = %s, cpf = %s, birth_date = %s, address = %s, value = %s, percentage = %s, owner_value = %s, lead_value = %s, update_date = %s
            WHERE id = %s
        """
        cursor.execute(atualizar_pessoa_query, (name, cpf, birth_date, address, value, percentage, valor_total, valor_descontado, current_date, id))
        conexao.commit()
        cursor.close()
        conexao.close()

        # Log da atualização bem-sucedida
        logging.info(f"Atualização bem-sucedida: ID={id}, Nome={name}, CPF={cpf}, Data de Nascimento={birth_date}, Endereço={address}, Valor={value}, Porcentagem={percentage}, Valor Total={valor_total}, Valor Descontado={valor_descontado}, Data de Atualização={current_date}")

        return True  # Indica que a atualização foi bem-sucedida

    except Exception as e:
        logging.error(f"Erro ao atualizar pessoa: {e}")
        return False  # Indica que ocorreu um erro na atualização

def calcular_valor_descontado(valor_depositado, porcentagem_pago):
    try:
        valor_total = valor_depositado - (valor_depositado * (porcentagem_pago / 100))
        valor_total = valor_total.quantize(Decimal('0.00'))
        valor_descontado = valor_depositado - valor_total
        return valor_total, valor_descontado

    except Exception as e:
        print(f"Erro ao calcular valor descontado: {e}")
        return None, None