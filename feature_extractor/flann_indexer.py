import numpy as np
import cv2
import simplejson as json
import mser
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from datetime import datetime

FLANN_INDEX_KMEANS = 2
DB = None

IMG_SIZE_W = 800
IMG_SIZE_H = 600

class Index():
  """
  Container class for holding index and required lists
  """

  def __init__(self, index, imgs, features):
    self.index = index
    self.imgs = imgs
    self.features = features


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

def build_index(imgs, features, branch_factor):
  index_params = dict(algorithm = FLANN_INDEX_KMEANS, branching = branch_factor, iterations = -1)
  search_params = dict(checks=50) 
  flann = cv2.FlannBasedMatcher(index_params, search_params) 

  flann.add(np.array(features))
  flann.train()

  index = Index(flann, imgs, features) 
  return index 

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
  if img.shape != (IMG_SIZE_H, IMG_SIZE_W):
    img = cv2.resize(img, (IMG_SIZE_W, IMG_SIZE_H))

  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  kp = mser.detect(gray)
  descriptor = cv2.DescriptorExtractor_create("SIFT")
  kp, des = descriptor.compute(gray, kp)
  return des

def print_hist(hist):
  for i in hist:
    print i, len(hist[i])

def get_n_best_matches(matches, imgs, n):
  matches = [ (imgs[img][0], len(f)) for img, f in hist(matches).iteritems() ]
  matches = sorted(matches, key=lambda x: x[1])
  return matches[-n:]

def match_img(img, index):
  start = datetime.now()

  des = get_descriptors(img)
  matches = index.index.knnMatch(des, k=1)
  matches = get_n_best_matches(matches, index.imgs, 5)

  fin = datetime.now()
  print "Match time: ", (fin - start).seconds
  return matches 
  

flann = None
TEST_PICS_DIR = "../test_pics/"

def main():
  global flann
  imgs = get_imgs()
  features = get_features(imgs)
  
  start = datetime.now()
  flann = build_index(imgs, features, 20)
  fin = datetime.now()
  print "Building index time: ", (fin - start).seconds

  import os

  for filename in os.listdir(TEST_PICS_DIR):
    if filename.endswith(".jpg"):
      matches = match_img(os.path.join(TEST_PICS_DIR, filename), flann)
      print filename
      for m in matches: print m

if __name__ == '__main__':
  main()
