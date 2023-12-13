# Passo a Passo para rodar a API

Esse README fornece um guia passo a passo para configurar e executar a API de IPTU.

## Clonar os Repositórios
```bash
git clone https://github.com/FreelasDosIrmoes/API-IPTU.git
git clone https://github.com/FreelasDosIrmoes/MsgSender-API.git
```

OU

```bash
git clone git@github.com:FreelasDosIrmoes/API-IPTU.git
git clone git@github.com:FreelasDosIrmoes/MsgSender-API.git
```

## Configuração de Ambiente

Aqui são as etapas necessárias para configurar e executar o ambiente de desenvolvimento.

### Pré-requisitos

- Ter os pacotes:
  - python3
  - python-venv
- Docker instalado
  
### Instalação e Execução do banco de dados
```bash
docker run -d \
  --name postgres_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=iptu-db \
  -e PGDATA=/data/postgres \
  -v postgres:/data/postgres \
  -p 5432:5432 \
  postgres:14-alpine
```

### Criação do ambiente virtual e configuração da API-IPTU: 
```bash
cd API-IPTU
python3 -m venv venv
. venv/bin/active
pip install -Ur requirements.txt
python -m flask db init
python -m flask db migrate
python -m flask db upgrade
python main.py
```

### Criação do ambiente virtual e configuração da API-MSG: 
```bash
cd MsgSender-API
python3 -m venv venv
. venv/bin/active
pip install -Ur requirements.txt
python main.py
```



## Documentação
### Após rodar a API siga a instrução abaixo:
###  Para acessar a documentação para fácil implementação: http://localhost:5001/apidocs/index.html
