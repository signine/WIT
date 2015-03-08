import numpy as np
import cv2
import sys, os
import score
sys.path.append(os.path.join(os.getcwd(), "../indexer"))
sys.path.append(os.path.join(os.getcwd(), "../feature_extractor"))
import mser
from kmeans_tree_matcher import KMeansTreeMatcher
from datetime import datetime
from img_match import ImgMatch

class SearchService():
  IMG_SIZE_W = 800
  IMG_SIZE_H = 600

  index = None
  def __group_by_img(self, matches):
    """
    Returns a dictionary of img to feature count
    """
    his = {}
    for f_match in matches:
      for m in f_match:
        for img in m.imgs:
          if img in his:
            his[img] += 1
          else:
            his[img] = 1
    return his

    for m in matches:
      if m[0].imgIdx in his:
        his[m[0].imgIdx].append(m[0])
      else:
        his[m[0].imgIdx] = [m[0]]
    return his
  
  def get_descriptors(self, img):
    img = cv2.imread(img)
    if img.shape != (self.IMG_SIZE_H, self.IMG_SIZE_W):
      img = cv2.resize(img, (self.IMG_SIZE_W, self.IMG_SIZE_H))
  
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kp = mser.detect(gray)
    descriptor = cv2.DescriptorExtractor_create("SIFT")
    kp, des = descriptor.compute(gray, kp)
    return des
  
  def get_n_best_matches(self, matches, n):
    # Group by features then sort
    matches = sorted(matches, key=lambda x: x.count)
    return matches[-n:]
  
  def match_img(self, img):
    index = self.get_index()
    des = self.get_descriptors(img)
    matches = index.knn_match(des, k=1)
    matches = self.get_n_best_matches(matches, 5)
    return matches 

  def get_index(self):
    if not self.index:
      self.index = KMeansTreeMatcher() 
    return self.index

  def search(self, img):
    start = datetime.now()

    matches = self.match_img(img)
    matches = score.score(matches)

    for m in matches:
      print m.location, m.score
    fin = datetime.now()
    print "Search time: ", (fin - start).seconds, " seconds"
    return matches
  
  def warm_cache(self):
    for filename in os.listdir(TEST_PICS_DIR):
      if filename.endswith(".jpg"):
        matches = self.search(os.path.join(TEST_PICS_DIR, filename))

TEST_PICS_DIR = "../test_pics/"

def main():
  search_service = SearchService()

  for filename in os.listdir(TEST_PICS_DIR):
    if filename.endswith(".jpg"):
      matches = search_service.search(os.path.join(TEST_PICS_DIR, filename))
      print filename
      for m in matches:
        print m.location, m.score
        #print m.img_data, m.count

if __name__ == '__main__':
  main()

