import numpy as np
import cv2
import sys, os
from img_utils import get_imgs, get_features
from datetime import datetime

FLANN_INDEX_KMEANS = 2

class Index():
  """
  Container class for holding index and required lists
  """

  def __init__(self, index, imgs, features):
    self.index = index
    self.imgs = imgs
    self.features = features

def build_index(branch_factor, **kwargs):
  """
    Optional args: imgs, features (Defaults to building index for images)
  """

  if 'imgs' in kwargs:
    if 'features' not in kwargs: raise Exception("Missing 'features' arg")
    imgs = kwargs['imgs']
    features = kwargs['features']
  else:
    imgs = get_imgs()
    features = get_features(imgs)

  if len(imgs) != len(features): raise Exception("img vector length not equal to feature vector")

  start = datetime.now()
  index_params = dict(algorithm = FLANN_INDEX_KMEANS, branching = branch_factor, iterations = -1)
  search_params = dict(checks=50) 
  flann = cv2.FlannBasedMatcher(index_params, search_params) 

  flann.add(features)
  flann.train()
  index = Index(flann, imgs, features) 

  fin = datetime.now()
  print "Build index time: ", (fin - start).seconds
  return index 
