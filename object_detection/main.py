import serial
import cv2
import numpy as np
import imutils
from collections import deque
from imutils.video import VideoStream
import argparse



import time
import ArduinoCOM


def nothing(x):
    pass


serPort = "COM3"
baudRate = 9600
ser = serial.Serial(serPort, baudRate)
print("Serial port " + serPort + " opened  Baudrate " + str(baudRate))

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
                help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size")
args = vars(ap.parse_args())


pts = deque(maxlen=args["buffer"])

cv2.namedWindow("tracking")

cv2.createTrackbar("LH","tracking", 0, 360, nothing)
cv2.createTrackbar("UH","tracking", 360, 360, nothing)

cv2.createTrackbar("LM","tracking", 0, 255, nothing)
cv2.createTrackbar("UM","tracking", 255, 255, nothing)

cv2.createTrackbar("LE","tracking", 0, 255, nothing)
cv2.createTrackbar("UE","tracking", 255, 255, nothing)

vs = VideoStream(src=0)
vs.start()

# allow the camera or video file to warm up

centersss = []

while True:

    frame = vs.read()

    if frame is None:
        break

    LH = cv2.getTrackbarPos("LH","tracking")
    UH = cv2.getTrackbarPos("LH", "tracking")

    LM = cv2.getTrackbarPos("LM", "tracking")
    UM = cv2.getTrackbarPos("LM", "tracking")

    LE = cv2.getTrackbarPos("LE", "tracking")
    UE = cv2.getTrackbarPos("LE", "tracking")

    pinkLower = (160, 0, 0)
    pinkUpper = (180, 255, 255)

    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)


    mask = cv2.inRange(hsv, pinkLower, pinkUpper)
    res = cv2.bitwise_and(frame, frame, mask=mask)

    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)


    # contours
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # contour with the largest area
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)

            send = "<HI,"+ str(center[0]) + "," + str(center[1]) + ">"
            #send = "<HI,301,226>"
            ArduinoCOM.sendToArduino(ser, send)
            print(ArduinoCOM.recvFromArduino(ser))

            for i in range(1, len(pts)):

                if pts[i - 1] is None or pts[i] is None:
                    continue

                thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
                cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)


    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)
    cv2.imshow("Result", res)

    key = cv2.waitKey(1) & 0xFF

    # quit
    if key == ord("q"):


        break



    pts.appendleft(center)


cv2.destroyAllWindows()
ser.close()

# x goes 0 - 600
# y goes 0 - 450