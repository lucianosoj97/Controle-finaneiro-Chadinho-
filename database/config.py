import os
import psycopg2
import urllib.parse as urlparse

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    url = urlparse.urlparse(DATABASE_URL)
    db_config = {
        'database': url.path[1:],
        'user': url.username,
        'password': url.password,
        'host': url.hostname,
        'port': url.port
    }
else:
    # Sua configuração padrão ou de desenvolvimento
    db_config = {
        'host': 'ec2-44-206-18-218.compute-1.amazonaws.com',
        'database': 'd23ojnd1ratrgv',
        'user': 'jyaonnebrgerlp',
        'password': '0ccf3e309091ee3c59ec42da55ed197a1e32300228bf43b8eee72b44b7d53b9a'
    }

# Conexão usando psycopg2, por exemplo
conn = psycopg2.connect(**db_config)