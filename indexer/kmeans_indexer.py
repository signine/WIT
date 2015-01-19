import numpy as np
import simplejson as json
from sklearn import cluster
from img_utils import get_imgs, get_features_np, get_features, convert_to_numpy
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.sql import text

class KMeansNode():
  
  def __init__(self, data):
    self.data = data 
    self.children = []
    self.parent = None
    self.count = 0 # Number of data points clustered for this node
    self.imgs = [] # ids of images that have this feature

class KMeansTree():

  INSERT_NODE_SQL = text("INSERT INTO kmeans_tree (parent_id, descriptor, images, features) VALUES (:parent_id, :des, :images, :features);")
  UPDATE_CHILDREN_SQL = text("UPDATE kmeans_tree SET children=:children where id=:id;")

  def __init__(self, branch):
    self.data = [] # Flat list of all features, used for clustering
    self.root = None
    self.db = None
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

    self.__build_index_files()

    fin = datetime.now()
    print "Train time: ", (fin - start).seconds

  def __build_index_files(self):
    print "Building index files"
    for img, features in self.imgs:
      for f in features:
        img_id = img[0]
        nodes = self.knn_search(f, k=1)
        n = nodes[0]
        d = self.__distance(f, n.data) 
        if d != 0: print d, img
        if img_id not in n.imgs: n.imgs.append(img_id)

  def __cluster(self, data):
    #print "Cl len: ", len(data)
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

  def __distance(self, d1, d2):
    return np.linalg.norm(d1-d2)

  def knn_match(self, data_list, **kwargs):
    """
    Takes a list of features and returnes best matches for each feature
    """

    return [ self.knn_search(data, **kwargs) for data in data_list ]


  def knn_search(self, data, **kwargs):
    """
    Takes one feature and returns nearest neighbors
    """
    if 'k' in kwargs:
      k = kwargs['k']
    else:
      k = 1

    if not self.root: raise Exception("Tree has not been built")

    queue = [self.root]
    ret = []
    self.__knn_search(data, queue, ret, k)
    return ret

  def __knn_search(self, data, queue, ret, k):
    if k == 0: return ret
    if len(queue) == 0: return ret

    node = queue.pop()
    if len(node.children) > 0:
      dis = [ (c, self.__distance(data, c.data)) for c in node.children ]
      dis = sorted(dis, key=lambda x: x[1], reverse=True)
      new_c, dis = zip(*dis)
      queue += new_c
      self.__knn_search(data, queue, ret, k)
    else:
      k -= 1
      ret.append(node)
      self.__knn_search(data, queue, ret, k)

  def save_to_db(self):
    print "Saving to db"
    s = datetime.now()
    if not self.root: raise Exception("Tree has not been built")

    self.__save_node(self.root, None)

    f = datetime.now()
    print "Time: ", (f - s).seconds

  def __get_db(self):
    if not self.db:
      self.db = create_engine("mysql://root@localhost:3306/WIT")
    return self.db
  
  def __save_node(self, node, parent_id):
    """
    Recursively inserts a node into db
    Returns id of node
    """
    db = self.__get_db()
    if type(node.data) == np.ndarray:
      data = json.dumps(node.data.tolist())
    else:
      data = ''
    row = db.execute(self.INSERT_NODE_SQL, parent_id=parent_id, des=data, images=json.dumps(node.imgs), features=node.count) 
    node_id = row.lastrowid

    children_ids = [ self.__save_node(c, node_id) for c in node.children ]
    db.execute(self.UPDATE_CHILDREN_SQL, id=node_id, children=json.dumps(children_ids))
    return node_id

def build_index(branch_factor):
  imgs = get_imgs()
  features = get_features_np(imgs)
  img_data = zip(imgs, features)
  
  print "Total features: ", len(img_data)
  index = KMeansTree(branch_factor)
  index.add_imgs(img_data)
  index.train()
  return index

def traverse(root, lst):
  lst.append(root.count)
  for c in root.children:
    traverse(c, lst)
  return lst

tree = None

def main():
  global tree
  imgs = get_imgs()
  features = get_features_np(imgs)
  img_data = zip(imgs, features)
  
  print len(img_data)
  tree = KMeansTree(20)
  tree.add_imgs(img_data)
  tree.train()
  tree.save_to_db()

if __name__ == '__main__':
  main()
