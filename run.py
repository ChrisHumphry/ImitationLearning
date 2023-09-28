import math
import numpy as np
from openpose import util
from openpose.body import Body
from openpose.hand import Hand
from pepper.robot import Pepper
import time
import argparse
import cv2


def move_robot(robot, angles, hands, label=None):
    if angles is not None:
        body_angles_in_radians = [math.radians(x) for x in angles[:4]]
        direction = []
        direction.append(math.radians(0))
        direction.append(math.radians(0))
        body_angles_in_radians = direction + body_angles_in_radians
        robot.move_joint_by_angle(["LShoulderPitch", "RShoulderPitch", "LShoulderRoll", "LElbowRoll", "RShoulderRoll", "RElbowRoll"], body_angles_in_radians, 0.4)
        time.sleep(.2)
    if hands is not None:
        robot.hand("left", int(hands[0]) > 50)
        robot.hand("right", int(hands[1]) > 50)


def analyse_image(img):
    body_estimation = Body('model/body_pose_model.pth')
    hand_estimation = Hand('model/hand_pose_model.pth')
    candidate, subset = body_estimation(img)
    body_angles = util.draw_bodypose(candidate, subset)
    # Offset joints
    if body_angles:
        body_angles[0] = body_angles[0] - 90
        if body_angles[1] <0:
            body_angles.append(0)
            body_angles[1] = -1*body_angles[1]
        else:
            body_angles.append(100)
        if body_angles[3] <0:
            body_angles.append(0)
            body_angles[3] = -1*body_angles[3]
        else:
            body_angles.append(100)
        body_angles[1] = - (180 - body_angles[1])
        body_angles[2] = - (body_angles[2] - 90)
        body_angles[3] = 180 - body_angles[3]
        hands_list = util.handDetect(candidate, subset, img)
        all_hand_peaks = []
        for x, y, w, is_left in hands_list:
            peaks = hand_estimation(img[y:y+w, x:x+w, :])
            peaks[:, 0] = np.where(peaks[:, 0]==0, peaks[:, 0], peaks[:, 0]+x)
            peaks[:, 1] = np.where(peaks[:, 1]==0, peaks[:, 1], peaks[:, 1]+y)
            all_hand_peaks.append(peaks)

        is_left_hand_open, is_right_hand_open = util.draw_handpose(all_hand_peaks, False)
        lhand = 100 if is_left_hand_open else 0
        rhand = 100 if is_right_hand_open else 0
        return body_angles, [lhand, rhand]
    return None, None

def mimic_direct(robot):
    robot.subscribe_camera("camera_top", 2, 30)
    count = 1
    while True:
        oriImg = robot.get_camera_frame(show=True)
        angles, hands = analyse_image(oriImg)
        cv2.imshow("frame", oriImg)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
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
    mimic_direct(robot)
    robot.autonomous_life_on()
