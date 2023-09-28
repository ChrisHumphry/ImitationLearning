import qi
import numpy
import cv2

class Pepper:
    def __init__(self, ip_address, port=9559):
        self.session = qi.Session()
        try:
            self.session.connect("tcp://" + ip_address + ":" + str(port))
        except RuntimeError:
            print ("Can't connect to Naoqi. Please check your script arguments.")
            return
        self.posture_service = self.session.service("ALRobotPosture")
        self.motion_service = self.session.service("ALMotion")
        self.autonomous_life_service = self.session.service("ALAutonomousLife")
        self.camera_device = self.session.service("ALVideoDevice")

        self.camera_link = None

        print("[INFO]: Robot is initialized at " + ip_address + ":" + str(port))

    def stand(self):
        """Get robot into default standing position known as `StandInit` or `Stand`"""
        self.posture_service.goToPosture("Stand", 1.0)
        print("[INFO]: Robot is in default position")
    
    def autonomous_life(self):
        """
        Switch autonomous life on/off
        """
        state = self.autonomous_life_service.getState()
        if state == "disabled":
            print("Enabling the autonomous life")
            self.autonomous_life_service.setState("interactive")
        else:
            print("Disabling the autonomous life")
            self.autonomous_life_service.setState("disabled")
            self.stand()

    def autonomous_life_on(self):
        """Switch autonomous life on"""
        self.autonomous_life_service.setState("interactive")
        print("[INFO]: Autonomous life is on")

    def hand(self, hand, close):
        """
        Close or open hand

        :param hand: Which hand
            - left
            - right
        :type hand: string
        :param close: True if close, false if open
        :type close: boolean
        """
        hand_id = None
        if hand == "left":
            hand_id = "LHand"
        elif hand == "right":
            hand_id = "RHand"

        if hand_id:
            if close:
                self.motion_service.setAngles(hand_id, 0.0, 0.2)
                #print("[INFO]: Hand " + hand + "is closed")
            else:
                self.motion_service.setAngles(hand_id, 1.0, 0.2)
                #print("[INFO]: Hand " + hand + "is opened")
        else:
            print("[INFO]: Cannot move a hand")

    def subscribe_camera(self, camera, resolution, fps):
        color_space = 13

        camera_index = None
        if camera == "camera_top":
            camera_index = 0
        elif camera == "camera_bottom":
            camera_index = 1
        elif camera == "camera_depth":
            camera_index = 2
            resolution = 1
            color_space = 11
        
        self.camera_link = self.camera_device.subscribeCamera("Camera_Stream" + str(numpy.random.random()),
                                                              camera_index, resolution, color_space, fps)
        if self.camera_link:
            print("[INFO]: Camera is initialized")
        else:
            print("[ERROR]: Camera is not initialized properly")

    def unsubscribe_camera(self):
        """Unsubscribe to camera after you don't need it"""
        self.camera_device.unsubscribe(self.camera_link)
        print("[INFO]: Camera was unsubscribed")

    def get_camera_frame(self, show):
        image_raw = self.camera_device.getImageRemote(self.camera_link)
        image = numpy.frombuffer(image_raw[6], numpy.uint8).reshape(image_raw[1], image_raw[0], 3)
        image = cv2.flip(image, 0)

        # if show:
        #     cv2.imshow("Pepper Camera", image)
        #     cv2.waitKey(-1)
        #     cv2.destroyAllWindows()

        return image

    def get_depth_frame(self, show):
        """
        Get depth frame from subscribed camera link.

        .. warning:: Please subscribe to camera before getting a camera frame. After \
        you don't need it unsubscribe it.

        :param show: Show image when recieved and wait for `ESC`
        :type show: bool
        :return: image
        :rtype: cv2 image
        """
        image_raw = self.camera_device.getImageRemote(self.camera_link)
        image = numpy.frombuffer(image_raw[6], numpy.uint8).reshape(image_raw[1], image_raw[0], 3)

        if show:
            cv2.imshow("Pepper Camera", image)
            cv2.waitKey(-1)
            cv2.destroyAllWindows()

        return image
