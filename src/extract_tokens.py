from pathlib import Path

import cv2
import numpy as np
import pandas as pd


# --------------------------------------------------
# Rutas
# --------------------------------------------------

project_path = Path(__file__).resolve().parent.parent

image_path = project_path / "output" / "primer_frame.jpg"
csv_path = project_path / "output" / "classified_tokens.csv"

tokens_path = project_path / "output" / "tokens"
audit_path = project_path / "output" / "tokens_audit.jpg"


# --------------------------------------------------
# Configuración
# --------------------------------------------------

UPSCALE = 8

# Nuestros tokens tienen radio ~7-8 px.
# Usamos un margen pequeño para llevarnos
# toda la ficha sin incluir demasiada interfaz.
PADDING = 4


# --------------------------------------------------
# Crear carpeta
# --------------------------------------------------

tokens_path.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# Cargar imagen
# --------------------------------------------------

image = cv2.imread(str(image_path))

if image is None:
    print("ERROR: no se pudo abrir la imagen.")
    exit()


# --------------------------------------------------
# Cargar datos
# --------------------------------------------------

df = pd.read_csv(csv_path)

print(f"Tokens encontrados en CSV: {len(df)}")


# --------------------------------------------------
# Imagen para auditoría
# --------------------------------------------------

audit_image = image.copy()


# --------------------------------------------------
# Procesar cada token
# --------------------------------------------------

for _, row in df.iterrows():

    token_id = int(row["id"])

    x = int(row["x"])
    y = int(row["y"])
    radius = int(row["radius"])

    # ----------------------------------------------
    # Tamaño del recorte
    # ----------------------------------------------

    size = radius * 2 + PADDING * 2

    x1 = max(0, x - radius - PADDING)
    y1 = max(0, y - radius - PADDING)

    x2 = min(
        image.shape[1],
        x + radius + PADDING
    )

    y2 = min(
        image.shape[0],
        y + radius + PADDING
    )

    token = image[y1:y2, x1:x2]

    if token.size == 0:
        print(
            f"Token {token_id}: "
            "recorte vacío."
        )
        continue


    # ----------------------------------------------
    # Agrandar
    # ----------------------------------------------

    enlarged = cv2.resize(
        token,
        None,
        fx=UPSCALE,
        fy=UPSCALE,
        interpolation=cv2.INTER_LANCZOS4
    )


    # ----------------------------------------------
    # Escala de grises
    # ----------------------------------------------

    gray = cv2.cvtColor(
        enlarged,
        cv2.COLOR_BGR2GRAY
    )


    # ----------------------------------------------
    # Binarización Otsu
    # ----------------------------------------------

    _, binary = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )


    # ----------------------------------------------
    # Máscara para buscar blanco
    # ----------------------------------------------

    hsv = cv2.cvtColor(
        enlarged,
        cv2.COLOR_BGR2HSV
    )

    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]

    white_mask = (
        (saturation < 80) &
        (value > 150)
    )

    white_mask = (
        white_mask.astype(np.uint8) * 255
    )


    # ----------------------------------------------
    # Guardar imágenes
    # ----------------------------------------------

    original_path = (
        tokens_path /
        f"token_{token_id:02d}_original.png"
    )

    gray_path = (
        tokens_path /
        f"token_{token_id:02d}_gray.png"
    )

    binary_path = (
        tokens_path /
        f"token_{token_id:02d}_binary.png"
    )

    white_path = (
        tokens_path /
        f"token_{token_id:02d}_white.png"
    )

    cv2.imwrite(
        str(original_path),
        enlarged
    )

    cv2.imwrite(
        str(gray_path),
        gray
    )

    cv2.imwrite(
        str(binary_path),
        binary
    )

    cv2.imwrite(
        str(white_path),
        white_mask
    )


    # ----------------------------------------------
    # Dibujar auditoría
    # ----------------------------------------------

    cv2.circle(
        audit_image,
        (x, y),
        radius + 4,
        (0, 255, 0),
        2
    )

    cv2.putText(
        audit_image,
        str(token_id),
        (x + radius + 5, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        1
    )


# --------------------------------------------------
# Guardar auditoría
# --------------------------------------------------

cv2.imwrite(
    str(audit_path),
    audit_image
)


print("\n=== TERMINADO ===")
print(f"Tokens procesados: {len(df)}")
print(f"Carpeta: {tokens_path}")
print(f"Auditoría: {audit_path}")