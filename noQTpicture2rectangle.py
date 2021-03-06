# python3 /home/mka/PycharmProjects/TesserAct/noQTpicture2rectangle.py '*-*.jpg' 40 60
# sometimes 55 77
# in a directory containing initially only jpg, png, tiff files
# the arguments are initial box size in x and y
"""
1) Read selected picture (automated)
2) the dimension of x is forced by fixed ratio
3) you can move the rectancle by up=w down=z left=a right=d, bigger=+, smaller=-
4) when done press L if mistakes press r and start picture again
5) give corresponding alphabet by a keystroke

Various resolutions are in directories Rectangle*
unscaled samples with original resolution of the rectangle box are in dir NotScaled
Negative samples are in dir NegativeSamples (they have white ball on top of plates)


Finnish car number plate: 118 mm x 442 mm

"""

import sys
import numpy as np
import cv2
from matplotlib import pyplot as plt

class MouseRectangle():
    """ get a rectangle by mouse"""
    def __init__(self, xpixel=None, ypixel=None):
        #super().__init__()
        self.refPts = []
        self.oldPts = []
        self.cropping = False
        self.image = None
        self.ratio = None
        self.xpixel= xpixel
        self.ypixel = ypixel

    def set_image(self, image):
        self.image = image

    def set_init_position(self):
        upleft = [int(self.image.shape[1] / 2), int(self.image.shape[0] / 2)]
        downright = [int(self.image.shape[1] / 2) + self.xpixel, int(self.image.shape[0] / 2) + self.ypixel]
        self.set_refPts([upleft, downright])

    def reset(self):
        self.refPts = []
        self.cropping = False
        self.set_init_position()

    def resetToPrevious(self):
        self.set_refPts([self.refPts[0], self.refPts[1]])
        self.oldPts = []

    def get_refPts(self):
        return self.refPts

    def set_refPts(self, refPts):
        self.refPts = refPts

    def set_oldPts(self):
        for refPt in self.refPts:
            self.oldPts.append(refPt.copy())

    def get_oldPts(self):
        return self.oldPts

    def set_ratio(self, ratio):
        """self y/x ratio for the selection box"""
        if self.ratio is not None:
            self.ratio = ratio
        else:
            # assume long eu plates
            self.ratio = 442/118

    def get_ratio(self):
        return self.ratio




