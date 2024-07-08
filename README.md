<h1 align="center">
  <br>
  Projeto da disciplina TEC 502 - Concorrência e Conectividade
  <br>
</h1>
<div>
 
> Este projeto foi desenvolvido como parte da disciplina MI - Concorrência e Conectividade, do curso de Engenharia de Computação da Universidade Estadual de Feira de Santana (UEFS).



## Introdução 
Este relatório apresenta a solução desenvolvida para implementar um sistema de transações bancárias semelhante ao Pix, em um país que não possui um banco central. A principal demanda do governo era a criação de um sistema que permitisse a realização de pagamentos, depósitos e transferências entre contas de diferentes bancos, sem utilizar recursos centralizados para controlar as transações.

Com o objetivo de atender aos requisitos solicitados, foi estabelecido um consórcio bancário que contratou uma equipe de especialistas em sistemas distribuídos. A solução proposta foi baseada em um sistema distribuído que garante a comunicação eficiente e segura entre os bancos, permitindo que os clientes realizem transações atômicas sobre suas contas, sejam elas de pessoa física (particulares ou conjuntas) ou jurídica.

Os desafios principais incluíam a prevenção de movimentações de dinheiro além do saldo disponível e a eliminação do risco de duplo gasto, onde o mesmo dinheiro poderia ser transferido para mais de uma conta simultaneamente.

