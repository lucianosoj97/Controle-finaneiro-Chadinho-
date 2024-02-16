from flask import Flask, render_template, request, redirect, url_for, session
from functions.login_validation import login_validator
from functions.new_register import criar_registro
from functions.list import obter_cadastros
from functions.dashboard import get_dashboard_data
from functions.edit import edit_person, update_person
from functions.token import token_valido
from database.config import DatabaseConfig
import psycopg2
import uuid
from datetime import datetime

app = Flask(__name__, static_folder='static')
app.secret_key = 'sua_chave_secreta'  # Chave secreta para uso de sessões

@app.route('/', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def process_login():
    email_digitado = request.form['username']
    senha_digitada = request.form['password']

    try:
        if login_validator.validar_credenciais(email_digitado, senha_digitada):
            # Se as credenciais estiverem corretas, defina o usuário na sessão
            token = str(uuid.uuid4())
            session['token'] = token
            session.modified = True
            session['logged_in'] = True
            cadastros = obter_cadastros()

            return redirect(url_for('dashboard'))
        else:
            # Se as credenciais estiverem incorretas, renderize a página de login novamente com uma mensagem de erro
            return render_template('login.html', error_message="E-mail ou senha incorretos.")

    except Exception as e:
        print(f"Erro ao autenticar: {e}")
        # Se houver um erro ao autenticar, renderize a página de login novamente com uma mensagem de erro
        return render_template('login.html', error_message="Erro ao autenticar.")

@app.route('/dashboard')
def dashboard():
    if 'token' not in session:
        # Se o token não estiver presente na sessão, redirecione para a página de login
        return redirect(url_for('login'))

    # Verificar se o token é válido (você precisará implementar esta função)
    if not token_valido(session['token']):
        # Se o token não for válido, redirecione para a página de login
        return redirect(url_for('login'))

    # Obter dados do dashboard
    valor_limpo, valor_arrecadado, porcentagem_leads = get_dashboard_data()
    valor_limpo_str = '{:,.2f}'.format(valor_limpo).replace(',', 'v').replace('.', ',').replace('v', '.')
    valor_arrecadado_str = '{:,.2f}'.format(valor_arrecadado).replace(',', 'v').replace('.', ',').replace('v', '.')
    porcentagem_leads_str = '{:,.2f}'.format(porcentagem_leads).replace(',', 'v').replace('.', ',').replace('v', '.')

    return render_template('dashboard.html', valor_limpo=valor_limpo_str, valor_arrecadado=valor_arrecadado_str, porcentagem_leads=porcentagem_leads_str)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Verificar se o usuário está autenticado
    if 'token' not in session or not token_valido(session['token']):
        # Se o token não estiver presente ou não for válido, redirecione para a página de login
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Obtenha os dados do formulário HTML
        nome = request.form['full_name']
        cpf = request.form['cpf']
        birth_date = request.form['birth_date']
        endereco = request.form['address']
        valor_depositado = request.form['deposit_amount']
        porcentagem_pago = request.form['payment_percentage']

        # Chame a função criar_registro com os dados do formulário
        criar_registro(nome, cpf, birth_date, endereco, valor_depositado, porcentagem_pago)

        return redirect('/dashboard')  # Redirecione para a página inicial após a criação do registro

    return render_template('register.html')

@app.route('/list')
def list_people():
    # Verificar se o usuário está autenticado
    if 'token' not in session or not token_valido(session['token']):
        # Se o token não estiver presente ou não for válido, redirecione para a página de login
        return redirect(url_for('login'))

    # Obtenha os cadastros do banco de dados
    cadastros = obter_cadastros()

    if not cadastros:
        return render_template('list.html', people=[])
    formatted_cadastros = []
    for cadastro in cadastros:
        formatted_cadastro = list(cadastro)
        formatted_cadastro[5] = '{:,.2f}'.format(formatted_cadastro[5]).replace(',', 'v').replace('.', ',').replace('v', '.')
        formatted_cadastro[5] = f'R$ {cadastro[5]}'  # Formata o valor monetário
        formatted_cadastro[6] = f'{cadastro[6]}%'  # Formata o valor monetário
        formatted_cadastros.append(formatted_cadastro)

    return render_template('list.html', people=formatted_cadastros)

@app.route('/logout')
def logout():
    # Limpa a sessão do usuário
    session.clear()
    # Redireciona para a página de login
    return redirect(url_for('login'))

@app.route('/edit/<id>')
def edit_route(id):
    # Verificar se o usuário está autenticado
    if 'token' not in session or not token_valido(session['token']):
        # Se o token não estiver presente ou não for válido, redirecione para a página de login
        return redirect(url_for('login'))

    return edit_person(id)

@app.route('/update', methods=['POST'])
def update_person_route():
    # Verificar se o usuário está autenticado
    if 'token' not in session or not token_valido(session['token']):
        # Se o token não estiver presente ou não for válido, redirecione para a página de login
        return redirect(url_for('login'))

    if request.method == 'POST':
        id = request.form['id']
        name = request.form['full_name']
        cpf = request.form['cpf']
        birth_date = request.form['birth_date']
        address = request.form['address']
        value = request.form['deposit_amount']
        percentage = request.form['payment_percentage']

        # Chame a função para atualizar a pessoa no banco de dados
        if update_person(id, name, cpf, birth_date, address, value, percentage):
            # Se a atualização for bem-sucedida, redirecione para alguma página
            return redirect(url_for('list_people'))
        else:
            # Se houver um erro na atualização, redirecione para outra página ou exiba uma mensagem de erro
            return redirect(url_for('outra_pagina'))

@app.route('/send_whatsapp_message')
def send_whatsapp_message():
    # Seu código para enviar a mensagem para o WhatsApp aqui
    return redirect('https://wa.me/48984876498/?text=Preciso%20de%20acesso%20ao%20controle%20financeiro.')

@app.route('/delete/<uuid:id>', methods=['GET'])
def delete(id):
    deletion_date = datetime.now()
    # Conectar ao banco de dados PostgreSQL
    conexao = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conexao.cursor()

    # SQL para atualizar a coluna deletiondate
    sql_update_query = """ UPDATE register SET deletion_date = %s WHERE id = %s """
    cursor.execute(sql_update_query, (deletion_date, str(id)))

    conexao.commit()  # Confirmar a transação
    cursor.close()
    conexao.close()  # Fechar a conexão

    # Redirecionar para outra página, por exemplo, a lista de cadastros
    get_dashboard_data()
    return redirect(url_for('list_people'))



if __name__ == '__main__':
    app.run(debug=True)
