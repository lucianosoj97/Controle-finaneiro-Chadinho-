import os
import pandas as pd
import psycopg2
from database.config import DatabaseConfig

def tabela_para_excel(nome_arquivo):
    try:
        # Caminho para a pasta de Downloads no Windows
        caminho_downloads = os.path.join(os.getenv('USERPROFILE'), 'Downloads')
        nome_arquivo_completo = os.path.join(caminho_downloads, nome_arquivo)

        # Configuração da conexão com o banco de dados
        db_config = DatabaseConfig.get_db_config()
        conexao = psycopg2.connect(**db_config)

        # Criação do SQL query
        consulta_sql = """
                        SELECT name, cpf, birth_date, address, deposit_amount, amount_received, positive_balance, payment_percentage, betting_house, update_date, creation_date
                        FROM register;
                        """
        df = pd.read_sql_query(consulta_sql, conexao)

        if df.empty:
            print("Nenhum dado foi retornado pela consulta.")
            return  # Ou lide com a situação de outra forma que faça sentido para o seu caso

        # Renomeando colunas
        df.rename(columns={
            'name': 'Nome',
            'cpf': 'CPF',
            'birth_date': 'Data de Nascimento',
            'address': 'Endereço',
            'deposit_amount': 'Valor Depositado',
            'payment_percentage': 'Valor Pago',
            'amount_received': 'Valor Recebido',
            'positive_balance': 'Lucro',
            'update_date': 'Data de Atualização',
            'betting_house': 'Casa de Aposta',
            'creation_date': 'Data do Cadastro'
        }, inplace=True)

        df['Data de Nascimento'] = pd.to_datetime(df['Data de Nascimento']).dt.strftime('%d/%m/%Y')
        df['Data de Atualização'] = pd.to_datetime(df['Data de Atualização']).dt.strftime('%d/%m/%Y')
        df['Data do Cadastro'] = pd.to_datetime(df['Data do Cadastro']).dt.strftime('%d/%m/%Y')


        for coluna in ['Valor Depositado', 'Valor Pago', 'Valor Recebido','Lucro' ]:
            df[coluna] = df[coluna].apply(formatar_moeda)

        # Escrevendo o DataFrame para um arquivo Excel na pasta de Downloads
        with pd.ExcelWriter(nome_arquivo_completo, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Dados', index=False)

        os.startfile(nome_arquivo_completo)

    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
    finally:
        # Fechando a conexão com o banco de dados em qualquer caso
        if conexao:
            conexao.close()

def formatar_moeda(valor):
    if valor is None or valor == 0:
        return 'R$ 0,00'
    else:
        return f'R$ {valor:,.2f}'.replace('.', 'X').replace(',', '.').replace('X', ',')
