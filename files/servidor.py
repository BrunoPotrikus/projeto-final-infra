from concurrent import futures
import grpc
import messenger_pb2
import messenger_pb2_grpc
import psycopg2
from queue import Queue

class ServidorMensageiro(messenger_pb2_grpc.MessengerServicer):
    def __init__(self):
        self.clientes = {}
        self.filas_de_mensagem = {}
        self.conn = psycopg2.connect(
            dbname="messenger_db",
            user="user",
            password="password",
            host="db"
        )

    def Conectar(self, request, context):
        nome_cliente = request.nome
        self.clientes[nome_cliente] = context
        self.filas_de_mensagem[nome_cliente] = Queue()
        print(f"Cliente {nome_cliente} conectado.")
        return messenger_pb2.StatusConexao(conectado=True)

    def EnviarMensagem(self, request, context):
        remetente = request.remetente
        destinatario = request.destinatario
        conteudo = request.conteudo

        with self.conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO messages (sender, receiver, content) VALUES (%s, %s, %s)",
                (remetente, destinatario, conteudo)
            )
            self.conn.commit()

        print(f"Mensagem enviada de {remetente} para {destinatario}: {conteudo}")
        return messenger_pb2.Empty()

    def ReceberMensagem(self, request, context):
        nome_cliente = request.nome
        while True:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT sender, content FROM messages WHERE receiver = %s", (nome_cliente,))
                rows = cursor.fetchall()
                for row in rows:
                    yield messenger_pb2.Mensagem(remetente=row[0], conteudo=row[1])
                    cursor.execute("DELETE FROM messages WHERE receiver = %s AND sender = %s AND content = %s", (nome_cliente, row[0], row[1]))
                self.conn.commit()

def executar():
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    messenger_pb2_grpc.add_MessengerServicer_to_server(ServidorMensageiro(), servidor)
    servidor.add_insecure_port('[::]:50051')
    servidor.start()
    print("Servidor conectado na porta 50051")
    servidor.wait_for_termination()

if __name__ == '__main__':
    executar()