class Example():



    def __init__(self, *args):
        """ set filenames we act on 
            and the x-y-dimension of the area in pixels (it can be scaled later)
        """
        
        import glob
        self.fnames =glob.glob(sys.argv[1])
        try:
            xpixel = int(sys.argv[2])
            ypixel = int(sys.argv[3])
        except:
            print("setting default values for pixels")
            xpixel = 40
            ypixel = 10
        print("INIT:", xpixel, ypixel)

        self.mouse = MouseRectangle(xpixel=xpixel, ypixel=ypixel)
        self.mouse.set_ratio(xpixel/ypixel)


    def getNewName(self, oldname, subdir):
        """
        get new filename with extra path
        for instance 
        oldname = 'file.txt', subdir='output'
        returns 'currentdir/output/file.txt' 
        and makes 'output' directory if it does not exist
        """
        import os
        #dir = os.path.dirname(oldname)
        dir = os.getcwd()
        name = os.path.basename(oldname)
        #generate new dir if it doesnot exist
        newdir = dir + '/'+ subdir
        if not os.path.exists(newdir):
            os.makedirs(newdir)
        return newdir+'/'+'sample_'+name

    def saveImage(self, image, ratio, fname):
        import os.path
        import time
        intValidChars = [ord('0'), ord('1'), ord('2'),
                         ord('3'), ord('4'), ord('5'),
                         ord('6'), ord('7'), ord('8'),
                         ord('9'),
                         ord('a'), ord('b'), ord('c'),
                         ord('d'), ord('e'), ord('f'),
                         ord('g'), ord('h'), ord('i'),
                         ord('j'), ord('k'), ord('l'),
                         ord('m'), ord('n'), ord('o'),
                         ord('p'), ord('q'), ord('r'),
                         ord('s'), ord('t'), ord('u'),
                         ord('v'), ord('w'), ord('x'),
                         ord('y'), ord('z'), ord('å'),
                         ord('ä'), ord('ö'), ord('-')]

        while True:
            print("give the letter to be saved")
            intChar = cv2.waitKey(0)
            clone=image.copy()
            if intChar in intValidChars:

                # all samples will get individual filename
                for i in range(999):
                    basename=chr(intChar)+str(i)
                    if not(os.path.isfile(basename+'.tif')):
                        break
                fullname = self.getNewName(oldname=basename, subdir='output')
                refPts = self.mouse.get_refPts()
                letter = clone[refPts[0][1]:refPts[1][1], refPts[0][0]:refPts[1][0]]
                flattenedImage = letter.reshape((1, letter.shape[0] * letter.shape[1]))
                cv2.imwrite(fullname+'.tif', letter)
                np.savetxt(fullname+'.txt', flattenedImage)
                allname=self.getNewName(oldname='all.box', subdir='output')
                with open(allname, 'a') as f:
                    f.write(chr(intChar)+ \
                            ' ' + str(refPts[0][0]) + \
                            ' ' + str(image.shape[1]-refPts[0][1]) + \
                            ' ' + str(refPts[1][0]) + \
                            ' ' + str(image.shape[1]-refPts[1][1]) + \
                            ' 0 \n')
                print('letter '+ chr(intChar)+' was saved')
                #font = cv2.FONT_HERSHEY_SIMPLEX
                                
                #cv2.rectangle(clone, tuple(refPts[-2]), tuple(refPts[-1]), (0, 0, 255), 1)
                #cv2.putText(clone,chr(intChar),tuple(refPts[-1]),
                #            font, 50,(0,0,255),2,cv2.LINE_AA)
                #cv2.imshow("clone", clone)
                #time.sleep(2)
                #cv2.imshow("image", image)
                break
            else:
                print ("sorry, not a valid character, try again")


    def showDialog(self):
        import math

        
        #fnames =glob.glob('*jpg')
        #fnames = fnames + glob.glob('*png')
        #fnames = fnames + glob.glob('*tif')

        for fname in self.fnames:
                img = cv2.imread(fname)
                gray = cv2.imread(fname, 0)
                print("size:", img.shape[0], img.shape[1])

                clone = img.copy()
                self.mouse.set_image(image=img)
                self.mouse.set_init_position()
                refPts = self.mouse.get_refPts()

                for i in range(0, len(refPts), 2):
                    print("printing",refPts[0], refPts[1])
                    cv2.rectangle(img, tuple(refPts[i]), tuple(refPts[i + 1]), (255, 0, 0), 10)
                oldPts = self.mouse.get_oldPts()
                for i in range(0, len(oldPts), 2):
                    cv2.rectangle(img, tuple(oldPts[i]), tuple(oldPts[i + 1]), (0, 255, 0), 1)

                # keep looping until the '*' key is pressed
                while True:
                    while True:
                        # display the image and wait for a keypress
                        cv2.imshow("image", img)
                        key = cv2.waitKey(33)
                        change = False
                        # if the 'r' key is pressed, reset the cropping region
                        if key == ord("r"):
                            img = clone.copy()
                            self.mouse.reset()
                            self.mouse.set_image(image=img)

                        elif key == ord("+"):
                            refPts = self.mouse.get_refPts()
                            refPts[-2][0]= refPts[-2][0] - 1
                            refPts[-2][1]= refPts[-2][1] - 1
                            refPts[-1][0] = refPts[-1][0] + 1
                            refPts[-1][1] = refPts[-1][1] + 1
                            self.mouse.set_refPts(refPts)
                            change = True
                        elif key == ord("-"):
                            refPts = self.mouse.get_refPts()
                            refPts[-2][0] = refPts[-2][0] + 1
                            refPts[-2][1] = refPts[-2][1] + 1
                            refPts[-1][0] = refPts[-1][0] - 1
                            refPts[-1][1] = refPts[-1][1] - 1
                            self.mouse.set_refPts(refPts)
                            change = True
                        elif key == ord("w"):
                            #up
                            refPts = self.mouse.get_refPts()
                            refPts[-2][1] = refPts[-2][1] - 1
                            refPts[-1][1] = refPts[-1][1] - 1
                            self.mouse.set_refPts(refPts)
                            change = True
                        elif key == ord("z"):
                            #up
                            refPts = self.mouse.get_refPts()
                            refPts[-2][1] = refPts[-2][1] + 1
                            refPts[-1][1] = refPts[-1][1] + 1
                            self.mouse.set_refPts(refPts)
                            change = True
                        elif key == ord("d"):
                            #up
                            refPts = self.mouse.get_refPts()
                            refPts[-2][0] = refPts[-2][0] + 1
                            refPts[-1][0] = refPts[-1][0] + 1
                            self.mouse.set_refPts(refPts)
                            change = True
                        elif key == ord("a"):
                            #up
                            refPts = self.mouse.get_refPts()
                            refPts[-2][0] = refPts[-2][0] - 1
                            refPts[-1][0] = refPts[-1][0] - 1
                            self.mouse.set_refPts(refPts)
                            change = True

                        # if the 'L' key is pressed, break from the loop
                        elif key == ord("l"):
                            break
                        #print(key)
                        if key == ord("*"):  # if star key was pressed
                            break
                        
                        if change:
                            change = False
                            img = clone.copy()
                            for i in range(0,len(refPts),2):
                                cv2.rectangle(img, tuple(refPts[i]), tuple(refPts[i+1]), (255, 0, 0), 2)
                            oldPts = self.mouse.get_oldPts()
                            for i in range(0, len(oldPts), 2):
                                cv2.rectangle(img, tuple(oldPts[i]), tuple(oldPts[i + 1]), (0, 255, 0), 1)
                            self.mouse.set_image(image=img)
                            
                    if key == ord("*"):  # if star key was pressed
                        self.mouse.resetToPrevious()
                        break
                    self.saveImage(gray.copy(), self.mouse.get_ratio(), fname)
                    self.mouse.set_oldPts()
                    #self.mouse.reset()




               
        
if __name__ == '__main__':

    ex = Example(sys.argv)
    ex.showDialog()

