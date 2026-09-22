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

output_dir = project_path / "output" / "dorsals_v2"
audit_path = project_path / "output" / "dorsals_audit_v2.jpg"

output_dir.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# Configuración
# --------------------------------------------------

UPSCALE = 10
PADDING = 4

# Radio relativo del área central donde puede
# estar el dorsal.
CORE_RATIO = 0.75


# --------------------------------------------------
# Cargar
# --------------------------------------------------

image = cv2.imread(str(image_path))
df = pd.read_csv(csv_path)

if image is None:
    print("No se pudo abrir la imagen.")
    exit()

print(f"Fichas encontradas: {len(df)}")


# --------------------------------------------------
# Auditoría
# --------------------------------------------------

audit_tiles = []


# --------------------------------------------------
# Procesar cada ficha
# --------------------------------------------------

for _, row in df.iterrows():

    token_id = int(row["id"])

    x = int(row["x"])
    y = int(row["y"])
    radius = int(row["radius"])

    team = row["team"]


    # ----------------------------------------------
    # Recortar ficha
    # ----------------------------------------------

    x1 = max(
        0,
        x - radius - PADDING
    )

    y1 = max(
        0,
        y - radius - PADDING
    )

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
        continue


    # ----------------------------------------------
    # Agrandar
    # ----------------------------------------------

    token = cv2.resize(
        token,
        None,
        fx=UPSCALE,
        fy=UPSCALE,
        interpolation=cv2.INTER_LANCZOS4
    )


    height, width = token.shape[:2]

    center_x = width / 2
    center_y = height / 2


    # ----------------------------------------------
    # Máscara circular CENTRAL
    # ----------------------------------------------
    #
    # Esta vez NO excluimos el centro.
    # Excluimos únicamente el borde exterior.
    #

    yy, xx = np.ogrid[:height, :width]

    distance = np.sqrt(
        (xx - center_x) ** 2 +
        (yy - center_y) ** 2
    )

    token_radius = min(
        width,
        height
    ) / 2

    core_radius = token_radius * CORE_RATIO

    core_mask = (
        distance <= core_radius
    )


    # ----------------------------------------------
    # HSV
    # ----------------------------------------------

    hsv = cv2.cvtColor(
        token,
        cv2.COLOR_BGR2HSV
    )

    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]


    # ----------------------------------------------
    # Detectar dorsal
    # ----------------------------------------------

    if team == "RACING":

        # Blanco sobre azul oscuro
        digit_mask = (
            (saturation < 80) &
            (value > 150)
        )

    else:

        # Rival y arqueros:
        # oscuro sobre fondo claro
        digit_mask = (
            value < 130
        )


    # Aplicamos solamente la zona central
    digit_mask = (
        digit_mask &
        core_mask
    )


    # ----------------------------------------------
    # Caso especial ID 06
    # ----------------------------------------------
    #
    # Eliminamos solamente la zona superior
    # donde aparece "Miranda".
    #

    if token_id == 6:

        digit_mask[
            :int(height * 0.38),
            :
        ] = False


    # ----------------------------------------------
    # Convertir a imagen binaria
    # ----------------------------------------------

    digit_mask = (
        digit_mask.astype(np.uint8) * 255
    )


    # ----------------------------------------------
    # Cierre morfológico
    # ----------------------------------------------
    #
    # NO hacemos apertura.
    # Las letras son muy pequeñas y una apertura
    # podría destruir los trazos del número.
    #

    kernel = np.ones(
        (2, 2),
        np.uint8
    )

    digit_mask = cv2.morphologyEx(
        digit_mask,
        cv2.MORPH_CLOSE,
        kernel
    )


    # ----------------------------------------------
    # Guardar máscara
    # ----------------------------------------------

    mask_path = (
        output_dir /
        f"dorsal_{token_id:02d}.png"
    )

    cv2.imwrite(
        str(mask_path),
        digit_mask
    )


    # ----------------------------------------------
    # Encontrar componentes
    # ----------------------------------------------

    contours, _ = cv2.findContours(
        digit_mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    components = []

    for contour in contours:

        cx, cy, cw, ch = cv2.boundingRect(
            contour
        )

        area = cw * ch

        if area >= 15:

            components.append(
                (
                    cx,
                    cy,
                    cw,
                    ch,
                    area
                )
            )


    components.sort(
        key=lambda item: item[0]
    )


    # ----------------------------------------------
    # Dibujar componentes
    # ----------------------------------------------

    visualization = token.copy()

    for index, (
        cx,
        cy,
        cw,
        ch,
        area
    ) in enumerate(components):

        cv2.rectangle(
            visualization,
            (cx, cy),
            (cx + cw, cy + ch),
            (0, 255, 0),
            2
        )

        cv2.putText(
            visualization,
            str(index),
            (cx, max(cy - 5, 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1
        )


    # ----------------------------------------------
    # Mini auditoría
    # ----------------------------------------------

    mask_bgr = cv2.cvtColor(
        digit_mask,
        cv2.COLOR_GRAY2BGR
    )

    scale = 0.30

    token_small = cv2.resize(
        visualization,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_AREA
    )

    mask_small = cv2.resize(
        mask_bgr,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_AREA
    )

    tile = np.hstack(
        (
            token_small,
            mask_small
        )
    )

    cv2.putText(
        tile,
        f"ID {token_id} | {team}",
        (5, 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        1
    )

    audit_tiles.append(tile)


# --------------------------------------------------
# Construir auditoría
# --------------------------------------------------

if audit_tiles:

    tile_height = max(
        tile.shape[0]
        for tile in audit_tiles
    )

    tile_width = max(
        tile.shape[1]
        for tile in audit_tiles
    )

    normalized_tiles = []

    for tile in audit_tiles:

        canvas = np.zeros(
            (
                tile_height,
                tile_width,
                3
            ),
            dtype=np.uint8
        )

        canvas[
            :tile.shape[0],
            :tile.shape[1]
        ] = tile

        normalized_tiles.append(canvas)


    columns = 4

    rows = int(
        np.ceil(
            len(normalized_tiles) / columns
        )
    )

    blank = np.zeros_like(
        normalized_tiles[0]
    )

    while len(normalized_tiles) < rows * columns:

        normalized_tiles.append(
            blank.copy()
        )


    row_images = []

    for r in range(rows):

        row = np.hstack(
            normalized_tiles[
                r * columns:
                (r + 1) * columns
            ]
        )

        row_images.append(row)


    audit = np.vstack(row_images)

    cv2.imwrite(
        str(audit_path),
        audit
    )


print("\n=== TERMINADO ===")
print(f"Fichas procesadas: {len(df)}")
print(f"Máscaras: {output_dir}")
print(f"Auditoría: {audit_path}")