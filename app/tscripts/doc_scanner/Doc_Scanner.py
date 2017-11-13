# import the necessary packages

from imutils import resize
from skimage.filters import threshold_local
import numpy as np
import argparse
import cv2
import os


class Doc_scanner:
    def __init__(self):
        pass

    def order_points(self, pts):
        #initialise a list of coordinates that will be ordered
    #    such that the first entry in the list is the top left,
    #    the second entry is the top-right, the third entry is the
    #    bottom right, and the fourth is the bottom left
        rect = np.zeros((4, 2), dtype = "float32")

    #    the top left point will be the smallest sum, wheras
    #    the bottom right point will have the largest sum
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

    #    now compute the difference between the points, the
    #    top right point will have the smallest difference,
    #    whereas the bottom left will have the largest difference

        diff = np.diff(pts, axis = 1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

    #    return the ordered coordinates
        return rect

    def four_point_transform(self, image, pts):
        #obtain a consistent order of the points and unpackthem
        #individually
        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect
    #    compute the width of the new image, which will be the
    #    maximum distance between the bottom right and bottom left
    #    x-coords or the top right and top left coords
        widthA = np.sqrt(((br[0] - bl[0]) **2) + ((br[1] - bl[1]) **2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
    #    compute the height of the new image,
    #    which will be the max distance
    #    between the  top right and bottom right y coords
    #    or the top left and bottom left y coords
        heightA = np.sqrt(((tr[0] - br[0]) **2) + ((tr[1] - br[1]) **2))
        heightB= np.sqrt(((tl[0] - bl[0]) **2) + ((tl[1] - bl[1]) **2))
        maxHeight = max(int(heightA), int(heightB))
        # now that we have the dimensions of the new image, construct
        # the set of destination points to obtain a "birds eye view",
        # (i.e. top-down view) of the image, again specifying points
        # in the top-left, top-right, bottom-right, and bottom-left
        # order

        dst = np.array([
            [0,0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight -1],
            [0, maxHeight -1]], dtype = "float32")

         #compute the perspective transform matrix and apply it
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

        #return the warped image
        return warped


    def doc_scanner(self, path, filename):
        # load the image and compute the ratio of the old height
        # to the new height, clone it, and resize it
        image = path + filename
        print('this is the image path '+ image)
        path, ext = os.path.splitext(image)
        image = cv2.imread(image)
        print('image_read')
        ratio = image.shape[0] / 500.0
        orig = image.copy()
        image = resize(image, height = 500)

        # convert the image to grayscale, blur it, and find edges
        # in the image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(gray, 75, 200)

        # show the original image and the edge detected image
        print("STEP 1: Edge Detection")
        #find the contours in the edged image, keeping only the
        #largest ones, and initialise the screen contour
        (_, cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print(len(cnts))
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)

        #loop over the contours
        for c in cnts:
            #approximate the contour
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            #if the approximated contour has 4 points, then assume
            #that screen is found
            if len(approx) == 4:
                #print("SUCCESS")
                screenCnt = approx
                break
                #print("approx 1", screenCnt)

        #show the contour of the piece of paper
        print("STEP 2: Find contours of paper")
        cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
        #apply the four point transform
        #to obtain top down view
        warped = self.four_point_transform(orig, screenCnt.reshape(4,2) * ratio)
        print('warp achieved')
        #convert the warped image to grayscale
        #then threshold it, to give it
        #that 'black and white' paper effect
        warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        #warped1= threshold_local(warped, 251, offset=10, param=0)
        warped2 = threshold_local(warped, 1, offset = 1, param=0)
        warped = warped.astype("uint8")*255
        #warped1 = warped1.astype("uint8")*255
        warped2 = warped2.astype("uint8")*255
        #warped1 = cv2.bitwise_not(warped1)
        warped2 = cv2.bitwise_not(warped2)
        #kernel1 = np.ones((1,3), np.uint8)
        kernel1 = np.ones((1,1), np.uint8)
        dilation = cv2.dilate(warped2, kernel1, 5)

        #show the original and scanned images
        print("STEP 3 :Apply perspective transform")
        #warp1 = resize(warped1, height = 650)
        warp2 = resize(warped2, height = 650)
        dilate = resize(dilation, height = 650)
        print('warped and dilated')
        save_fileW = '{}{}{}'.format(path, '_transformed_warped', ext)
        save_fileD = '{}{}{}'.format(path, '_transformed_dilated', ext)
        print('Save files: ' + save_fileW + save_fileD)
        cv2.imwrite(save_fileW, warp2 )
        cv2.imwrite(save_fileD, dilate )
        original = '{}{}'.format(path, ext)
        print('files_written')
        print('basenames: ' + os.path.basename(save_fileW), os.path.basename(save_fileD), original)
        return os.path.basename(save_fileW), os.path.basename(save_fileD), os.path.basename(path)
