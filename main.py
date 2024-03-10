from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_file
from functions.login_validation import login_validator
from functions.new_register import criar_registro
from functions.list import obter_cadastros
from functions.dashboard import get_dashboard_data
from functions.edit import edit_person, update_person
from functions.token import token_valido
from functions.change_password import alterar_senha, validar_codigo, verificar_email_usuario
from functions.withdeawal_list import gerenciamento_de_contas
from functions.saque import realizar_saque
from functions.history_saque import buscar_historico_saques
from functions.report import tabela_para_excel
from database.config import DatabaseConfig
import psycopg2
import uuid
import os

app = Flask(__name__, static_folder='static')
app.secret_key = 'sua_chave_secreta'  # Chave secreta para uso de sessões

@app.route('/', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def process_login():
    # Acessando dados do formulário
    username = request.form.get('username')
    password = request.form.get('password')

    if login_validator.validar_credenciais(username, password):
        # Se as credenciais estiverem corretas
        token = str(uuid.uuid4())
        session['token'] = token
        session.modified = True
        session['logged_in'] = True
        # Redireciona o usuário para a página do dashboard
        return redirect(url_for('dashboard'))
    else:
        # Pode usar flash() para enviar mensagens de erro de volta para o template
        flash("E-mail ou senha incorretos.", "error")
        # Redireciona de volta para a página de login ou renderiza novamente o template de login com mensagem de erro
        return redirect(url_for('login'))  # ou return render_template('login.html', error="E-mail ou senha incorretos.")

@app.route('/dashboard')
def dashboard():
    if 'token' not in session:
        return redirect(url_for('login'))

    if not token_valido(session['token']):
        return redirect(url_for('login'))

    deposit_amount, amount_received, positive_balance, payment_percentage = get_dashboard_data()

    # Aplicar a formatação aos valores
    deposit_amount = formatar_como_real(deposit_amount)
    amount_received = formatar_como_real(amount_received)
    positive_balance = formatar_como_real(positive_balance)
    payment_percentage = formatar_como_real(payment_percentage)

    # Passar valores para o template usando argumentos nomeados
    return render_template(
        'dashboard.html',
        deposit_amount=deposit_amount,
        amount_received=amount_received,
        positive_balance=positive_balance,
        payment_percentage=payment_percentage
    )

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'token' not in session or not token_valido(session['token']):
        return redirect(url_for('login'))

    if request.method == 'POST':
        full_name = request.form['full_name']
        cpf = request.form['cpf']
        birth_date = request.form['birth_date']
        address = request.form['address']
        deposit_amount = request.form['deposit_amount']
        amount_received = request.form['amount_received']
        positive_balance = request.form['positive_balance']
        payment_percentage = request.form['payment_percentage']
        betting_house = request.form['betting_house']
        print('deposit_amount:', deposit_amount)

        criar_registro(full_name, cpf, birth_date, address, deposit_amount, amount_received, positive_balance, payment_percentage, betting_house)

        flash('Cadastro realizado com sucesso!', 'success')
        return redirect('/list')
    return render_template('register.html')

@app.route('/list')
def list_people():
    if 'token' not in session or not token_valido(session['token']):
        # Se o token não estiver presente ou não for válido, redirecione para a página de login
        return redirect(url_for('login'))

    cadastros = obter_cadastros()

    if not cadastros:
        return render_template('list.html', people=[])
    formatted_cadastros = []
    for cadastro in cadastros:
        formatted_cadastro = list(cadastro)
        formatted_cadastro[3] = cadastro[3].strftime("%d/%m/%Y")
        formatted_cadastro[5] = f'R$ {formatted_cadastro[5]:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.') if formatted_cadastro[5] else 'R$ 0,00'
        formatted_cadastro[6] = f'R$ {formatted_cadastro[6]:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.') if formatted_cadastro[6] else 'R$ 0,00'
        formatted_cadastro[7] = f'R$ {formatted_cadastro[7]:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.') if formatted_cadastro[7] else 'R$ 0,00'
        formatted_cadastro[8] = f'R$ {formatted_cadastro[8]:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.') if formatted_cadastro[8] else 'R$ 0,00'
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
        deposit_amount = request.form['deposit_amount']
        amount_received = request.form['amount_received']
        positive_balance = request.form['positive_balance']
        payment_percentage = request.form['payment_percentage']
        betting_house = request.form['betting_house']


        # Chame a função para atualizar a pessoa no banco de dados
        if update_person(id, name, cpf, birth_date, address, deposit_amount,amount_received, positive_balance, payment_percentage, betting_house):
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
    db_config = DatabaseConfig.get_db_config()
    conexao = psycopg2.connect(**db_config)
    cursor = conexao.cursor()

    sql_delete_query = """ DELETE FROM register WHERE id = %s """
    sql_delete2_query = """ DELETE FROM withdrawal_history WHERE register_id = %s """

    cursor.execute(sql_delete_query, (str(id),))
    cursor.execute(sql_delete2_query, (str(id),))

    conexao.commit()  # Confirmar a transação
    cursor.close()
    conexao.close()  # Fechar a conexão

    # Redirecionar para outra página, por exemplo, a lista de cadastros
    get_dashboard_data()
    return redirect(url_for('list_people'))

