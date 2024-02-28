import urllib.parse as urlparse

class DatabaseConfig:
    @staticmethod
    def get_db_config():
        # Definir a URL do banco de dados diretamente no formato esperado por urlparse
        # Exemplo: 'postgres://user:password@host:port/dbname'
        # Você deve substituí-la pela URL real do seu banco de dados Supabase
        DATABASE_URL = 'postgres://postgres.cpfwmmxlbytjrjcnlnjg:FHDSsnuzXbbA35sT@aws-0-us-east-1.pooler.supabase.com:5432/postgres'
        url = urlparse.urlparse(DATABASE_URL)

        # Construir e retornar um dicionário com as configurações de conexão
        return {
            "database": url.path[1:],  # Remove a '/' inicial do nome do banco de dados
            "user": url.username,
            "password": url.password,
            "host": url.hostname,
            "port": url.port
        }
