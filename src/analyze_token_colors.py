from pathlib import Path
import cv2
import numpy as np
import csv


# --------------------------------------------------
# Rutas
# --------------------------------------------------

project_path = Path(__file__).resolve().parent.parent

image_path = project_path / "output" / "primer_frame.jpg"
csv_path = project_path / "output" / "token_colors.csv"
image_output_path = project_path / "output" / "token_colors.jpg"


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

gray = cv2.cvtColor(field, cv2.COLOR_BGR2GRAY)

gray = cv2.GaussianBlur(
    gray,
    (9, 9),
    2
)


# --------------------------------------------------
# Detector principal
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
    ).astype(int)


normal = detect_circles(18)

sensitive = detect_circles(12)


# --------------------------------------------------
# Candidatos adicionales
# --------------------------------------------------

tokens = []


# Detecciones normales
for x, y, radius in normal:

    tokens.append(
        {
            "x": x,
            "y": y,
            "radius": radius,
            "source": "normal"
        }
    )


# Candidatos sensibles
for x, y, radius in sensitive:

    duplicate = False

    for token in tokens:

        distance = np.sqrt(
            (x - token["x"]) ** 2 +
            (y - token["y"]) ** 2
        )

        if distance < 14:
            duplicate = True
            break

    if not duplicate:

        tokens.append(
            {
                "x": x,
                "y": y,
                "radius": radius,
                "source": "sensitive"
            }
        )


# --------------------------------------------------
# Arqueros
# --------------------------------------------------

penalty_width = 170

penalty_y1 = int(height_field * 0.25)
penalty_y2 = int(height_field * 0.75)

left_area = field[
    penalty_y1:penalty_y2,
    0:penalty_width
]

right_area = field[
    penalty_y1:penalty_y2,
    width_field - penalty_width:width_field
]


clahe = cv2.createCLAHE(
    clipLimit=3.0,
    tileGridSize=(8, 8)
)


def detect_goalkeepers(region):

    gray_region = cv2.cvtColor(
        region,
        cv2.COLOR_BGR2GRAY
    )

    enhanced = clahe.apply(gray_region)

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


goalkeepers = []

left = detect_goalkeepers(left_area)

for x, y, radius in left:

    real_x = x
    real_y = y + penalty_y1

    goalkeepers.append(
        (real_x, real_y, radius)
    )


right = detect_goalkeepers(right_area)

for x, y, radius in right:

    real_x = (
        x
        + width_field
        - penalty_width
    )

    real_y = y + penalty_y1

    goalkeepers.append(
        (real_x, real_y, radius)
    )


# Agregar arqueros evitando duplicados
for x, y, radius in goalkeepers:

    duplicate = False

    for token in tokens:

        distance = np.sqrt(
            (x - token["x"]) ** 2 +
            (y - token["y"]) ** 2
        )

        if distance < 14:
            duplicate = True
            break

    if not duplicate:

        tokens.append(
            {
                "x": x,
                "y": y,
                "radius": radius,
                "source": "goalkeeper"
            }
        )


# --------------------------------------------------
# Ordenar espacialmente
# --------------------------------------------------

tokens.sort(
    key=lambda token: (
        token["y"],
        token["x"]
    )
)


print(f"Fichas totales: {len(tokens)}")


# --------------------------------------------------
# Analizar color
# --------------------------------------------------

results = []


for index, token in enumerate(tokens):

    x = token["x"]
    y = token["y"]
    radius = token["radius"]

    real_x = x + x_field
    real_y = y + y_field

    # Recorte alrededor de la ficha
    padding = 2

    x1 = max(0, x - radius - padding)
    y1 = max(0, y - radius - padding)
    x2 = min(width_field, x + radius + padding)
    y2 = min(height_field, y + radius + padding)

    patch = field[
        y1:y2,
        x1:x2
    ]

    hsv = cv2.cvtColor(
        patch,
        cv2.COLOR_BGR2HSV
    )

    h, w = hsv.shape[:2]

    center_x = w / 2
    center_y = h / 2

    yy, xx = np.ogrid[:h, :w]

    distance = np.sqrt(
        (xx - center_x) ** 2 +
        (yy - center_y) ** 2
    )

    # Anillo:
    # evita el centro donde suele estar el dorsal
    inner_radius = max(radius * 0.35, 2)
    outer_radius = max(radius * 0.90, inner_radius + 1)

    ring_mask = (
        (distance >= inner_radius) &
        (distance <= outer_radius)
    )

    pixels = hsv[ring_mask]

    if len(pixels) == 0:
        continue

    median_h = float(np.median(pixels[:, 0]))
    median_s = float(np.median(pixels[:, 1]))
    median_v = float(np.median(pixels[:, 2]))

    mean_h = float(np.mean(pixels[:, 0]))
    mean_s = float(np.mean(pixels[:, 1]))
    mean_v = float(np.mean(pixels[:, 2]))

    results.append(
        {
            "id": index,
            "x": real_x,
            "y": real_y,
            "radius": radius,
            "source": token["source"],
            "median_h": median_h,
            "median_s": median_s,
            "median_v": median_v,
            "mean_h": mean_h,
            "mean_s": mean_s,
            "mean_v": mean_v
        }
    )


# --------------------------------------------------
# Mostrar resultados
# --------------------------------------------------

print("\n=== COLORES ===")

for result in results:

    print(
        f"ID {result['id']:02d} | "
        f"x={result['x']:4d} | "
        f"y={result['y']:4d} | "
        f"H={result['median_h']:6.1f} | "
        f"S={result['median_s']:6.1f} | "
        f"V={result['median_v']:6.1f} | "
        f"{result['source']}"
    )


# --------------------------------------------------
# Guardar CSV
# --------------------------------------------------

with open(
    csv_path,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "id",
            "x",
            "y",
            "radius",
            "source",
            "median_h",
            "median_s",
            "median_v",
            "mean_h",
            "mean_s",
            "mean_v"
        ]
    )

    writer.writeheader()

    writer.writerows(results)


# --------------------------------------------------
# Dibujar resultados
# --------------------------------------------------

for result in results:

    x = result["x"]
    y = result["y"]
    radius = result["radius"]

    # Verde por ahora, solamente para visualizar
    cv2.circle(
        image,
        (x, y),
        radius + 3,
        (0, 255, 0),
        2
    )

    text = f"{result['id']}"

    cv2.putText(
        image,
        text,
        (x - 5, y - radius - 6),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        1
    )


cv2.imwrite(
    str(image_output_path),
    image
)


print("\nCSV guardado en:")
print(csv_path)

print("\nImagen guardada en:")
print(image_output_path)