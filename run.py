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

def move_robot(robot, angles, hands, label=None):
    if angles is not None:
        body_angles_in_radians = [math.radians(x) for x in angles[:4]]
        direction = []
        direction.append(math.radians(0)) if int(angles[-2]) > 50 else direction.append(math.radians(180))
        direction.append(math.radians(0)) if int(angles[-1]) > 50 else direction.append(math.radians(180))
        body_angles_in_radians = direction + body_angles_in_radians
        print(body_angles_in_radians)
        robot.move_joint_by_angle(["LShoulderPitch", "RShoulderPitch", "LShoulderRoll", "LElbowRoll", "RShoulderRoll", "RElbowRoll"], body_angles_in_radians, 0.4)
        time.sleep(.2)
    if hands is not None:
        robot.hand("left", int(hands[0]) > 50)
        robot.hand("right", int(hands[1]) > 50)

def mimic(robot):
    # for image in os.listdir('images/'):
    #     print(image)
    #     oriImg = cv2.imread('images/' + image)
    #     _, image_encoded = cv2.imencode('.jpg', oriImg)
    #     image_bytes = image_encoded.tobytes()
    #     data = requests.post('http://128.205.43.183:5006/imitate', files={'image': image_bytes}).json()
    #     angles = data['angles']
    #     hands = data['hand']
    #     count = 0
    #     while count < 5:
    #         move_robot(robot, angles, hands)
    #         count += 1

    # for robo cam
    robot.subscribe_camera("camera_depth", 2, 30)
    # cap = cv2.VideoCapture(0)
    # cap.set(3, 640)
    # cap.set(4, 480)
    count = 1
    while True:
        oriImg = robot.get_camera_frame(show=True)
        oriImg = cv2.flip(oriImg, 0)
        _, image_encoded = cv2.imencode('.jpg', oriImg)
        image_bytes = image_encoded.tobytes()
        # ret, oriImg = cap.read()
        # _, image_encoded = cv2.imencode('.jpg', oriImg)
        # image_bytes = image_encoded.tobytes()

        # angles, hands = analyse_image(oriImg)
        print("detecting")
        data = requests.post('http://128.205.43.183:5006/imitate', files={'image': image_bytes}).json()
        print(data)
        angles = data['angles']
        hands = data['hand']
        # cv2.imshow("frame", oriImg)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        move_robot(robot, angles, hands)
        count += 1
    robot.unsubscribe_camera()

def get_robot(ip, port=9559):
    robot = Pepper(ip, port)
    s = robot.autonomous_life_service.getState()
    if s != "disabled":
        print("Disabling the autonomous life")
        robot.autonomous_life_service.setState("disabled")
    robot.stand()
    return robot

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    robot = get_robot(ip="10.0.255.8")
    record = False
    mimic(robot)
    # robot.autonomous_life_on()
