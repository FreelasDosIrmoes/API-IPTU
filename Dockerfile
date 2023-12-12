# Define a imagem base a ser usada, Python 3.11.4 com Debian "buster" slim.
FROM python:3.11.4-slim-buster

# Define o diretório de trabalho no contêiner como "/app".
WORKDIR /app

# Copia todos os arquivos e diretórios do diretório de construção local para o diretório de trabalho no contêiner.
COPY . .

# Atualiza o cache de pacotes do sistema operacional no contêiner.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        g++ \
        gnupg \
        unixodbc-dev \
        libgssapi-krb5-2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instala as bibliotecas Python especificadas no arquivo requirements.txt.
RUN pip install --no-cache-dir --force -r requirements.txt

EXPOSE 5001

# Define o comando padrão a ser executado quando o contêiner é iniciado.
CMD ["python", "-Bu", "main.py"]