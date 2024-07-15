import requests
import concurrent.futures

# URLs das rotas de transferência
url1 = 'http://localhost:2525/transferir'
url2 = 'http://localhost:2527/transferir'

# Dados da transferência para a primeira URL
data1 = {
    'nome_banco_destino': 'Banco 3',
    'numero_conta_destino': 0,
    'valor_conta_destino': 90,
    'transferencias': [
        {'numero_conta_origem': 0, 'nome_banco_origem': 'Banco 1', 'valor': 10},
        {'numero_conta_origem': 0, 'nome_banco_origem': 'Banco 2', 'valor': 80}
    ]
}

# Dados da transferência para a segunda URL
data2 = {
    'nome_banco_destino': 'Banco 3',
    'numero_conta_destino': 0,
    'valor_conta_destino': 90,
    'transferencias': [
        {'numero_conta_origem': 0, 'nome_banco_origem': 'Banco 2', 'valor': 10},
        {'numero_conta_origem': 0, 'nome_banco_origem': 'Banco 2', 'valor': 80}
    ]
}

def make_transfer(url, data):
    response = requests.post(url, json=data)
    return response.json()

# Usando ThreadPoolExecutor para fazer requisições paralelas
with concurrent.futures.ThreadPoolExecutor() as executor:
    future1 = executor.submit(make_transfer, url1, data1)
    future2 = executor.submit(make_transfer, url2, data2)

    # Coletando os resultados
    result1 = future1.result()
    result2 = future2.result()

    print("Resultado da transferência para a primeira URL:", result1)
    print("Resultado da transferência para a segunda URL:", result2)