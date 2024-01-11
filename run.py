import math
import numpy as np
from openpose import util
from openpose.body import Body
from openpose.hand import Hand
from pepper.robot import Pepper
import time
import argparse
import cv2
import requests
import copy
import os
import json
import datetime
import io
from PIL import Image
import keyboard
import base64
import pika

params = pika.URLParameters('amqp://zftppdhz:i4bn6ElyHC-AGgswO3czf3pulF6hpOjy@albatross.rmq.cloudamqp.com/zftppdhz')
params.socket_timeout = 5
# params.ssl_options.context


connection = pika.BlockingConnection(params)
rabbit_channel = connection.channel()
rabbit_channel.queue_declare(queue='image_queue')

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
            robot.move_joint_by_angle(["LShoulderPitch", "RShoulderPitch", "LShoulderRoll", "LElbowRoll", "RShoulderRoll", "RElbowRoll"], angle[:-2], 0.2)
        else:
            if crouch:
                robot.stand()
                crouch = False
            robot.move_joint_by_angle(["LShoulderPitch", "RShoulderPitch", "LShoulderRoll", "LElbowRoll", "RShoulderRoll", "RElbowRoll", "LHipRoll", "RHipRoll"], angle, 0.2)
        time.sleep(.5)

def mimic(robot):
    # video_file = 'video.mp4'
    # cap = cv2.VideoCapture(video_file)
    # angles = []

    # while(cap.isOpened()):
    #     start = datetime.datetime.now()
    #     _, frame = cap.read()
    #     if frame is None:
    #         break

    #     _, frame_encoded = cv2.imencode('.jpg', frame)
    #     frame_bytes = frame_encoded.tobytes()
    #     print("Sending to server after", str(datetime.datetime.now() - start))
    #     data = requests.post('http://128.205.43.183:5006/imitate', files={'image': frame_bytes}).json()
    #     angles.append(data['angles'])
    #     print("Returned from server after", str(datetime.datetime.now() - start))

    # with open("angles.json", "w") as f:
    #     json.dump(angles, f)

    # f = open("angles.json", "r")
    # angles = json.load(f)

    # LShoulderPitch radians -2.0857 to 2.0857 angles -119.5 to 119.5
    # RShoulderPitch radians -2.0857 to 2.0857 angles -119.5 to 119.5
    # LShoulderRoll radians 0.0087 to 1.5620 angles 0.5 to 89.5
    # LElbowRoll radians -1.5620 to -0.0087 angles -89.5 to -0.5
    # RShoulderRoll radians -1.5620 to -0.0087 angles -89.5 to -0.5
    # RElbowRoll radians 0.0087 to 1.5620 angles 0.5 to 89.5
    # move_robot(robot, angles)

    # for image in os.listdir('images/'):
    #     if '.jpeg' in image or '.jpg' in image:
    #         start = datetime.datetime.now()
    #         print(image)
    #         oriImg = cv2.imread('images/' + image)
    #         _, image_encoded = cv2.imencode('.jpg', oriImg)
    #         image_bytes = image_encoded.tobytes()
    #         # data = requests.post('http://128.205.43.183:5006/imitate', files={'image': image_bytes}).json()
    #         data = json.dumps({'image': image_bytes.encode('base64'), 'name': image.split('.')[0]})
    #         rabbit_channel.basic_publish(exchange='', routing_key='image_queue', body=data)
            # angles = data['angles']
            # print(angles)
            # print("ML time", str(datetime.datetime.now() - start))
            # # count = 0
            # # while count < 20:
            # start = datetime.datetime.now()
            # move_robot(robot, [angles])
            # print("movement time", str(datetime.datetime.now() - start))
                # count += 1

    # for robo cam
    # cv2.namedWindow('video', cv2.WINDOW_NORMAL)
    robot.subscribe_camera("camera_top", 1, 1)
    count = 1
    while True:
        oriImg = robot.get_camera_frame(show=False)
        count += 1
        if count % 2 == 0 or count % 3 == 0:
            continue
        # cv2.resizeWindow('Continuous Image Display', oriImg.shape[0], oriImg.shape[1])
        _, image_encoded = cv2.imencode('.jpg', oriImg)
        image_bytes = image_encoded.tobytes()
        # print("detecting")
        data = json.dumps({'image': image_bytes.encode('base64'), 'name': 'test'})
        rabbit_channel.basic_publish(exchange='', routing_key='image_queue', body=data)
        # data = requests.post('http://128.205.43.183:5006/imitate', files={'image': image_bytes}).json()
        count += 1
        if count > 500:
            break

    robot.unsubscribe_camera()

def get_robot(ip, port=9559):
    robot = Pepper(ip, port)
    s = robot.autonomous_life_service.getState()
    if s != "disabled":
        print("Disabling the autonomous life")
        robot.autonomous_life_service.setState("disabled")
    robot.stand()
    robot.move_joint_by_angle("HeadPitch", 0.2, 0.4)
    return robot

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    robot = get_robot(ip="10.0.255.22") # Nao 10.0.255.22 Pepper 10.0.255.8
    record = False
    mimic(robot)
    robot.autonomous_life_on()
