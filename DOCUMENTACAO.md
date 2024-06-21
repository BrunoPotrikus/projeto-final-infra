# Documentação do Projeto

## Descrição

O projeto implementa uma aplicação de mensagens utilizando gRPC para comunicação assíncrona entre um cliente e um servidor. Este documento fornece uma visão geral dos componentes, instruções de uso e detalhes da arquitetura utilizada.

## Componentes do Projeto

### 1. Proto File (`messenger.proto`)

O arquivo `messenger.proto` define os serviços e mensagens gRPC utilizados na comunicação entre cliente e servidor.

### 1.1 Definição do Serviço Messenger

```
service Messenger {
    rpc Conectar (InformacaoCliente) returns (StatusConexao);
    rpc EnviarMensagem (Mensagem) returns (Empty);
    rpc ReceberMensagem (InformacaoCliente) returns (stream Mensagem);
}
```

O serviço `Messenger` define três métodos RPC (Remote Procedure Call):

- **Conectar**: Este método é usado pelo cliente para se conectar ao servidor. Ele recebe uma mensagem `InformacaoCliente` e retorna um `StatusConexao`.
- **EnviarMensagem**: Este método permite que o cliente envie uma mensagem para o servidor.
- **ReceberMensagem**: Este método é usado pelo cliente para receber mensagens do servidor de forma assíncrona.

### 1.2 Estrutura das Mensagens

```
message InformacaoCliente {
    string nome = 1;
}
```
`InformacaoCliente` é uma estrutura simples que contém um campo `nome`, representado como uma string. Este campo é usado para identificar o nome do cliente ao conectar-se ou receber mensagens.

```
message StatusConexao {
    bool conectado = 1;
}
```
`StatusConexao` contém um único campo `conectado`, que é um booleano usado para indicar se o cliente está conectado (true) ou não (false). É retornada como resposta ao método `Conectar`.

```
message Mensagem {
    string remetente = 1;
    string destinatario = 2;
    string conteudo = 3;
}
```
`Mensagem` é utilizada para representar as mensagens trocadas entre os clientes e o servidor.

```
message Empty {}
```
`Empty` é usada como um tipo de mensagem vazia, que não contém nenhum campo. Ela é usada como tipo de retorno para métodos gRPC que não precisam retornar dados específicos.

### 2. Cliente (`cliente.py`)

O cliente é responsável por se conectar ao servidor, enviar mensagens e receber mensagens de outros clientes via gRPC.

### 3. Servidor (`servidor.py`)

O servidor gRPC gerencia conexões de clientes, armazena mensagens recebidas em um banco de dados PostgreSQL e envia mensagens de volta aos clientes apropriados.

### 4. Banco de Dados (PostgreSQL)

Utilizado para armazenar mensagens enviadas pelos clientes. O esquema do banco de dados é definido no arquivo SQL de inicialização (`init_db.sql`).

### 5. Docker

Os Dockerfiles (`Dockerfile.cliente` e `Dockerfile.servidor`) são usados para criar imagens Docker do cliente e do servidor, respectivamente. O arquivo `docker-compose.yml` configura os serviços (cliente, servidor, banco de dados) e a rede para comunicação entre eles.

### 5.1 Dockerfile.cliente

```
FROM ubuntu:latest
```
Este Dockerfile utiliza a imagem base `ubuntu:latest`, que é baseada na versão mais recente do Ubuntu.

```
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.9 \
    python3.9-venv \
    python3.9-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*
```
Instalação de Dependências do Sistema:

- `software-properties-common`: Pacote comum de propriedades de software necessário para adicionar repositórios.
- `python3.9`, `python3.9-venv`, `python3.9-dev`, `python3-pip`: Python 3.9 e pacotes relacionados, instalados para executar a aplicação Python dentro do contêiner.
- `add-apt-repository ppa:deadsnakes/ppa`: Adiciona o PPA (Personal Package Archive) `deadsnakes/ppa` para obter a versão desejada do Python 3.9.
- `rm -rf /var/lib/apt/lists/*`: Remove listas de pacotes baixadas para economizar espaço em disco após a instalação dos pacotes.

```
WORKDIR /app
```
Define o diretório de trabalho dentro do contêiner como `/app`, onde os arquivos da aplicação serão copiados e onde o ambiente virtual Python será configurado.

```
RUN python3.9 -m venv venv
ENV PATH="/app/venv/bin:$PATH"
```
Cria um ambiente virtual Python (`venv`) dentro do diretório `/app` e configura a variável de ambiente `PATH` para usar o ambiente virtual.

```
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
```
Copia o arquivo `requirements.txt` para o contêiner e instala as dependências Python listadas nele. O comando `pip install --upgrade pip` garante que a versão mais recente do pip seja usada antes da instalação das dependências.

```
COPY cliente.py /app/cliente.py
COPY messenger.proto /app/messenger.proto
```
Copia os arquivos essenciais da aplicação (`cliente.py` e `messenger.proto`) para o diretório `/app` dentro do contêiner. Esses arquivos são necessários para executar o cliente e para compilar o arquivo `.proto`.

```
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. messenger.proto
```
Compila o arquivo `messenger.proto` usando `grpc_tools.protoc` para gerar o código Python necessário para comunicação gRPC. Os arquivos gerados (`messenger_pb2.py` e `messenger_pb2_grpc.py`) são utilizados pelo cliente Python para se comunicar com o servidor.

