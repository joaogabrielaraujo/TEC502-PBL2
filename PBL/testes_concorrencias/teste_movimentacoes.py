import requests
import concurrent.futures

# URLs das rotas
url_saque = 'http://127.0.0.1:2525/saque'
url_deposito = 'http://127.0.0.1:2525/deposito'

# Dados para os saques
data_saque1 = {
    'numero_conta': 0,
    'valor': 20
}

data_saque2 = {
    'numero_conta': 2,
    'valor': 10
}

# Dados para o depósito
data_deposito = {
    'numero_conta': '0',
    'nome_banco': 'Banco 1',
    'valor': 150
}

def make_request(url, data):
    response = requests.post(url, json=data)
    return response.json()

# Usando ThreadPoolExecutor para fazer requisições paralelas
with concurrent.futures.ThreadPoolExecutor() as executor:
    future_saque1 = executor.submit(make_request, url_saque, data_saque1)
    future_saque2 = executor.submit(make_request, url_saque, data_saque2)
    future_deposito = executor.submit(make_request, url_deposito, data_deposito)

    # Coletando os resultados
    result_saque1 = future_saque1.result()
    result_saque2 = future_saque2.result()
    result_deposito = future_deposito.result()

    print("Resultado do Saque 1:", result_saque1)
    print("Resultado do Saque 2:", result_saque2)
    print("Resultado do Depósito:", result_deposito)