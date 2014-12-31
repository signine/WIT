import numpy as np
import cv2
import simplejson as json
import mser
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from datetime import datetime

FLANN_INDEX_KMEANS = 2
DB = None

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

def build_index(branch_factor, **kwargs):
  """
    Optional args: imgs, features
  """

  if 'imgs' in kwargs:
    if 'features' not in kwargs: raise Exception("Missing 'features' arg")
    imgs = kwargs['imgs']
    features = kwargs['features']
  else:
    imgs = get_imgs()
    features = get_features(imgs)

  start = datetime.now()
  index_params = dict(algorithm = FLANN_INDEX_KMEANS, branching = branch_factor, iterations = -1)
  search_params = dict(checks=50) 
  flann = cv2.FlannBasedMatcher(index_params, search_params) 

  flann.add(np.array(features))
  flann.train()
  index = Index(flann, imgs, features) 

  fin = datetime.now()
  print "Build index time: ", (fin - start).seconds
  return index 
