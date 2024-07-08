from flask import Flask, request, jsonify, render_template, request
from Classes.classes import  Conta, Conta_conjunta, Pessoa_fisica, Pessoa_juridica
from banco import Banco
import requests
import os


app = Flask(__name__, template_folder='templates', static_folder='static')

NUMERO_BANCO = os.getenv('NUMERO_BANCO', '1')

host = "0.0.0.0"
#IP_BANCO1 = os.getenv('IP_BANCO1', "localhost")
IP_BANCO1 = os.getenv('IP_BANCO1', "0.0.0.0")
NOME_BANCO1 = os.getenv('NOME_BANCO1', 'Banco 1')
PORTA_BANCO1 = os.getenv('PORTA_BANCO1', '2525')
URL_BANCO1 = f"http://{IP_BANCO1}:{PORTA_BANCO1}"

#IP_BANCO2 = os.getenv('IP_BANCO2', "localhost")
IP_BANCO2 = os.getenv('IP_BANCO2', "0.0.0.0")
NOME_BANCO2 = os.getenv('NOME_BANCO2', 'Banco 2') 
PORTA_BANCO2 = os.getenv('PORTA_BANCO2', '2527')
URL_BANCO2 = f"http://{IP_BANCO2}:{PORTA_BANCO2}"

#IP_BANCO3 = os.getenv('IP_BANCO3', "localhost")
IP_BANCO3 = os.getenv('IP_BANCO3', "0.0.0.0")
NOME_BANCO3 = os.getenv('NOME_BANCO3', 'Banco 3') 
PORTA_BANCO3 = os.getenv('PORTA_BANCO3', '2529')
URL_BANCO3 = f"http://{IP_BANCO3}:{PORTA_BANCO3}"

BANCOS = {
    NOME_BANCO1: {
        'url': URL_BANCO1
    },
    NOME_BANCO2: {
        'url': URL_BANCO2
    },
    NOME_BANCO3: {
        'url': URL_BANCO3
    }
}

banco = Banco(eval(f"NOME_BANCO{NUMERO_BANCO}"), BANCOS)

#Rota responsável por cadastrar uma pessoa_fisica
@app.route('/cadastro_pessoa_fisica', methods=['POST'])
def cadastrar_conta_pessoa_fisica():
    data = request.get_json()
    nome = data.get('nome', '')
    cpf = data.get('cpf', '')
    senha = data.get('senha', '')

    if not nome or not cpf or not senha:
        return jsonify({'message': 'Nome, CPF e senha são obrigatórios'}), 400

    if banco.busca_cliente(cpf): 
        return jsonify({'message': "Cliente já cadastrado"}), 400

    try: 
        pessoa_fisica = Pessoa_fisica(nome, cpf, senha)
        conta_pessoa_fisica = Conta(banco.numero, banco.nome, pessoa_fisica)
        pessoa_fisica.adicionar_conta(conta_pessoa_fisica)
        banco.cadastro_cliente(pessoa_fisica) 
        banco.atualizar_numero_contas()
        return jsonify({'message': 'Conta Para Pessoa fisica criada com sucesso', 'cpf': pessoa_fisica.identificador, 'Numero conta': conta_pessoa_fisica.numero
                        ,'Nome do Banco': conta_pessoa_fisica.nome_banco}), 201
    
    except Exception as e: 
        return jsonify({'message': f'Falha ao criar pessoa fisica, Exceção:{e}'}), 500

#Rota responsável por cadastrar uma pessoa_juridica
@app.route('/cadastro_pessoa_juridica', methods=['POST'])
def cadastrar_conta_pessoa_juridica():
    data = request.get_json()
    nome = data.get('nome', '')
    cnpj = data.get('cnpj', '')
    senha = data.get('senha', '')

    if not nome or not cnpj or not senha:
        return jsonify({'message': 'Nome, CNPJ e senha são obrigatórios'}), 400
    
    if banco.busca_cliente(cnpj): 
        return jsonify({'message': "Cliente já cadastrado"}), 400

    try:
        pessoa_juridica = Pessoa_juridica(nome, cnpj, senha)
        conta_pessoa_juridica = Conta(banco.numero, banco.nome, pessoa_juridica)
        pessoa_juridica.adicionar_conta(conta_pessoa_juridica)
        banco.cadastro_cliente(pessoa_juridica)
        banco.atualizar_numero_contas()
        return jsonify({'message': 'Conta Para Pessoa Juridica criada com sucesso', 'cnpj': pessoa_juridica.identificador , 'Numero conta': conta_pessoa_juridica.numero
                        ,'Nome do Banco': conta_pessoa_juridica.nome_banco}), 201
    except Exception as e: 
        return jsonify({'message': f'Falha ao criar pessoa juridica, Exceção:{e}'}), 500

