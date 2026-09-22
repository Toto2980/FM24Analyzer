from pathlib import Path

import cv2
import numpy as np
import pandas as pd


# --------------------------------------------------
# Rutas
# --------------------------------------------------

project_path = Path(__file__).resolve().parent.parent

classified_path = (
    project_path /
    "output" /
    "classified_tokens.csv"
)

labels_path = (
    project_path /
    "output" /
    "token_labels.csv"
)

dorsals_path = (
    project_path /
    "output" /
    "dorsals_v2"
)

templates_path = (
    project_path /
    "output" /
    "templates_v2"
)

audit_path = (
    project_path /
    "output" /
    "template_audit_v2.jpg"
)


# --------------------------------------------------
# Configuración
# --------------------------------------------------

TEMPLATE_WIDTH = 32
TEMPLATE_HEIGHT = 40

# Mucho más permisivo que antes.
MIN_AREA = 4
MIN_HEIGHT = 4


# --------------------------------------------------
# Cargar etiquetas
# --------------------------------------------------

labels = pd.read_csv(
    labels_path,
    dtype={"dorsal": str}
)

print(
    f"Fichas etiquetadas: {len(labels)}"
)


# --------------------------------------------------
# Banco de muestras
# --------------------------------------------------

digit_samples = {
    str(i): []
    for i in range(10)
}


# --------------------------------------------------
# Extraer componentes
# --------------------------------------------------

def extract_components(mask):

    _, binary = cv2.threshold(
        mask,
        127,
        255,
        cv2.THRESH_BINARY
    )

    num_labels, labels_img, stats, centroids = (
        cv2.connectedComponentsWithStats(
            binary,
            connectivity=8
        )
    )

    components = []

    for i in range(1, num_labels):

        x, y, width, height, area = (
            stats[i]
        )

        if area < MIN_AREA:
            continue

        if height < MIN_HEIGHT:
            continue

        components.append(
            {
                "x": int(x),
                "y": int(y),
                "w": int(width),
                "h": int(height),
                "area": int(area)
            }
        )

    components.sort(
        key=lambda item: item["x"]
    )

    return components


# --------------------------------------------------
# Separar un componente en dos dígitos
# --------------------------------------------------

def split_component(component, mask):

    x = component["x"]
    y = component["y"]
    w = component["w"]
    h = component["h"]

    crop = mask[
        y:y + h,
        x:x + w
    ]

    if crop.shape[1] < 4:
        return []


    # ----------------------------------------------
    # Proyección vertical
    # ----------------------------------------------

    vertical_projection = (
        np.sum(crop > 0, axis=0)
    )

    # Buscamos una zona interna con pocos píxeles.
    left_limit = max(
        1,
        int(w * 0.25)
    )

    right_limit = min(
        w - 2,
        int(w * 0.75)
    )

    if right_limit <= left_limit:
        return []


    split_x = (
        left_limit +
        int(
            np.argmin(
                vertical_projection[
                    left_limit:right_limit
                ]
            )
        )
    )


    # Si no hay realmente un valle,
    # descartamos la división.
    minimum = vertical_projection[
        split_x
    ]

    maximum = vertical_projection.max()

    if maximum == 0:
        return []

    if minimum > maximum * 0.55:

        # No hay separación clara.
        return []


    left = {
        "x": x,
        "y": y,
        "w": split_x,
        "h": h,
        "area": int(
            np.sum(crop[:, :split_x] > 0)
        )
    }

    right = {
        "x": x + split_x,
        "y": y,
        "w": w - split_x,
        "h": h,
        "area": int(
            np.sum(crop[:, split_x:] > 0)
        )
    }

    return [
        left,
        right
    ]


# --------------------------------------------------
# Normalizar dígito
# --------------------------------------------------

def normalize_component(
    mask,
    component
):

    x = component["x"]
    y = component["y"]
    w = component["w"]
    h = component["h"]

    padding = 2

    x1 = max(
        0,
        x - padding
    )

    y1 = max(
        0,
        y - padding
    )

    x2 = min(
        mask.shape[1],
        x + w + padding
    )

    y2 = min(
        mask.shape[0],
        y + h + padding
    )

    crop = mask[
        y1:y2,
        x1:x2
    ]

    if crop.size == 0:
        return None


    # ----------------------------------------------
    # Escalado manteniendo proporción
    # ----------------------------------------------

    scale = min(
        (TEMPLATE_WIDTH - 4) / crop.shape[1],
        (TEMPLATE_HEIGHT - 4) / crop.shape[0]
    )

    new_width = max(
        1,
        int(crop.shape[1] * scale)
    )

    new_height = max(
        1,
        int(crop.shape[0] * scale)
    )

    resized = cv2.resize(
        crop,
        (
            new_width,
            new_height
        ),
        interpolation=cv2.INTER_AREA
    )


    # ----------------------------------------------
    # Centrar
    # ----------------------------------------------

    canvas = np.zeros(
        (
            TEMPLATE_HEIGHT,
            TEMPLATE_WIDTH
        ),
        dtype=np.uint8
    )

    offset_x = (
        TEMPLATE_WIDTH -
        new_width
    ) // 2

    offset_y = (
        TEMPLATE_HEIGHT -
        new_height
    ) // 2

    canvas[
        offset_y:
        offset_y + new_height,
        offset_x:
        offset_x + new_width
    ] = resized


    _, canvas = cv2.threshold(
        canvas,
        80,
        255,
        cv2.THRESH_BINARY
    )

    return canvas


