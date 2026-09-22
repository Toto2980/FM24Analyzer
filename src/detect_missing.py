from pathlib import Path
import cv2
import numpy as np


# --------------------------------------------------
# Rutas
# --------------------------------------------------

project_path = Path(__file__).resolve().parent.parent

image_path = project_path / "output" / "primer_frame.jpg"
output_path = project_path / "output" / "jugadores_completo.jpg"


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


# --------------------------------------------------
# Recortar cancha
# --------------------------------------------------

field = image[
    y_field:y_field + height_field,
    x_field:x_field + width_field
]

gray = cv2.cvtColor(field, cv2.COLOR_BGR2GRAY)

gray = cv2.GaussianBlur(
    gray,
    (9, 9),
    2
)


# --------------------------------------------------
# Función para detectar círculos
# --------------------------------------------------

def detect_circles(param2):
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=15,
        param1=80,
        param2=param2,
        minRadius=6,
        maxRadius=10
    )

    if circles is None:
        return []

    return np.round(
        circles[0]
    ).astype(int).tolist()


# --------------------------------------------------
# Detector original
# --------------------------------------------------

normal = detect_circles(18)

print(f"Detecciones normales: {len(normal)}")


# --------------------------------------------------
# Detector sensible
# --------------------------------------------------

sensitive = detect_circles(12)

print(f"Detecciones sensibles: {len(sensitive)}")


# --------------------------------------------------
# Buscar candidatos nuevos
# --------------------------------------------------

candidates = []

for x, y, radius in sensitive:

    # Convertir a coordenadas de pantalla
    real_x = x + x_field
    real_y = y + y_field

    # Comprobar si ya existe una detección normal cerca
    already_detected = False

    for nx, ny, nr in normal:

        distance = np.sqrt(
            (x - nx) ** 2 +
            (y - ny) ** 2
        )

        if distance < 14:
            already_detected = True
            break

    if not already_detected:
        candidates.append(
            (real_x, real_y, radius)
        )


# --------------------------------------------------
# Resultado
# --------------------------------------------------

print(f"Candidatos nuevos: {len(candidates)}")

for index, (x, y, radius) in enumerate(candidates):

    print(
        f"Candidato {index}: "
        f"x={x}, y={y}, radio={radius}"
    )


# --------------------------------------------------
# Dibujar detecciones normales
# --------------------------------------------------

for index, (x, y, radius) in enumerate(normal):

    real_x = x + x_field
    real_y = y + y_field

    # Rojo = detección original
    cv2.circle(
        image,
        (real_x, real_y),
        radius,
        (0, 0, 255),
        2
    )

    cv2.putText(
        image,
        f"N{index}",
        (
            real_x - 8,
            real_y - radius - 5
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (0, 0, 255),
        1
    )


# --------------------------------------------------
# Dibujar candidatos nuevos
# --------------------------------------------------

for index, (x, y, radius) in enumerate(candidates):

    # Amarillo = candidato nuevo
    cv2.circle(
        image,
        (x, y),
        radius,
        (0, 255, 255),
        2
    )

    cv2.putText(
        image,
        f"C{index}",
        (
            x - 8,
            y - radius - 5
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (0, 255, 255),
        1
    )


# --------------------------------------------------
# Guardar
# --------------------------------------------------

success = cv2.imwrite(
    str(output_path),
    image
)

if success:
    print("\nImagen guardada:")
    print(output_path)
else:
    print("\nNo se pudo guardar la imagen.")