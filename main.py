import os
import cvzone
from cvzone.ClassificationModule import Classifier
import cv2

cap = cv2.VideoCapture(0)
classifier = Classifier('Resources/Model/keras_model.h5', 'Resources/Model/labels.txt')
imgArrow=cv2.imread('Resources/arrow.png', cv2.IMREAD_UNCHANGED)
classIdBin=0

# Import all the waste images
imgWasteList = []
pathFolderWaste = 'Resources/Waste'
pathList = os.listdir(pathFolderWaste)
# print(pathFolderWaste)
for path in pathList:
    imgWasteList.append(cv2.imread(os.path.join(pathFolderWaste, path), cv2.IMREAD_UNCHANGED))

# Import all the waste images
imgBinsList = []
pathFolderBins = 'Resources/Bins'
pathList = os.listdir(pathFolderBins)
# print(pathFolderWaste)
for path in pathList:
    imgBinsList.append(cv2.imread(os.path.join(pathFolderBins, path), cv2.IMREAD_UNCHANGED))

# 0=Fondo
# 1=

# 0=Recyclable
# 1=Hazardous
# 2=Food
# 3=Residual

classDic={0:None,
          1:3,
          2:0,
          3:2,
          4:3,
          5:1,
          6:3,
          7:0,
          8:1}

while True:
    _, img = cap.read()
    imgResize = cv2.resize(img, (454, 340))

    imgBackground = cv2.imread('Resources/background.png')

    predection = classifier.getPrediction(img)
    # print(predection)
    classId = predection[1]
    # print(classId)
    if classId !=0:
        imgBackground = cvzone.overlayPNG(imgBackground, imgWasteList[classId-1], (909, 127))
        imgBackground = cvzone.overlayPNG(imgBackground, imgArrow, (978, 320))

        classIdBin = classDic[classId]

    imgBackground = cvzone.overlayPNG(imgBackground, imgBinsList[classIdBin], (895, 374))

    imgBackground[148:148+340, 159:159+454] = imgResize

    # Displays
    # cv2.imshow('Image', img)
    cv2.imshow('Output', imgBackground)
    cv2.waitKey(1)