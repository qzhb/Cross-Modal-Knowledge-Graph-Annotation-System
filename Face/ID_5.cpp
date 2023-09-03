/*************************************************************************
	> File Name: test.cpp
	> Author: 
	> Mail: 
	> Created Time: 2019年08月20日 星期二 10时40分38秒
 ************************************************************************/
#include "stdlib.h"
#include <dirent.h>
#include <iostream>
#include <cstring>
#include <string>
#include <vector>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>

#include <seeta/FaceDetector2.h>
#include <seeta/PointDetector2.h>
#include <seeta/FaceCropper2.h>
#include <seeta/FaceRecognizer.h>
#include <seeta/Struct_cv.h>

#include <fstream>
#include <sstream>
#include <iomanip>

#include <zmq.hpp>

int register_image(seeta::FaceDetector2 &FD, seeta::PointDetector2 &PD, seeta::FaceRecognizer2 &FR, const std::string &filename)
{
    cv::Mat mat = cv::imread(filename);
    if (mat.empty()) return -1;
    seeta::cv::ImageData image = mat;
    SeetaRect *face = FD.Detect(image);
    if (!face) return -1;
    SeetaPointF *points = PD.Detect(image, *face);
    if (!points) return -1;
    return FR.Register(image, points);  // Reture -1 if failed.
}

std::vector <std::string> findfile(std::string path)
{
    DIR *dp;
    struct dirent *dirp;
    std::vector<std::string> filename;
    if( (dp=opendir(path.c_str()))==NULL)
        perror("open dir error");
        while( (dirp=readdir(dp))!=NULL){
            if( (strcmp(dirp->d_name, ".")!=0) &&  (strcmp(dirp->d_name, "..")!=0)){
                filename.push_back(path + std::string(dirp->d_name));
        }
    }
    for (int i = 0;i<filename.size();i++)
        std::cout<<i<<":"<<filename[i]<<std::endl;
    closedir(dp);
    return filename;
}

std::string int2str( int val )
{
    std::ostringstream out;
    out<<val;
    return out.str();
}

    seeta::FaceDetector2 FD("bindata/SeetaFaceDetector2.0.ats");
    seeta::PointDetector2 PD("bindata/SeetaPointDetector2.0.pts5.ats");
    seeta::FaceRecognizer2 FR("bindata/SeetaFaceRecognizer2.0.ats");
    seeta::FaceCropper2 FC;
std::vector<std::string> DB_init(std::string db){

    int OK_ = -1;
    
    std::vector<std::string> Face_DB;
    std::vector <std::string> image_list = findfile(db);
    for (int img=0;img<image_list.size(); img++){
        OK_ = register_image(FD, PD, FR, image_list[img]);
        if (OK_!=-1)
            Face_DB.push_back(image_list[img]);
        else
        std::cout << image_list[img] << std::endl;
    }
    return Face_DB;
}
    
