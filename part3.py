from is_wire.core import Channel, StatusCode, Status, Logger
from is_wire.rpc import ServiceProvider, LogInterceptor
import time
import random
from is_msgs import common_pb2


log = Logger(name='Robo')

positionRobo = common_pb2.Position(x = 2, y = 4, z = 5)

def move(position, ctx):
    time.sleep(0.2)

    if position.x < 0 or position.y < 0 or position.z < 0:
        log.error("The number must be positive")
        return Status(StatusCode.OUT_OF_RANGE, "The number must be positive")

    elif position.x > 5 or position.y > 5 or position.z > 5:
        log.error("The number must be less than 5")
        return Status(StatusCode.OUT_OF_RANGE, "The number must be less than 5")  
    
    else:

        if position.x == 0 and position.y == 0 and position.z == 0: #Get position
            #positionRobo.x += position.x
            #positionRobo.y += position.y
            #positionRobo.z += position.z
            return positionRobo
        
        else:# Move position
            positionRobo.x = position.x
            positionRobo.y = position.y
            positionRobo.z = position.z 
            return positionRobo     

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
            function=move,
            request_type= common_pb2.Position,
            reply_type= common_pb2.Position)

    def run(self):
        self.provider.run() # Blocks forever processing requests

rpcServer = RpcServer(host = "10.10.2.7", port = "30000").initServiceProvider()
rpcServer.callDelegate(filaTopic = "Controle.Robo1")
rpcServer.run()