import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as img
import pytesseract
from PIL import Image
import glob

def colort(color):
    if(color[2]>100 and color[1]<=color[2] and color[2] > color[0] + 35):
        #(color[2] > 100 and color[1] < 60 and color[0] < 60)
        #or (color[2] < 100 and color[1] < 80 and color[0] < 50 and color[2] > color[0] and color[2] > color[1])
        #or (color[2] > 150 and color[1] <= color[2] and color[0] < 100)
        #or ((color[2] - color[0]) > 50 and color[2] > color[1] and color[2] > color[0])):
        return True
    else:
        return False

def processLog(filename):
    #Open this image and make a Numpy version for easy processing
    im = Image.open(filename).convert('RGBA').convert('RGB')
    #im = cv2.imread(filename, cv2.COLOR_BGR2RGB)
    imnp = np.array(im)
    h, w = imnp.shape[:2]

    #Get list of unique colours...
    #Arrange all pixels into a tall column of 3 RGB values and find unique rows (colours)
    colors, counts = np.unique(imnp.reshape(-1, 3), axis = 0, return_counts = 1)

    #Iterate through unique colours
    per = 0.00

    for index, color in enumerate(colors):
        count = counts[index]
        proportion = (100 * count) / (h * w)
        if(colort(color)):
            #print('color: {}, count: {}, proportation: {:.2f}%'.format(color, count, proportion))
            per = per + proportion

    print('per: {:.2f}%'.format(per))

    return round(per, 2)

plt.style.use('dark_background' )

test1=[]
test2=[]