#Rota responsável por cadastrar uma conta conjunta
@app.route('/cadastro_conta_conjunta', methods=['POST'])
def cadastrar_conta_conjunta():
    data = request.get_json()
    identificador1 = data.get('identificador1', '')
    identificador2 = data.get('identificador2', '')
    senha = data.get('senha', '')

    if not identificador1 or not identificador2 or not senha:
        return jsonify({'message': 'Identificadores e senha são obrigatórios'}), 400

    try:
        cliente1 = banco.busca_cliente(identificador1)
        cliente2 = banco.busca_cliente(identificador2)

        if not cliente1 or not cliente2:
            return jsonify({'message': 'Um ou ambos os clientes não foram encontrados'}), 404

        conta_conjunta = Conta_conjunta(banco.numero, banco.nome, [cliente1, cliente2])
        cliente1.adicionar_conta(conta_conjunta)
        cliente2.adicionar_conta(conta_conjunta)
        banco.atualizar_numero_contas()
        
        return jsonify({
            'message': 'Conta conjunta criada com sucesso',
            'identificadores': [cliente1.identificador, cliente2.identificador],
            'numero_conta': conta_conjunta.numero,
            'nome_banco': conta_conjunta.nome_banco
        }), 201
    except Exception as e:
        return jsonify({'message': f'Falha ao criar conta conjunta, Exceção: {e}'}), 500

#Rota responsável por fazer o login 
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    identificador = data.get('identificador', '')
    senha = data.get('senha', '')

    if not identificador or not senha:
        return jsonify({'message': 'Identificador (CPF/CNPJ) e senha são obrigatórios'}), 400

    cliente = banco.logar_cliente(identificador, senha)
    if cliente:
        return jsonify({'message': 'Login bem-sucedido', 'identificador': cliente.identificador, 'nome': cliente.nome}), 200
    else:
        return jsonify({'message': 'Identificador ou senha incorretos'}), 401

#Rota responsável por fazer o logout
@app.route('/logout', methods =['POST'])
def logout(): 
    banco.deslogar_cliente()
    return jsonify({'message': "Cliente deslogado com sucesso"}), 200

#Rota responsável por obter todas as contas de um cliente em todos os bancos
@app.route('/contas_cliente/<identificador>', methods=['GET'])
def contas_cliente(identificador):

    if not identificador:
        return jsonify({'message': 'Identificador (CPF/CNPJ) é obrigatório'}), 400

    cliente = banco.busca_cliente(identificador)
    if not cliente:
        return jsonify({'message': 'Cliente não encontrado'}), 404

    contas_cliente = banco.busca_contas(identificador)
    if not contas_cliente:
        return jsonify({'message': 'Cliente não possui contas cadastradas'}), 404

    contas_info = []
    
    for nome_banco, info in banco.bancos.items():
        if nome_banco == banco.nome: 
            for conta in contas_cliente:
                contas_info.append({
                    'numero_conta': conta.numero,
                    'saldo': conta.saldo,
                    'clientes': [cliente.nome for cliente in conta.clientes],
                    'historico_transacoes': conta.historico.transacoes,
                    'nome_banco': conta.nome_banco
                    })
        else: 
            try:
                url = info['url']
                response = requests.get(f'{url}/get_contas/{identificador}', )
                if response.status_code == 200:
                    dados = response.json()
                    lista_contas = dados["contas"] 
                    contas_info = contas_info + lista_contas
                elif response.status_code == 500: 
                    print(f'Nenhuma conta encontrada no banco {nome_banco}')
            except Exception as e: 
                print(f"Exceção ocorreu")
    

    return jsonify({'contas': contas_info}), 200 

