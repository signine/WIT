import cv2
import numpy as np

FEATURE_DETECTOR = "MSER"
FEATURE_DESCRIPTOR = "SIFT"

def main():
  img = cv2.imread("college_1_45_0.jpg")
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

  detector = cv2.FeatureDetector_create(FEATURE_DETECTOR)
  descriptor = cv2.DescriptorExtractor_create(FEATURE_DESCRIPTOR)

  kp = detector.detect(img)
  kp, des = descriptor.compute(img, kp)

  img2 = cv2.drawKeypoints(gray, kp, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
  cv2.imwrite('mser_keypoints2.jpg', img2)


if __name__ == "__main__":
  main()


