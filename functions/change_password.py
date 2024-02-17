from database.config import DatabaseConfig
import psycopg2
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


def verificar_email_usuario(email):
    db_config = DatabaseConfig.get_db_config()
    conexao = psycopg2.connect(**db_config)

    cursor = conexao.cursor()

    try:
        # Substitua 'tabela_usuarios' pelo nome real da sua tabela de usuários
        query = "SELECT EXISTS(SELECT 1 FROM usuário WHERE username = %s)"

        cursor.execute(query, (email,))
        existe = cursor.fetchone()[0]  # Retorna True se o usuário existir, False caso contrário

        conexao.close()  # Não esqueça de fechar a conexão após a consulta
        return existe
    except psycopg2.Error as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return False  # Retorna False em caso de erro na consulta

def gerar_e_enviar_codigo(email):
    codigo = ''.join(random.choices(string.digits, k=6))

    # Usando variáveis de ambiente para as credenciais SMTP
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "luciano.soj97@gmail.com"
    smtp_password = "vcny vlho ucob whiy"

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = email
    msg['Subject'] = "Seu código de redefinição de senha"

    body = f"""<html><head></head><body>
        <h2>Redefinição de Senha</h2>
        <p>Olá,</p>
        <p>Você solicitou a redefinição de sua senha. Use o código abaixo para continuar o processo de redefinição de senha no nosso aplicativo:</p>
        <p><b>Código de Redefinição:</b> {codigo}</p>
        <p>Se você não solicitou a redefinição de senha, por favor ignore este e-mail ou entre em contato conosco se achar que isso é um erro.</p>
        <br><p>Atenciosamente,</p><p>Sua Equipe</p>
    </body></html>"""
    msg.attach(MIMEText(body, 'html'))

    #try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.sendmail(smtp_user, email, msg.as_string())
    server.quit()
    print("E-mail enviado com sucesso.")
        
        # Salva o código no banco de dados
    db_config = DatabaseConfig.get_db_config()
    conexao = psycopg2.connect(**db_config)
    cursor = conexao.cursor()
    query = "UPDATE usuário SET codigo = %s WHERE username = %s"
    cursor.execute(query, (codigo, email))
    conexao.commit()
    cursor.close()
    conexao.close()

    #except Exception as e:
        #print(f"Erro ao enviar e-mail ou salvar código: {e}")

def validar_codigo(email, codigo_usuario):
    db_config = DatabaseConfig.get_db_config()
    conexao = psycopg2.connect(**db_config)

    cursor = conexao.cursor()

    try:
        # Substitua 'sua_tabela_de_usuarios' pelo nome real da sua tabela de usuários
        # e 'codigo_redefinicao' pelo nome da coluna que armazena o código
        query = "SELECT codigo FROM usuário WHERE username = %s"

        cursor.execute(query, (email,))
        codigo_armazenado = cursor.fetchone()

        if codigo_armazenado and codigo_armazenado[0] == codigo_usuario:
            # Código corresponde, retorna True
            return True
        else:
            # Código não corresponde ou usuário não encontrado, retorna False
            return False
    except psycopg2.Error as e:
        print(f"Erro ao validar o código: {e}")
        return False
    finally:
        cursor.close()
        conexao.close()

def alterar_senha(email, nova_senha):
    db_config = DatabaseConfig.get_db_config()
    conexao = psycopg2.connect(**db_config)
    cursor = conexao.cursor()

    try:
        # Atualiza diretamente a senha sem usar hash
        query = "UPDATE usuário SET password = %s WHERE username = %s"  # Ajuste os nomes de coluna e tabela conforme necessário

        cursor.execute(query, (nova_senha, email))

        if cursor.rowcount == 0:
            # Nenhum usuário encontrado com o e-mail fornecido
            return False

        conexao.commit()
        return True
    except psycopg2.Error as e:
        print(f"Erro ao atualizar a senha: {e}")
        return False
    finally:
        cursor.close()
        conexao.close()
