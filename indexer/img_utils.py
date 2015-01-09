import numpy as np
import simplejson as json
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from datetime import datetime

DB = None

def convert_to_numpy(features):
  """
  Converts a list of features to a numpy list
  """
  ret = [] 
  for img in features:
    i = []
    for f in img:
      f = map(lambda x: np.float32(x), f)
      f = np.array(f)
      i.append(f)
    ret.append(np.array(i))

  return np.array(ret)

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
  """
  Input: list of tuples return from 'get_imgs'
  """
  start = datetime.now()
  db = get_db_conn()
  features_query = text("SELECT descriptor from features join images on images.id = features.image_id where algorithm = 'MSER' and features.image_id = :image_id")
  features = [ [ json.loads(f[0]) for f in db.execute(features_query, image_id=i[0]) ] for i in imgs ]
  fin = datetime.now()
  print "Fetching features: ", (fin - start).seconds
  return features

def get_features_np(imgs):
  """
  Extremely slow. Should only be used for Flann Indexer
  """
  features = get_features(imgs)
  features = convert_to_numpy(features)
  return features
