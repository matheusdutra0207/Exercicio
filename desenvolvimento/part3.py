from is_wire.core import Channel, StatusCode, Status, Logger
from is_wire.rpc import ServiceProvider, LogInterceptor
import time
import random
from is_msgs import common_pb2
from is_msgs.robot_pb2 import RobotTaskRequest
from google.protobuf.empty_pb2 import Empty

log = Logger(name='Robo')

ip = "192.168.0.105"
class Robot():

    def __init__(self,id ,x ,y ,z):
        self.id = id
        self.positionX = x
        self.positionY = y
        self.positionZ = z
   
    def get_id(self):
        return self.id

    def set_position(self, x, y, z):
        self.positionX = x
        self.positionY = y
        self.positionZ = z

    def get_position(self):
        return self.positionX, self.positionY, self.positionZ

#positionRobo = common_pb2.Position(x = 0, y = 0, z = 0)

def move(idPosition, ctx):
    time.sleep(0.2)

    if idPosition.basic_move_task.positions[0].x < 0 or idPosition.basic_move_task.positions[0].y < 0 or idPosition.basic_move_task.positions[0].z < 0:
        log.error("The number must be positive")
        return Status(StatusCode.OUT_OF_RANGE, "The number must be positive")

    elif idPosition.basic_move_task.positions[0].x > 5 or idPosition.basic_move_task.positions[0].y > 5 or idPosition.basic_move_task.positions[0].z > 5:
        log.error("The number must be less than 5")
        return Status(StatusCode.OUT_OF_RANGE, "The number must be less than 5")  
    
    else:
        #Get position
        if idPosition.basic_move_task.positions[0].x == 0 and idPosition.basic_move_task.positions[0].y == 0 and idPosition.basic_move_task.positions[0].z == 0: 
            for robot in robots:
                if robot.id == idPosition.id:
                    idPosition.basic_move_task.positions[0].x, idPosition.basic_move_task.positions[0].y, idPosition.basic_move_task.positions[0].z = robot.get_position()

            return idPosition
        
        else:# Move position
            for robot in robots:
                if robot.id == idPosition.id:

                    setX = idPosition.basic_move_task.positions[0].x
                    setY = idPosition.basic_move_task.positions[0].y
                    setZ = idPosition.basic_move_task.positions[0].z
                    robot.set_position(setX, setY, setZ)
                    idPosition.basic_move_task.positions[0].x, idPosition.basic_move_task.positions[0].y, idPosition.basic_move_task.positions[0].z = robot.get_position()

                    #return Status(StatusCode.Ok, f"Position set to {setX}, {setY}, {setZ} 5")
                    return idPosition 

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
            request_type= RobotTaskRequest,
            reply_type= RobotTaskRequest)

    def run(self):
        self.provider.run() # Blocks forever processing requests

robots = [Robot(1, 2, 3, 1), Robot(2, 1, 1, 1), Robot(3, 2, 2, 2)]

rpcServer = RpcServer(host = ip, port = "5672").initServiceProvider()
rpcServer.callDelegate(filaTopic = "Controle.Robo1")
rpcServer.run()