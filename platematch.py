import cv2
import numpy as np
from matplotlib import pyplot as plt

def _init_(self):
    pass

def readImg(filepath):
    img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    return img

def diffImg(img1, img2):
    # Initiate SIFT detector
    orb = cv2.ORB_create()

    # find the keypoints and descriptors with SiFT
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    # create BFMatcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = True)

    # Match descriptors.
    matches = bf.match(des1, des2)

    # Sort them in the order of their distance.
    res = None
    matches = sorted(matches, key = lambda x:x.distance)
    res = cv2.drawMatches(img1, kp1, img2, kp2, matches[:30], res, flags = 0)
    cv2.imshow('afdas', res)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # BFMatcher with default params
    #df = cv2.BFMatcher()
    #matches = df.knnMatch(des1, des2, k = 2)

    # Apply ratio test
    #good = []
    #for m, n in matches:
    #    if m.distance < 0.75 * n.distance:
    #        good.append([m])

    # Draw first 10 matches.
    #knn_image = cv2.drawMatchesKnn(img1, kp1, img2, kp2, good, None, flags = 0)
    #plt.imshow(knn_image)
    #plt.show()

def run():
    filepath1 = 'image/elect1_sub.jpg'
    filepath2 = 'image/elect1_sub.jpg'

    img1 = readImg(filepath1)
    img2 = readImg(filepath2)

    diffImg(img1, img2)

run()
