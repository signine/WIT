import numpy as np
from sklearn import cluster
from img_utils import get_imgs, get_features_np, get_features, convert_to_numpy
from datetime import datetime

class KMeansNode():
  
  def __init__(self, data):
    self.data = data # Flat list of all features, used for clustering
    self.children = []
    self.parent = None
    self.count = 0 # Number of data points clustered for this node
    self.imgs = [] # Images that have this feature

class KMeansTree():

  def __init__(self, branch):
    self.data = []
    self.root = None
    self.branch = branch
    self.imgs = [] # List of tuples ((img metadata), [features])

  def add_imgs(self, imgs):
    self.imgs += imgs

  def train(self):
    start = datetime.now()
    # Flatten and collect all features
    self.data = np.array([ feature for img in self.imgs for feature in img[1] ])
    print "Data : ", len(self.data)
    self.data = self.__remove_duplicates(self.data)
    print "Data set: ", len(self.data)

    self.root = KMeansNode(None)
    self.root.children = self.__build_tree(self.data)
    self.__set_parent(self.root.children, self.root)
    self.root.count = len(self.data)

    fin = datetime.now()
    print "Train time: ", (fin - start).seconds
  
  def __cluster(self, data):
    print "Cl len: ", len(data)
    #start = datetime.now()

    km = cluster.KMeans(n_clusters=self.branch, init='k-means++')
    km.fit(data)

    #fin = datetime.now()
    #print "Cl time: ", (fin - start).seconds
    return km

  def __set_parent(self, nodes, parent):
    """
    Sets the parent to a list of nodes
    """
    for n in nodes: 
      n.parent = parent

  def __build_tree(self, data):
    """
    Returns a list of root nodes   
    """
    nodes = []
    if len(data) < self.branch:
      return [ KMeansNode(d) for d in data ]
    else:
      c = self.__cluster(data)
  
      i = 0
      while i < len(c.cluster_centers_):
        cluster_data = data[np.where(c.labels_ == i)]
        if len(cluster_data) > 1:
          node = KMeansNode(c.cluster_centers_[i])
          node.children = self.__build_tree(cluster_data)
          self.__set_parent(node.children, node)
          node.count = len(cluster_data)
        elif len(cluster_data) == 0:
          if c.cluster_centers_[i] in data:
            node = KMeansNode(c.cluster_centers_[i])
          else:
            i += 1
            continue
        else:
          node = KMeansNode(cluster_data[0])

        nodes.append(node)
        i += 1
    return nodes

  def __remove_duplicates(self, features):
    a = features.view(np.dtype((np.void, features.dtype.itemsize * features.shape[1])))
    _, ids = np.unique(a, return_index=True)
    return features[ids]

def traverse(root, lst):
  lst.append(root.count)
  for c in root.children:
    traverse(c, lst)
  return lst

imgs = get_imgs()
features = get_features_np(imgs)
img_data = zip(imgs, features)

print len(img_data)
tree = KMeansTree(20)
tree.add_imgs(img_data)
tree.train()

"""
start = datetime.now()

kmeans = cluster.KMeans(n_clusters=20, init='k-means++')
kmeans.fit(features)

labels_count = np.bincount(kmeans.labels_)
labels_count_ids = np.nonzero(labels_count)[0]

print zip(labels_count_ids, labels_count[labels_count_ids])

print kmeans.labels_.min(), kmeans.labels_.max(), len(kmeans.cluster_centers_)
fin = datetime.now()
print "Time: ", (fin - start).seconds
"""
