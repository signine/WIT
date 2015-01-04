import numpy as np
from sklearn import cluster
from img_utils import get_imgs, get_features, convert_to_numpy
from datetime import datetime

class KMeansNode():
  
  def __init__(self, data):
    self.data = feature
    self.children = []
    self.parent = None

  def add_child(self, child):
    self.children.append(child)

  def remove_child(self, child):
    self.children.remove(child)

class KMeansTree():

  def __init__(self, branch):
    self.data = []
    self.root = None
    self.branch = branch

  def set_data(self, data):
    self.data = data

  def add(self, data):
    self.data.append(data)
  
  def train(self):
    self.root = self.__build_tree(self.data)


  def __build_tree(self, data):
    
    



def flatten_features(features):
  return np.array([ f for img in features for f in img ])

imgs = get_imgs()
features = convert_to_numpy(get_features(imgs))
features = flatten_features(features)

print len(features)

start = datetime.now()

kmeans = cluster.KMeans(n_clusters=20, init='k-means++')
kmeans.fit(features)

labels_count = np.bincount(kmeans.labels_)
labels_count_ids = np.nonzero(labels_count)[0]

print zip(labels_count_ids, labels_count[labels_count_ids])

fin = datetime.now()
print "Time: ", (fin - start).seconds


