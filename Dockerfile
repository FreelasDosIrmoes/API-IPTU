# Define a imagem base a ser usada, Python 3.11.4 com Debian "buster" slim.
FROM python:3.11.4-slim-buster

# Define o diretório de trabalho no contêiner como "/app".
WORKDIR /app

# Copia todos os arquivos e diretórios do diretório de construção local para o diretório de trabalho no contêiner.
COPY . .

# Atualiza o cache de pacotes do sistema operacional no contêiner.
RUN apt-get update \
  # Inicia a instalação de pacotes do sistema com confirmação automática.
  && apt-get install -y \
    # Não instala as dependências recomendadas pelos pacotes.
    --no-install-recommends \
    # Não instala as dependências sugeridas pelos pacotes.
    --no-install-suggests \
    # Instala pacotes essenciais, como curl, gcc, g++, gnupg, unixodbc-dev, libgssapi-krb5-2.
    curl gcc g++ gnupg unixodbc-dev \
    unixodbc-dev \
    libgssapi-krb5-2 && \
    # Limpa o cache de pacotes para economizar espaço.
    apt-get autoclean && \
    # Remove pacotes desnecessários para economizar espaço.
    apt-get autoremove && \
    # Atualiza novamente o cache de pacotes.
    apt-get update

# Instala as bibliotecas Python especificadas no arquivo requirements.txt.
RUN pip install --no-cache-dir --force -r requirements.txt

# Define o comando padrão a ser executado quando o contêiner é iniciado.
CMD [ "python", "-Bu", "main.py" ]