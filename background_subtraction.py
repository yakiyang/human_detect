import numpy as np
import cv2
import time
import serial


class BackGroundSubtractor:

	def __init__(self,alpha,firstFrame):
		self.alpha  = alpha
		self.backGroundModel = firstFrame

    def setBackground(self,frame):
		self.backGroundModel = frame
	
        def getForeground(self,frame):

		self.backGroundModel =  frame * self.alpha + self.backGroundModel * (1 - self.alpha)
		return cv2.absdiff(self.backGroundModel.astype(np.uint8),frame)

s=serial.Serial("/dev/ttyACM0",115200,timeout=0.5)

cam = cv2.VideoCapture(0)
cam.set(3,  640)
cam.set(4, 480)
section=[0 ,53 ,103 ,150 ,195 ,238 ,280 ,320 ,360 ,405 ,450 ,500 ,553 ,608]
center_section=7
now_degree=0
# Just a simple function to perform
# some filtering before any further processing.
def denoise(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.GaussianBlur(frame,(21,21),0)
    
    return frame

ret,frame = cam.read()
if ret is True:
	backSubtractor = BackGroundSubtractor(0.3,denoise(frame))
	run = True
else:
	run = False

flag=0 #判斷是否運行background substraction的符號
while(run):
        #讀取arduino來的data
        str_receive=s.read()
        
        #在傳送位置資料後，arduino會因資料傳輸延遲，而無法立即將background subtraction停止，因此須先將自己block，避免錯誤的資料傳輸
        if flag==1 :
            while str_receive.decode() !='1' :
                print("flag=1 receive!=1");
                str_receive=s.read()

        print("receive:")
        print(str_receive.decode())
        print("flag:")
        print(flag)

        #flag=1時馬達旋轉，暫停background subtraction，等待接收馬達停止訊號（0），將flag設為0（馬達停止狀態）
        #buffer會保留舊的影像資料，因此須先將影像讀出
        while  flag == 1:
            str_receive=s.read()
            if str_receive.decode() == '0':
                ret,frame = cam.read()
                ret,frame = cam.read()
                ret,frame = cam.read()
                ret,frame = cam.read()
                flag=0
            print("receive:")
            print(str_receive.decode())
            print("flag:")
            print(flag)

        # Read a frame from the camera
        ret,frame = cam.read()

	# If the frame was properly read.
	if ret is True:
        print("start background substrution")
		# get the foreground
		foreGround = backSubtractor.getForeground(denoise(frame))
        
		# Apply thresholding on the background and display the resulting mask
		ret, mask = cv2.threshold(foreGround, 15, 255, cv2.THRESH_BINARY)
                
		# Note: The mask is displayed as a RGB image, you can
		# display a grayscale image by converting 'foreGround' to
		# a grayscale before applying the threshold.
		mask = cv2.dilate(mask, None, iterations=2)
                cnts, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
 
                #設定抓到物體大小臨界值
                x1=1000
                y1=1000
                x2=0
                y2=0
                #將抓到的零碎區塊合成為一大區塊
                for c in cnts:
                    if cv2.contourArea(c) < 750:
                        continue
                    (x ,y ,w ,h)=cv2.boundingRect(c)
                    if x < x1 :
                        x1=x
                    if y < y1 :
                        y1=y
                    if x+w >= x2 :
                        x2=x+w
                    if y+h >= y2 :
                        y2=y+h

                #若抓到的物體寬大於高則不抓（判定應該不是人體）
                if abs(x2-x1) > abs(y2-y1):
                    x1=0
                    y1=0
                    x2=1000
                    y2=1000

                human_width=abs(x2-x1)
                #若抓到物體寬度小於250則不抓
                if human_width <= 250 :
                    cv2.rectangle(frame ,(x1 ,y1) ,(x2 ,y2) ,(0 ,0 ,255) ,2)
                    #計算物體中心位置
                    x_cen=(x2+x1)/2
                    new_section=7
                    #判斷人體中心位置所屬區塊
                    #left
                    if x_cen>=section[0] and x_cen<section[1] :
                        new_section=1
                    if x_cen>=section[1] and x_cen<section[2] :
                        new_section=2
                    if x_cen>=section[2] and x_cen<section[3] :
                        new_section=3
                    if x_cen>=section[3] and x_cen<section[4] :
                        new_section=4
                    if x_cen>=section[4] and x_cen<section[5] :
                        new_section=5
                    if x_cen>=section[5] and x_cen<section[6] :
                        new_section=6
                    if x_cen>=section[6] and x_cen<section[7] :
                        new_section=7
                    #rigth
                    if x_cen>=section[7] and x_cen<section[8] :
                        new_section=8
                    if x_cen>=section[8] and x_cen<section[9] :
                        new_section=9
                    if x_cen>=section[9] and x_cen<section[10] :
                        new_section=10
                    if x_cen>=section[10] and x_cen<section[11] :
                        new_section=11
                    if x_cen>=section[11] and x_cen<section[12] :
                        new_section=12
                    if x_cen>=section[12] and x_cen<section[13] :
                        new_section=13
                    #計算旋轉角度並傳送給arduino
                    rotate_degree=-(new_section-center_section)*5
                    now_degree=now_degree+rotate_degree
                    send_str=""
                    send_str=str(rotate_degree)
                    s.write(send_str.encode())
                    #send data後，設定flag為1暫停background subtraction，等待馬達旋轉
                    flag=1
                    print("==================")
                    print("rotate degree:")
                    print(rotate_degree)
                    print("now section:")
                    print(new_section)
                    print("==================")

                #分割影像中各角度區塊
                lineThickness = 1
                cv2.line(frame, (320, 0), (320, 480), (0,255,0), lineThickness)
                cv2.line(frame, (360, 0), (360, 480), (0,255,0), lineThickness)
                cv2.line(frame, (405, 0), (405, 480), (0,255,0), lineThickness)
                cv2.line(frame, (450, 0), (450, 480), (0,255,0), lineThickness)
                cv2.line(frame, (500, 0), (500, 480), (0,255,0), lineThickness)
                cv2.line(frame, (553, 0), (553, 480), (0,255,0), lineThickness)
                cv2.line(frame, (608, 0), (608, 480), (0,255,0), lineThickness)
                cv2.line(frame, (280, 0), (280, 480), (0,255,0), lineThickness)
                cv2.line(frame, (238, 0), (238, 480), (0,255,0), lineThickness)
                cv2.line(frame, (195, 0), (195, 480), (0,255,0), lineThickness)
                cv2.line(frame, (150, 0), (150, 480), (0,255,0), lineThickness)
                cv2.line(frame, (103, 0), (103, 480), (0,255,0), lineThickness)
                cv2.line(frame, (53, 0), (53, 480), (0,255,0), lineThickness)
                cv2.line(frame, (0, 0), (0, 480), (0,255,0), lineThickness)
                
                rotate_degree=0
                new_section=7
                
		cv2.imshow('input',frame)
		key = cv2.waitKey(10) & 0xFF
	else:
		break

        if key == 27:
		break

cam.release()
