import numpy as np
import cv2
import sys, os
import score
sys.path.append(os.path.join(os.getcwd(), "../indexer"))
sys.path.append(os.path.join(os.getcwd(), "../feature_extractor"))
import flann_indexer
import mser
from datetime import datetime
from img_match import ImgMatch

class SearchService():
  IMG_SIZE_W = 800
  IMG_SIZE_H = 600

  index = None

  def hist(self, matches):
    his = {}
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
  
  def print_hist(self, hist):
    for i in hist:
      print i, len(hist[i])
  
  def get_n_best_matches(self, matches, imgs, n):
    # Group by features then sort
    matches = [ ImgMatch(imgs[img], f) for img, f in self.hist(matches).iteritems() ]
    matches = sorted(matches, key=lambda x: x.count)
    return matches[-n:]
  
  def match_img(self, img, index):
    des = self.get_descriptors(img)
    matches = index.index.knnMatch(des, k=1)
    matches = self.get_n_best_matches(matches, index.imgs, 5)
    return matches 

  def get_index(self):
    if not self.index:
      self.index = flann_indexer.build_index(20)
    return self.index

  def search(self, img):
    start = datetime.now()

    index = self.get_index()
    matches = self.match_img(img, index)
    matches = score.score(matches)

    fin = datetime.now()
    print "Search time: ", (fin - start).seconds
    return matches

TEST_PICS_DIR = "../test_pics/"

def main():
  search_service = SearchService()

  for filename in os.listdir(TEST_PICS_DIR):
    if filename.endswith(".jpg"):
      matches = search_service.search(os.path.join(TEST_PICS_DIR, filename))
      print filename
      for m in matches:
        print m.location, m.score

if __name__ == '__main__':
  main()

