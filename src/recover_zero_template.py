from pathlib import Path

import cv2
import numpy as np
import pandas as pd


# ==================================================
# RUTAS
# ==================================================

project_path = Path(__file__).resolve().parent.parent

labels_path = (
    project_path
    / "output"
    / "token_labels.csv"
)

masks_path = (
    project_path
    / "output"
    / "dorsals_v2"
)

output_path = (
    project_path
    / "output"
    / "templates_source"
    / "0"
)

audit_path = (
    project_path
    / "output"
    / "zero_recovery_audit.jpg"
)

output_path.mkdir(
    parents=True,
    exist_ok=True
)


# ==================================================
# CONFIGURACIÓN
# ==================================================

TARGET_WIDTH = 32
TARGET_HEIGHT = 40

# En un dorsal 10, buscamos la separación
# en esta región relativa del ancho.
SEARCH_START = 0.25
SEARCH_END = 0.70


# ==================================================
# NORMALIZAR
# ==================================================

def normalize_digit(mask):

    points = cv2.findNonZero(mask)

    if points is None:
        return None

    x, y, w, h = cv2.boundingRect(points)

    crop = mask[
        y:y + h,
        x:x + w
    ]

    if crop.size == 0:
        return None

    padding = 2

    padded = cv2.copyMakeBorder(
        crop,
        padding,
        padding,
        padding,
        padding,
        cv2.BORDER_CONSTANT,
        value=0
    )

    h, w = padded.shape

    scale = min(
        (TARGET_WIDTH - 4) / w,
        (TARGET_HEIGHT - 4) / h
    )

    new_w = max(
        1,
        int(w * scale)
    )

    new_h = max(
        1,
        int(h * scale)
    )

    resized = cv2.resize(
        padded,
        (new_w, new_h),
        interpolation=cv2.INTER_AREA
    )

    canvas = np.zeros(
        (
            TARGET_HEIGHT,
            TARGET_WIDTH
        ),
        dtype=np.uint8
    )

    offset_x = (
        TARGET_WIDTH - new_w
    ) // 2

    offset_y = (
        TARGET_HEIGHT - new_h
    ) // 2

    canvas[
        offset_y:
        offset_y + new_h,
        offset_x:
        offset_x + new_w
    ] = resized

    _, canvas = cv2.threshold(
        canvas,
        127,
        255,
        cv2.THRESH_BINARY
    )

    return canvas


# ==================================================
# ENCONTRAR SEPARACIÓN DE "10"
# ==================================================

def split_10(mask):

    # ----------------------------------------------
    # Buscar todos los píxeles del dorsal
    # ----------------------------------------------

    points = cv2.findNonZero(mask)

    if points is None:
        return None

    x, y, w, h = cv2.boundingRect(points)

    block = mask[
        y:y + h,
        x:x + w
    ]

    if block.shape[1] < 20:
        return None


    # ----------------------------------------------
    # Proyección vertical
    # ----------------------------------------------

    projection = np.sum(
        block > 127,
        axis=0
    )

    start = max(
        1,
        int(w * SEARCH_START)
    )

    end = min(
        w - 2,
        int(w * SEARCH_END)
    )

    if end <= start:
        return None


    # ----------------------------------------------
    # Suavizamos la proyección
    # ----------------------------------------------

    smooth = cv2.GaussianBlur(
        projection.astype(np.float32),
        (1, 7),
        0
    ).flatten()


    # ----------------------------------------------
    # Buscar el valle
    # ----------------------------------------------

    split_x = (
        start
        + int(
            np.argmin(
                smooth[start:end]
            )
        )
    )


    # ----------------------------------------------
    # Comprobación de calidad del valle
    # ----------------------------------------------

    maximum = float(
        smooth.max()
    )

    minimum = float(
        smooth[split_x]
    )

    if maximum <= 0:
        return None


    # Si la separación no es clara,
    # no inventamos un corte.
    if minimum > maximum * 0.60:
        return None


    # ----------------------------------------------
    # Quedarnos con la parte derecha
    # ----------------------------------------------

    zero = block[
        :,
        split_x:
    ]


    # ----------------------------------------------
    # Encontrar solamente la masa del 0
    # ----------------------------------------------

    points_zero = cv2.findNonZero(
        zero
    )

    if points_zero is None:
        return None

    zx, zy, zw, zh = cv2.boundingRect(
        points_zero
    )

    zero = zero[
        zy:zy + zh,
        zx:zx + zw
    ]


    return zero, split_x, block


# ==================================================
# CARGAR ETIQUETAS
# ==================================================