#Rota responsável por obter todas as contas de um cliente em um banco
@app.route('/get_contas/<identificador>', methods=['GET'])
def get_contas(identificador):
    if not identificador:
        return jsonify({'message': 'Identificador (CPF/CNPJ) é obrigatório'}), 400

    cliente = banco.busca_cliente(identificador)
    if not cliente:
        return jsonify({'message': 'Cliente não encontrado'}), 500

    contas_cliente = banco.busca_contas(identificador)
    if not contas_cliente:
        return jsonify({'message': 'Cliente não possui contas cadastradas'}), 500

    contas_info = []

    if contas_cliente: 
        for conta in contas_cliente:
                contas_info.append({
                    'numero_conta': conta.numero,
                    'saldo': conta.saldo,
                    'clientes': [cliente.nome for cliente in conta.clientes],
                    'historico_transacoes': conta.historico.transacoes,
                    'nome_banco': conta.nome_banco
                    })
        return jsonify({ 'contas': contas_info }), 200 
    else: 
        return jsonify({ 'message': 'Conta não encontrada' }), 500

#Rota responsável por obter uma conta de um cliente em um banco 
@app.route('/get_conta/<nome_banco>/<numero_conta>', methods=['GET'])
def get_conta(nome_banco, numero_conta):
    if nome_banco is None or (numero_conta is None):
        return jsonify({'message': 'Nome do banco, número da conta e são obrigatórios'}), 500

    numero_conta = int(numero_conta)

    if nome_banco == banco.nome:
        conta = banco.busca_conta(numero_conta)
        
        if conta: 
            dicionario_conta = {
                'numero_conta': conta.numero,
                'saldo': conta.saldo,
                'clientes': [cliente.nome for cliente in conta.clientes],
                'historico_transacoes': conta.historico.transacoes,
                'nome_banco': conta.nome_banco
            }
            return jsonify({ 'conta': dicionario_conta }), 200 
        else: 
            return jsonify({ 'message': 'Conta não encontrada' }), 500
    else: 
        if nome_banco == NOME_BANCO1: 
            return banco.busca_conta_externa(URL_BANCO1, nome_banco, numero_conta)
        elif nome_banco == NOME_BANCO2: 
            return banco.busca_conta_externa(URL_BANCO2, nome_banco, numero_conta)
        elif nome_banco == NOME_BANCO3: 
            return banco.busca_conta_externa(URL_BANCO3, nome_banco, numero_conta)
        else: 
            return jsonify({'message': 'Banco inexistente'}), 500

#Rota responsavel por obter o identificador do cliente logado 
@app.route('/get_identificador', methods=['GET'])
def get_identificador(): 
    if banco.cliente_logado != None: 
        return jsonify({'identificador': f'{banco.cliente_logado.identificador}'}), 200
    else: 
        return jsonify({'message': 'Não há cliente logado'}), 500

#Rota responsavel por obter o nome do banco 
@app.route('/get_nome_banco', methods=['GET'])
def get_nome_banco(): 
    return jsonify({'nome_banco': f'{banco.nome}'}), 200

#Rota responsavél por realizar um deposito em qualquer conta que um banco possua
@app.route('/deposito', methods=['POST'])
def deposito():
    data = request.get_json()
    numero_conta = data.get('numero_conta', '')
    nome_banco = data.get('nome_banco', '')
    valor = data.get('valor', 0)

    if nome_banco is None or (numero_conta is None) or valor <= 0:
        return jsonify({'message': 'Nome do banco, número da conta e valor válido são obrigatórios'}), 500

    numero_conta = int(numero_conta)
    if nome_banco == banco.nome:
        conta = banco.busca_conta(numero_conta)
        if not conta:
            return jsonify({'message': 'Conta não encontrada'}), 500
        try:
            conta.lock.acquire(blocking=True)
            sucesso, mensagem = conta.depositar(valor)
            if sucesso:
                conta.lock.release()
                return jsonify({'message': mensagem}), 200
            else:
                conta.lock.release()
                return jsonify({'message': mensagem}), 500
        except Exception as e:
            conta.lock.release()
            print(f'Erro durante a transação: {str(e)}')
            return jsonify({'message': "Conta em outra transação no momento, aguarde e tente novamente"}), 500

    else: 
        if nome_banco == NOME_BANCO1: 
            return banco.deposito_outro_banco(URL_BANCO1, numero_conta,nome_banco, valor)
        elif nome_banco == NOME_BANCO2: 
            return banco.deposito_outro_banco(URL_BANCO2, numero_conta,nome_banco, valor)
        elif nome_banco == NOME_BANCO3: 
            return banco.deposito_outro_banco(URL_BANCO3, numero_conta,nome_banco, valor)
        else: 
            return jsonify({'message': 'Banco inexistente'}), 500

