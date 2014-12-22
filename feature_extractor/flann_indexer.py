import numpy as np
import cv2
import simplejson as json
import mser
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from datetime import datetime

FLANN_INDEX_KMEANS = 2
imgs = None

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

def build_index():
  global imgs
  start = datetime.now()
  all_images_query = text("SELECT * FROM images")
  features_query = text("SELECT descriptor from features join images on images.id = features.image_id where algorithm = 'MSER' and features.image_id = :image_id")

  db = create_engine("mysql://root@localhost:3306/WIT")

  imgs = [ img for img in db.execute(all_images_query) ]
  features = [ [ json.loads(f[0]) for f in db.execute(features_query, image_id=i[0]) ] for i in imgs ]
  features = convert_to_numpy(features)

  index_params = dict(algorithm = FLANN_INDEX_KMEANS, branching = 10, iterations = -1)
  search_params = dict(checks=50) 
  flann = cv2.FlannBasedMatcher(index_params, search_params) 
  
  fin = datetime.now()
  print "Fetching data time: ", (fin - start).seconds

  flann.add(np.array(features))

  flann.train()
  return flann

def hist(l):
  his = {}
  for i in l:
    if i in his:
      his[i] += 1
    else:
      his[i] = 1
  return his

flann = None
matches = None

start = datetime.now()
flann = build_index()
fin = datetime.now()

print "Building index time: ", (fin - start).seconds

img = cv2.imread("IMG_20141125_140931.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
kp = mser.detect(gray)
descriptor = cv2.DescriptorExtractor_create("SIFT")
kp, des = descriptor.compute(gray, kp)
#matches = flann.knnMatch(des[0], k=1)
  
"""
if __name__ == '__main__':
  main()
"""
