import os
import subprocess
import cvzone
from cvzone.ClassificationModule import Classifier
from PIL import Image, ImageTk
import tkinter as tk
import cv2
import RPi.GPIO as GPIO
import time

# Configuración de pines para el motor paso a paso
CLK_PIN = 6  # Pin GPIO6 (Paso)
CW_PIN = 5   # Pin GPIO5 (Dirección)

# Configuración de GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(CLK_PIN, GPIO.OUT)
GPIO.setup(CW_PIN, GPIO.OUT)

# Función para capturar imagen con libcamera-still
def capture_image():
    # Reducir el tiempo de espera de 1000ms a 500ms
    # Agregar opciones para optimizar la captura
    subprocess.run([
        "libcamera-still",
        "-t", "500",           # Reducir tiempo de espera a 500ms
        "-n",                  # No mostrar preview
        "--immediate",         # Captura inmediata
        "--nopreview",        # Desactivar preview
        "--rotation", "0",     # Si no necesitas rotación
        "--width", "640",      # Reducir resolución si es posible
        "--height", "480",     # Reducir resolución si es posible
        "-o", "test.jpg"
    ])
    return cv2.imread("test.jpg")


# Función para capturar y clasificar la imagen
def capture_and_classify():
    global captured, imgBackground, classIdBin

    img = capture_image()
    imgResize = cv2.resize(img, (454, 340))
    prediction = classifier.getPrediction(img)
    classId = prediction[1]  # Obtener el ID de la clase

    # Debugging output para ver la clasificación
    print(f"Imagen capturada, ClassId: {classId}")

    # Verificación de la clasificación y asociación con el tacho
    if classId in classDic:
        classIdBin = classDic[classId]  # Obtener el contenedor asignado según el classId
        print(f"ClassId: {classId}, Contenedor asignado: {classIdBin}")

        # Clasificacion de los IDs

        if classId == 8 or classId == 5:
            print("peligroso")
            control_motor(0)
        elif classId == 3:
            print("reciclable")
            control_motor(1900)
        elif classId == 1 or classId == 4 or classId == 6:
            print("otros")
            control_motor(900)
        elif classId == 2 or classId == 7:
            print("reciclable")
            control_motor(2750)

        # Verificar si la imagen del residuo está en el rango
        if classId > 0 and classId <= len(imgWasteList):
            imgWaste = imgWasteList[classId - 1]  # Restamos 1 porque la lista comienza en 0
            imgBackground = cvzone.overlayPNG(imgBackground, imgWaste, (909, 127))
            print(f"Imagen del residuo {classId} mostrada correctamente.")
        else:
            print(f"Error: No hay imagen de residuo para ClassId {classId}")

        # Mostrar la flecha
        imgBackground = cvzone.overlayPNG(imgBackground, imgArrow, (978, 320))

        # Mostrar el contenedor si la asignación es válida
        if classIdBin is not None and 0 <= classIdBin < len(imgBinsList):
            imgBin = imgBinsList[classIdBin]  # Obtenemos la imagen del contenedor
            imgBackground = cvzone.overlayPNG(imgBackground, imgBin, (895, 374))
            print(f"Imagen del contenedor {classIdBin} mostrada correctamente.")
        else:
            print(f"Error: Contenedor no válido para ClassId {classId}")
    else:
        print(f"Error: ClassId {classId} no encontrado en classDic")

    # Mostrar la imagen capturada en la pantalla
    imgBackground[148:148 + 340, 159:159 + 454] = imgResize
    captured = True
    update_image()


# Función para controlar el motor si el ID clasificado es 8
def control_motor(STEPS):
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.OUT)
        GPIO.setup(18, GPIO.OUT)
        GPIO.setup(CLK_PIN, GPIO.OUT)
        GPIO.setup(CW_PIN, GPIO.OUT)
        # Girar en sentido horario (CW)
        GPIO.output(CW_PIN, GPIO.HIGH)  # Sentido horario
        for _ in range(STEPS):
            GPIO.output(CLK_PIN, GPIO.HIGH)
            time.sleep(0.0001)  # Ajusta para la velocidad del motor
            GPIO.output(CLK_PIN, GPIO.LOW)
            time.sleep(0.001)

        print("Motor Forward")
        GPIO.output(17, GPIO.HIGH)
        GPIO.output(18, GPIO.LOW)
        time.sleep(1)  # Espera 1 segundo

        print("Motor Backward")
        GPIO.output(17, GPIO.LOW)
        GPIO.output(18, GPIO.HIGH)
        time.sleep(1)  # Espera 1 segundo

        # Girar en sentido antihorario (CCW)
        GPIO.output(CW_PIN, GPIO.LOW)  # Sentido antihorario
        for _ in range(STEPS):
            GPIO.output(CLK_PIN, GPIO.HIGH)
            time.sleep(0.0001)
            GPIO.output(CLK_PIN, GPIO.LOW)
            time.sleep(0.001)

        time.sleep(1)  # Pausa de 1 segundo antes de terminar
        GPIO.cleanup()
    except KeyboardInterrupt:
        print("\nControl de motor interrumpido")

    finally:
        # Limpieza de GPIO al finalizar el programa
        GPIO.cleanup()


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
