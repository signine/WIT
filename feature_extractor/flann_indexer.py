import numpy as np
import cv2
import simplejson as json
from sqlalchemy import create_engine
from sqlalchemy.sql import text

FLANN_INDEX_KMEANS = 2

def main():
  all_images_query = text("SELECT * FROM images")
  features_query = text("SELECT descriptor from features join images on images.id = features.image_id where algorithm = 'MSER' and features.image_id = :image_id")

  db = create_engine("mysql://root@localhost:3306/WIT")

  imgs = [ img for img in db.execute(all_images_query) ]
  features = [ [ json.loads(f) for f in db.execute(features_query, image_id=i[0]) ] for i in imgs ]
  print len(imgs)
  print len(features)

  print features[0][0]

  index_params = dict(algorithm = FLANN_INDEX_KMEANS, branching = 10, iterations = -1)
  search_params = dict(checks=50)   # or pass empty dictionary
  flann = cv2.FlannBasedMatcher(index_params, search_params) 


if __name__ == '__main__':
  main()