@app.route('/verify_email', methods=['POST'])
def api_verify_email():
    data = request.get_json()  # Obtém os dados enviados na solicitação
    email = data.get('email')

    if email:
        existe = verificar_email_usuario(email)  # Substitua pela sua função que verifica o email
        if existe:
            session['reset_email'] = email  # Armazena o email na sessão
            return jsonify({'exists': True})
        else:
            return jsonify({'exists': False})
    else:
        return jsonify({'error': 'E-mail não fornecido'}), 400

@app.route('/change_password')
def change_password():
    return render_template('change_password.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    # Garante que o email foi armazenado na sessão
    email = session.get('reset_email')
    if not email:
        return render_template('error.html', error="Sessão expirada ou inválida.")

    if request.method == 'POST':
        codigo = request.form.get('codigo')
        nova_senha = request.form.get('novaSenha')

        # Aqui você chamaria suas funções para validar o código e alterar a senha
        if validar_codigo(email, codigo) and alterar_senha(email, nova_senha):
            session.pop('reset_email', None)  # Limpa o email da sessão após o uso
            return redirect(url_for('login', message="Senha alterada com sucesso!"))
        else:
            return render_template('reset_password.html', error="Código inválido ou expirado ou não foi possível alterar a senha.")
    else:
        # Para solicitações GET, simplesmente mostra o formulário de redefinição
        return render_template('reset_password.html')

@app.route('/account_management')
def account_management():
    if 'token' not in session or not token_valido(session['token']):
        return redirect(url_for('login'))

    raw_accounts = gerenciamento_de_contas()  # Esta função retorna os dados necessários
    print('Raw accounts data:', raw_accounts)

    # Lista para armazenar os cadastros ajustados
    adjusted_accounts = []

    for account in raw_accounts:
        # Extrai os dados de cada conta
        account_id, name, betting_house, owner_value = account

        owner_value = float(owner_value)

        # Adiciona o cadastro ajustado à lista, usando um dicionário para facilitar o acesso no template
        adjusted_accounts.append({
            'id': account_id,
            'name': name,
            'betting_house': betting_house if betting_house else 'N/A',  # Trata o caso de betting_house ser None
            'saldo': f'R$ {owner_value:,.2f}'.replace('.', 'v').replace(',', '.').replace('v', ',')
        })

    # Passa a lista de cadastros ajustados para o template
    return render_template('withdrawal_history.html', accounts=adjusted_accounts)

@app.route('/realizar-saque', methods=['POST'])
def saque():
    register_id = request.form['register_id']
    saque_amount_str = request.form['saque_amount']
    saque_amount_str = saque_amount_str.replace(".", "")
    saque_amount_str = saque_amount_str.replace(",", ".")

    saque_amount = float(saque_amount_str)
    try:
        realizar_saque(register_id, saque_amount)
        flash("Saque realizado com sucesso.", "success")
    except Exception as e:
        flash(str(e), "error")
    
    return redirect(url_for('account_management'))

@app.route('/get-withdraw-history', methods=['GET'])
def get_withdraw_history():
    account_id = request.args.get('account_id')
    historico = buscar_historico_saques(account_id)
    return jsonify(historico)

@app.route('/generate_report', methods=['POST'])
def gerar_relatorio():
    # Obtém o nome do relatório a partir dos dados do formulário
    nome_relatorio = request.form.get('reportName')
    nome_arquivo = f"{nome_relatorio}.xlsx"

    # Caminho para a pasta de Downloads no Windows
    caminho_downloads = os.path.join(os.getenv('USERPROFILE'), 'Downloads')
    nome_arquivo_completo = os.path.join(caminho_downloads, nome_arquivo)

    # Chama a função para gerar o relatório, passando o nome do arquivo como argumento
    tabela_para_excel(nome_arquivo_completo)

    # Tenta enviar o arquivo gerado para download
    try:
        return send_file(nome_arquivo_completo, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/report')
def configuracao_relatorio():

    return render_template('report.html')

def formatar_como_real(valor):
    if valor is None or valor == 0:
        return 'R$ 0,00'
    else:
        return 'R$ {:,.2f}'.format(valor).replace(',', 'v').replace('.', ',').replace('v', '.')

if __name__ == '__main__':
    app.run(debug=True)
