from __future__ import print_function
from is_wire.core import Channel, Message, Subscription, Logger
import socket
from RequisicaoRobo_pb2 import RequisicaoRobo
from is_msgs.common_pb2 import Position
import time
import random

log = Logger(name='Interface')
ip = "192.168.0.105"


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
    channel = Channel(f"amqp://guest:guest@{ip}:5672")
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
    publish(ip = ip, port = "5672", topic="Controle.Console",messageText = messageLigar)

    #Espera pela reposta ligado ou nao ligado.
    subscribe = Subscribe(host = ip, port = "5672")
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
    requestRobo = RequisicaoRobo()

    while True:
        try:
            idRobot = random.randint(1, 3)
            requestRobo.id = idRobot
            break
        except ValueError:
            log.info("The number must be a int")

    while True:
        function = "Get" if random.randint(1, 2) == 1 else "Move"
        if function == "Get":
            requestRobo.function = function
            break

        elif function == "Move":
            requestRobo.function = function
            break

    while True:
        if function == "Move":
            try:
                x = random.randint(1, 5)
                y = random.randint(1, 5)              
                z = random.randint(-2, 6)              
                requestRobo.positions.x = x
                requestRobo.positions.y = y
                requestRobo.positions.z = z
                break

            except ValueError: 
                log.info("The number must be a int")
        else:
            break

    reply = request(
        content = requestRobo, 
        ip = ip, 
        port = "5672", 
        topic = "Requisicao.Robo")

    if reply.status.why == '':
        
        newPosition = reply.unpack(RequisicaoRobo)
        log.info(f'{(newPosition.positions.x, newPosition.positions.y, newPosition.positions.z)}')

    else:
        log.error(reply.status.why)