#Rota responsável por realizar um saque em um banco que um cliente esteja logado
@app.route('/saque', methods=['POST']) 
def saque(): 
    data = request.get_json()
    numero_conta = data.get('numero_conta', '')
    valor = data.get('valor', 0)
    valor = float(valor)
    if (numero_conta is None) or valor <= 0:
        return jsonify({'message': 'Valor válido é obrigatório'}), 500
    
    numero_conta = int(numero_conta) 

    conta = banco.busca_conta(numero_conta)
    if not conta:
        return jsonify({'message': 'Conta não encontrada'}), 500
    try:
        conta.lock.acquire(blocking=True)
        sucesso, mensagem = conta.retirar(valor, banco.cliente_logado)
        if sucesso:
            conta.lock.release()
            return jsonify({'message': mensagem}), 200
        else:
            conta.lock.release()
            return jsonify({'message': mensagem}), 500
    except Exception as e:
        conta.lock.release()
        print(f'Erro durante a transação: {str(e)}')
        return jsonify({'message': "Conta em outra transação no momento, aguarde e tente novamente"}), 500

#Rota responsavel por preparar transferencia de uma conta de um banco externo
@app.route('/preparar_transferencia', methods=['POST'])
def preparar_transferencia(): 
    data = request.get_json()
    numero_conta = data.get('numero_conta', '')
    nome_banco = data.get('nome_banco', '')
    tipo = data.get('tipo', '')
    valor = data.get('valor', 0)

    if nome_banco is None or (numero_conta is None) or tipo is None or valor <= 0 or valor is None:
        return jsonify({'message': 'Nome do banco, número da conta,  tipo de preparação e valor válido são obrigatórios'}), 500
    
    numero_conta = int(numero_conta) 

    if nome_banco == banco.nome: 
        conta = banco.busca_conta(numero_conta)
        if not conta:
            return jsonify({'message': 'Conta não encontrada'}), 500
        try:
            conta.lock.acquire(blocking=True)
            sucesso, mensagem = conta.preparar_transferencia(valor, tipo)
            if sucesso:
                conta.lock.release()
                return jsonify({'message': mensagem}), 200
            else:
                conta.lock.release()
                return jsonify({'message': mensagem}), 500
        except Exception as e:
            conta.lock.release()
            print(f'Erro durante a transação: {str(e)}')
            return jsonify({'message': "Conta em outra transação no momento, aguarde e tente novamente"}), 500
    else: 
        if nome_banco == NOME_BANCO1: 
            return banco.preparar_conta_externa(URL_BANCO1, numero_conta, nome_banco, valor, tipo)
        elif nome_banco == NOME_BANCO2: 
            return banco.preparar_conta_externa(URL_BANCO2, numero_conta,nome_banco, valor, tipo)
        elif nome_banco == NOME_BANCO3: 
            return banco.preparar_conta_externa(URL_BANCO3, numero_conta,nome_banco, valor, tipo)
        else: 
            return jsonify({'message': 'Banco inexistente'}), 500

