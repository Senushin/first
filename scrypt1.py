from flask import Flask, render_template, Response, send_file
import cv2
import numpy as np
import time

videoPath = 'static/video.ogv'

app = Flask(__name__)
cap = cv2.VideoCapture(videoPath)

fps = int(cap.get(cv2.CAP_PROP_FPS))

lower_blue = np.array([90, 50, 30], dtype = "uint8")
upper_blue = np.array([140, 255, 255], dtype = "uint8")

@app.route('/')
def index():
    return render_template('index.html')

def gen():
    counter = 0
    counter2 =0
    state = 0
    ti = 1
    ki = 1
    while (cap.isOpened()):

        rval, frame = cap.read()
        if rval == True:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV )
            thresh = cv2.inRange(hsv, lower_blue, upper_blue)
            blur = cv2.GaussianBlur(thresh,(5,5),1)
            kernelSize = 4
            element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*kernelSize+1,
            2*kernelSize+1),(kernelSize, kernelSize))
            imOpened = cv2.morphologyEx(blur, cv2.MORPH_OPEN,element,iterations=3)
            moments = cv2.moments(imOpened, 1)
            dM01 = moments['m01']
            dM10 = moments['m10']
            dArea = moments['m00']
            contours, hierarchy = cv2.findContours(imOpened, cv2.RETR_LIST ,
            cv2.CHAIN_APPROX_SIMPLE )
            m00 = [None]*len(contours)
            for i,cntr in enumerate (contours):
                M = cv2.moments(cntr)
                m00[i] = M["m00"]
            if m00:
                maxV = max(m00)
                maxI = m00.index(max(m00))
                if m00[maxI]>2000:
                    x,y,w,h = cv2.boundingRect(contours[maxI])
                    cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,255), 3)
            if dArea > 7500:
                x = int(dM10 / dArea)
                y = int(dM01 / dArea)
                #cv2.circle(frame, (x, y), 10, (0,0,255), -1)
                if x<10 or x>1210 or y<100 or y>670 and state==1:
                    counter+=1
                    if counter>=4:
                        cv2.imwrite('out_'+str(ti)+'.jpg', frame)
                        yield (b'--frame2\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + open('out_'+str(ti)+'.jpg', 'rb').read() + b'\r\n')
                        ti+=1
                        state =0
                        counter = 0
                if 20<x<1200 and 20<y<710 and state ==0:
                    counter2+=1
                    if counter2>=3:
                        cv2.imwrite('in_'+str(ki)+'.jpg', frame)
                        yield (b'--frame2\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + open('in_'+str(ti)+'.jpg', 'rb').read() + b'\r\n')
                        ki+=1
                        state =1
                        counter2=0
            cv2.imwrite('t.jpg', frame)
            time.sleep(1/fps)
            yield (b'--frame1\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')
        else:
            cap.release()
            break


@app.route ('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame1')

@app.route ('/out_1')
def out_1():
    filename = 'out_1.jpg'
    return send_file(filename, mimetype='image/jpg')
@app.route ('/out_2')
def out_2():
    filename = 'out_2.jpg'
    return send_file(filename, mimetype='image/jpg')
@app.route ('/in_1')
def in_1():
    filename = 'in_1.jpg'
    return send_file(filename, mimetype='image/jpg')
@app.route ('/in_2')
def in_2():
    filename = 'in_2.jpg'
    return send_file(filename, mimetype='image/jpg')
@app.route ('/in_3')
def in_3():
    filename = 'in_3.jpg'
    return send_file(filename, mimetype='image/jpg')


if __name__ == '__main__':
    app.run(host = '7.7.7.7')
