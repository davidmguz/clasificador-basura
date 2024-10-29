import os
import subprocess
import cvzone
from cvzone.ClassificationModule import Classifier
from PIL import Image, ImageTk
import tkinter as tk
import cv2

# Función para capturar imagen con libcamera-still
def capture_image():
    subprocess.run(["libcamera-still", "-t", "5000", "-n", "-o", "test.jpg"])
    return cv2.imread("test.jpg")

# Función para capturar y clasificar la imagen
def capture_and_classify():
    global captured, imgBackground, classIdBin

    img = capture_image()
    imgResize = cv2.resize(img, (454, 340))
    predection = classifier.getPrediction(img)
    classId = predection[1]

    if classId != 0:
        imgBackground = cvzone.overlayPNG(imgBackground, imgWasteList[classId - 1], (909, 127))
        imgBackground = cvzone.overlayPNG(imgBackground, imgArrow, (978, 320))
        classIdBin = classDic[classId]

    if classIdBin is not None and classIdBin >= 0 and classIdBin < len(imgBinsList):
        imgBackground = cvzone.overlayPNG(imgBackground, imgBinsList[classIdBin], (895, 374))

    imgBackground[148:148 + 340, 159:159 + 454] = imgResize
    captured = True
    update_image()

# Función para reiniciar la imagen
def reset_image():
    global captured, imgBackground
    imgBackground = cv2.imread('Resources/background.png')
    captured = False
    update_image()

# Función para actualizar la imagen en la interfaz
def update_image():
    imgShow = cv2.cvtColor(imgBackground, cv2.COLOR_BGR2RGB)
    imgPIL = Image.fromarray(imgShow)
    imgTk = ImageTk.PhotoImage(imgPIL)
    lbl_img.config(image=imgTk)
    lbl_img.image = imgTk

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Clasificación de Residuos - Raspberry Pi")

# Frame para los botones
btn_frame = tk.Frame(root)
btn_frame.pack(side=tk.TOP, pady=10)

btn_capture = tk.Button(btn_frame, text="Capturar Imagen", command=capture_and_classify)
btn_capture.pack(side=tk.LEFT, padx=5)

btn_reset = tk.Button(btn_frame, text="Reiniciar Imagen", command=reset_image)
btn_reset.pack(side=tk.LEFT, padx=5)

# Label para la imagen
lbl_img = tk.Label(root)
lbl_img.pack(pady=10)

# Inicialización
classifier = Classifier('Resources/Model/keras_model.h5', 'Resources/Model/labels.txt')
imgArrow = cv2.imread('Resources/arrow.png', cv2.IMREAD_UNCHANGED)
classIdBin = 0

imgWasteList = []
pathFolderWaste = 'Resources/Waste'
pathList = os.listdir(pathFolderWaste)
for path in pathList:
    imgWasteList.append(cv2.imread(os.path.join(pathFolderWaste, path), cv2.IMREAD_UNCHANGED))

imgBinsList = []
pathFolderBins = 'Resources/Bins'
pathList = os.listdir(pathFolderBins)
for path in pathList:
    imgBinsList.append(cv2.imread(os.path.join(pathFolderBins, path), cv2.IMREAD_UNCHANGED))

classDic = {0: None, 1: 3, 2: 0, 3: 2, 4: 3, 5: 1, 6: 3, 7: 0, 8: 1}
imgBackground = cv2.imread('Resources/background.png')
captured = False

update_image()
root.mainloop()