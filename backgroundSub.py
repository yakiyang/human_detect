import numpy as np
import cv2
import time
import math

def find_marker(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 35, 125)
    _ ,cnts,_ = cv2.findContours(edged.copy(), cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    c = max(cnts, key = cv2.contourArea)
    return c


def distance_to_camera(knownWidth, focalLength, perWidth):
    return (knownWidth * focalLength) / perWidth



class BackGroundSubtractor:
	def __init__(self,alpha,firstFrame):
		self.alpha  = alpha
		self.backGroundModel = firstFrame
    def setBackground(self,frame):
        self.backGroundModel =  frame
	def getForeground(self,frame):
		self.backGroundModel =  frame * self.alpha + self.backGroundModel * (1 - self.alpha)
		return cv2.absdiff(self.backGroundModel.astype(np.uint8),frame)



def denoise(frame):
    frame = cv2.cvtColor(frame ,cv2.COLOR_BGR2GRAY)
    #    frame = cv2.medianBlur(frame,5)
    frame = cv2.GaussianBlur(frame,(21,21),0)
    return frame


cam = cv2.VideoCapture(0)
cam.set(3, 640)
cam.set(4, 480)

ret,frame = cam.read()
if ret is True:
	backSubtractor = BackGroundSubtractor(0.3,denoise(frame))
	run = True
else:
	run = False

while(run):

	ret,frame = cam.read()
    k = cv2.waitKey(33)
    if k != -1:
       backSubtractor.setBackground(denoise(frame))
           
	if ret is True:
        
		foreGround = backSubtractor.getForeground(denoise(frame))
		ret, mask = cv2.threshold(foreGround, 15, 255, cv2.THRESH_BINARY)
        mask=cv2.dilate(mask,None,iterations=2)
        _ ,cnts ,_ = cv2.findContours(mask.copy() ,cv2.RETR_EXTERNAL ,cv2.CHAIN_APPROX_SIMPLE)
        

        x1=1000
        y1=1000
        x2=0
        y2=0
        angle=0
        for c in cnts:
            if cv2.contourArea(c) < 500 :
                continue
            (x ,y ,w ,h)=cv2.boundingRect(c)
            if x < x1 :
                x1=x
            if y < y1 :
                y1=y
            if x+w > x2 :
                x2=x+w
            if y+h > y2 :
                y2=y+h

        x=(x1+x2)/2
        section=7

        if x>0 and x<=53:
            section=0
        if x>53 and x<=103:
            section=1
        if x>103 and x<=150:
            section=2
        if x>150 and x<=195:
            section=3
        if x>195 and x<=238:
            section=4
        if x>238 and x<=280:
            section=5
        if x>280 and x<=320:
            section=6
        if x>320 and x<=360:
            section=7
        if x>360 and x<=405:
            section=8
        if x>405 and x<=450:
            section=9
        if x>450 and x<=500:
            section=10
        if x>500 and x<=553:
            section=11
        if x>553 and x<=608:
            section=12
        if x>608 and x<=640:
            section=13


        cv2.rectangle(frame ,(x1 ,y1) ,(x2 ,y2) ,(0 ,255 ,0) ,2)
        cv2.circle(frame,((x1+x2)/2,(y1+y2)/2), 3, (0,255,0), -1)

        #center
        cv2.line(frame ,(320 ,0) ,(320 ,480) ,(0 ,0 ,255) ,1)
        cv2.putText(frame, "7", (330,30), cv2.FONT_HERSHEY_SIMPLEX ,1 ,(0,0,255),2 ,cv2.LINE_AA);
    
        #right
        cv2.line(frame ,(360 ,0) ,(360 ,480) ,(0 ,0 ,255) ,1)
        cv2.putText(frame, "8", (370,30), cv2.FONT_HERSHEY_SIMPLEX ,1 ,(0,0,255),2 ,cv2.LINE_AA);
        cv2.line(frame ,(405 ,0) ,(405 ,480) ,(0 ,0 ,255) ,1)
        cv2.putText(frame, "9", (415,30), cv2.FONT_HERSHEY_SIMPLEX ,1 ,(0,0,255),2 ,cv2.LINE_AA);
        cv2.line(frame ,(450 ,0) ,(450 ,480) ,(0 ,0 ,255) ,1)
        cv2.putText(frame, "10", (460,30), cv2.FONT_HERSHEY_SIMPLEX ,1 ,(0,0,255),2 ,cv2.LINE_AA);
        cv2.line(frame ,(500 ,0) ,(500 ,480) ,(0 ,0 ,255) ,1)
        cv2.putText(frame, "11", (510,30), cv2.FONT_HERSHEY_SIMPLEX ,1 ,(0,0,255),2 ,cv2.LINE_AA);
        cv2.line(frame ,(553 ,0) ,(553 ,480) ,(0 ,0 ,255) ,1)
        cv2.putText(frame, "12", (563,30), cv2.FONT_HERSHEY_SIMPLEX ,1 ,(0,0,255),2 ,cv2.LINE_AA);
        cv2.line(frame ,(608 ,0) ,(608 ,480) ,(0 ,0 ,255) ,1)
        cv2.putText(frame, "13", (610,30), cv2.FONT_HERSHEY_SIMPLEX ,0.5 ,(0,0,255),1 ,cv2.LINE_AA);
        
        #left
        cv2.line(frame ,(280 ,0) ,(280 ,480) ,(0 ,0 ,255) ,1)
        cv2.putText(frame, "6", (290,30), cv2.FONT_HERSHEY_SIMPLEX ,1 ,(0,0,255),2 ,cv2.LINE_AA);
        cv2.line(frame ,(238 ,0) ,(238 ,480) ,(0 ,0 ,255) ,1)
        cv2.putText(frame, "5", (248,30), cv2.FONT_HERSHEY_SIMPLEX ,1 ,(0,0,255),2 ,cv2.LINE_AA);
        cv2.line(frame ,(195 ,0) ,(195 ,480) ,(0 ,0 ,255) ,1)
        cv2.putText(frame, "4", (200,30), cv2.FONT_HERSHEY_SIMPLEX ,1 ,(0,0,255),2 ,cv2.LINE_AA);
        cv2.line(frame ,(150 ,0) ,(150 ,480) ,(0 ,0 ,255) ,1)
        cv2.putText(frame, "3", (160,30), cv2.FONT_HERSHEY_SIMPLEX ,1 ,(0,0,255),2 ,cv2.LINE_AA);
        cv2.line(frame ,(103 ,0) ,(103 ,480) ,(0 ,0 ,255) ,1)
        cv2.putText(frame, "2", (113,30), cv2.FONT_HERSHEY_SIMPLEX ,1 ,(0,0,255),2 ,cv2.LINE_AA);
        cv2.line(frame ,(53 ,0) ,(53 ,480) ,(0 ,0 ,255) ,1)
        cv2.putText(frame, "1", (63,30), cv2.FONT_HERSHEY_SIMPLEX ,1 ,(0,0,255),2 ,cv2.LINE_AA);
        cv2.line(frame ,(0 ,0) ,(0 ,480) ,(0 ,0 ,255) ,1)
        cv2.putText(frame, "0", (10,30), cv2.FONT_HERSHEY_SIMPLEX ,1 ,(0,0,255),2 ,cv2.LINE_AA);

        #text
        cv2.putText(frame, str(section), (10,450), cv2.FONT_HERSHEY_SIMPLEX ,1 ,(255,0,0),2 ,cv2.LINE_AA);


        cv2.imshow('input',frame)
        time.sleep(1)
        key = cv2.waitKey(10) & 0xFF
#    else :
#        break

#	if key == 27:
#        break

cam.release()
cv2.destroyAllWindows()