df = pd.read_csv(
    labels_path,
    dtype={"dorsal": str}
)

ten_players = df[
    df["dorsal"] == "10"
]

print(
    f"Dorsales 10 encontrados: "
    f"{len(ten_players)}"
)


# ==================================================
# AUDITORÍA
# ==================================================

audit_items = []


# ==================================================
# RECUPERAR CEROS
# ==================================================

for _, row in ten_players.iterrows():

    token_id = int(
        row["id"]
    )

    mask_path = (
        masks_path
        / f"dorsal_{token_id:02d}.png"
    )

    mask = cv2.imread(
        str(mask_path),
        cv2.IMREAD_GRAYSCALE
    )

    if mask is None:

        print(
            f"ID {token_id}: "
            "máscara inexistente."
        )

        continue


    # ----------------------------------------------
    # Intentamos primero encontrar el 0
    # directamente como componente derecho.
    # ----------------------------------------------

    binary = (
        mask > 127
    ).astype(np.uint8) * 255


    num_labels, labels, stats, _ = (
        cv2.connectedComponentsWithStats(
            binary,
            connectivity=8
        )
    )


    components = []

    for component_id in range(
        1,
        num_labels
    ):

        x, y, w, h, area = (
            stats[component_id]
        )

        if area < 100:
            continue

        components.append(
            {
                "label": component_id,
                "x": int(x),
                "y": int(y),
                "w": int(w),
                "h": int(h),
                "area": int(area)
            }
        )


    components.sort(
        key=lambda c: c["x"]
    )


    zero = None


    # ----------------------------------------------
    # Caso: el 0 ya está separado
    # ----------------------------------------------

    right_candidates = [
        c
        for c in components
        if c["w"] >= 25
        and c["h"] >= 40
    ]


    if right_candidates:

        # El carácter más a la derecha
        # es nuestro mejor candidato al 0.
        right = max(
            right_candidates,
            key=lambda c: c["x"]
        )

        component_mask = (
            labels == right["label"]
        ).astype(np.uint8) * 255

        zero = component_mask[
            right["y"]:
            right["y"] + right["h"],
            right["x"]:
            right["x"] + right["w"]
        ]

        print(
            f"ID {token_id:02d} → "
            "0 separado directamente"
        )


    # ----------------------------------------------
    # Caso: 1 y 0 están fusionados
    # ----------------------------------------------

    if zero is None:

        result = split_10(
            binary
        )

        if result is not None:

            zero, split_x, block = (
                result
            )

            print(
                f"ID {token_id:02d} → "
                f"0 recuperado por corte "
                f"x={split_x}"
            )

        else:

            print(
                f"ID {token_id:02d} → "
                "NO SE PUDO RECUPERAR"
            )

            continue


    # ----------------------------------------------
    # Normalizar
    # ----------------------------------------------

    normalized = normalize_digit(
        zero
    )

    if normalized is None:

        print(
            f"ID {token_id:02d} → "
            "falló normalización"
        )

        continue


    # ----------------------------------------------
    # Guardar
    # ----------------------------------------------

    output_file = (
        output_path
        / f"zero_{token_id:02d}.png"
    )

    cv2.imwrite(
        str(output_file),
        normalized
    )


    # ----------------------------------------------
    # Auditoría
    # ----------------------------------------------

    audit = cv2.cvtColor(
        normalized,
        cv2.COLOR_GRAY2BGR
    )

    cv2.putText(
        audit,
        f"ID {token_id}:0",
        (2, 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.28,
        (0, 255, 0),
        1
    )

    audit_items.append(
        audit
    )


# ==================================================
# CREAR AUDITORÍA
# ==================================================

if audit_items:

    columns = 4

    cell_width = 50
    cell_height = 55

    rows = int(
        np.ceil(
            len(audit_items)
            / columns
        )
    )

    audit_image = np.zeros(
        (
            rows * cell_height,
            columns * cell_width,
            3
        ),
        dtype=np.uint8
    )


    for index, item in enumerate(
        audit_items
    ):

        row = index // columns
        column = index % columns

        x = column * cell_width
        y = row * cell_height

        resized = cv2.resize(
            item,
            (40, 50),
            interpolation=cv2.INTER_NEAREST
        )

        audit_image[
            y:y + 50,
            x:x + 40
        ] = resized


    cv2.imwrite(
        str(audit_path),
        audit_image
    )


print("\n=== TERMINADO ===")
print(
    f"Plantillas guardadas en: "
    f"{output_path}"
)

print(
    f"Auditoría: {audit_path}"
)