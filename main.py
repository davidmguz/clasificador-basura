from cvzone.ClassificationModule import Classifier
import cv2

cap = cv2.VideoCapture(0)
classifier = Classifier('Resources/Model/keras_model.h5', 'Resources/Model/labels.txt')
while True:
    _, img = cap.read()
    predection = classifier.getPrediction(img)
    print(predection)
    cv2.imshow('Image', img)
    cv2.waitKey(1)