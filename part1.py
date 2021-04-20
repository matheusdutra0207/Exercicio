from __future__ import print_function
from is_wire.core import Channel, Message, Subscription, Logger
import socket
from RequisicaoRobo_pb2 import RequisicaoRobo
from common_pb2 import Position
import time

log = Logger(name='Interface')

class Subscribe:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        # Connect to the broker
        self.channel = Channel(f"amqp://guest:guest@{self.host}:{self.port}")

    def createFila(self, topic):        
        # Subscribe to the desired topic(s)
        self.subscription = Subscription(self.channel)
        self.subscription.subscribe(topic=topic)
        self.message = self.channel.consume()

def publish(ip, port, topic, messageText):
    channel = Channel("amqp://guest:guest@10.10.2.7:30000")
    message = Message()
    message.body = messageText.encode('utf-8')
    channel.publish(message, topic=topic)


def request(content, ip, port, topic):
    channel = Channel(f"amqp://guest:guest@{ip}:{port}")
    subscription = Subscription(channel)
    request = Message(content=content, reply_to=subscription)
    channel.publish(request, topic=topic)

    try:
        reply = channel.consume(timeout=2.0)
        return reply
        #return reply.unpack(RequisicaoRobo)

    except socket.timeout:
        log.info('No reply :(')

while True:
    #Envia mensgame ligar sistema.
    log.info("Inicializando")
    messageLigar = "Ligar sistema"
    publish(ip = "10.10.2.7", port = "30000", topic="Controle.Console",messageText = messageLigar)

    #Espera pela reposta ligado ou nao ligado.
    subscribe = Subscribe(host = "10.10.2.7", port = "30000")
    subscribe.createFila(topic="Controle.Console")
    log.info("Aguardando mensagens")

    messageString = subscribe.message.body.decode('utf-8')
    if messageString == "Sistema ligado":
        log.info(messageString)
        break

    log.info(messageString)
    time.sleep(1)

while True:
    time.sleep(1)

    while True:
        requestRobo = RequisicaoRobo()
        requestRobo.id = 1
        function = input("Digite 'Get' para pegar posicao ou 'Move' para mover o robor: ")
        if function == "Get":
            requestRobo.function = function
            requestRobo.positions.x = 1
            requestRobo.positions.y = 1
            requestRobo.positions.z = 1
            break

        if function == "Move":
            requestRobo.function = function
            x = int(input("Digite a cordenada 'x': "))
            y = int(input("Digite a cordenada 'y': "))               
            z = int(input("Digite a cordenada 'z': "))               
            requestRobo.positions.x = x
            requestRobo.positions.y = y
            requestRobo.positions.z = z
            break

    reply = request(
        content = requestRobo, 
        ip = "10.10.2.7", 
        port = "30000", 
        topic = "Requisicao.Robo")

    if reply.status.why == '':
        
        newPosition = reply.unpack(RequisicaoRobo)
        log.info(f'{(newPosition.positions.x, newPosition.positions.y, newPosition.positions.z)}')

    else:
        log.error(reply.status.why)
