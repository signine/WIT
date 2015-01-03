import numpy as np
from sklearn import cluster
from img_utils import get_imgs, get_features, convert_to_numpy
from datetime import datetime


def flatten_features(features):
  return np.array([ f for img in features for f in img ])

imgs = get_imgs()
features = convert_to_numpy(get_features(imgs))
features = flatten_features(features)

print len(features)

start = datetime.now()

kmeans = cluster.KMeans(n_clusters=5, init='k-means++')
kmeans.fit(features)

fin = datetime.now()
print "Time: ", (fin - start).seconds


