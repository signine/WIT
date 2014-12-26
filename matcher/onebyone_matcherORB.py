import cv2
import numpy as np
import sys
import os
import time
FEATURE_DETECTOR = "SIFT"
FEATURE_DESCRIPTOR = "SURF"
MATCHES_NUM = 100
USE_MATCH_RANGE = True
RANGE_START = 0
RANGE_END = 300
DISTANCE_LIMIT = 300
RATIO_TEST = False
best_matches= []


def draw_matches(imgt, imgq, kpt, kpq, matches, **kwargs):
	"""
	Draws lines between matching keypoints.
	Training image on left and query image on right.
	imgt - training image
	imgq - query image
	kpqt - training keypoints
	kpq - query keypoints
	matches
	kwargs
	numbers = true Write numbers instead of lines
	"""
	# Filter out keypoints that are not in matches
	kpq = [ kpq[m.queryIdx] for m in matches ]
	kpt = [ kpt[m.trainIdx] for m in matches ]
	img3 = cv2.drawKeypoints(imgt, kpt, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
	img4 = cv2.drawKeypoints(imgq, kpq, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
	combined_image = np.hstack((img3, img4))
	height, width, depth = img3.shape
	if "numbers" in kwargs and kwargs["numbers"]:
		draw_lines = False
	else:
		draw_lines = True
	for i,m in enumerate(matches):
		print m.distance
		x1 = int(kpt[i].pt[0])
		y1 = int(kpt[i].pt[1])
		x2 = int(kpq[i].pt[0])
		y2 = int(kpq[i].pt[1])
		if draw_lines:
			cv2.line(combined_image, (x1, y1), (x2 + width, y2), (255, 0, 0), 1)
		else:
			cv2.putText(combined_image, str(i), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0)
			cv2.putText(combined_image, str(i), (x2 + width, y2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0)
	cv2.imshow("Matches", combined_image)
	cv2.waitKey()
	cv2.destroyAllWindows()

	
def main():
	global best_matches


	#set up detectors/descriptors
	orb = cv2.ORB()
	detector = cv2.FeatureDetector_create(FEATURE_DETECTOR)
	descriptor = cv2.DescriptorExtractor_create(FEATURE_DESCRIPTOR)
	FLANN_INDEX_KDTREE = 0
	index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
	search_params = dict(checks=50) # or pass empty dictionary
	bf = cv2.BFMatcher()
	#flann = cv2.FlannBasedMatcher(index_params, search_params)
	if RATIO_TEST:
		knn = 2
	else:
		knn = 1
	
	#compose db
	images = []
	grayimages = []
	best_matches = []
	keypoints = []
	descriptors = []
	i = 0
	for filename in os.listdir("database"):
		if filename.endswith((".jpg")):
			print(filename)
			images.append(cv2.imread("database/" + filename))
			grayimages.append(cv2.cvtColor(images[i], cv2.COLOR_BGR2GRAY))
			kp2 = orb.detect(grayimages[i])
			kp2, des2 = orb.compute(grayimages[i], kp2)
			keypoints.append(kp2)
			descriptors.append(des2)
			i = i+1
	
	#prompt user for query image
	img_name = raw_input("Please enter image name: ")
	print "you entered", img_name
	img1 = cv2.imread(img_name)
	gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
	kp1 = orb.detect(gray1)
	kp1, des1 = orb.compute(gray1, kp1)
	print "Img1 features: ", len(des1)
	
	print "length of descriptors: ", len(descriptors)
	
	#find match
	i = 0
	best_image = 0
	startglobal = time.clock()
	new_matches = [];
	best_matches =  [[None] for x in range(1000)];
	for image in images :
			matches = bf.knnMatch(descriptors[i], des1, k=knn)
			print "Total matches: ", len(matches)
			if USE_MATCH_RANGE:
				start = RANGE_START
				end = RANGE_END
			else:
				start = 0
				end = MATCHES_NUM

			if RATIO_TEST:
			# ratio test
				for j,(m,n) in enumerate(matches):
					if m.distance < 0.7*n.distance:
						print "here";
						best_matches[i].append((matches[j]))
						
				# Filter by distance
				best_matches[i] =([ m[0] for m in new_matches if m[0].distance < DISTANCE_LIMIT][start:end])
			else:
				best_matches[i] = ([ m[0] for m in matches if m[0].distance < DISTANCE_LIMIT][start:end])
			best_matches[i] = sorted(best_matches[i], key=lambda x: x.distance)	
			print "Good matches: ", len(best_matches[i])	
			if len(best_matches[i]) > len(best_matches[best_image]):
				best_image = i
				print("best match :", i)
			i = i+1
	print "Total time to match image:", time.clock() - startglobal			
	draw_matches(img1, images[best_image], kp1, keypoints[best_image], best_matches[best_image])

	
if __name__ == "__main__":
	main()
