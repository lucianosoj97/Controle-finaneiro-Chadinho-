from flask import session

def token_valido(token):
    # Verificar se o token está presente na sessão
    if 'token' not in session or session['token'] != token:
        return False

    # Aqui você pode adicionar lógica adicional para verificar a validade do token, como verificar se ele expirou
    # Se a validação for bem-sucedida, retorne True
    # Caso contrário, retorne False

    return True