import time
import pika
import json
import base64
import cv2
import numpy as np
from pepper.robot import Pepper

params = pika.URLParameters('amqp://zftppdhz:i4bn6ElyHC-AGgswO3czf3pulF6hpOjy@albatross.rmq.cloudamqp.com/zftppdhz')
params.socket_timeout = 5
# params.ssl_options.context


connection = pika.BlockingConnection(params)
rabbit_channel = connection.channel()
rabbit_channel.queue_declare(queue='image_queue')

rabbit_channel.queue_declare(queue='angle_queue')

def get_robot(ip, port=9559):
    robot = Pepper(ip, port)
    s = robot.autonomous_life_service.getState()
    if s != "disabled":
        print("Disabling the autonomous life")
        robot.autonomous_life_service.setState("disabled")
    robot.stand()
    robot.move_joint_by_angle("HeadPitch", 0.2, 0.4)
    return robot

robot = get_robot(ip="10.0.255.22") # Nao 10.0.255.22 Pepper 10.0.255.8
record = False

crouch = False
def move_robot(robot, angles):
    for angle in angles:
        if 'nan' in angle:
            continue
        if angle[-1] == -10:
            global crouch
            crouch = True
            robot.crouch()
            print(angle[:-2])
            robot.move_joint_by_angle(["LShoulderPitch", "RShoulderPitch", "LShoulderRoll", "LElbowRoll", "RShoulderRoll", "RElbowRoll"], angle[:-2], 0.4)
        else:
            if crouch:
                robot.stand()
                crouch = False
            robot.move_joint_by_angle(["LShoulderPitch", "RShoulderPitch", "LShoulderRoll", "LElbowRoll", "RShoulderRoll", "RElbowRoll", "LHipRoll", "RHipRoll"], angle, 0.4)
        time.sleep(.05)

def callback(ch, method, properties, body):
    body = json.loads(body)
    if body['angles']:
        angles = [body['angles']]
        move_robot(robot, angles)

        img_bytes = base64.b64decode(body['image'])
        
        nparr = np.frombuffer(img_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        cv2.imshow('video', cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        cv2.waitKey(1)

rabbit_channel.basic_consume('angle_queue',
  callback,
  auto_ack=True)
rabbit_channel.start_consuming()
connection.close()