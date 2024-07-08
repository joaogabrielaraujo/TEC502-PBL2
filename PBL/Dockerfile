# Use a imagem oficial do Python como imagem base
FROM python:3.11-slim

# Defina o diretório de trabalho
WORKDIR /app

# Copie o arquivo de requisitos para o diretório de trabalho
COPY requirements.txt .

# Instale as dependências
RUN pip install -r requirements.txt

# Copie o conteúdo da aplicação para o diretório de trabalho
COPY . .

# Defina as variáveis de ambiente
ENV NUMERO_BANCO=1

ENV IP_BANCO1="0.0.0.0"
ENV NOME_BANCO1="Banco 1"
ENV PORTA_BANCO1=4578

ENV IP_BANCO2="0.0.0.0"
ENV NOME_BANCO2="Banco 2"
ENV PORTA_BANCO2=4574

ENV IP_BANCO3="0.0.0.0"
ENV NOME_BANCO3="Banco 3"
ENV PORTA_BANCO3=4572



# Comando para rodar a aplicação
CMD ["python", "API_banco.py"]