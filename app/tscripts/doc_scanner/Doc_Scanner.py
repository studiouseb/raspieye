# import the necessary packages
from transform import four_point_transform
import imutils
from skimage.filters import threshold_local
#from skimage.filters import threshold_sauvola
import numpy as np
import argparse
import cv2
#from matplotlib.backends.backend_pdf import PdfPages
#from matplotlib import pyplot as plt

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True,
    help = "Path to the image to be scanned")
args = vars(ap.parse_args())

# load the image and compute the ratio of the old height
# to the new height, clone it, and resize it
image = cv2.imread(args["image"])
ratio = image.shape[0] / 500.0
orig = image.copy()
image = imutils.resize(image, height = 500)
 
# convert the image to grayscale, blur it, and find edges
# in the image
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(gray, 75, 200)
 
# show the original image and the edge detected image
print("STEP 1: Edge Detection")
#cv2.imshow("Image", image)
#cv2.imshow("Edged", edged)
#cv2.waitKey(0)
#cv2.destroyAllWindows()

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
#cv2.imshow("Outline", image)
#cv2.waitKey(0)
#cv2.destroyAllWindows()


#apply the four point transform
#to obtain top down view
warped = four_point_transform(orig, screenCnt.reshape(4,2) * ratio)
#convert the warped image to grayscale
#then threshold it, to give it
#that 'black and white' paper effect
warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
warped1= threshold_local(warped, 251, offset=10, param=0)
warped2 = threshold_local(warped, 1, offset = 1, param=0)
#binary_sauvola = threshold_sauvola(warped, window_size=5, k=0.7)
warped = warped.astype("uint8")*255
warped1 = warped1.astype("uint8")*255
warped2 = warped2.astype("uint8")*255
warped1 = cv2.bitwise_not(warped1)
warped2 = cv2.bitwise_not(warped2)
kernel1 = np.ones((1,3), np.uint8)
kernel2 = np.ones((3,1), np.uint8)
dilation = cv2.dilate(warped2, kernel, 5)

#binary_sauvola = binary_sauvola.astype("uint8")*255


#show the original and scanned images
print("STEP 3 :Apply perspective transform")
#cv2.imshow("Original", imutils.resize(orig, height = 650))
cv2.imshow("Scanned Warped1", imutils.resize(warped1, height = 650))
cv2.imshow("Scanned1 Warped2", imutils.resize(warped2, height = 650))
cv2.imshow("Dilated Warp", imutils.resize(dilation, height = 650))
#cv2.imshow("Scanned binarysauvola", imutils.resize(binary_sauvola, height = 650))
#cv2.imshow("Warped_raw", imutils.resize(warped, height = 650))
#cv2.imshow("Scanned1 Warped2", imutils.resize(warped, height = 650))
#cv2.imshow("Scanned binarysauvola", imutils.resize(warped, height = 650))
cv2.waitKey(0)
cv2.imwrite('receipt.png', warped2 )
cv2.imwrite('receipt_dila.png', dilation )