#Rota responsavel por realizar a confirmação de uma conta de um banco externo
@app.route('/confirmar_transferencia', methods=['POST'])
def confirmar_transferencia(): 
    data = request.get_json()
    numero_conta = data.get('numero_conta', '')
    nome_banco = data.get('nome_banco', '')
    tipo = data.get('tipo', '')
    valor = data.get('valor', 0)

    if nome_banco is None or (numero_conta is None) or tipo is None or valor <= 0:
        return jsonify({'message': 'Nome do banco, número da conta,  tipo de preparação e valor válido são obrigatórios'}), 500
    
    numero_conta = int(numero_conta) 

    if nome_banco == banco.nome: 
        conta = banco.busca_conta(numero_conta)
        if not conta:
            return jsonify({'message': 'Conta não encontrada'}), 500
        try:
            conta.lock.acquire(blocking=True)
            sucesso, mensagem = conta.confirmar_transferencia(valor, nome_banco, numero_conta, tipo)
            if sucesso:
                conta.lock.release()
                return jsonify({'message': mensagem}), 200
            else:
                conta.lock.release()
                return jsonify({'message': mensagem}), 500
        except Exception as e:
            conta.lock.release()
            print(f'Erro durante a transação: {str(e)}')
            return jsonify({'message': "Conta em outra transação no momento, aguarde e tente novamente"}), 500
    else: 
        if nome_banco == NOME_BANCO1: 
            return banco.confirmacao_conta_externa(URL_BANCO1, numero_conta, nome_banco, valor, tipo)
        elif nome_banco == NOME_BANCO2: 
            return banco.confirmacao_conta_externa(URL_BANCO2, numero_conta, nome_banco, valor, tipo)
        elif nome_banco == NOME_BANCO3: 
            return banco.confirmacao_conta_externa(URL_BANCO3, numero_conta, nome_banco, valor, tipo)
        else: 
            return jsonify({'message': 'Banco inexistente'}), 500

#Rota reponsavel por desfazer alterações em uma conta de um bano externo
@app.route('/desfazer_transferencia', methods=['POST'])
def desfazer_transferencia(): 
    data = request.get_json()
    numero_conta = data.get('numero_conta', '')
    nome_banco = data.get('nome_banco', '')
    tipo = data.get('tipo', '')
    valor = data.get('valor', 0)

    if nome_banco is None or (numero_conta is None) or tipo is None or valor <= 0:
        return jsonify({'message': 'Nome do banco, número da conta,  tipo de preparação e valor válido são obrigatórios'}), 500
    
    numero_conta = int(numero_conta) 

    if nome_banco == banco.nome: 
        conta = banco.busca_conta(numero_conta)
        if not conta:
            return jsonify({'message': 'Conta não encontrada'}), 500
        try:
            conta.lock.acquire(blocking=True)
            sucesso, mensagem = conta.desfazer_transferencia(tipo)
            if sucesso:
                conta.lock.release()
                return jsonify({'message': mensagem}), 200
            else:
                conta.lock.release()
                return jsonify({'message': mensagem}), 500
        except Exception as e:
            conta.lock.release()
            print(f'Erro durante a transação: {str(e)}')
            return jsonify({'message': f"Exceção {e}"}), 500
    else: 
        if nome_banco == NOME_BANCO1: 
            return banco.desfazer_conta_externa(URL_BANCO1, numero_conta, nome_banco, valor, tipo)
        elif nome_banco == NOME_BANCO2: 
            return banco.desfazer_conta_externa(URL_BANCO2, numero_conta, nome_banco, valor, tipo)
        elif nome_banco == NOME_BANCO3: 
            return banco.desfazer_conta_externa(URL_BANCO3, numero_conta, nome_banco, valor, tipo)
        else: 
            return jsonify({'message': 'Banco inexistente'}), 500

