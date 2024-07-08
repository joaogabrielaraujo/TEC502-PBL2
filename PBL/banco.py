from flask import Flask, request, jsonify, render_template, request, redirect, url_for, flash
from Classes.classes import * 
import requests

class Banco: 

    def __init__(self, nome, bancos): 
        self.nome = nome 
        self._clientes = [] 
        self._numero = 0 
        self._cliente_logado = None
        self.bancos = bancos

    #Função responsável por verificar na lista de cliente do banco se existe o cliente passado 
    def busca_cliente(self, identificador):
        for cliente in self._clientes: 
            if cliente.identificador == identificador: 
                return cliente 
        return False
    
    #Função que recebe um cpf ou cnpj e retorna todas as contas atreladas ao cliente especifico
    def busca_contas(self,identificador): 
        if(self._clientes): 
            for cliente in self._clientes:
                 if cliente.identificador == identificador: 
                     return cliente.contas
        return False
    
    #Função que recebe o numero de uma conta e retorna uma conta que exista com o mesmo numero
    def busca_conta(self,numero): 
        try:
            if(self._clientes): 
                for cliente in self._clientes:
                    for conta in cliente.contas: 
                        if conta.numero == numero: 
                            return conta
            return False
        except Exception as e:
            print(f"Exceção: {e}")
            return False

    #Função responsável por cadastrar um cliente
    def cadastro_cliente(self, cliente):
        self._clientes.append(cliente)
        return True

    #Função responsável por criar um conta
    def criar_conta(self, conta, identificador): 
        cliente = self.busca_cliente(identificador)

        if cliente: 
            cliente.adicionar_conta(conta)
            return True
        
        return False

    #Função responsável por atualizar o número de contas
    def atualizar_numero_contas(self): 
        self._numero += 1

    #Função para logar cliente
    def logar_cliente(self, identificador, senha): 
        cliente = self.busca_cliente(identificador)  
        if cliente and cliente.senha == senha: 
            self.cliente_logado = cliente
            return cliente
        else: 
            return False

    #Função para deslogar cliente
    def deslogar_cliente(self): 
        self._cliente_logado = None

    #Função para buscar URL do banco a patir do nome
    def buscar_url(self, nome_banco): 
        bancos = self.bancos
        if nome_banco in bancos:
            return bancos[nome_banco]
        else:
            return None  

    #Função para fazer a requisição de deposito par um banco externo
    def deposito_outro_banco(self, url, numero_conta, nome_banco, valor): 
        try:
            dados = {'numero_conta':numero_conta, 'nome_banco': nome_banco, 'valor': valor}
            response = requests.post(f'{url}/deposito', json=dados)
            if response.status_code == 200:
                return jsonify({'message': response.json().get('message')}), 200
            elif response.status_code == 500: 
                return jsonify({'message': response.json().get('message')}), 500
        except Exception as e: 
            print(f"Exceção: {e}")

    #Função para pegar uma conta de um banco externo para rota externa
    def busca_conta_externa(self, url, nome_banco, numero_conta): 
        try:
            response = requests.get(f'{url}/get_conta/{nome_banco}/{numero_conta}')
            if response.status_code == 200:
                return jsonify( {"conta": response.json().get('conta')} ), 200
            elif response.status_code == 500: 
                return jsonify({'message': response.json().get('message')}), 500
        except Exception as e: 
            print(f"Exceção: {e}")
    
    #Função para pegar uma conta de um banco externo para rota interna
    def busca_conta_externa_interna(self, url, nome_banco, numero_conta): 
        try:
            response = requests.get(f'{url}/get_conta/{nome_banco}/{numero_conta}')
            if response.status_code == 200:
                return response
            elif response.status_code == 500: 
                return response
        except Exception as e: 
            print(f"Exceção: {e}")

    #Função que recebe contas e as prepara para realizar uma transferência
    def preparacao_contas(self, transferencias, preparados, preparacao):
        for transferencia in transferencias:
            numero_conta_origem = transferencia['numero_conta_origem']
            nome_banco_origem = transferencia['nome_banco_origem']
            valor = transferencia['valor'] 
            valor = float(valor)

            # Encontrar a conta de origem
            if nome_banco_origem == self.nome:
                conta_origem = self.busca_conta(numero_conta_origem)
                if not conta_origem:
                    mensagem = "Conta não encontrada"
                    preparados = False
                    break
    
                # Preparar a transferência na conta de origem
                conta_origem.lock.acquire(blocking=True)
                preparados, mensagem = conta_origem.preparar_transferencia(valor, "saque")
                conta_origem.lock.release()
                if preparados:
                    preparacao.append((nome_banco_origem, numero_conta_origem, valor, "saque"))
            else: 
                for nome_banco, info in self.bancos.items(): 
                    if nome_banco == nome_banco_origem: 
                        response = self.busca_conta_externa_interna(info['url'],nome_banco_origem,numero_conta_origem)
                        if response.status_code == 200: 
                            response = self.preparar_conta_externa(info['url'],numero_conta_origem,nome_banco_origem,valor,"saque")  
                            if response.status_code == 200: 
                                mensagem = response.json().get('message')
                                preparacao.append((nome_banco_origem, numero_conta_origem, valor, 'saque'))
                            else: 
                                mensagem = response.json().get('message')
                                preparados = False 
                                break
                        else: 
                            mensagem = response.json().get('message')
                            preparados = False 
                            break
                if preparados == False: 
                    break 

        return preparados, preparacao, mensagem
    
    #Função que prepara uma conta de um banco externo 
    def preparar_conta_externa(self, url, numero_conta, nome_banco, valor, tipo):
        try:
            dados = {'numero_conta':numero_conta, 'nome_banco': nome_banco, 'valor': valor, 'tipo': tipo}
            response = requests.post(f'{url}/preparar_transferencia', json=dados)
            if response.status_code == 200:
                return response
            elif response.status_code == 500: 
                return response
                #return jsonify({'message': response.json().get('message')}), 500
        except Exception as e: 
            print(f"Exceção: {e}")

    #Função para realizar a confirmação de contas de para realizar transferencia  
    def confirmacao_contas(self, preparacao, sucesso_confirmacao):
        response = False
        for nome_banco_conta,numero_conta,valor, tipo in preparacao:
            if nome_banco_conta == self.nome:
                conta_origem = self.busca_conta(numero_conta)
                if not conta_origem:
                    mensagem = "Conta não encontrada"
                    sucesso_confirmacao = False 
                    break 
                conta_origem.lock.acquire(blocking=True)
                sucesso_confirmacao, mensagem = conta_origem.confirmar_transferencia(nome_banco_conta, numero_conta, valor, tipo)
                conta_origem.lock.release()
            else: 
                for nome_banco, info in self.bancos.items(): 
                    if nome_banco == nome_banco_conta: 
                        response = self.confirmacao_conta_externa(info['url'],numero_conta,nome_banco_conta,valor,tipo)  
                        if response.status_code == 200: 
                            mensagem = response.json().get('message')
                        else: 
                            mensagem = response.json().get('message')
                            sucesso_confirmacao = False 
                            break
                if response == False: 
                    mensagem = "Banco não encontrado"
                    sucesso_confirmacao = False 
                if sucesso_confirmacao == False: 
                    break 

        return sucesso_confirmacao, mensagem

    #Função para confirmar em uma conta de um banco externo 
    def confirmacao_conta_externa(self, url, numero_conta, nome_banco, valor, tipo):
        try:
            dados = {'numero_conta':numero_conta, 'nome_banco': nome_banco, 'valor': valor, 'tipo': tipo}
            response = requests.post(f'{url}/confirmar_transferencia', json=dados)
            if response.status_code == 200:
                return response
                #return jsonify({'message': response.json().get('message')}), 200
            elif response.status_code == 500: 
                return response
                #return jsonify({'message': response.json().get('message')}), 500
        except Exception as e: 
            print(f"Exceção: {e}")

    #Função para desfazer alterações feitas nas contas (Rollback)
    def desfazer_alterações(self, preparacao, sucesso): 
        if not preparacao: 
            mensagem = "Não existem contas a serem desfeitas"
        for nome_banco_conta,numero_conta, valor, tipo in preparacao:
            if nome_banco_conta == self.nome:
                conta_origem = self.busca_conta(numero_conta)
                if not conta_origem:
                    sucesso = False 
                    break 
                conta_origem.lock.acquire(blocking=True)
                sucesso, mensagem = conta_origem.desfazer_transferencia(tipo)
                conta_origem.lock.release()
            else: 
                for nome_banco, info in self.bancos.items(): 
                    if nome_banco == nome_banco_conta: 
                        response = self.desfazer_conta_externa(info['url'],numero_conta,nome_banco_conta,valor,tipo)  
                        if response.status_code == 200: 
                            mensagem = response.json().get('message')
                        else: 
                            mensagem = response.json().get('message')
                            sucesso = False 
                            break
                if sucesso == False: 
                    break 
        return sucesso, mensagem

    #Função responsavel por desfazer alterações em uma conta de um banco externo 
    def desfazer_conta_externa(self, url, numero_conta, nome_banco, valor, tipo):
        try:
            dados = {'numero_conta':numero_conta, 'nome_banco': nome_banco, 'valor': valor, 'tipo': tipo}
            response = requests.post(f'{url}/desfazer_transferencia', json=dados)
            if response.status_code == 200:
                return response
                #return jsonify({'message': response.json().get('message')}), 200
            elif response.status_code == 500:
                return response 
                #return jsonify({'message': response.json().get('message')}), 500
        except Exception as e: 
            print(f"Exceção: {e}")

    @property
    def clientes(self):
        return self._clientes
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def cliente_logado(self):
        return self._cliente_logado
    
    @cliente_logado.setter
    def cliente_logado(self, valor):
        self._cliente_logado = valor