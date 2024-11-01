import os
import subprocess
import cv2
import cvzone
from cvzone.ClassificationModule import Classifier
from PIL import Image, ImageTk
import tkinter as tk

# Diccionario para contar los residuos
#waste_counter = {i: 0 for i in range(1, 9)}  # Suponiendo que hay 8 clases de residuos

# Ruta de imagen
image_path = 'imagen.jpg'


# Función para capturar y clasificar la imagen
def capture_and_classify():
    global captured, imgBackground, classIdBin

    # Captura la imagen usando libcamera
    subprocess.run(f"libcamera-still -o {image_path}", shell=True)

    # Lee la imagen capturada con OpenCV
    img = cv2.imread(image_path)

    if img is None:
        print("Error: No se pudo leer la imagen.")
        return

    # Redimensiona la imagen
    imgResize = cv2.resize(img, (454, 340))

    # Clasificación de la imagen
    predection = classifier.getPrediction(imgResize)
    classId = predection[1]

    if classId != 0:
        imgBackground = cvzone.overlayPNG(imgBackground, imgWasteList[classId-1], (909, 127))
        imgBackground = cvzone.overlayPNG(imgBackground, imgArrow, (978, 320))
        classIdBin = classDic[classId]

        # Actualizar contador
        #waste_counter[classId] += 1

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


# Función para actualizar la imagen y los contadores en la interfaz
def update_image():
    imgShow = cv2.cvtColor(imgBackground, cv2.COLOR_BGR2RGB)
    imgPIL = Image.fromarray(imgShow)
    imgTk = ImageTk.PhotoImage(imgPIL)
    lbl_img.config(image=imgTk)
    lbl_img.image = imgTk
    #update_counter_labels()


# Función para actualizar los contadores en la interfaz
#def update_counter_labels():
#    for i in range(1, 9):  # Suponiendo que hay 8 clases de residuos
#        lbl_counters[i - 1].config(text=f"Tipo {i}: {waste_counter[i]}")


# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Clasificación de Residuos")

# Crear un marco para los botones
frame_buttons = tk.Frame(root)
frame_buttons.pack(side=tk.TOP, fill=tk.X, pady=10)

btn_capture = tk.Button(frame_buttons, text="Capturar Imagen", command=capture_and_classify)
btn_capture.pack(side=tk.LEFT, padx=5)

btn_reset = tk.Button(frame_buttons, text="Reiniciar Imagen", command=reset_image)
btn_reset.pack(side=tk.LEFT, padx=5)

# Crear una etiqueta para la imagen
lbl_img = tk.Label(root)
lbl_img.pack(pady=10)

# Crear etiquetas para mostrar los contadores
frame_counters = tk.Frame(root)
frame_counters.pack(side=tk.BOTTOM, pady=10)

lbl_counters = []
for i in range(8):  # Suponiendo que hay 8 clases de residuos
    lbl_counter = tk.Label(frame_counters, text=f"Tipo {i+1}: 0")
    lbl_counter.pack(pady=2)
    lbl_counters.append(lbl_counter)

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

classDic = {0: None,
            1: 3,
            2: 0,
            3: 2, 4: 3, 5: 1, 6: 3, 7: 0, 8: 1}
imgBackground = cv2.imread('Resources/background.png')
captured = False

update_image()
root.mainloop()
