import numpy as np
import cv2

class Square:
  def __init__(self, top_left, bottom_right, center, height):
    self.top_left = top_left
    self.bottom_right = bottom_right 
    self.center = center 
    self.height = height 

def get_center(pt1, pt2):
  x = (pt1[0] + pt2[0]) / 2.0
  y = (pt1[1] + pt2[1]) / 2.0
  return (x, y)

def get_squares(regions, max_size=5000):
  sqrs = []
  for r in regions:
    x, y, wth, ht = cv2.boundingRect(r.reshape(-1, 1, 2)) 
    sqr_ht = max(wth, ht)
    if sqr_ht*sqr_ht > max_size: continue

    center = get_center((x, y), (x + wth, y + ht)) 
    top_left = (int(center[0]) - sqr_ht/2, int(center[1]) + sqr_ht/2)
    bottom_right = (int(center[0]) + sqr_ht/2, int(center[1]) - sqr_ht/2)
    
    sqrs.append(Square(top_left, bottom_right, center, sqr_ht))
  
  return sqrs

def detect_keypoints(img, max_size = 5000):
  mser = cv2.MSER(_max_area = max_size)
  regions = mser.detect(img, None)
  sqrs = get_squares(regions, max_size=max_size)
  keypoints = [ cv2.KeyPoint(s.center[0], s.center[1], s.height) for s in sqrs ]
  return keypoints

def wait():
  cv2.waitKey()
  cv2.destroyAllWindows()

def main():
  #img1 = cv2.imread("116_college_10_315_0.jpg")
  img1 = cv2.imread("1_college_1_0_0.jpg")
  vis = img1.copy()
  gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
  
  mser = cv2.MSER(_max_area = 5000)
  regions = mser.detect(gray1, None)
  print len(regions)

  """
  circles = [cv2.minEnclosingCircle(p.reshape(-1, 1, 2)) for p in regions]
  recs = [cv2.boundingRect(p.reshape(-1, 1, 2)) for p in regions]
  for c in circles:
    center = (int(c[0][0]),int(c[0][1]))
    radius = int(c[1])
    cv2.circle(vis, center, radius,(0,255,0),1)
  """
  """
  recs = [cv2.boundingRect(p.reshape(-1, 1, 2)) for p in regions]
  recs = sorted(recs, key=lambda x: x[3]*x[3])
  
  for r in recs[-20:]:
    print r[3]*r[3]
    cv2.rectangle(vis, (r[0], r[1]), (r[0] + r[2], r[1] + r[3]),(255, 0,255), 1)
  print "----"
  """
  sqrs = get_squares(regions)
  sqrs = sorted(sqrs, key=lambda x: x.height*x.height)
  cnt  = 0
  for s in sqrs[:]:
    cnt += 1
    print s.height*s.height
    cv2.rectangle(vis, s.top_left, s.bottom_right,  (0, 255, 0), 1)
  
  print cnt

  descriptor = cv2.DescriptorExtractor_create("SIFT")
  kp = detect_keypoints(gray1)
  kp, des1 = descriptor.compute(gray1, kp)
  print "Img1 features: ", len(des1)

  #cv2.imshow('img', vis)
  #wait()
  
if __name__ == '__main__':
  main()
