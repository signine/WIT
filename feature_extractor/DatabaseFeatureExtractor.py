import cv2
import numpy as np
import os, sys
import mysql.connector
import simplejson as json
import mser
FEATURE_DETECTOR = "MSER"
FEATURE_DESCRIPTOR = "SIFT"

def get_detector():
  if FEATURE_DETECTOR == "MSER":
    return mser
  else:
    return cv2.FeatureDetector_create(FEATURE_DETECTOR)

def main():
  image_dir = sys.argv[1]
  if not image_dir:
    print "Usage: python DatabaseFeatureExtractor.py <image dir>"
    return

  detector = get_detector() 
  descriptor = cv2.DescriptorExtractor_create(FEATURE_DESCRIPTOR)
  try:
    cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='wit', buffered=True)
  except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      print("Database does not exists")
    else:
      print(err)
  else: 
    cursor = cnx.cursor()
    
    for filename in os.listdir(image_dir):
      if filename.endswith(".jpg"):
        img = cv2.imread(os.path.join(image_dir, filename))
        imageid = filename.split('_')
        print filename

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        kp = detector.detect(img)
        kp, des = descriptor.compute(img, kp)
        j = 0
        for keypoint in kp:
          insert_string = ("INSERT INTO features " 
          "(image_id, x, y, size, angle, descriptor, algorithm)"     
          "VALUES (%s, %s, %s, %s, %s, %s, '%s')" %(imageid[0], keypoint.pt[0], keypoint.pt[1], keypoint.size, keypoint.angle, json.dumps(str(des[j])), FEATURE_DETECTOR) )
          cursor.execute(insert_string)
          j=j+1
  cnx.commit()
  cursor.close()      
  cnx.close()

if __name__ == "__main__":
  main()
