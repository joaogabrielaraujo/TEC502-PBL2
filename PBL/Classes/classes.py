from datetime import datetime
import threading 

class Historico:
    def __init__(self, transacoes=None):
        self._transacoes = transacoes if transacoes else []
        self._codigo_transacao = 0

    def adicionar_transacao(self, transacao):
        self._transacoes.append(transacao)
        self._codigo_transacao += 1

    def remover_transacao(self, codigo): 
        for transacao in self._transacoes: 
            if transacao["codigo"] == codigo: 
                self._transacoes.remove(transacao)
                return None
                
    @property
    def transacoes(self):
        return self._transacoes
    
    @property
    def codigo_transacoes(self):
        return self._codigo_transacao

class ContaBase:
    def __init__(self, numero, nome_banco, clientes=None):
        self._nome_banco = nome_banco
        self._saldo = 0
        self._saldo_anterior = 0
        self._numero = numero
        self._clientes = clientes if clientes else []
        self.codigo_ultima_transacao = None
        self._historico = Historico()
        self.lock = threading.Lock()

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def clientes(self):
        return self._clientes

    @property
    def historico(self):
        return self._historico
    
    @property
    def nome_banco(self):
        return self._nome_banco

    #Função que deposita um valor em uma conta
    def depositar(self, valor):
        if valor <= 0:
            return False, 'Valor do depósito deve ser maior que zero'  # Retorna uma tupla com False e mensagem de erro
        self._saldo_anterior = self._saldo
        self._saldo += valor
        codigo_transacao = self._historico.codigo_transacoes
        self._historico.adicionar_transacao({
            "codigo": codigo_transacao,
            "tipo": "Deposito",
            "valor": valor, 
            "data": datetime.now().strftime('%d/%m/%Y %H:%M:%S'),

        })
        return True, f'Depósito de {valor} na conta {self._numero} realizado com sucesso'
    
    #Função que retira um valor em uma conta
    def retirar(self, valor, cliente_logado):
        if valor <= 0:
            return False, 'Valor do saque deve ser maior que zero'  # Retorna uma tupla com False e mensagem de erro
        if self._saldo < valor:
            return False, 'Saldo insuficiente para realizar o saque'  # Retorna uma tupla com False e mensagem de erro

        if cliente_logado == None: 
            return False, 'Realize o login para fazer o saque'

        tamanho_clientes = self.clientes 
        if tamanho_clientes == 1:
            if self.clientes[0].identificador  != cliente_logado.identificador: 
                return False, 'Cliente sem  autorização para realizar o saque' # Retorna uma tupla com False e mensagem de erro
        elif tamanho_clientes == 2: 
            if (self.clientes[0].identificador != cliente_logado.identificador) or (self.clientes[1].identificador != cliente_logado.identificador): 
                return False, 'Cliente sem  autorização para realizar o saque' # Retorna uma tupla com False e mensagem de erro
        
        self._saldo_anterior = self._saldo
        self._saldo -= valor
        codigo_transacao = self._historico.codigo_transacoes
        self._historico.adicionar_transacao({
            "codigo": codigo_transacao,
            "tipo": "Saque",
            "valor": valor, 
            "data": datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        })
        return True, f'Saque de {valor} realizado com sucesso'

    #Função que prepara uma conta para uma transferência
    def preparar_transferencia(self, valor, tipo):
        if tipo == 'saque':
            if self._saldo >= valor: 
                self._saldo_anterior = self._saldo 
                self._saldo -= valor
                return True, "Preparação feita com sucesso"
            else: 
                return False, "Preparação falhou, saldo insuficiente"
        return False, "Preparação falhou"

    #Função para confirmar a transferência
    def confirmar_transferencia(self,valor, nome_banco, numero_conta, tipo):
        codigo_transacao = self._historico.codigo_transacoes
        self.codigo_ultima_transacao = codigo_transacao
        if tipo == 'saque':
            self._historico.adicionar_transacao({
                "codigo": codigo_transacao,
                "tipo": f"Transferencia para {nome_banco} para conta de número: {numero_conta}",
                "valor": valor,
                "data": datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            })
            return True, "Confirmação feita com sucesso"
        elif tipo == 'deposito': 
            self._saldo_anterior = self._saldo 
            self._saldo += valor
            self._historico.adicionar_transacao({
                "codigo": codigo_transacao,
                "tipo": f"Transferencia recebida",
                "valor": valor,
                "data": datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            })
            return True, "Confirmação feita com sucesso" 
        else: 
            return False, "Confirmaçõa não foi possivel de ser feita"
    
    #Função para desfazer operações(Rollback)
    def desfazer_transferencia(self, tipo):
        if tipo == 'saque':
            valor = self._saldo_anterior - self._saldo
            self._saldo += valor
            if self.codigo_ultima_transacao != None:
                try:
                    codigo_transacao = self.codigo_ultima_transacao
                    self._historico.remover_transacao(codigo_transacao)
                except Exception as e: 
                    print(f'Exceção: {e}') 
            mensagem = "Sucesso em desfazer operação"
            return (True, mensagem)
        elif tipo == 'deposito':
            valor = self._saldo -  self._saldo_anterior
            self._saldo -= valor
            if self.codigo_ultima_transacao != None:
                codigo_transacao = self.codigo_ultima_transacao
                self._historico.remover_transacao(codigo_transacao)
            mensagem = "Sucesso em desfazer operação"
            return (True, mensagem) 
        mensagem = "Tipo especificado, incorreto"
        return (False, mensagem)


class Conta(ContaBase):
    def __init__(self, numero, nome_banco, cliente, **kw):
        super().__init__(numero, nome_banco, [cliente], **kw)

class Conta_conjunta(ContaBase):
    def __init__(self, numero, nome_banco, clientes, **kw):
        super().__init__(numero, nome_banco, clientes, **kw)

class Cliente:
    def __init__(self, nome, identificador, senha, contas=None):
        self._contas = contas if contas else []
        self._identificador = identificador
        self._nome = nome
        self._senha = senha

    def realizar_transacao(self, conta, transacao, **kw):
        transacao.registrar(conta)

    def adicionar_conta(self, conta, **kw):
        self._contas.append(conta)

    @property
    def contas(self):
        return self._contas

    @property
    def identificador(self):
        return self._identificador

    @property
    def nome(self):
        return self._nome

    @property
    def senha(self):
        return self._senha

class Pessoa_fisica(Cliente):
    def __init__(self, nome, cpf, senha, contas=None, **kw):
        super().__init__(nome, cpf, senha, contas, **kw)

class Pessoa_juridica(Cliente):
    def __init__(self, nome, cnpj, senha, contas=None, **kw):
        super().__init__(nome, cnpj, senha, contas, **kw)