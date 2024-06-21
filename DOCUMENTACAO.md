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

### 2. Cliente (`cliente.py`)

O cliente é responsável por se conectar ao servidor, enviar mensagens e receber mensagens de outros clientes via gRPC.

### 3. Servidor (`servidor.py`)

O servidor gRPC gerencia conexões de clientes, armazena mensagens recebidas em um banco de dados PostgreSQL e envia mensagens de volta aos clientes apropriados.

### 4. Banco de Dados (PostgreSQL)

Utilizado para armazenar mensagens enviadas pelos clientes. O esquema do banco de dados é definido no arquivo SQL de inicialização (`init_db.sql`).

### 5. Docker

Os Dockerfiles (`Dockerfile.cliente` e `Dockerfile.servidor`) são usados para criar imagens Docker do cliente e do servidor, respectivamente. O arquivo `docker-compose.yml` configura os serviços (cliente, servidor, banco de dados) e a rede para comunicação entre eles.

### 6. Ansible

O playbook `playbook.yml` automatiza a implantação da aplicação, instalando dependências, configurando o ambiente Docker e iniciando os contêineres.

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
