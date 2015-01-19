import numpy as np
import sys, os 
import simplejson as json
sys.path.append(os.path.join(os.getcwd(), "../indexer"))
from img_utils import get_imgs, get_features_np, get_features, convert_to_numpy
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.sql import text

class KMeansNode():
  
  def __init__(self):
    self.id = None
    self.parent = None
    self.descriptor = None
    self.features = None
    self.children = []
    self.imgs = []

class KMeansTreeMatcher():
  def __init__(self):
    self.db = create_engine("mysql://root@localhost:3306/WIT")
    self.node_cache = {}
    self.img_cache = {}

    self.root = self.__fetch_root()
    self.node_cache[self.root.id] = self.root 

  def __fetch_root(self):
    q = self.db.execute(text("SELECT * FROM kmeans_tree WHERE parent_id IS NULL"))
    return self.__sql_to_object(iter(q).next())
  
  def __fetch_node(self, id):
    q = self.db.execute(text("SELECT * FROM kmeans_tree WHERE id=:id"), id=id)
    return self.__sql_to_object(iter(q).next())

  def __sql_to_object(self, sql):
    obj = KMeansNode()
    obj.id = sql[0]
    obj.parent = sql[1]
    obj.features = sql[5]
    obj.children = json.loads(sql[3])
    obj.imgs = json.loads(sql[4])

    descriptor = sql[2]
    if descriptor is not None and descriptor != '': 
      obj.descriptor = self.__convert_to_numpy(json.loads(descriptor))

    return obj

  def __convert_to_numpy(self, feature):
      f = map(lambda x: np.float32(x), feature)
      return np.array(f)
      
  def knn_match(self, feature_list, **kwargs):
    """
    Takes a list of features and returnes best matches for each feature
    """

    return [ self.knn_search(data, **kwargs) for data in feature_list ]


  def knn_search(self, feature, **kwargs):
    """
    Takes one feature and returns nearest neighbors
    """
    s = datetime.now()
    if 'k' in kwargs:
      k = kwargs['k']
    else:
      k = 1

    queue = [self.root]
    ret = []
    self.__knn_search(feature, queue, ret, k)

    f = datetime.now()
    print "Search time: ", (f-s).seconds
    return ret

  def __knn_search(self, feature, queue, ret, k):
    if k == 0: return ret
    if len(queue) == 0: return ret

    node = queue.pop()
    if len(node.children) > 0:
      dis = []
      for id in node.children:
        n = self.__get_node(id)
        dis.append((n, self.__distance(feature, n.descriptor)))
      dis = sorted(dis, key=lambda x: x[1], reverse=True)
      new_c, dis = zip(*dis)
      queue += new_c
      self.__knn_search(feature, queue, ret, k)
    else:
      k -= 1
      ret.append(node)
      self.__knn_search(feature, queue, ret, k)
    
  def __distance(self, d1, d2):
    return np.linalg.norm(d1-d2)

  def __get_node(self, id):
    if id not in self.node_cache:
      node = self.__fetch_node(id)
      self.node_cache[id] = node
    return self.node_cache[id]

def main():
  tree = KMeansTreeMatcher()

  imgs = get_imgs()
  features = get_features_np(imgs)

  p = tree.knn_match(features[0])
  for k in p:
    for i in k:
      print i.imgs

if __name__ == '__main__':
  main()
