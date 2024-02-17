from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functions.login_validation import LoginValidator
from functions.new_register import criar_registro
from functions.list import obter_cadastros
from functions.dashboard import get_dashboard_data
from functions.edit import edit_person, update_person
from functions.token import token_valido
from functions.change_password import alterar_senha, validar_codigo, verificar_email_usuario, gerar_e_enviar_codigo
from database.config import DatabaseConfig
import psycopg2
import uuid
from datetime import datetime

app = Flask(__name__, static_folder='static')
app.secret_key = 'sua_chave_secreta'  # Chave secreta para uso de sessões

@app.route('/', methods=['GET'])
def init():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    validator = LoginValidator()  # Assumindo que você tem um construtor adequado
    if validator.validar_credenciais(username, password):
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error_message="E-mail ou senha incorretos.")

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
        try:
            # Convertendo a string para float antes de formatar
            valor_float = float(formatted_cadastro[5])
            # Formatação como valor monetário
            formatted_cadastro[5] = 'R$ {:,.2f}'.format(valor_float).replace(',', 'v').replace('.', ',').replace('v', '.')
        except ValueError:
            # Caso não seja possível converter para float, mantém o valor original ou trata o erro
            formatted_cadastro[5] = f'R$ {formatted_cadastro[5]}'
        # Presumindo que cadastro[6] é um valor numérico e pode ser diretamente formatado como porcentagem
        formatted_cadastro[6] = f'{cadastro[6]}%'
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
    db_config = DatabaseConfig.get_db_config()
    conexao = psycopg2.connect(**db_config)
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

@app.route('/verify_email', methods=['POST'])
def api_verify_email():
    data = request.get_json()
    email = data.get('email')
    if email:
        existe = verificar_email_usuario(email)  # Substitua pela sua função que verifica o email
        if existe:
            session['reset_email'] = email  # Armazena o email na sessão
            # Aqui chamamos a função para gerar e enviar o código
            gerar_e_enviar_codigo(email)  # Substitua pela sua função que gera e envia o código
            return jsonify({'exists': True})
        else:
            return jsonify({'exists': False})
    else:
        return jsonify({'error': 'E-mail não fornecido'}), 400

@app.route('/change_password')
def change_password():
    email = session.get('reset_email')
    if email:
        # Passa o email para o template
        return render_template('change_password.html', reset_email=email)
    else:
        return redirect(url_for('login'))

@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data['email']
    resetCode = data['resetCode']
    newPassword = data['newPassword']

    if validar_codigo(email, resetCode):
        if alterar_senha(email, newPassword):
            return jsonify({'success': True, 'message': 'Senha alterada com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Não foi possível alterar a senha.'})
    else:
        return jsonify({'success': False, 'message': 'Código inválido ou expirado.'})

if __name__ == '__main__':
    app.run(debug=True)
