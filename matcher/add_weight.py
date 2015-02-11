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
    index = KMeansTreeMatcher() 
    img = cv2.imread(img)
    if img.shape != (IMG_SIZE_H, IMG_SIZE_W):
      img = cv2.resize(img, (IMG_SIZE_W, IMG_SIZE_H)) 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kp = mser.detect(gray)
    descriptor = cv2.DescriptorExtractor_create("SIFT")
    kp, des = descriptor.compute(gray, kp)
    matches, img_matches = index.knn_match( des, k=1)
    img_matches = sorted(img_matches, key=lambda x: img_matches[x])
    img_matches = img_matches[-4:]
    matches = sorted(matches, key=lambda x: x.count)
    matches = matches[-4:]
    #make sure the best matches are the same, the 4 i have access to in the database are the best matches!
    db = create_engine("mysql://root@localhost:3306/WIT")
    for img_id in img_matches:
      print img_id
      #q = db.execute(text("SELECT id,lat,lng,street_name,weight FROM images WHERE id=:id"), id=img_id)
      #print iter(q).next()
      #edit those fields:
      db.execute(text("UPDATE images SET weight=5 WHERE id=:id"), id=img_id)
      #q = db.execute(text("SELECT id,lat,lng,street_name,weight FROM images WHERE id=:id"), id=img_id)
      #print iter(q).next()

    return matches

    

def main():
  for filename in os.listdir(NOISE_PICS_DIR):
    print filename
    if filename.endswith(".jpg") or filename.endswith(".JPG"):
      matches = noise_search_and_update(os.path.join(NOISE_PICS_DIR, filename))
      for m in matches:
        print m.location, m.weight

if __name__ == '__main__':
  main()
  
