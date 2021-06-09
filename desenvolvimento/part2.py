from __future__ import print_function
from is_wire.core import Channel, Message, Subscription, StatusCode, Status, Logger
import socket
from is_wire.rpc import ServiceProvider, LogInterceptor
import time
from RequisicaoRobo_pb2 import RequisicaoRobo
#import common_pb2
import random
from is_msgs.robot_pb2 import PathRequest
from is_msgs.robot_pb2 import RobotTaskRequest
from is_msgs.common_pb2 import Position

ip = "192.168.0.105"


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
        reply = channel.consume(timeout=1.0)
        return reply

    except socket.timeout:
        log.info('No reply :(')

def controlRobo(requisicaoRobo, ctx):

    time.sleep(0.2)
    if requisicaoRobo.function == "Move":
        idPosition = RobotTaskRequest()
        idPosition.id = requisicaoRobo.id
        idPosition.basic_move_task.positions.extend([Position(
                                                x = requisicaoRobo.positions.x, 
                                                y = requisicaoRobo.positions.y, 
                                                z = requisicaoRobo.positions.z)])
        
        reply = request(
            content = idPosition, 
            ip = ip, 
            port = "5672", 
            topic = "Controle.Robo1")

        if reply.status.code == StatusCode.OK:
            newPosition = reply.unpack(RobotTaskRequest)
            requisicaoRobo.positions.x = newPosition.basic_move_task.positions[0].x
            requisicaoRobo.positions.y = newPosition.basic_move_task.positions[0].y
            requisicaoRobo.positions.z = newPosition.basic_move_task.positions[0].z
            return requisicaoRobo
        
        else:
            return Status(StatusCode.OUT_OF_RANGE, reply.status.why)



    elif requisicaoRobo.function == "Get":

        idPosition = RobotTaskRequest()
        idPosition.id = requisicaoRobo.id
        idPosition.basic_move_task.positions.extend([Position(
                                                x = 0, 
                                                y = 0, 
                                                z = 0)])

        reply = request(
            content = idPosition, 
            ip = ip, 
            port = "5672", 
            topic = "Controle.Robo1")
        
        getPosition = reply.unpack(RobotTaskRequest)

        requisicaoRobo.positions.x = getPosition.basic_move_task.positions[0].x
        requisicaoRobo.positions.y = getPosition.basic_move_task.positions[0].y
        requisicaoRobo.positions.z = getPosition.basic_move_task.positions[0].z

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
    subscribe = Subscribe(host = ip, port = "5672")
    subscribe.createFila(topic="Controle.Console")
    log.info("Aguardando mensagens")

    messageString = subscribe.message.body.decode('utf-8')
    time.sleep(1)

    log.info(messageString)
    randomNumber = random.randint(0, 2)
    if randomNumber == 1: #Sitema foi ligado 
        messageOK = "Sistema ligado"
        log.info(messageOK)
        publish(ip = ip, port = "5672", topic="Controle.Console",messageText = messageOK)
        break
    
    else:
        messageLoss = "Tente novamente"
        log.info(messageLoss)
        publish(ip = ip, port = "5672", topic="Controle.Console",messageText = messageLoss)

rpcServer = RpcServer(host = ip, port = "5672").initServiceProvider()
rpcServer.callDelegate(filaTopic = "Requisicao.Robo")
rpcServer.run()