#Rota reposnsavel por realizar a transferencia
@app.route('/transferir', methods=['POST'])
def transferir():
    data = request.json
    nome_banco_destino = data.get('nome_banco_destino')
    numero_conta_destino = data.get('numero_conta_destino')
    valor_conta_destino = data.get('valor_conta_destino', 0)
    transferencias = data.get('transferencias')  # Lista de dicionários com as transferências

    # Fase 1: Preparação
    preparados = True
    preparacao = []

    #Preparação das contas que irão ter dinheiro retirado
    preparados, preparacao, mensagem = banco.preparacao_contas(transferencias, preparados, preparacao)
    
    if not preparados:
        sucesso = True
        sucesso, msg = banco.desfazer_alterações(preparacao, sucesso)
        return jsonify({"success": False, "message": mensagem}), 500

    #Confirmação e commit das operações
    sucesso_confirmacao = True 
    preparacao.append((nome_banco_destino, numero_conta_destino, valor_conta_destino, "deposito"))
    sucesso_confirmacao, mensagem  = banco.confirmacao_contas(preparacao, sucesso_confirmacao)

    if sucesso_confirmacao:
        return jsonify({"success": True, "message": "Transferência realizada com sucesso"}), 200
    else:
        # Se houve falha, desfazer as operações preparadas
        sucesso = True
        sucesso, msg = banco.desfazer_alterações(preparacao, sucesso)
        return jsonify({"success": False, "message": mensagem}), 500


'''
====================================================================================+
ROTAS QUE VÃO SER UTILIZADAS PARA USAR O FRONTEND
====================================================================================+
'''


#Rota para pagina de login
@app.route('/')
def login_page():
    return render_template('login.html')

#Rota para a página de Home
@app.route('/home')
def home_page():
    try:
        url = eval(f"URL_BANCO{NUMERO_BANCO}")

        identificador = banco.cliente_logado.identificador
        # 2. Se tiver identificador, obter as informações das contas do cliente
        contas_info = []
        if identificador:
            contas_response = requests.get(f'{url}/contas_cliente/{identificador}')
            if contas_response.status_code == 200:
                contas_info = contas_response.json()['contas']
            else:
                # Lida com o caso em que não foi possível obter as contas
                contas_info = []

        # 3. Obter o nome do banco através da rota /get_nome_banco
        nome_banco_response = requests.get(f'{url}/get_nome_banco')  # Substitua pelo URL correto
        if nome_banco_response.status_code == 200:
            nome_banco = nome_banco_response.json()['nome_banco']
        else:
            nome_banco = 'Banco Desconhecido'

    except Exception as e:
        print(f'Erro ao obter informações: {str(e)}')
        nome_banco = 'Banco Desconhecido'
        contas_info = []

    # 4. Renderizar o template home.html passando as informações obtidas
    return render_template('home.html', nome_banco=nome_banco, contas=contas_info)

#Rota para a pagina de cadastro
@app.route('/cadastro')
def cadastro_page():
    return render_template('cadastro.html') 

#Rota para renderizar a página de depósito
@app.route('/deposito_page')
def deposito_page():
    return render_template('deposito.html', nome_banco=banco.nome)  # Renderiza o template HTML para o depósito

#Rota para acessar a página de saque
@app.route('/saque_page')
def saque_page():
    # Renderiza o template saque.html (crie este template com os campos necessários)
    return render_template('saque.html')

# Rota para a página de Transferência
@app.route('/transferencia_page')
def transferencia_page():
    try:
        url = eval(f"URL_BANCO{NUMERO_BANCO}")

        identificador = banco.cliente_logado.identificador
        contas_info = []

        # 1. Se tiver identificador, obter as informações das contas do cliente
        if identificador:
            contas_response = requests.get(f'{url}/contas_cliente/{identificador}')
            if contas_response.status_code == 200:
                contas_info = contas_response.json()['contas']
            else:
                # Lida com o caso em que não foi possível obter as contas
                contas_info = []

        # 2. Obter o nome do banco através da rota /get_nome_banco
        nome_banco_response = requests.get(f'{url}/get_nome_banco')
        if nome_banco_response.status_code == 200:
            nome_banco = nome_banco_response.json()['nome_banco']
        else:
            nome_banco = 'Banco Desconhecido'

    except Exception as e:
        print(f'Erro ao obter informações: {str(e)}')
        nome_banco = 'Banco Desconhecido'
        contas_info = []

    # 3. Renderizar o template transferencia.html passando as informações obtidas
    return render_template('transferencia.html', nome_banco=nome_banco, contas=contas_info)



if __name__ == '__main__':
    app.run(host=eval(f"IP_BANCO{NUMERO_BANCO}"), port=eval(f"PORTA_BANCO{NUMERO_BANCO}"))