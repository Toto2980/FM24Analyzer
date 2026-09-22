from pathlib import Path
import cv2
import numpy as np


# --------------------------------------------------
# Rutas
# --------------------------------------------------

project_path = Path(__file__).resolve().parent.parent

image_path = project_path / "output" / "primer_frame.jpg"
output_path = project_path / "output" / "arqueros_detectados.jpg"


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
# Dimensiones aproximadas de las áreas de penal
# --------------------------------------------------
#
# Son regiones de búsqueda amplias a propósito.
# Después las podemos calibrar mejor.
#

penalty_height = 210
penalty_width = 170

left_area = field[
    int(height_field * 0.25):int(height_field * 0.75),
    0:penalty_width
]

right_area = field[
    int(height_field * 0.25):int(height_field * 0.75),
    width_field - penalty_width:width_field
]


# --------------------------------------------------
# Crear CLAHE
# --------------------------------------------------

clahe = cv2.createCLAHE(
    clipLimit=3.0,
    tileGridSize=(8, 8)
)


# --------------------------------------------------
# Detector especial
# --------------------------------------------------

def detect_goalkeeper(region):

    gray = cv2.cvtColor(
        region,
        cv2.COLOR_BGR2GRAY
    )

    # Mejoramos contraste local
    enhanced = clahe.apply(gray)

    enhanced = cv2.GaussianBlur(
        enhanced,
        (7, 7),
        2
    )

    circles = cv2.HoughCircles(
        enhanced,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=15,
        param1=70,
        param2=10,
        minRadius=5,
        maxRadius=11
    )

    if circles is None:
        return []

    return np.round(
        circles[0]
    ).astype(int)


# --------------------------------------------------
# Analizar áreas
# --------------------------------------------------

left_circles = detect_goalkeeper(left_area)
right_circles = detect_goalkeeper(right_area)


print("=== RESULTADO ===")
print(f"Candidatos área izquierda: {len(left_circles)}")
print(f"Candidatos área derecha: {len(right_circles)}")


# --------------------------------------------------
# Dibujar izquierda
# --------------------------------------------------

for index, (cx, cy, radius) in enumerate(left_circles):

    real_x = cx + x_field
    real_y = (
        cy
        + y_field
        + int(height_field * 0.25)
    )

    cv2.circle(
        image,
        (real_x, real_y),
        radius,
        (255, 0, 255),
        2
    )

    cv2.putText(
        image,
        f"L{index}",
        (real_x + 5, real_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 0, 255),
        2
    )


# --------------------------------------------------
# Dibujar derecha
# --------------------------------------------------

for index, (cx, cy, radius) in enumerate(right_circles):

    real_x = (
        cx
        + x_field
        + width_field
        - penalty_width
    )

    real_y = (
        cy
        + y_field
        + int(height_field * 0.25)
    )

    cv2.circle(
        image,
        (real_x, real_y),
        radius,
        (255, 0, 255),
        2
    )

    cv2.putText(
        image,
        f"R{index}",
        (real_x + 5, real_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 0, 255),
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
    print("\nImagen guardada en:")
    print(output_path)
else:
    print("\nNo se pudo guardar la imagen.")