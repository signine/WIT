#define _CRT_SECURE_NO_DEPRECATE

#include <stdio.h>
#include <iostream>
#include <opencv/cv.h>
#include <opencv/highgui.h>
#include <opencv2/features2d/features2d.hpp>
#include <opencv2/nonfree/nonfree.hpp>
#include "opencv2/nonfree/features2d.hpp"
#include <dirent.h>
#include <sys/types.h>
#include "mysql_connection.h"
#include "mysql_driver.h"
#include "mysql_error.h"

int main(int argc, const char* argv[])
{
	//DB stuff - I need to fix - Having linking issues
	sql::mysql::MySQL_Driver *driver;
	sql::Connection *conn;
	//driver = sql::mysql::get_mysql_driver_instance();
	//conn = driver->connect("tcp://127.0.0.1:3306", "user", "password");

	cv::SiftFeatureDetector detector;
	cv::SiftDescriptorExtractor  extractor;
	const char* directory =  argv[1];
	if (directory == NULL) return -1;
	DIR *dir;
	struct dirent *image;
	if ((dir = opendir(directory)) != NULL)
	{
		//iterate through all images in the directory
		while ((image = readdir(dir)) != NULL) 
		{
			if (image->d_name[0] == '.') continue;
			std::vector<cv::KeyPoint> keypoints;
			cv::Mat descriptors;
			std::ostringstream ss;

			//extract image id from file name
			int i = 0;
			while (image->d_name[i] != '_' && image->d_name[i] != '.')
			{
				ss << image->d_name[i];
				i++;
			}
			std::string imageId(ss.str());

            //detect keypoints and extract decriptors
			const cv::Mat cvimage = cv::imread(image->d_name, 0);
			printf(image->d_name);
			detector.detect(cvimage, keypoints);
			extractor.compute(cvimage, keypoints, descriptors);
			
			//add all keypoints of the image to the database
		    for (int i = 0; i < keypoints.size(); i++)
		    {
				cv::Range range1 = cv::Range(2, 2);
				ss.str("");
				float* descPtr = descriptors.ptr<float>(i);
				for (int j = 0; j < descriptors.cols; j++)
					ss << *descPtr++ << ", ";
				std::string descriptorString(ss.str());
				//what primary key do i use? 
			    //sql::mysql::mysql_query(conn, "INSERT INTO features VALUES ( i, imageId, keypoints[i].pt.x, keypoints[i].pt.y, keypoints[i].size, keypoints[i].angle, descriptorString)");
			}
		}
		closedir(dir);
	}
	delete conn;
}
