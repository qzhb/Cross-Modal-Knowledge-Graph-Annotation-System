g++ ID_5.cpp -o ID_5.o -std=c++11 `pkg-config opencv --cflags --libs` -I. -L./lib/x64 -lSeetaFaceDetector200 -lSeetaPointDetector200 -lSeetaFaceCropper200 -lSeetaFaceRecognizer200 -lzmq -Wl,-rpath,./lib/x64