# --------------------------------------------------
# Auditoría
# --------------------------------------------------

audit_items = []


# --------------------------------------------------
# Procesar cada ficha
# --------------------------------------------------

for _, row in labels.iterrows():

    token_id = int(row["id"])
    dorsal = str(row["dorsal"]).strip()

    if not dorsal.isdigit():
        continue


    mask_path = (
        dorsals_path /
        f"dorsal_{token_id:02d}.png"
    )

    mask = cv2.imread(
        str(mask_path),
        cv2.IMREAD_GRAYSCALE
    )

    if mask is None:

        print(
            f"ID {token_id}: "
            "no se pudo abrir la máscara."
        )

        continue


    expected_digits = len(dorsal)

    components = extract_components(
        mask
    )


    # ----------------------------------------------
    # Diagnóstico
    # ----------------------------------------------

    print(
        f"\nID {token_id:02d} | "
        f"dorsal={dorsal} | "
        f"componentes={len(components)}"
    )


    # ----------------------------------------------
    # Caso normal
    # ----------------------------------------------

    if len(components) == expected_digits:

        selected = components


    # ----------------------------------------------
    # Un componente para dos dígitos
    # ----------------------------------------------

    elif (
        expected_digits == 2
        and len(components) == 1
    ):

        print(
            "  → Intentando separación vertical..."
        )

        selected = split_component(
            components[0],
            mask
        )

        if len(selected) != 2:

            print(
                "  → No se pudo separar."
            )

            continue


    # ----------------------------------------------
    # Más componentes de los esperados
    # ----------------------------------------------

    elif len(components) > expected_digits:

        # Elegimos los componentes de mayor área.
        selected = sorted(
            components,
            key=lambda item: item["area"],
            reverse=True
        )[:expected_digits]

        selected.sort(
            key=lambda item: item["x"]
        )


    # ----------------------------------------------
    # Otro caso
    # ----------------------------------------------

    else:

        print(
            "  → No hay suficientes componentes."
        )

        continue


    # ----------------------------------------------
    # Normalizar dígitos
    # ----------------------------------------------

    for digit, component in zip(
        dorsal,
        selected
    ):

        normalized = normalize_component(
            mask,
            component
        )

        if normalized is None:
            continue

        digit_samples[
            digit
        ].append(normalized)


        # ------------------------------------------
        # Auditoría
        # ------------------------------------------

        canvas = cv2.cvtColor(
            normalized,
            cv2.COLOR_GRAY2BGR
        )

        cv2.putText(
            canvas,
            f"{token_id}:{digit}",
            (2, 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.28,
            (0, 255, 0),
            1
        )

        audit_items.append(
            canvas
        )


# --------------------------------------------------
# Guardar plantillas
# --------------------------------------------------

templates_path.mkdir(
    parents=True,
    exist_ok=True
)


print("\n=== MUESTRAS POR DÍGITO ===")

for digit in range(10):

    digit_str = str(digit)

    samples = digit_samples[
        digit_str
    ]

    print(
        f"{digit}: "
        f"{len(samples)} muestras"
    )

    digit_dir = (
        templates_path /
        digit_str
    )

    digit_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    for index, sample in enumerate(samples):

        path = (
            digit_dir /
            f"sample_{index:02d}.png"
        )

        cv2.imwrite(
            str(path),
            sample
        )


# --------------------------------------------------
# Auditar
# --------------------------------------------------

if audit_items:

    columns = 10

    rows = int(
        np.ceil(
            len(audit_items) /
            columns
        )
    )

    audit = np.zeros(
        (
            rows * TEMPLATE_HEIGHT,
            columns * TEMPLATE_WIDTH,
            3
        ),
        dtype=np.uint8
    )


    for index, item in enumerate(
        audit_items
    ):

        row = index // columns
        column = index % columns

        x = (
            column *
            TEMPLATE_WIDTH
        )

        y = (
            row *
            TEMPLATE_HEIGHT
        )

        audit[
            y:y + TEMPLATE_HEIGHT,
            x:x + TEMPLATE_WIDTH
        ] = item


    cv2.imwrite(
        str(audit_path),
        audit
    )


# --------------------------------------------------
# Resumen
# --------------------------------------------------

missing = [
    digit
    for digit in range(10)
    if len(
        digit_samples[str(digit)]
    ) == 0
]


print("\n=== RESULTADO FINAL ===")

if missing:

    print(
        "Faltan plantillas para:"
    )

    print(
        ", ".join(
            map(str, missing)
        )
    )

else:

    print(
        "Tenemos muestras de "
        "los 10 dígitos."
    )

print(
    f"\nPlantillas: {templates_path}"
)

print(
    f"Auditoría: {audit_path}"
)