from ultralytics import SAM
import cv2
import os

# Cargar modelo (y descargar en caso que no esté presente)
model = SAM("sam_b.pt")

# Ubicación de la imagen
image_path = os.path.join('../Logicadeagentes/droneUploads/DroneView_20240904_131100151.png')

# Cargar la imagen
image = cv2.imread(image_path)

# Verificar si la imagen se cargó correctamente
if image is None:
    print("Error al cargar la imagen.")
else:
    # Aplicar el modelo a la imagen con bounding boxes predefinidos
    results = model(image, bboxes=[100, 100, 1200, 800])

    # Obtenemos el frame con los objetos detectados y ya graficados con su bounding box y etiqueta
    annotated_image = results[0].plot()

    # Mostrar la imagen con los resultados
    cv2.imshow('SAM2', annotated_image)

    # Esperar hasta que se presione una tecla para cerrar la ventana
    cv2.waitKey(0)
    cv2.destroyAllWindows()