from pathlib import Path
import cv2
import numpy as np


# --------------------------------------------------
# Rutas
# --------------------------------------------------

project_path = Path(__file__).resolve().parent.parent

image_path = project_path / "output" / "primer_frame.jpg"
output_path = project_path / "output" / "jugadores_detectados.jpg"


# --------------------------------------------------
# Cargar imagen
# --------------------------------------------------

image = cv2.imread(str(image_path))

if image is None:
    print("ERROR: no se pudo abrir la imagen.")
    exit()

print(f"Imagen cargada: {image.shape[1]}x{image.shape[0]}")


# --------------------------------------------------
# Región de la cancha
# --------------------------------------------------

x_field = 183
y_field = 48
width_field = 913
height_field = 623


# --------------------------------------------------
# Recortar solamente la cancha
# --------------------------------------------------

field = image[
    y_field:y_field + height_field,
    x_field:x_field + width_field
]

print(
    f"Analizando cancha: "
    f"{width_field}x{height_field}"
)


# --------------------------------------------------
# Preparar imagen
# --------------------------------------------------

gray = cv2.cvtColor(field, cv2.COLOR_BGR2GRAY)

gray = cv2.GaussianBlur(
    gray,
    (9, 9),
    2
)


# --------------------------------------------------
# Buscar círculos
# --------------------------------------------------

circles = cv2.HoughCircles(
    gray,
    cv2.HOUGH_GRADIENT,
    dp=1,
    minDist=15,
    param1=80,
    param2=18,
    minRadius=5,
    maxRadius=30
)


# --------------------------------------------------
# Dibujar resultados sobre imagen completa
# --------------------------------------------------

if circles is None:

    print("NO SE DETECTARON CÍRCULOS.")

else:

    circles = np.round(
        circles[0, :]
    ).astype(int)

    print(
        f"Círculos detectados: "
        f"{len(circles)}"
    )

    for index, (cx, cy, radius) in enumerate(circles):

        # Convertimos las coordenadas
        # del recorte a coordenadas de pantalla.
        real_x = cx + x_field
        real_y = cy + y_field

        # Círculo
        cv2.circle(
            image,
            (real_x, real_y),
            radius,
            (0, 0, 255),
            2
        )

        # Centro
        cv2.circle(
            image,
            (real_x, real_y),
            2,
            (0, 255, 0),
            3
        )

        # Índice
        cv2.putText(
            image,
            str(index),
            (
                real_x - 5,
                real_y - radius - 5
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 255),
            2
        )


# --------------------------------------------------
# Guardar
# --------------------------------------------------

success = cv2.imwrite(
    str(output_path),
    image
)

if success:

    print("Imagen guardada correctamente.")
    print(output_path)

else:

    print("ERROR: no se pudo guardar la imagen.")