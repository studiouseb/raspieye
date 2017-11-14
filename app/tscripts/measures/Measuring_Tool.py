# import the necessary packages
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
#import argparse
import imutils
import cv2
import os
#import Webcam from webcam

#webcam = Webcam()
#webcam.start()

class Measuring_Tool:

    def __init__(self):
        pass

    def order_points(self, pts):
        # sort the points based on their x-coordinates
        xSorted = pts[np.argsort(pts[:, 0]), :]

        # grab the left-most and right-most points from the sorted
        # x-roodinate points
        leftMost = xSorted[:2, :]
        rightMost = xSorted[2:, :]

        # now, sort the left-most coordinates according to their
        # y-coordinates so we can grab the top-left and bottom-left
        # points, respectively
        leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
        (tl, bl) = leftMost

        # now that we have the top-left coordinate, use it as an
        # anchor to calculate the Euclidean distance between the
        # top-left and right-most points; by the Pythagorean
        # theorem, the point with the largest distance will be
        # our bottom-right point
        D = dist.cdist(tl[np.newaxis], rightMost, "euclidean")[0]
        (br, tr) = rightMost[np.argsort(D)[::-1], :]

        # return the coordinates in top-left, top-right,
        # bottom-right, and bottom-left order
        return np.array([tl, tr, br, bl], dtype="float32")


    def image_load(self, image):

        #load the calibration file

        with np.load('/home/pi/prj/scripts/chalice/raspieye/app/tscripts/measures/camera_calibrations/20170521_00h31m26s560859_Calibration.npz') as X:
            mtx, dist, _, _ = [X[i] for i in ('mtx', 'dist', 'rvecs', 'tvecs')]

        # load our input image, convert it to grayscale, and blur it slightly
        #image = webcam.get_current_frame()

        image = cv2.imread(image)

        h,  w = image.shape[:2]
        newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
        dst = cv2.undistort(image, mtx, dist, None, newcameramtx)
        x,y,w,h = roi
        dst = dst[y:y+h, x:x+w]
        image = dst
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (15, 15), 0)

        return gray, image

    def edge_detection(self, gray):
        # perform edge detection, then perform a dilation + erosion to
        # close gaps in between object edges
        edged = cv2.Canny(gray, 50, 100)
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)
        return edged

    def find_contours(self, edged):
        # find contours in the edge map
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[1]
        return cnts

    def midpoint(self, ptA, ptB):
        return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

    #renamed main function
    def measure(self, path, image):

        path = path
        image = image
        image_ = image
        path_, ext_ = os.path.splitext(image)

        image = path + image
        gray, image = self.image_load(image)
        edged = self.edge_detection(gray)
        cnts = self.find_contours(edged)

        # sort the contours from left-to-right and initialize the bounding box
        # point colors
        (cnts, _) = contours.sort_contours(cnts)
        colors = ((0, 0, 255), (240, 0, 159), (255, 0, 0), (255, 255, 0))

        #set the size in mm of the reference object e.g. 0.50 c coin = 22 (i.e. 22 mm). Set the unit at whatever you want returned.
        pixelsPerMetric = 65


    # loop over the contours individually
        orig = image.copy()
        for c in cnts:
        # if the contour is not sufficiently large, ignore it
            if cv2.contourArea(c) < 300:
                continue

            # compute the rotated bounding box of the contour

            box = cv2.minAreaRect(c)
            box = cv2.boxPoints(box)
            box = np.array(box, dtype="int")

            # order the points in the contour such that they appear
            # in top-left, top-right, bottom-right, and bottom-left
            # order, then draw the outline of the rotated bounding
            # box
            box = perspective.order_points(box)
            cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

            # loop over the original points and draw them
            for (x, y) in box:
                cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

            # unpack the ordered bounding box, then compute the midpoint
            # between the top-left and top-right coordinates, followed by
            # the midpoint between bottom-left and bottom-right coordinates
            (tl, tr, br, bl) = box
            (tltrX, tltrY) = self.midpoint(tl, tr)
            (blbrX, blbrY) = self.midpoint(bl, br)

            # compute the midpoint between the top-left and top-right points,
            # followed by the midpoint between the top-righ and bottom-right
            (tlblX, tlblY) = self.midpoint(tl, bl)
            (trbrX, trbrY) = self.midpoint(tr, br)

            # draw the midpoints on the image
            cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
            cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (0, 255, 0), -1)
            cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (0, 0, 255), -1)
            cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (175, 75, 175), -1)

            # draw lines between the midpoints
            cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
                (255, 0, 255), 1)
            cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
                (255, 0, 255), 1)

            # compute the Euclidean distance between the midpoints
            dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
            dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

            # compute the size of the object
            dimA = dA / pixelsPerMetric
            dimB = dB / pixelsPerMetric

            # draw the object sizes on the image
            cv2.putText(orig, "{:.2f}cm".format(dimB),
                (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
                1, (255, 255, 255), 2)
            cv2.putText(orig, "{:.2f}cm".format(dimA),
                (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
                1, (255, 255, 255), 2)


        original = '{}{}{}{}'.format(path, path_, '_measured', ext_)


        cv2.imwrite(original, orig)
        return os.path.basename(original)
