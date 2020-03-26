from PIL import Image

def colort(color):
        if(color[2]>100 and color[1]<=color[2] and color[2] > color[0] + 35):
            return True
        else:
            return False

img = Image.open('numPlate.jpg').convert('RGBA')
datas = img.getdata()
newData = []
for item in datas:
    if(colort(item)):
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

img.putdata(newData)

img.save('Colortest.png', 'PNG')
