#imports
import numpy as np
import cv2

class ColorDescriptor:
    def __init__(self, bins):
        #store number of bins for the 3d histogram
        self.bins = bins

    def describe(self, image):
        #convert the image to HSV
        #initialise the features used to quanity the image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        features = []

        #get dimensions & compute centre of image
        (h, w) = image.shape[:2]
        (cX, cY) = (int(w * 0.5), int(h * 0.5))

        #divide the image into four rectangles(topleft, top right, bottomright, bottom left)
        segments = [(0, cX, 0, cY), (cX, w, 0, cY), (cX, w, cY, h), (0, cX, cY, h)]

        #construct eliptical mask representing the centre of the image
        (axesX, axesY) = (int((w * 0.75) / 2), int((h * 0.75) / 2))


        ellipMask = np.zeros(image.shape[:2], dtype = "uint8")
        cv2.ellipse(ellipMask, (cX, cY), (axesX, axesY), 0, 0, 360, 255, -1)

        #loop over the segments
        for (startX, endX, startY, endY) in segments:
            #construct a mask for each corner of the image, subtracting the elliptical centre from it
            cornerMask = np.zeros(image.shape[:2], dtype = "uint8")
            cv2.rectangle(cornerMask, (startX, startY), (endX, endY), 255, -1)
            cornerMask = cv2.subtract(cornerMask, ellipMask)

            #extract a colour histogram from the image, then update the feature vector
            hist = self.histogram(image, cornerMask)
            features.extend(hist)

        #extract a color histogram from the elliptical region and update the feature vector
        hist = self.histogram(image, ellipMask)
        features.extend(hist)

        #return the feature vector
        return features

    def histogram(self, image, mask):
        #extract 3d colour hist from the masked region, using the supplied number of bins per channel; then
        #normalise the histogram
        hist = cv2.calcHist([image], [0, 1, 2], mask, self.bins,
            [0, 180, 0, 256, 0, 256])
        dst = np.zeros(image.shape[:2], dtype = "uint8")
        hist = cv2.normalize(hist, dst).flatten()

        #return the hist
        return hist



