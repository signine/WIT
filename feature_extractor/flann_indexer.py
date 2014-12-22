import numpy as np
import cv2
import simplejson as json
import mser
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from datetime import datetime

FLANN_INDEX_KMEANS = 2
DB = None

def convert_to_numpy(features):
  ret = []
  for img in features:
    i = []
    for f in img:
      f = map(lambda x: np.float32(x), f)
      f = np.array(f)
      i.append(f)
    ret.append(np.array(i))

  return ret

def get_db_conn():
  global DB
  if not DB:
    DB = create_engine("mysql://root@localhost:3306/WIT")
  return DB

def get_imgs():
  db = get_db_conn()
  all_images_query = text("SELECT * FROM images")
  return [ img for img in db.execute(all_images_query) ]

def get_features(imgs):
  start = datetime.now()
  db = get_db_conn()
  features_query = text("SELECT descriptor from features join images on images.id = features.image_id where algorithm = 'MSER' and features.image_id = :image_id")
  features = [ [ json.loads(f[0]) for f in db.execute(features_query, image_id=i[0]) ] for i in imgs ]
  features = convert_to_numpy(features)
  fin = datetime.now()
  print "Fetching features: ", (fin - start).seconds
  return features

def build_index(features):
  index_params = dict(algorithm = FLANN_INDEX_KMEANS, branching = 10, iterations = -1)
  search_params = dict(checks=50) 
  flann = cv2.FlannBasedMatcher(index_params, search_params) 

  flann.add(np.array(features))

  flann.train()
  return flann

def hist(matches):
  his = {}
  for m in matches:
    if m[0].imgIdx in his:
      his[m[0].imgIdx].append(m[0])
    else:
      his[m[0].imgIdx] = [m[0]]
  return his

def get_descriptors(img):
  img = cv2.imread(img)
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  kp = mser.detect(gray)
  descriptor = cv2.DescriptorExtractor_create("SIFT")
  kp, des = descriptor.compute(gray, kp)
  return des

def print_hist(hist):
  for i in hist:
    print i, len(hist[i])

flann = None
matches = None

imgs = get_imgs()
features = get_features(imgs)

start = datetime.now()
flann = build_index(features)
fin = datetime.now()

print "Building index time: ", (fin - start).seconds

des1 = get_descriptors("IMG_20141125_140931.jpg")
des2 = get_descriptors("IMG_20141125_163021.jpg") 
matches1 = flann.knnMatch(des1, k=1)
matches2 = flann.knnMatch(des2, k=1)

his1 = hist(matches1)
his2 = hist(matches2)
  
"""
if __name__ == '__main__':
  main()
"""