#Sumário
- [Api](#Api)
  -   [2PC - Two-Phase Commit](#2pc---two-phase-commit)
  -   [Rotas para Gerenciamento de Contas](#rotas-para-gerenciamento-de-contas)


# Api
## 2PC - Two-Phase Commit 
O código apresentado utiliza um método de "two phase commit" (compromisso em duas fases) em conjunto com bloqueios (locks) para garantir a consistência das operações bancárias distribuídas.

O "two phase commit" é um protocolo utilizado para garantir a atomicidade das transações distribuídas, ou seja, garantir que todas as operações relacionadas a uma transação sejam executadas com sucesso ou que nenhuma delas seja executada. No contexto do código fornecido:
### Preparação (Fase 1):
* Função preparar_transferencia() e preparar_conta_externa(): Essas funções são responsáveis por preparar as contas envolvidas na transação. Isso inclui verificar se as contas existem, aplicar bloqueios (lock.acquire()) para garantir exclusividade durante a modificação da conta e realizar qualquer outra preparação necessária, como verificar saldos suficientes para transferências.

* Bloqueios (Locks): Os bloqueios são fundamentais para garantir que apenas uma thread ou processo por vez possa modificar uma determinada conta. Isso previne problemas de consistência que poderiam ocorrer se múltiplos processos tentassem modificar a mesma conta simultaneamente. Após a preparação, os bloqueios são liberados (lock.release()) para permitir que outras operações possam ser executadas.

### Confirmação (Fase 2):
Após a fase de preparação, o sistema avança para a fase de confirmação das transações preparadas:

* Função confirmar_transferencia() e confirmacao_conta_externa(): Estas funções são responsáveis por confirmar as operações preparadas na fase anterior. Isso inclui efetuar transferências reais entre contas dentro do banco ou enviar solicitações de transferência para bancos externos, dependendo do destino da transação.

* Commit ou Rollback: Durante esta fase, é crucial garantir que todas as operações preparadas sejam efetivadas (commit) apenas se todas forem executadas com sucesso. Caso contrário, se ocorrer algum erro durante a confirmação, é necessário desfazer (rollback) todas as operações preparadas para manter a integridade dos dados.

###  Desfazer (Rollback):
Se ocorrer qualquer falha durante a preparação ou confirmação das transações, é necessário desfazer todas as operações preparadas para evitar estados inconsistentes no sistema:

* Função desfazer_transferencia() e desfazer_conta_externa(): Essas funções são acionadas em caso de erro durante a preparação ou confirmação das transações. Elas revertem quaisquer modificações feitas durante a preparação, garantindo que nenhuma mudança inconsistente seja persistida no sistema.

## Rotas para Gerenciamento de Contas
### Rota para cadastrar uma pessoa física:
* `POST` /cadastro_pessoa_fisica
* Recebe dados JSON (nome, CPF, senha) e cadastra uma pessoa física.
* Verifica se todos os dados obrigatórios foram fornecidos e se o cliente já está cadastrado.
  Em caso de sucesso, retorna uma mensagem de confirmação e detalhes da conta criada.

### Rota para cadastrar uma pessoa jurídica:
* `POST` /cadastro_pessoa_juridica
* Recebe dados JSON (nome, CNPJ, senha) e cadastra uma pessoa jurídica.
* Verifica se todos os dados obrigatórios foram fornecidos e se o cliente já está cadastrado.
  Em caso de sucesso, retorna uma mensagem de confirmação e detalhes da conta criada.
  
### Rota para cadastrar uma conta conjunta:
* `POST` /cadastro_conta_conjunta
* Recebe dados JSON (identificador1, identificador2, senha) e cadastra uma conta conjunta.
* Verifica se os identificadores e a senha foram fornecidos e se os clientes existem.
  Em caso de sucesso, retorna uma mensagem de confirmação e detalhes da conta criada.
  
### Rota para fazer login:
* `POST` /login
* Recebe dados JSON (identificador, senha) e autentica o cliente.
* Verifica se o identificador e a senha foram fornecidos.
* Em caso de sucesso, retorna uma mensagem de login bem-sucedido e detalhes do cliente.
  
### Rota para fazer logout:
* `POST` /logout
* Desloga o cliente atualmente logado.
* Retorna uma mensagem de confirmação de logout.
  
### Rota para obter todas as contas de um cliente em todos os bancos:
* `GET` /contas_cliente/<identificador>
* Recebe um identificador (CPF/CNPJ) e retorna todas as contas associadas a esse cliente em todos os bancos.
* Verifica se o identificador foi fornecido e se o cliente existe.
* Em caso de sucesso, retorna uma lista de todas as contas do cliente.
  
### Rota para obter todas as contas de um cliente em um banco específico:
* `GET` /get_contas/<identificador>
* Recebe um identificador (CPF/CNPJ) e retorna todas as contas associadas a esse cliente no banco atual.
* Verifica se o identificador foi fornecido e se o cliente existe.
* Em caso de sucesso, retorna uma lista de todas as contas do cliente no banco atual.
  
### Rota para obter uma conta de um cliente em um banco específico:
* `GET` /get_conta/<nome_banco>/<numero_conta>
* Recebe o nome do banco e o número da conta e retorna os detalhes dessa conta.
* Verifica se o nome do banco e o número da conta foram fornecidos.
* Em caso de sucesso, retorna os detalhes da conta.
  
### Rota para obter o identificador do cliente logado:
* `GET` /get_identificador
* Retorna o identificador (CPF/CNPJ) do cliente atualmente logado.
* Verifica se há um cliente logado.
* Em caso de sucesso, retorna o identificador do cliente logado.
  
### Rota para obter o nome do banco:
* `GET` /get_nome_banco
* Retorna o nome do banco atual.

## Rotas Designadas para Lógica Bancária
### Rota responsável por realizar um depósito em qualquer conta que um banco possua
* Endpoint: /deposito
* Método HTTP: `POST`
* Funcionalidade:
*   Recebe dados em formato JSON contendo o número da conta, nome do banco e valor a ser depositado.
    Valida os dados recebidos e executa o depósito na conta correspondente:
*    Se o banco for o mesmo em que o cliente está logado (banco.nome), o depósito é realizado diretamente na conta interna usando métodos do objeto banco.
      Caso contrário, delega a operação para o método deposito_outro_banco do objeto banco, que lida com depósitos em bancos externos.
     
### Rota responsável por realizar um saque em um banco que um cliente esteja logado
* Endpoint: /saque
* Método HTTP: `POST`
* Funcionalidade:
*   Recebe dados em formato JSON contendo o número da conta e o valor a ser sacado.
*   Valida os dados e executa o saque na conta correspondente usando métodos do objeto banco.
  
### Rota responsável por preparar uma transferência de uma conta de um banco externo
* Endpoint: /preparar_transferencia
* Método HTTP: `POST`
* Funcionalidade:
*   Recebe dados em formato JSON contendo o número da conta, nome do banco, tipo de transferência e valor a ser transferido.
* Valida os dados e prepara a transferência:
    Se o banco for o mesmo em que o cliente está logado (banco.nome), prepara a transferência usando métodos do objeto banco.
    Caso contrário, delega a operação para o método preparar_conta_externa do objeto banco, que prepara a conta externa para a transferência.
  
### Rota responsável por confirmar uma transferência de uma conta de um banco externo
* Endpoint: /confirmar_transferencia
* Método HTTP: `POST`
* Funcionalidade:
    Recebe dados em formato JSON contendo o número da conta, nome do banco, tipo de transferência e valor a ser transferido.
* Valida os dados e confirma a transferência:
    Se o banco for o mesmo em que o cliente está logado (banco.nome), confirma a transferência usando métodos do objeto banco.
    Caso contrário, delega a operação para o método confirmacao_conta_externa do objeto banco, que confirma a transferência na conta externa.
  
### Rota responsável por desfazer alterações em uma conta de um banco externo
* Endpoint: /desfazer_transferencia
* Método HTTP: `POST`
* Funcionalidade:
    Recebe dados em formato JSON contendo o número da conta, nome do banco, tipo de transferência e valor a ser desfeito.
* Valida os dados e desfaz as alterações:
    Se o banco for o mesmo em que o cliente está logado (banco.nome), desfaz as alterações usando métodos do objeto banco.
    Caso contrário, delega a operação para o método desfazer_conta_externa do objeto banco, que desfaz as alterações na conta externa.
  
### Rota responsável por realizar a transferência entre contas
* Endpoint: /transferir
* Método HTTP: `POST`
* Funcionalidade:
    Recebe dados em formato JSON contendo o nome do banco de destino, número da conta de destino, valor a ser transferido e uma lista de transferências adicionais.
* Executa a transferência em duas fases:
    Preparação: Prepara todas as contas envolvidas na transferência.
    Confirmação: Confirma as operações preparadas.
    Usa métodos do objeto banco para realizar essas operações de preparação e confirmação.
  
## Rotas Designadas para Interface
### Rota para página de login
* Endpoint: /
* Método HTTP: `GET`
* Funcionalidade:
    Renderiza o template login.html, que geralmente contém formulários para login.
<div align ="center">
  <img width="800px" align="center" src="https://github.com/joaogabrielaraujo/PBLrede2/blob/main/PBL/img/telaLogin.jpg">
</div>

### Rota para a página de Home
* Endpoint: /home
* Método HTTP: `GET`
* Funcionalidade:
    Tenta obter informações das contas do cliente logado e o nome do banco.
    Realiza chamadas HTTP para endpoints específicos do banco usando requests.get.
    Se obter sucesso nas chamadas, renderiza o template home.html passando o nome do banco e informações das contas.
<div align ="center">
  <img width="800px" align="center" src="https://github.com/joaogabrielaraujo/PBLrede2/blob/main/PBL/img/telaHome.jpg">
</div>

### Rota para a página de cadastro
* Endpoint: /cadastro
* Método HTTP: `GET`
* Funcionalidade:
    Renderiza o template cadastro.html, utilizado para cadastro de novos clientes.
<div align ="center">
  <img width="800px" align="center" src="https://github.com/joaogabrielaraujo/PBLrede2/blob/main/PBL/img/telaCadastro.jpg">
</div>

### Rota para renderizar a página de depósito
* Endpoint: /deposito_page
* Método HTTP: `GET`
* Funcionalidade:
    Renderiza o template deposito.html, que provavelmente contém formulários para realizar depósitos em contas.
<div align ="center">
  <img width="500px" align="center" src="https://github.com/joaogabrielaraujo/PBLrede2/blob/main/PBL/img/telaDeposito.jpg">
</div>

### Rota para acessar a página de saque
* Endpoint: /saque_page
* Método HTTP: `GET`
* Funcionalidade:
    Renderiza o template saque.html, onde são disponibilizados formulários para realizar saques de contas bancárias.
<div align ="center">
  <img width="500px" align="center" src="https://github.com/joaogabrielaraujo/PBLrede2/blob/main/PBL/img/telaSaque.jpg">
</div>

### Rota para a página de Transferência
* Endpoint: /transferencia_page
* Método HTTP: `GET`
* Funcionalidade:
    Tenta obter informações das contas do cliente logado e o nome do banco.
    Realiza chamadas HTTP para endpoints específicos do banco usando requests.get.
    Se obter sucesso nas chamadas, renderiza o template transferencia.html passando o nome do banco e informações das contas.
  
<div align ="center">
  <img width="800px" align="center" src="https://github.com/joaogabrielaraujo/PBLrede2/blob/main/PBL/img/telaTransferencia.jpg">
</div>

# Conclusão
