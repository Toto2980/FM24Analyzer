from pathlib import Path
import cv2
import numpy as np


# --------------------------------------------------
# Rutas
# --------------------------------------------------

project_path = Path(__file__).resolve().parent.parent
image_path = project_path / "output" / "primer_frame.jpg"


# --------------------------------------------------
# Configuración de la cancha
# --------------------------------------------------

x_field = 183
y_field = 48
width_field = 913
height_field = 623


# --------------------------------------------------
# Cargar imagen
# --------------------------------------------------

image = cv2.imread(str(image_path))

if image is None:
    print("No se pudo abrir la imagen.")
    exit()


field = image[
    y_field:y_field + height_field,
    x_field:x_field + width_field
]


# --------------------------------------------------
# Preparar
# --------------------------------------------------

gray = cv2.cvtColor(field, cv2.COLOR_BGR2GRAY)

gray = cv2.GaussianBlur(
    gray,
    (9, 9),
    2
)


# --------------------------------------------------
# Detectar fichas
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


if circles is None:
    print("No se detectaron fichas.")
    exit()


circles = np.round(
    circles[0]
).astype(int)


# --------------------------------------------------
# Mostrar datos
# --------------------------------------------------

radii = []

print("\n=== DETECCIONES ===")

for index, (x, y, radius) in enumerate(circles):

    real_x = x + x_field
    real_y = y + y_field

    radii.append(radius)

    print(
        f"{index:02d} | "
        f"x={real_x:4d} "
        f"y={real_y:4d} "
        f"radio={radius:2d}"
    )


# --------------------------------------------------
# Estadísticas
# --------------------------------------------------

radii = np.array(radii)

print("\n=== ESTADÍSTICAS ===")

print(f"Cantidad: {len(radii)}")
print(f"Radio mínimo: {radii.min()}")
print(f"Radio máximo: {radii.max()}")
print(f"Radio promedio: {radii.mean():.2f}")
print(f"Radio mediano: {np.median(radii):.2f}")