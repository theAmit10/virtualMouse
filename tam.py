import cv2
import numpy as np
import tah as htm
import time
#import autopy

import pyautogui
import mouse
 


pyautogui.FAILSAFE = False
##########################
wCam, hCam = 640, 480

#wCam, hCam = 1040, 780
frameR = 100 # Frame Reduction
smoothening = 7
tipIds = [4, 8, 12, 16, 20]
#########################

pTime = 0
plocX, plocY = 0,
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1 , detectionCon=0.7, trackCon=0.7)
#wScr, hScr = autopy.screen.size()
wScr, hScr = pyautogui.size() # get the size of the screen




# print(wScr, hScr)

while True:
    # 1. Find hand Landmarks
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = detector.findHands(img)
    lmList, bbox = detector.tafindPosition(img)
    #print(lmList)
    #print(len(lmList))
    # 2. Get the tip of the index and middle fingers
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:] # coordinates of index 
        x2, y2 = lmList[12][1:] # coordinates of middle finger
        # print(x1, y1, x2, y2)
    
    # 3. Check which fingers are up
    fingers = []
    if len(lmList) != 0:
        

        # Thumb
        if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
            fingers.append(1) # if the finger is open than we will append 1 else we append 0
        else:
            fingers.append(0)

        # 4 Fingers
        for id in range(1, 5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                fingers.append(1)# if the finger is open than we will append 1 else we append 0
            else:
                fingers.append(0)

        print(fingers)
        #totalFingers = fingers.count(1)


    if len(lmList) != 0:
        #cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), # getting a particular area where only mouse move
        #(255, 0, 255), 2)
        # 4. Only Index Finger : Moving Mode
        if fingers[1] == 1 and fingers[2] == 0:
            # 5. Convert Coordinates
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr)) # interp is used to convert from one range to another range
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
            # 6. Smoothen Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening
        
            # 7. Move Mouse
            #autopy.mouse.move(wScr - clocX, clocY)  -> to inverse the screen value we have to do wScr - clocY -> clocY is the converted value
            op = wScr - clocX
            pyautogui.moveRel(op, clocY,duration=2)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED) # whenenver we are in moving mode it show us a circle
            plocX, plocY = clocX, clocY
            
        # 8. Both Index and middle fingers are up : Clicking Mode
        if fingers[1] == 1 and fingers[2] == 1:
            # 9. Find distance between fingers
            length, img, lineInfo = detector.findDistance(8, 12, img)
            print(length)
            # 10. Click mouse if distance short
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]),
                15, (0, 255, 0), cv2.FILLED)
                #autopy.mouse.click()
                #pyautogui.click()





    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
    (255, 0, 0), 3)
    # 12. Display
    cv2.imshow("Image", img)
    if(cv2.waitKey(10) & 0xFF == ord('q') ):
        break