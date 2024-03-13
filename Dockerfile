# Use a imagem oficial do Selenium com o Chrome Headless como base
FROM selenium/standalone-chrome:latest

# Define o diretório de trabalho no contêiner como "/app".
WORKDIR /app

# Copia todos os arquivos e diretórios do diretório de construção local para o diretório de trabalho no contêiner.
COPY . .

# RUN mkdir Downloads

# Instala as dependências do sistema operacional.
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip

# Instala as bibliotecas Python especificadas no arquivo requirements.txt.
RUN pip install --no-cache-dir --force -r requirements.txt

# Volta para o usuário padrão do Selenium

# Exponha a porta necessária (substitua pela porta correta se for diferente)
EXPOSE 5001

# RUN test -d migrations || flask db init

# RUN flask db migrate

# RUN flask db upgrade
# Define o comando padrão a ser executado quando o contêiner é iniciado.
ENTRYPOINT [ "bash","entrypoint.sh" ]