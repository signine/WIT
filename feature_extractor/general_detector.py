import cv2
import numpy as np
import sys

FEATURE_DETECTOR = "SIFT"
FEATURE_DESCRIPTOR = "SIFT"

def main():
  img_file = sys.argv[1]
  if not img_file:
    print "Usage: python general_detector.py <image>"
    return 

  img = cv2.imread(img_file)
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

  detector = cv2.FeatureDetector_create(FEATURE_DETECTOR)
  descriptor = cv2.DescriptorExtractor_create(FEATURE_DESCRIPTOR)

  kp = detector.detect(gray)
  kp, des = descriptor.compute(gray, kp)

  img2 = cv2.drawKeypoints(gray, kp, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
  cv2.imshow('keypoints', img2)
  cv2.waitKey()
  cv2.destroyAllWindows()


if __name__ == "__main__":
  main()


