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
                        SELECT name, cpf, email, address, value, percentage, update_date, 
                            creation_date, birth_date, lead_value, owner_value, betting_house 
                        FROM register;
                        """

        # Usando pandas para ler a consulta SQL diretamente para um DataFrame
        df = pd.read_sql_query(consulta_sql, conexao)

        if df.empty:
            print("Nenhum dado foi retornado pela consulta.")
            return  # Ou lide com a situação de outra forma que faça sentido para o seu caso

        # Renomeando colunas
        df.rename(columns={
            'name': 'Nome',
            'cpf': 'CPF',
            'email': 'Email',
            'address': 'Endereço',
            'value': 'Valor Depositado',
            'percentage': 'Porcentagem Paga',
            'update_date': 'Data de Atualização',
            'creation_date': 'Data do Cadastro',
            'birth_date': 'Data de Nascimento',
            'lead_value': 'Valor Pago para Pessoa',
            'owner_value': 'Valor Destinado para Mim',
            'betting_house': 'Casa de Aposta'
        }, inplace=True)

        df['Data de Nascimento'] = pd.to_datetime(df['Data de Nascimento']).dt.strftime('%d/%m/%Y')

        # Formatação dos valores monetários
        for coluna in ['Valor Depositado', 'Valor Pago para Pessoa', 'Valor Destinado para Mim']:
            df[coluna] = df[coluna].apply(formatar_moeda)

        # Escrevendo o DataFrame para um arquivo Excel na pasta de Downloads
        with pd.ExcelWriter(nome_arquivo_completo, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Dados', index=False)

        print(f"Relatório da tabela 'register' foi salvo como '{nome_arquivo_completo}' com sucesso.")

    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
    finally:
        # Fechando a conexão com o banco de dados em qualquer caso
        if conexao:
            conexao.close()

def formatar_moeda(valor):
    try:
        # Converte o valor para float e depois formata como moeda
        valor_num = float(valor)
        return f'R$ {valor_num:,.2f}'.replace('.', 'X').replace(',', '.').replace('X', ',')
    except (ValueError, TypeError):
        # Se o valor não puder ser convertido para float, retorna como está
        return valor