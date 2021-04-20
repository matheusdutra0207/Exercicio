from __future__ import print_function
from is_wire.core import Channel, Message, Subscription, StatusCode, Status, Logger
import socket
from is_wire.rpc import ServiceProvider, LogInterceptor
import time
from RequisicaoRobo_pb2 import RequisicaoRobo
import common_pb2
import random


log = Logger(name='Gateway')

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
        reply = channel.consume(timeout=1.0)
        return reply

    except socket.timeout:
        log.info('No reply :(')

def controlRobo(requisicaoRobo, ctx):

    time.sleep(0.2)
    if requisicaoRobo.function == "Move":
        
        reply = request(
            content = requisicaoRobo.positions, 
            ip = "10.10.2.7", 
            port = "30000", 
            topic = "Controle.Robo1")

        if reply.status.why == '':
            newPosition = reply.unpack(common_pb2.Position)
            requisicaoRobo.positions.x = newPosition.x
            requisicaoRobo.positions.y = newPosition.y
            requisicaoRobo.positions.z = newPosition.z
            return requisicaoRobo
        
        else:
            return Status(StatusCode.OUT_OF_RANGE, reply.status.why)



    elif requisicaoRobo.function == "Get":

        requisicaoRobo.positions.x = 0
        requisicaoRobo.positions.y = 0
        requisicaoRobo.positions.z = 0

        reply = request(
            content = requisicaoRobo.positions, 
            ip = "10.10.2.7", 
            port = "30000", 
            topic = "Controle.Robo1")
        
        getPosition = reply.unpack(common_pb2.Position)

        requisicaoRobo.positions.x = getPosition.x
        requisicaoRobo.positions.y = getPosition.y
        requisicaoRobo.positions.z = getPosition.z

        return requisicaoRobo

class RpcServer:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.channel = Channel(f"amqp://guest:guest@{self.host}:{self.port}")

    def initServiceProvider(self):
        self.provider = ServiceProvider(self.channel)
        logging = LogInterceptor()  # Log requests to console
        self.provider.add_interceptor(logging)
        return self

    def callDelegate(self, filaTopic):
        self.provider.delegate(
            topic=filaTopic,
            function=controlRobo,
            request_type=RequisicaoRobo,
            reply_type=RequisicaoRobo)

    def run(self):
        self.provider.run() # Blocks forever processing requests

while True:
    log.info("Inicializando")
    subscribe = Subscribe(host = "10.10.2.7", port = "30000")
    subscribe.createFila(topic="Controle.Console")
    log.info("Aguardando mensagens")

    messageString = subscribe.message.body.decode('utf-8')
    time.sleep(1)

    log.info(messageString)
    randomNumber = random.randint(0, 2)
    if randomNumber == 1: #Sitema foi ligado 
        messageOK = "Sistema ligado"
        log.info(messageOK)
        publish(ip = "10.10.2.7", port = "30000", topic="Controle.Console",messageText = messageOK)
        break
    
    else:
        messageLoss = "Tente novamente"
        log.info(messageLoss)
        publish(ip = "10.10.2.7", port = "30000", topic="Controle.Console",messageText = messageLoss)

rpcServer = RpcServer(host = "10.10.2.7", port = "30000").initServiceProvider()
rpcServer.callDelegate(filaTopic = "Requisicao.Robo")
rpcServer.run()

