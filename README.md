# Eco_Car_NumberChecking_Project

#getNumber.py
---------------
50개의 데이터를 차트로 표현하는 소스코드 수정하는부분

51, 52줄의

print('elect/elect' + str(te) + '.jpg')

img_ori = cv2.imread('elect/elect' + str(te) + '.jpg')

->

print('number/' + str(te) + '.png')

img_ori = cv2.imread('number/' + str(te) + '.png')

#getNumber_test.py
----------------
하나의 데이터만을 확인하는 소스코드

#ColorCheck.py
----------------
번호판의 파란색부분은 RGB 값 [255, 255, 255]로 표현
