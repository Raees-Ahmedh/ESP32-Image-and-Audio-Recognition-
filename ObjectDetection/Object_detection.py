import cv2
import urllib.request
import numpy as np

# OBJECT CLASSIFICATION PROGRAM FOR VIDEO IN IP ADDRESS

url = 'http://192.168.8.184/cam-hi.jpg'
winName = 'ESP32 CAMERA'
cv2.namedWindow(winName, cv2.WINDOW_AUTOSIZE)

# Load class names
classNames = []
classFile = 'coco.names'
with open(classFile, 'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

# Load model
configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
weightsPath = 'frozen_inference_graph.pb'

net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

def set_conf_threshold(x):
    global conf_threshold
    conf_threshold = x / 100.0

conf_threshold = 0.5
cv2.createTrackbar('Confidence Threshold', winName, int(conf_threshold * 100), 100, set_conf_threshold)

while True:
    try:
        imgResponse = urllib.request.urlopen(url)
        imgNp = np.array(bytearray(imgResponse.read()), dtype=np.uint8)
        img = cv2.imdecode(imgNp, -1)
        imgResponse.close()  # Close the response to free up resources

        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)  # Rotate image if necessary

        # Resize image for better performance
        # scale_percent = 50  # Adjust as needed
        # width = int(img.shape[1] * scale_percent / 100)
        # height = int(img.shape[0] * scale_percent / 100)
        # img = cv2.resize(img, (width, height))

        classIds, confs, bbox = net.detect(img, confThreshold=conf_threshold)
        print(classIds, bbox)

        if len(classIds) != 0:
            for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                cv2.rectangle(img, box, color=(0, 255, 0), thickness=3)
                cv2.putText(img, classNames[classId - 1], (box[0] + 10, box[1] + 30),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow(winName, img)

        # Wait for ESC to be pressed to end the program
        tecla = cv2.waitKey(5) & 0xFF
        if tecla == 27:
            break
    except Exception as e:
        print(f"Error: {e}")
        break

cv2.destroyAllWindows()
