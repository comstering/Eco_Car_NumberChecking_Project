import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as img

#번호판 그림 사이즈를 조정하기
img_plate = cv2.imread('numPlate.jpg', cv2.IMREAD_COLOR)
img_resize = cv2.resize(img_plate, dsize=(300, 200), interpolation=cv2.INTER_CUBIC)


img_dst = img_resize[15:80, 10:35]
img_dst2 = img_resize[100:185, 10:35]
img_dst3 = img_resize[70:175, 265:290]


cv2.imshow("src", img_resize)

cv2.imwrite('2/first.jpg', img_dst)
cv2.imwrite('2/second.jpg', img_dst2)
cv2.imwrite('2/third.jpg', img_dst3)

plt.subplot(3, 1, 1)
plt.imshow(cv2.cvtColor(img_dst, cv2.COLOR_BGR2RGB))   
plt.subplot(3, 1, 2)
plt.imshow(cv2.cvtColor(img_dst2, cv2.COLOR_BGR2RGB))  
plt.subplot(3, 1, 3)
plt.imshow(cv2.cvtColor(img_dst3, cv2.COLOR_BGR2RGB))  


plt.show()

cv2.waitKey(0)
cv2.destroyAllWindos()


"""
height, width, channel = img_resize.shape

gray = cv2.cvtColor(img_resize, cv2.COLOR_BGR2GRAY)

structuringElement = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

imgTopHat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, structuringElement)
imgBlackHat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, structuringElement)

imgGrayscalePlusTopHat = cv2.add(gray, imgTopHat)
gray = cv2.subtract(imgGrayscalePlusTopHat, imgBlackHat)


#노이즈를 줄이기 위한 가우시안 블러
img_blurred = cv2.GaussianBlur(gray, ksize=(5, 5), sigmaX=0)

#이미지를 구분하기 쉽게 하기 위한 쓰레쉬 홀딩
img_thresh = cv2.adaptiveThreshold(
    img_blurred,
    maxValue=255.0,
    adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    thresholdType=cv2.THRESH_BINARY_INV,
    blockSize=19,
    C=9
)

cv2.imshow("thresh", img_thresh)


contours, _ = cv2.findContours(
    img_thresh,
    mode=cv2.RETR_LIST,
    method=cv2.CHAIN_APPROX_SIMPLE
)

temp_result = np.zeros((height, width, channel), dtype=np.uint8)

cv2.drawContours(temp_result, contours=contours, contourIdx=-1, color=(255, 255, 255))

cv2.imshow("temp", temp_result)
"""
