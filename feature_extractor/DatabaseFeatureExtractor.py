import cv2
import numpy as np
import os
import mysql.connector
import json
FEATURE_DETECTOR = "SIFT"
FEATURE_DESCRIPTOR = "SIFT"
def main():
	try:
		cnx = mysql.connector.connect(user='root', password='piesek',
								  host='127.0.0.1',
								  database='test')
	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("Something is wrong with your user name or password")
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			print("Database does not exists")
		else:
			print(err)
	else:	
		cursor = cnx.cursor()
		i = 0
		for filename in os.listdir(os.getcwd()):
			if filename.endswith((".jpg")):
				img = cv2.imread(filename)
				imageid = filename.split('_')
				print(imageid[0])
				gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
				detector = cv2.FeatureDetector_create(FEATURE_DETECTOR)
				descriptor = cv2.DescriptorExtractor_create(FEATURE_DESCRIPTOR)
				kp = detector.detect(img)
				kp, des = descriptor.compute(img, kp)
				j = 0
				for keypoint in kp:
					#with open("Output.txt", "a") as text_file:
					#	text_file.write("image info: %s %s %s %s %s %s %s \n  "% (i+j, imageid[0], keypoint.pt[0], keypoint.pt[1], keypoint.size, keypoint.angle, des[j]))
					insert_string = ("INSERT INTO features " 
					"(id, image_id, x, y, size, angle, descriptor)" 		
					"VALUES (%s, %s, %s, %s, %s, %s, %s)" %(i+j+1, imageid[0], keypoint.pt[0], keypoint.pt[1], keypoint.size, keypoint.angle, json.dumps(str(des[j]))) )
					cursor.execute(insert_string)
					j=j+1
				i=j
	cnx.commit()
	cursor.close()			
	cnx.close()
if __name__ == "__main__":
	main()
