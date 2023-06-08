# USAGE
# python ball_tracking.py --video ball_tracking_example.mp4
# python ball_tracking.py

# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
#greenLower = (29, 86, 6)
#greenUpper = (200, 255, 64)
pts = deque(maxlen=args["buffer"])

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    camera = cv2.VideoCapture(0)

# otherwise, grab a reference to the video file
else:
    camera = cv2.VideoCapture(args["video"])
    
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (600,450))

# keep looping
while True:
    # grab the current frame
    (grabbed, frame) = camera.read()

    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if args.get("video") and not grabbed:
        break

    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600)
    # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#    h, s, v = cv2.split(hsv)
#    h +=10 # 4
#    mask0=h*h>177
#    h_final = np.where(mask0, 179,h)
    
#    s +=100 # 5
#    mask1=s*s>255
#    s_final = np.where(mask1, 255, s)
#    
#    v +=0 # 6
#    mask2=v*v>255
#    v_final = np.where(mask2, 255, v)
#    
#    hsv_final = cv2.merge((h_final, s_final, v_final))
    
    #mask3=cv2.merge((mask0,mask1,mask2))
    height,width,channels = frame.shape
    h=int(width/3),int(2*width/3)
    v=int(height/3),int(2*height/3)
    for i in range (2):    
        cv2.line(frame, (0,v[i]),(width,v[i]) , (255, 100,0 ), thickness=3)
        cv2.line(frame, (h[i],0),(h[i],height) , (255, 100,0 ), thickness=3)
    
#    hsv_final = cv2.erode(hsv_final, None, iterations=2)
#    hsv_final = cv2.dilate(hsv_final, None, iterations=2)
#    frame=cv2.cvtColor(hsv_final, cv2.COLOR_HSV2BGR)
    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, greenLower, greenUpper)
#    mask = cv2.inRange(hsv_final, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None



    # only proceed if at least one contour was found
    
    

    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        centro=0
        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            if ((int(y) > v[0]) and (int(y) < v[1])):
                            if ((int(x) > h[0]) and (int(x) < h[1])):
                                cv2.circle(frame, (int(x), int(y)), int(radius),
                                           (0, 255, 0), 2)
                                centro=1
                                cv2.circle(frame, center, 5, (0, 255, 0), -1)
                                text = "Caliente"
                                cv2.putText(frame, text, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), lineType=cv2.LINE_AA) 
                            else:
                                cv2.circle(frame, (int(x), int(y)), int(radius),
                                           (0, 0, 255), 2)
                                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                                centro=0
                                text = "Frio"
                                cv2.putText(frame, text, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), lineType=cv2.LINE_AA) 
            else:
                            cv2.circle(frame, (int(x), int(y)), int(radius),
                                       (0, 0, 255), 2)
                            cv2.circle(frame, center, 5, (0, 0, 255), -1)
                            text = "Frio"
                            cv2.putText(frame, text, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), lineType=cv2.LINE_AA) 
                            centro=0
           
    # update the points queue
    pts.appendleft(center)

    # loop over the set of tracked points
    for i in range(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        if centro == 1 and radius>10:
            cv2.line(frame, pts[i - 1], pts[i], (0, 255, 0), thickness)
        
        elif centro == 0 and radius>10:
            cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    out.write(frame)

    # show the frame to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
        
    

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break


# cleanup the camera and close any open windows
out.release()
camera.release()
cv2.destroyAllWindows()