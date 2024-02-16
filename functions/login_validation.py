import psycopg2
from database.config import DatabaseConfig

class LoginValidator:
    def __init__(self):
        self.conexao = None
        self.conectar()

    def conectar(self):
        try:
            # Aqui você obtém a configuração do banco de dados usando a classe DatabaseConfig
            db_config = DatabaseConfig.get_db_config()
            self.conexao = psycopg2.connect(**db_config)
            print("Conexão bem-sucedida!")
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def desconectar(self):
        if self.conexao is not None:
            self.conexao.close()
            print("Conexão fechada.")
            self.conexao = None

    def validar_credenciais(self, email, senha):
        try:
            cursor = self.conexao.cursor()
            comando_sql_verificar_usuario = """
                SELECT 1 FROM usuário
                WHERE username = %s AND password = %s
            """
            valores = (email, senha)

            cursor.execute(comando_sql_verificar_usuario, valores)

            usuario_encontrado = cursor.fetchone()

            if usuario_encontrado:
                return True
            else:
                return False

        except Exception as e:
            print(f"Erro ao validar credenciais: {e}")
            return False

    def criar_extensao_uuid_ossp(self):
        try:
            cursor = self.conexao.cursor()
            cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
            self.conexao.commit()
            print("Extensão 'uuid-ossp' criada com sucesso!")
        except Exception as e:
            print(f"Erro ao criar a extensão 'uuid-ossp': {e}")

    def create_register_table(self):
        try:
            cursor = self.conexao.cursor()

            create_table_query = """
                CREATE TABLE IF NOT EXISTS register (
                    id UUID PRIMARY KEY,
                    name VARCHAR,
                    cpf VARCHAR,
                    email VARCHAR,
                    address VARCHAR,
                    value NUMERIC,
                    percentage NUMERIC,
                    update_date DATE,
                    creation_date DATE,
                    deletion_date DATE
                )
            """
            cursor.execute(create_table_query)
            self.conexao.commit()
            print("Tabela 'register' criada com sucesso!")

        except Exception as e:
            print(f"Erro ao criar a tabela 'register': {e}")

    def update_register_table(self):
        try:
            cursor = self.conexao.cursor()

            # Adiciona as novas colunas à tabela existente
            alter_table_query = """
                ALTER TABLE register
                ADD COLUMN IF NOT EXISTS birth_date DATE,
                ADD COLUMN IF NOT EXISTS lead_value NUMERIC,
                ADD COLUMN IF NOT EXISTS owner_value NUMERIC
            """
            cursor.execute(alter_table_query)
            self.conexao.commit()
            print("Colunas adicionadas com sucesso à tabela 'register'!")

        except Exception as e:
            print(f"Erro ao adicionar colunas à tabela 'register': {e}")

    def deletar_registros(self):
        try:
            cursor = self.conexao.cursor()

            # Query para excluir todos os registros da tabela register
            delete_query = "DELETE FROM register;"

            # Execute a query
            cursor.execute(delete_query)

            # Commit para efetivar a exclusão
            self.conexao.commit()

            print("Todos os registros da tabela 'register' foram excluídos com sucesso!")

        except Exception as e:
            print(f"Erro ao excluir registros da tabela 'register': {e}")

login_validator = LoginValidator()