for te in range(1, 51):
    #원본 이미지와 그레이 스케일 이미지 생성
    print('elect/elect' + str(te) + '.jpg')
    img_ori = cv2.imread('elect/elect' + str(te) + '.jpg')
    height, width, channel = img_ori.shape

    gray = cv2.cvtColor(img_ori, cv2.COLOR_BGR2GRAY)

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

    #cv2.imshow('Ecar_thresh', img_thresh)

    #윤곽선 찾기
    contours, _ = cv2.findContours(
        img_thresh,
        mode=cv2.RETR_LIST,
        method=cv2.CHAIN_APPROX_SIMPLE
    )

    temp_result = np.zeros((height, width, channel), dtype=np.uint8)

    cv2.drawContours(temp_result, contours=contours, contourIdx=-1, color=(255, 255, 255))


    #윤곽선 그리기

    #cv2.imshow('Ecar_contour', temp_result)

    #윤곽선을 감싸는 사각형 그리기
    contours_dict = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(temp_result, pt1=(x, y), pt2=(x+w, y+h), color=(255, 255, 255), thickness=2)
        
        contours_dict.append({
            'contour':contour,
            'x':x,
            'y':y,
            'w':w,
            'h':h,
            'cx':x+(w/2),   #중심좌표1
            'cy':y+(h/2)    #중심좌표2
        })

    #번호판의 숫자가 아닐만한것들 제외하고 사각형 그리기
    MIN_AREA = 80
    MIN_WIDTH, MIN_HEIGHT = 2, 8
    MIN_RATIO, MAX_RATIO = 0.25, 1.0

    possible_contours = []

    cnt = 0
    for d in contours_dict:
        area = d['w'] * d['h']  #면적
        ratio = d['w'] / d['h'] #비율

        if area > MIN_AREA and d['w'] > MIN_WIDTH and d['h'] > MIN_HEIGHT and MIN_RATIO < ratio < MAX_RATIO:
            d['idx'] = cnt
            cnt += 1
            possible_contours.append(d)

    temp_result = np.zeros((height, width, channel), dtype=np.uint8)

    for d in possible_contours:
        cv2.rectangle(temp_result, pt1=(d['x'], d['y']), pt2=(d['x']+d['w'], d['y']+d['h']), color=(255, 255, 255), thickness=2)
        
    #cv2.imshow('Ecar_filteredRect', temp_result)

    #순차적으로 정렬된 사각형을 찾기

    MAX_DIAG_MULTIPLYER = 5 # 5
    MAX_ANGLE_DIFF = 12.0 # 12.0
    MAX_AREA_DIFF = 0.5 # 0.5
    MAX_WIDTH_DIFF = 0.8
    MAX_HEIGHT_DIFF = 0.4
    MIN_N_MATCHED = 3 # 3

    def find_chars(contour_list):
        matched_result_idx = []

        for d1 in contour_list:
            matched_contours_idx = []
            for d2 in contour_list:
                if d1['idx'] == d2['idx']:
                    continue

                dx = abs(d1['cx'] - d2['cx'])
                dy = abs(d1['cy'] - d2['cy'])

                diagonal_length1 = np.sqrt(d1['w'] * 2 + d1['h'] **2)
                
                distance = np.linalg.norm(np.array([d1['cx'], d1['cy']]) - np.array([d2['cx'], d2['cy']]))
                if dx == 0:
                    angle_diff = 90
                else:
                    angle_diff = np.degrees(np.arctan(dy / dx))
                area_diff = abs(d1['w'] * d1['h'] - d2['w'] * d2['h']) / (d1['w'] * d1['h'])
                width_diff = abs(d1['w'] - d2['w']) / d1['w']
                height_diff = abs(d1['h'] - d2['h']) / d1['h']

                if distance < diagonal_length1 * MAX_DIAG_MULTIPLYER and angle_diff < MAX_ANGLE_DIFF and area_diff < MAX_AREA_DIFF and width_diff < MAX_WIDTH_DIFF and height_diff < MAX_HEIGHT_DIFF:
                    matched_contours_idx.append(d2['idx'])

            matched_contours_idx.append(d1['idx'])

            #연속되는 윤곽선이 3개 이하일때 무시
            if len(matched_contours_idx) < MIN_N_MATCHED:
                continue

            matched_result_idx.append(matched_contours_idx)

            #탈락한 요소들을 한번더 검사
            unmatched_contour_idx = []
            for d4 in contour_list:
                if d4['idx'] not in matched_contours_idx:
                    unmatched_contour_idx.append(d4['idx'])

            unmatched_contour = np.take(possible_contours, unmatched_contour_idx)

            recursive_contour_list = find_chars(unmatched_contour)
            
            for idx in recursive_contour_list:
                matched_result_idx.append(idx)
                
            break

        return matched_result_idx        

    result_idx = find_chars(possible_contours)

    #조건으로 필터링한 결과 출력
    matched_result = []
    for idx_list in result_idx:
        matched_result.append(np.take(possible_contours, idx_list))

    temp_result = np.zeros((height, width, channel), dtype=np.uint8)

    for r in matched_result:
        for d in r:
            cv2.rectangle(temp_result, pt1=(d['x'], d['y']), pt2=(d['x']+d['w'], d['y']+d['h']), color=(255, 255, 255), thickness=2)

    #cv2.imshow('Ecar_fil', temp_result)

    #번호판이 삐뚫어져 있으면 번호판 돌리기


    PLATE_WIDTH_PADDING = 1.3 # 1.3
    PLATE_HEIGHT_PADDING = 1.5 # 1.5
    MIN_PLATE_RATIO = 3
    MAX_PLATE_RATIO = 10

    plate_imgs = []
    plate_infos = []

    ori_plate_imgs = []
    ori_plate_infos = []

    for i, matched_chars in enumerate(matched_result):
        sorted_chars = sorted(matched_chars, key=lambda x: x['cx'])

        plate_cx = (sorted_chars[0]['cx'] + sorted_chars[-1]['cx']) / 2
        plate_cy = (sorted_chars[0]['cy'] + sorted_chars[-1]['cy']) / 2
        
        plate_width = (sorted_chars[-1]['x'] + sorted_chars[-1]['w'] - sorted_chars[0]['x']) * PLATE_WIDTH_PADDING
        
        sum_height = 0
        for d in sorted_chars:
            sum_height += d['h']

        plate_height = int(sum_height / len(sorted_chars) * PLATE_HEIGHT_PADDING)
        
        triangle_height = sorted_chars[-1]['cy'] - sorted_chars[0]['cy']
        triangle_hypotenus = np.linalg.norm(
            np.array([sorted_chars[0]['cx'], sorted_chars[0]['cy']]) - 
            np.array([sorted_chars[-1]['cx'], sorted_chars[-1]['cy']])
        )
        
        angle = np.degrees(np.arcsin(triangle_height / triangle_hypotenus))
        
        rotation_matrix = cv2.getRotationMatrix2D(center=(plate_cx, plate_cy), angle=angle, scale=1.0)
            
        #thresh한 이미지
        img_rotated = cv2.warpAffine(img_thresh, M=rotation_matrix, dsize=(width, height))

        #thresh 번호판 있는곳만 짜르기
        img_cropped = cv2.getRectSubPix(
            img_rotated, 
            patchSize=(int(plate_width) + 25, int(plate_height)), 
            center=(int(plate_cx), int(plate_cy))
        )
        
        #ori 이미지
        img_ori_copyed =  cv2.cvtColor(img_ori.copy(), cv2.COLOR_BGR2RGB)
        ori_img_rotated = cv2.warpAffine(img_ori_copyed, M=rotation_matrix, dsize=(width, height))

        #ori 번호판 있는곳만 짜르기
        ori_img_cropped = cv2.getRectSubPix(
            #img_ori_copyed,
            ori_img_rotated,
            patchSize=(int(plate_width), int(plate_height)), 
            center=(int(plate_cx), int(plate_cy))
        )
        
        if img_cropped.shape[1] / img_cropped.shape[0] < MIN_PLATE_RATIO or img_cropped.shape[1] / img_cropped.shape[0] < MIN_PLATE_RATIO > MAX_PLATE_RATIO:
            continue
        
        plate_imgs.append(img_cropped)
        plate_infos.append({
            'x': int(plate_cx - plate_width / 2),
            'y': int(plate_cy - plate_height / 2),
            'w': int(plate_width),
            'h': int(plate_height)
        })

        ori_plate_imgs.append(ori_img_cropped)

        #plt.subplot(len(matched_result), 1, i+1)
        #plt.imshow(ori_img_cropped, cmap='gray')


    #정확도 향상을 위해 한번더 쓰레쉬 홀딩, 컨투어 찾기    

    longest_idx, longest_text = 0, 0
    plate_chars = []

    for i, plate_img in enumerate(plate_imgs):
        plate_img = cv2.resize(plate_img, dsize=(0, 0), fx=1.6, fy=1.6)
        _, plate_img = cv2.threshold(plate_img, thresh=0.0, maxval=255.0, type=cv2.THRESH_BINARY | cv2.THRESH_OTSU)


        #컨투어 찾기
        contours, _ = cv2.findContours(plate_img, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)
        
        plate_min_x, plate_min_y = plate_img.shape[1], plate_img.shape[0]
        plate_max_x, plate_max_y = 0, 0

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            area = w * h
            ratio = w / h

            if area > MIN_AREA         and w > MIN_WIDTH and h > MIN_HEIGHT         and MIN_RATIO < ratio < MAX_RATIO:
                if x < plate_min_x:
                    plate_min_x = x
                if y < plate_min_y:
                    plate_min_y = y
                if x + w > plate_max_x:
                    plate_max_x = x + w
                if y + h > plate_max_y:
                    plate_max_y = y + h
                    
        img_result = plate_img[plate_min_y:plate_max_y, plate_min_x:plate_max_x]
        
        img_result = cv2.GaussianBlur(img_result, ksize=(3, 3), sigmaX=0)
        _, img_result = cv2.threshold(img_result, thresh=0.0, maxval=255.0, type=cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        img_result = cv2.copyMakeBorder(img_result, top=10, bottom=10, left=10, right=10, borderType=cv2.BORDER_CONSTANT, value=(0,0,0))

        #번호판인지 확인을 위해 pytesseract를 이용
        chars = pytesseract.image_to_string(img_result, lang='kor', config='--psm 7 --oem 0')

        result_chars = ''
        has_digit = False

        #번호판으로 예상되는 것들에 글자나 숫자가 있는지 확인
        for c in chars:
            if ord('가') <= ord(c) <= ord('힣') or c.isdigit():
                if c.isdigit():
                    has_digit = True
                result_chars += c
        plate_chars.append(result_chars)

        if has_digit and len(result_chars) > longest_text:
            longest_idx = i
        #plt.subplot(len(plate_imgs), 1, i+1)
        #plt.imshow(img_result, cmap='gray')
            
    print('longest: ' + str(longest_idx))
    info = plate_infos[longest_idx]

    img_out = img_ori.copy()

    cv2.rectangle(img_out, pt1=(info['x'], info['y']), pt2=(info['x']+info['w'], info['y']+info['h']), color=(255,0,0), thickness=2)
    #cv2.imshow('originFile', img_out)
    #cv2와 matplot은 각각 색구분 순서가 BGR와 RGB 이기 때문에 변환이 필요하다
    ConvertedImg = cv2.cvtColor(ori_plate_imgs[longest_idx], cv2.COLOR_RGB2BGR)
    #cv2.imshow('numberPlateShow', ConvertedImg)
    cv2.imwrite('numPlate.jpg', ConvertedImg)

    #Iterate over all images called "log*png" in current directory
    #for filename in glob.glob('test*png'):
    value = processLog('numPlate.jpg')
    test1.append(value)
    print(te)
    test2.append(te)

print(test1)
print(test2)

plt.scatter(test2, test1)
plt.xlabel('Number Plate')
plt.ylabel('%')

plt.title('Nomal Car Distribution Chart')
plt.xlim(0,51)
plt.ylim(0, 100)
plt.show()
