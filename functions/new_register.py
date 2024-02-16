import psycopg2
from database.config import DatabaseConfig
from decimal import Decimal
from datetime import datetime
from flask import flash, redirect, url_for


def criar_registro(nome, cpf, birth_date, endereco, valor_depositado, porcentagem_pago):
    try:
        db_config = DatabaseConfig.get_db_config()
        conexao = psycopg2.connect(**db_config)
        valor_depositado_formatado = Decimal(valor_depositado.replace('R$', '').replace('.', '').replace(',', ''))
        porcentagem_pago_formatada = Decimal(porcentagem_pago.replace('%', ''))
        current_date = datetime.now().strftime('%Y-%m-%d')

        valor_total, valor_descontado = calcular_valor_descontado(valor_depositado_formatado, porcentagem_pago_formatada)


        cursor = conexao.cursor()

        inserir_registro_query = """
            INSERT INTO register (id, name, cpf, birth_date, address, value, lead_value, owner_value, percentage, creation_date)
            VALUES (uuid_generate_v4(), %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(inserir_registro_query, (nome, cpf, birth_date, endereco, valor_depositado_formatado, valor_descontado, valor_total, porcentagem_pago_formatada, current_date))
        conexao.commit()
        cursor.close() 
        conexao.close()

        flash("Registro criado com sucesso!", "success")
        return redirect(url_for('list_people'))

    except Exception as e:
        print(f"Erro ao criar registro: {e}")
        flash("Erro ao criar registro.", "error")
        return redirect(url_for('register'))

def calcular_valor_descontado(valor_depositado, porcentagem_pago):
    try:
        valor_total = valor_depositado - (valor_depositado * (porcentagem_pago / 100))
        valor_total = valor_total.quantize(Decimal('0.00'))
        valor_descontado = valor_depositado - valor_total
        return valor_total, valor_descontado

    except Exception as e:
        print(f"Erro ao calcular valor descontado: {e}")
        return None, None