std::string ID(std::string imgss, std::vector<std::string> Face_DB){
    cv::Mat mat = cv::imread(imgss);
    std::string RESULT("Width: ");
    RESULT.append(int2str(mat.size().width));
    RESULT.append(std::string("Height: "));
    RESULT.append(int2str(mat.size().height));
    std::cout << "Width : " << mat.size().width << std::endl;
    std::cout << "Height: " << mat.size().height << std::endl;
    seeta::cv::ImageData image = mat;
    int num;    // save the number of detected faces
    SeetaRect *face = FD.Detect(image, &num);
    
    for (int i = 0; i < num; ++i, ++face)
    {
        RESULT.append(std::string("FACE: "));
        RESULT.append(int2str(face->x));
        RESULT.append(std::string(","));
        RESULT.append(int2str(face->y));
        RESULT.append(std::string(","));
        RESULT.append(int2str(face->width+face->x));
        RESULT.append(std::string(","));
        RESULT.append(int2str(face->height+face->y));

        std::cout << face->x << "," << face->y << "," << face->x+face->width << "," << face->y+face->height << ",";
    	auto points = PD.Detect(image, *face);
    	seeta::cv::ImageData cropped_face = FC.Crop(image, points); // crop face according to 5 landmarks
    
    	// cv::Mat cropped_face_mat = cropped_face;
    	// cv::imwrite("CROPPED_FACE.jpg", cropped_face_mat);

        // zmq::context_t context(1);
        // zmq::socket_t socket(context, ZMQ_REQ);
        // socket.connect("tcp://localhost:5555");

        // zmq::message_t request(5);
        // memcpy(request.data(), "Hello", 5);
        // socket.send(request);

        //  Get the reply.
        // zmq::message_t reply;
        // socket.recv(&reply);
        // std::string rpl = std::string(static_cast<char*>(reply.data()), reply.size());
        // std::cout << rpl << std::endl;
        RESULT.append(std::string("EMOTION: "));
        RESULT.append("DEFAULT");

	float SIM = 0;
        int top1 = FR.Recognize(image, points, &SIM);
	float *similar = FR.RecognizeEx(image, points);
	int top2 = 0;
        for (int i = 0; i < FR.MaxRegisterIndex(); ++i)
        {
            if(similar[top2]<similar[i] && (i!=top1))
		top2=i;
        }
	int top3 = 0;
        for (int i = 0; i < FR.MaxRegisterIndex(); ++i)
        {
            if(similar[top3]<similar[i] && (i!=top1) && (i!=top2))
		top3=i;
        }
	int top4 = 0;
        for (int i = 0; i < FR.MaxRegisterIndex(); ++i)
        {
            if(similar[top4]<similar[i] && (i!=top1) && (i!=top2) && (i!=top3))
		top4=i;
        }
	int top5 = 0;
        for (int i = 0; i < FR.MaxRegisterIndex(); ++i)
        {
            if(similar[top5]<similar[i] && (i!=top1) && (i!=top2) && (i!=top3) && (i!=top4))
		top5=i;
        }

        std::string str = Face_DB[top1];
        std::cout<<str<<",";
        RESULT.append(std::string("ID1: "));
        RESULT.append(str);

        str = Face_DB[top2];
        std::cout<<str<<",";
        RESULT.append(std::string("ID2: "));
        RESULT.append(str);

        str = Face_DB[top3];
        std::cout<<str<<",";
        RESULT.append(std::string("ID3: "));
        RESULT.append(str);

        str = Face_DB[top4];
        std::cout<<str<<",";
        RESULT.append(std::string("ID4: "));
        RESULT.append(str);

        str = Face_DB[top5];
        std::cout<<str<<",";
        RESULT.append(std::string("ID5: "));
        RESULT.append(str);
    }
        std::cout<<std::endl;
    
    std::ofstream ofs("info.txt");
    ofs<<RESULT;
    ofs.close();

    return RESULT;
    
}    

void split(const std::string& s,
    std::vector<std::string>& sv,
                  const char* delim = " ") {
    sv.clear();                                 // 1.
    char* buffer = new char[s.size() + 1];      // 2.
    std::copy(s.begin(), s.end(), buffer);      // 3.
    char* p = std::strtok(buffer, delim);       // 4.
    do {
        sv.push_back(p);                        // 5.
    } while ((p = std::strtok(NULL, delim)));   // 6.
    return;
}

main(int argc, char* argv[]){

   zmq::context_t contexts(1);
   zmq::socket_t socket_s(contexts, ZMQ_REP);
   socket_s.bind("tcp://*:5558");
   zmq::message_t rcv;
   std::vector<std::string> Face_DB;
   
   while(true){
        socket_s.recv(&rcv);
        std::string rpl = std::string(static_cast<char*>(rcv.data()), rcv.size());
        std::vector<std::string> sv;
        split(rpl, sv, " ");
	if(atoi(sv[2].c_str())==2){
            FR.Clear();
	    Face_DB = DB_init(sv[1]);
            zmq::message_t request_(8192);
            memcpy(request_.data(), "ggggg", 8192);
            socket_s.send(request_);
	}
	else{
	    if(atoi(sv[2].c_str())==1){
                FR.Clear();
	        Face_DB = DB_init(sv[1]);
	    }
	    std::string RESULT = ID(sv[0], Face_DB);
	        std::cout<<RESULT;
	    RESULT.append(std::string("END"));
            zmq::message_t request_(8192);
            memcpy(request_.data(), RESULT.c_str(), 8192);
            socket_s.send(request_);
	}
   }
   

    return 0;
}