```
CMD ["tail", "-f", "/dev/null"]
```
O comando `tail -f /dev/null` mantém o contêiner em execução sem realizar nenhuma ação, sendo útil para manter o contêiner ativo enquanto ele executa outras tarefas em segundo plano.

### 5.2 Dockerfile.servidor

Basicamente a mesma confguração do `Dockerfile.cliente`, apenas adicionando duas dependências:

- `build-essential`: Este pacote contém um conjunto de ferramentas essenciais para compilar e construir software no ambiente Linux.
- `libpq-dev`: Garante a compilação e a instalação das bibliotecas e extensões Python necessárias para acessar e manipular dados no PostgreSQL.

### 6. Ansible

O playbook `playbook.yml` automatiza a implantação da aplicação, instalando dependências, configurando o ambiente Docker e iniciando os contêineres.

```
  become: true
  become_method: sudo
  become_user: root
```
 - `become`: Habilita a execução das tarefas com privilégios elevados.
 - `become_method`: Define o método usado para adquirir privilégios elevados, neste caso, `sudo`.
 - `become_user`: Especifica o usuário como root para execução das tarefas com privilégios elevados.

 ```
   vars_files:
    - group_vars/vars.yml
 ```
Especifica os arquivos YAML que contêm variáveis a serem carregadas no playbook. Nesse caso, `vars.yml` contém variáveis `db_user`, `db_password` e `db_name`, necessárias para configurar o banco de dados da aplicação.

### 6.1 Tasks

```
- name: Garantir que o cache do apt está atualizado
      apt:
        update_cache: yes
```
Garante que o cache do apt esteja atualizado para garantir que as instalações de pacotes sejam baseadas nas informações mais recentes dos repositórios.

```
    - name: Instalar Docker e Docker Compose
      apt:
        name: 
          - docker.io
          - docker-compose
        state: present
```
Istalando os pacotes `docker.io` e `docker-compose`, garantindo que os pacotes estejam presentes no sistema com `state: present`

```
    - name: Garantir que o serviço Docker está em execução
      service:
        name: docker
        state: started
        enabled: yes
```
Habilita a inicialização do serviço Docker

- `state: started`: Garante que o serviço Docker esteja iniciado.
- `enabled: yes`: Habilita o serviço para iniciar automaticamente no boot do sistema.

```
    - name: Criar diretório do projeto
      file:
        path: /opt/messenger_app
        state: directory
        mode: '0755'
```
- `path`: Define o caminho do diretório a ser criado (`/opt/messenger_app`)
- `state: directory`: Define que será criado um diretório.
- `mode: 0755`: Permissões do diretório (rwxr-xr-x), permitindo leitura, escrita e execução para o proprietário e apenas leitura e execução para outros.

```
    - name: Copiar arquivos do projeto para o servidor
      copy:
        src: "{{ item }}"
        dest: /opt/messenger_app/
      with_items:
        - cliente.py
        - servidor.py
        - messenger.proto
        - Dockerfile.cliente
        - Dockerfile.servidor
        - docker-compose.yml
        - init_db.sql
        - requirements.txt
```
Copia todos os arquivos necessários para a aplicação para o repositório `/opt/messenger_app/`, criado na tarefa anterior.

```
    - name: Iniciar contêineres Docker
      shell: docker-compose up --build -d
      args:
        chdir: /opt/messenger_app
```
- `shell: docker-compose up --build -d`: Constroi e inicia os contêineres. O `-d` executa os contêineres em segundo plano.
- `chdir: /opt/messenger_app`: Define o diretório para a execução do comando.

```
    - name: Verificar se o contêiner do banco de dados está em execução
      community.docker.docker_container_info:
        name: db
      register: db_status_info
    - name: Verificar se o contêiner do servidor está em execução
      community.docker.docker_container_info:
        name: servidor
      register: servidor_status_info
    - name: Verificar se o contêiner do cliente está em execução
      community.docker.docker_container_info:
        name: cliente
      register: cliente_status_info
```
Verifica se os contêineres estão em execução.

## Arquitetura

A arquitetura do projeto é distribuída e escalável, utilizando gRPC para comunicação eficiente entre serviços, Docker para isolamento de contêineres e facilitação do ambiente de desenvolvimento e implantação, e PostgreSQL para persistência de dados.

### Fluxo de Funcionamento

1. **Inicialização do Ambiente**:
   - O Docker Compose é utilizado para configurar e interconectar os serviços (cliente, servidor, banco de dados) em uma rede interna definida.

2. **Comunicação Cliente-Servidor**:
   - O cliente se conecta ao servidor utilizando gRPC para enviar e receber mensagens.

3. **Persistência de Dados**:
   - As mensagens enviadas pelos clientes são armazenadas no banco de dados PostgreSQL para garantir a persistência dos dados.

## Instruções de Uso

### Pré-requisitos

- Docker e Docker Compose instalados.
- Ansible instalado (opcional, se desejar automatizar a implantação).

### Instalação e Execução

1. Clone o repositório do projeto:

   ```bash
   git clone https://github.com/seu-usuario/nome-do-repositorio.git
   cd nome-do-repositorio
