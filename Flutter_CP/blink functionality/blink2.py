import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot
import time
from tkinter import Tk, messagebox
import threading

def show_alert(message):
    """ Show a pop-up alert using Tkinter """
    def alert():
        root = Tk()
        root.withdraw()  # Hide the main window
        messagebox.showinfo("Alert", message)
        root.destroy()

    # Use threading to show alert without blocking
    threading.Thread(target=alert).start()

cap = cv2.VideoCapture(0)
detector = FaceMeshDetector(maxFaces=4)
plotY = LivePlot(640, 360, [0, 50], invert=False)

idList = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
LratioList = []
RratioList = []
blinkCounter = 0
counter = 0
color = (255, 0, 255)
ratioAvg = 0
threshold = 34
start_time = None  # Initialize start_time as None
first_60_seconds_passed = False
running = True

while running:
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    success, img = cap.read()
    img, faces = detector.findFaceMesh(img, draw=False)

    if faces:
        if start_time is None:  # Start the timer when the first face is detected
            start_time = time.time()

        face = faces[0]
        for id in idList:
            cv2.circle(img, face[id], 5, (255, 0, 255), cv2.FILLED)

        leftUp = face[159]
        leftDown = face[23]
        leftLeft = face[130]
        leftRight = face[243]

        rightUp = face[386]
        rightDown = face[374]
        rightLeft = face[362]
        rightRight = face[263]

        LlengthHor, _ = detector.findDistance(leftLeft, leftRight)
        LlengthVer, _ = detector.findDistance(leftUp, leftDown)

        RlengthHor, _ = detector.findDistance(rightLeft, rightRight)
        RlengthVer, _ = detector.findDistance(rightUp, rightDown)

        cv2.line(img, leftUp, leftDown, color, 3)
        cv2.line(img, leftLeft, leftRight, color, 3)
        cv2.line(img, rightUp, rightDown, color, 3)
        cv2.line(img, rightLeft, rightRight, color, 3)

        Lratio = int((LlengthVer / LlengthHor) * 100)
        LratioList.append(Lratio)
        if len(LratioList) > 3:
            LratioList.pop(0)
        LratioAvg = sum(LratioList) / len(LratioList)

        Rratio = int((RlengthVer / RlengthHor) * 100)
        RratioList.append(Rratio)
        if len(RratioList) > 3:
            RratioList.pop(0)
        RratioAvg = sum(RratioList) / len(RratioList)

        if Lratio > threshold:
            if LratioAvg < threshold and counter == 0:
                blinkCounter += 1
                counter = 1
                color = (0, 255, 0)
        elif Lratio > 29:
            if (LratioAvg - Lratio) > 5 and counter == 0:
                blinkCounter += 1
                counter = 1
                color = (0, 255, 0)
        else:
            if (LratioAvg - Lratio) > 2 and counter == 0:
                blinkCounter += 1
                counter = 1
                color = (0, 255, 0)
        if counter != 0:
            counter += 1
            if counter > 10:
                counter = 0
                color = (255, 0, 255)

        cvzone.putTextRect(img, f'Blink Counter: {blinkCounter}', (50, 100), colorR=color)
        LimgPlot = plotY.update(LratioAvg, color)
        RimgPlot = plotY.update(RratioAvg, color)

        img = cv2.resize(img, (640, 360))
        imgStack = cvzone.stackImages([img, LimgPlot, RimgPlot], 3, 1)
    else:
        img = cv2.resize(img, (640, 360))
        imgPlot = plotY.update(ratioAvg, color)
        imgStack = cvzone.stackImages([img, imgPlot, imgPlot], 3, 1)

    cv2.imshow("Image", imgStack)

    # Update timer and check blink rate
    if start_time is not None:
        elapsed_time = int(time.time() - start_time)
        cvzone.putTextRect(imgStack, f'Time elapsed: {elapsed_time} seconds', (50, 50), colorR=(0, 255, 0))

        if elapsed_time > 60:
            if not first_60_seconds_passed:
                first_60_seconds_passed = True  # Mark that the first 60 seconds have passed

            if first_60_seconds_passed:
                if elapsed_time > 0:
                    blink_rate = blinkCounter / (elapsed_time / 60)  # Blinks per minute

                    if blink_rate < 17:
                        # Display the alert without blocking
                        show_alert(f"Your blink rate is too low: {blink_rate:.2f} blinks per minute!")

        if elapsed_time > 120:  # Example: Stop after 2 minutes
            running = False
            cv2.destroyAllWindows()
            print(f"You blinked {blinkCounter} times!")

    cv2.waitKey(25)