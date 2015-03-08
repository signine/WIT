import numpy as np
import cv2
import sys, os
import search
from kmeans_tree_matcher import KMeansTreeMatcher
import mser
from sqlalchemy import create_engine
from sqlalchemy.sql import text
NOISE_PICS_DIR = "noise_pics/"
IMG_SIZE_W = 800
IMG_SIZE_H = 600

def noise_search_and_update(img):

    ''' add a weight to each feature match that matches more than 2 images '''
    index = KMeansTreeMatcher() 
    img = cv2.imread(img)
    if img.shape != (IMG_SIZE_H, IMG_SIZE_W):
      img = cv2.resize(img, (IMG_SIZE_W, IMG_SIZE_H)) 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kp = mser.detect(gray)
    descriptor = cv2.DescriptorExtractor_create("SIFT")
    kp, des = descriptor.compute(gray, kp)
    feature_matches = index.knn_match_for_weight( des, k=1)
    db = create_engine("mysql://root@localhost:3306/WIT")
    for node in feature_matches:
      if (len(node[0].imgs)) > 2:
        print node[0].id
        db.execute(text("UPDATE features SET weight=5 WHERE id=:id"), id=node[0].id)        
    return 0

   
def main():
  for filename in os.listdir(NOISE_PICS_DIR):
    print filename
    if filename.endswith(".jpg") or filename.endswith(".JPG"):
      matches = noise_search_and_update(os.path.join(NOISE_PICS_DIR, filename))

if __name__ == '__main__':
  main()
  
