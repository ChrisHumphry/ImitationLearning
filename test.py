import qi
import cv2
import numpy as np

# Connect to NAOqi on your robot
robot_ip = "10.0.255.8"  # or the actual IP address of your robot
session = qi.Session()
try:
    session.connect("tcp://" + robot_ip + ":9559")
except RuntimeError:
    print("Failed to connect to the robot. Make sure NAOqi is running on the robot and the IP address is correct.")
    exit(1)

# Get access to ALVideoDevice proxy
video_device = session.service("ALVideoDevice")

# Set up the camera parameters
camera_name = "DepthCamera"  # Change this if necessary
resolution = 2  # VGA resolution
color_space = 11  # Depth image format

# Subscribe to the camera feed
video_id = video_device.subscribeCamera("DepthSubscriber", 0, resolution, color_space, 15)
# "15" is the desired frame rate; you can adjust this value

try:
    while True:
        # Capture a depth frame
        depth_frame = video_device.getImageRemote(video_id)
        print(depth_frame)

        # Convert the depth frame to a NumPy array
        depth_image = np.frombuffer(depth_frame[6], dtype=np.uint16).reshape((depth_frame[1], depth_frame[0]))

        # Now you have the depth information in 'depth_image' as a NumPy array
        # You can process and analyze the depth data as needed

        # Display the depth image (for demonstration purposes)
        cv2.imshow("Depth Image", depth_image)
        cv2.waitKey(1)

except KeyboardInterrupt:
    pass

# Release the camera feed and disconnect from NAOqi
video_device.unsubscribe(video_id)
cv2.destroyAllWindows()
