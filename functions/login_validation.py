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
            print("Conexão bem-sucedidaaa!")

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
                ADD COLUMN IF NOT EXISTS balance NUMERIC;
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

    def update_usuario_table(self):
        try:
            cursor = self.conexao.cursor()

            # Renomeia a coluna 'deletiondate' para 'codigo'
            rename_column_query = """
                ALTER TABLE usuário RENAME COLUMN deletiondate TO codigo;
            """
            cursor.execute(rename_column_query)

            # Altera o tipo da coluna 'codigo' para VARCHAR(6)
            alter_column_type_query = """
                ALTER TABLE usuário ALTER COLUMN codigo TYPE VARCHAR(6) USING codigo::VARCHAR(6);
            """
            cursor.execute(alter_column_type_query)

            self.conexao.commit()
            print("Coluna 'deletiondate' renomeada para 'codigo' e tipo alterado para VARCHAR(6) com sucesso na tabela 'usuário'!")

        except Exception as e:
            print(f"Erro ao renomear e alterar tipo da coluna na tabela 'usuário': {e}")

    def create_withdrawal_history(self):
        try:
            cursor = self.conexao.cursor()

            # Verificar se a tabela já existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'withdrawal_history'
                );
            """)
            table_exists = cursor.fetchone()[0]

            if not table_exists:
                # Criar tabela se ela não existir
                create_table_query = """
                    CREATE TABLE withdrawal_history (
                        id SERIAL PRIMARY KEY,
                        register_id UUID NOT NULL,
                        initial_balance DECIMAL(10, 2) NOT NULL,
                        withdrawn_amount DECIMAL(10, 2) NOT NULL,
                        remaining_balance DECIMAL(10, 2) NOT NULL,
                        description TEXT,
                        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT fk_register
                            FOREIGN KEY(register_id) 
                            REFERENCES register(id)
                            ON DELETE CASCADE
                    );
                """
                cursor.execute(create_table_query)
                print("Tabela 'withdrawal_history' criada com sucesso!")
            else:
                # Adicionar colunas ausentes
                columns_to_check = [
                    ('initial_balance', 'DECIMAL(10, 2)'),
                    ('withdrawn_amount', 'DECIMAL(10, 2)'),
                    ('remaining_balance', 'DECIMAL(10, 2)'),
                    ('description', 'TEXT'),
                    ('timestamp', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ]

                for column_name, column_type in columns_to_check:
                    cursor.execute(f"""
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_name='withdrawal_history' AND column_name='{column_name}';
                    """)
                    if not cursor.fetchone():
                        cursor.execute(f"ALTER TABLE withdrawal_history ADD COLUMN {column_name} {column_type};")
                        print(f"Coluna '{column_name}' adicionada à tabela 'withdrawal_history'.")

            self.conexao.commit()

        except Exception as e:
            print(f"Erro ao criar a tabela 'withdrawal_history': {e}")
        finally:
            if cursor:
                cursor.close()

login_validator = LoginValidator()
