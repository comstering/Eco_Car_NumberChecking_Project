from PIL import Image
import numpy as np
import glob

def processLog(filename):
    print("Processing log: {}".format(filename))
    #Open this image and make a Numpy version for easy processing
    im = Image.open(filename).convert('RGBA').convert('RGB')
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
        if(color[0] < 100 & color[1] < 100 & color[2] > 120):
            print('color: {}, count: {}, proportation: {:.2f}%'.format(color, count, proportion))
            per = per + proportion

    #pper
    print('per: {:.2f}%'.format(per))

#Iterate over all images called "log*png" in current directory
#for filename in glob.glob('test*png'):
processLog('elect1_sub.jpg')
