import cv2
import numpy as np
import sys

FEATURE_DETECTOR = "MSER"
FEATURE_DESCRIPTOR = "SIFT"
MATCHES_NUM = 100
DISTANCE_LIMIT = 100

best_matches= []

def draw_matches(imgt, imgq, kpt, kpq, matches, **kwargs):
    """
    Draws lines between matching keypoints.
    Training image on left and query image on right.
    imgt - training image
    imgq - query image
    kpqt - training keypoints
    kpq - query keypoints
    matches 
    
    kwargs
    numbers = true Write numbers instead of lines
    """
    # Filter out keypoints that are not in matches
    kpq = [ kpq[m.queryIdx] for m in matches ]
    kpt = [ kpt[m.trainIdx] for m in matches ]
    
    img3 = cv2.drawKeypoints(imgt, kpt, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    img4 = cv2.drawKeypoints(imgq, kpq, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    combined_image = np.hstack((img3, img4))
    height, width, depth = img3.shape
    
    if "numbers" in kwargs and kwargs["numbers"]:
      draw_lines = False
    else:
      draw_lines = True
  
    for i,m in enumerate(matches):
      print m.distance
      x1 = int(kpt[i].pt[0])
      y1 = int(kpt[i].pt[1])
      x2 = int(kpq[i].pt[0])
      y2 = int(kpq[i].pt[1])
      if draw_lines:
        cv2.line(combined_image, (x1, y1), (x2 + width, y2), (255, 0, 0), 1)
      else:
        cv2.putText(combined_image, str(i),  (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0)
        cv2.putText(combined_image, str(i),  (x2 + width, y2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0)
  
    cv2.imshow("Matches", combined_image)
    cv2.waitKey()
    cv2.destroyAllWindows()
    

def main():
  global best_matches
  # img1 = train, img2 = query
  #img1 = cv2.imread("1_college_1_0_0.jpg")
  #img2 = cv2.imread("9_college_1_0_40.jpg")
  img1 = cv2.imread("109_college_10_0_0.jpg")
  #img1 = cv2.imread("104_college_9_315_0.jpg")
  img2 = cv2.imread("116_college_10_315_0.jpg")
  gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
  gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

  detector = cv2.FeatureDetector_create(FEATURE_DETECTOR)
  descriptor = cv2.DescriptorExtractor_create(FEATURE_DESCRIPTOR)

  kp1 = detector.detect(img1)
  kp1, des1 = descriptor.compute(img1, kp1)
  print "Img1 features: ", len(des1)

  kp2 = detector.detect(img2)
  kp2, des2 = descriptor.compute(img2, kp2)
  print "Img2 features: ", len(des2)

  # FLANN parameters
  FLANN_INDEX_KDTREE = 0
  index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
  search_params = dict(checks=50)   # or pass empty dictionary
  flann = cv2.FlannBasedMatcher(index_params, search_params) 

  # query des, train des
  matches = flann.knnMatch(des2, des1, k=2)
  print "Total matches: ", len(matches)

  # ratio test 
  for i,(m,n) in enumerate(matches):
    if m.distance < 0.7*n.distance:
      best_matches.append(matches[i])
      
  # Filter by distance
  best_matches = [ m[0] for m in best_matches if m[0].distance < DISTANCE_LIMIT][:MATCHES_NUM]
  best_matches = sorted(best_matches, key=lambda x: x[0].distance)

  print "Good mathces: ", len(best_matches)
  
  draw_matches(img1, img2, kp1, kp2, best_matches)


if __name__ == "__main__":
  main()