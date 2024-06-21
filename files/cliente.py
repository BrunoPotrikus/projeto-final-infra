import grpc
import messenger_pb2
import messenger_pb2_grpc
import threading

def conectar(endereco_servidor, nome_cliente):
    canal = grpc.insecure_channel(endereco_servidor)
    stub = messenger_pb2_grpc.MessengerStub(canal)
    resposta = stub.Conectar(messenger_pb2.InformacaoCliente(nome=nome_cliente))
    return resposta.conectado, stub

def enviar_mensagem(stub, remetente, destinatario, conteudo):
    stub.EnviarMensagem(messenger_pb2.Mensagem(remetente=remetente, destinatario=destinatario, conteudo=conteudo))

def receber_mensagens(stub, nome_cliente):
    for mensagem in stub.ReceberMensagem(messenger_pb2.InformacaoCliente(nome=nome_cliente)):
        print(f"\nMensagem recebida de {mensagem.remetente}: {mensagem.conteudo}")

def executar():
    endereco_servidor = '100.0.0.10:50051'
    nome_cliente = input("Digite seu nome: ")

    conectado, stub = conectar(endereco_servidor, nome_cliente)
    if conectado:
        print(f"{nome_cliente} conectado ao servidor!")

        threading.Thread(target=receber_mensagens, args=(stub, nome_cliente)).start()

        while True:
            destinatario = input("Digite o nome do destinatário: ")
            conteudo = input("Digite a mensagem: ")
            enviar_mensagem(stub, nome_cliente, destinatario, conteudo)
            
    else:
        print("Falha ao conectar ao servidor.")

if __name__ == '__main__':
    executar()
