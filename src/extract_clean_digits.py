from pathlib import Path

import cv2
import numpy as np
import pandas as pd


# --------------------------------------------------
# Rutas
# --------------------------------------------------

project_path = Path(__file__).resolve().parent.parent

labels_path = (
    project_path /
    "output" /
    "token_labels.csv"
)

masks_path = (
    project_path /
    "output" /
    "dorsals_v2"
)

output_path = (
    project_path /
    "output" /
    "digit_debug"
)

audit_path = (
    project_path /
    "output" /
    "digit_debug_audit.jpg"
)

output_path.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# Parámetros geométricos
# --------------------------------------------------

MIN_AREA = 300
MIN_HEIGHT = 40

MAX_HEIGHT = 70
MAX_WIDTH = 60


# --------------------------------------------------
# Cargar etiquetas
# --------------------------------------------------

df = pd.read_csv(
    labels_path,
    dtype={"dorsal": str}
)


# --------------------------------------------------
# Obtener componentes
# --------------------------------------------------

def get_components(mask):

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

    for i in range(1, num_labels):

        x, y, w, h, area = stats[i]

        components.append(
            {
                "x": int(x),
                "y": int(y),
                "w": int(w),
                "h": int(h),
                "area": int(area)
            }
        )

    return components


# --------------------------------------------------
# Componente dentro de límites
# --------------------------------------------------

def is_digit_like(component):

    return (
        component["h"] >= MIN_HEIGHT
        and component["h"] <= MAX_HEIGHT
        and component["w"] <= MAX_WIDTH
        and component["area"] >= MIN_AREA
    )


# --------------------------------------------------
# Distancia entre componentes
# --------------------------------------------------

def components_close(a, b):

    ax2 = a["x"] + a["w"]
    ay2 = a["y"] + a["h"]

    bx2 = b["x"] + b["w"]
    by2 = b["y"] + b["h"]

    horizontal_gap = max(
        0,
        max(
            b["x"] - ax2,
            a["x"] - bx2
        )
    )

    vertical_gap = max(
        0,
        max(
            b["y"] - ay2,
            a["y"] - by2
        )
    )

    # Si están muy cerca y sus alturas
    # pertenecen aproximadamente a la misma zona,
    # pueden ser fragmentos del mismo dígito.
    return (
        horizontal_gap <= 20
        and vertical_gap <= 20
    )


# --------------------------------------------------
# Unir componentes cercanos
# --------------------------------------------------

def merge_components(mask, components):

    changed = True

    while changed:

        changed = False

        for i in range(len(components)):

            for j in range(
                i + 1,
                len(components)
            ):

                a = components[i]
                b = components[j]

                if not components_close(a, b):
                    continue

                x1 = min(
                    a["x"],
                    b["x"]
                )

                y1 = min(
                    a["y"],
                    b["y"]
                )

                x2 = max(
                    a["x"] + a["w"],
                    b["x"] + b["w"]
                )

                y2 = max(
                    a["y"] + a["h"],
                    b["y"] + b["h"]
                )

                merged = {
                    "x": x1,
                    "y": y1,
                    "w": x2 - x1,
                    "h": y2 - y1,
                    "area": int(
                        np.sum(
                            mask[
                                y1:y2,
                                x1:x2
                            ] > 0
                        )
                    )
                }

                components.pop(j)
                components.pop(i)

                components.append(
                    merged
                )

                changed = True
                break

            if changed:
                break

    components.sort(
        key=lambda c: c["x"]
    )

    return components


# --------------------------------------------------
# Separar componente fusionado
# --------------------------------------------------

def split_component(mask, component):

    x = component["x"]
    y = component["y"]
    w = component["w"]
    h = component["h"]

    crop = mask[
        y:y + h,
        x:x + w
    ]

    projection = np.sum(
        crop > 127,
        axis=0
    )

    left = max(
        2,
        int(w * 0.25)
    )

    right = min(
        w - 3,
        int(w * 0.75)
    )

    if right <= left:
        return []

    split_x = (
        left
        + int(
            np.argmin(
                projection[left:right]
            )
        )
    )

    minimum = projection[split_x]

    maximum = projection.max()

    if maximum == 0:
        return []

    # Necesitamos un valle suficientemente marcado.
    if minimum > maximum * 0.55:
        return []

    first = {
        "x": x,
        "y": y,
        "w": split_x,
        "h": h
    }

    second = {
        "x": x + split_x,
        "y": y,
        "w": w - split_x,
        "h": h
    }

    return [
        first,
        second
    ]


# --------------------------------------------------
# Normalizar dígito
# --------------------------------------------------

def normalize_digit(mask, component):

    x = component["x"]
    y = component["y"]
    w = component["w"]
    h = component["h"]

    padding = 3

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

    target_w = 32
    target_h = 40

    scale = min(
        (target_w - 4) / crop.shape[1],
        (target_h - 4) / crop.shape[0]
    )

    new_w = max(
        1,
        int(crop.shape[1] * scale)
    )

    new_h = max(
        1,
        int(crop.shape[0] * scale)
    )

    resized = cv2.resize(
        crop,
        (new_w, new_h),
        interpolation=cv2.INTER_AREA
    )

    canvas = np.zeros(
        (target_h, target_w),
        dtype=np.uint8
    )

    offset_x = (
        target_w - new_w
    ) // 2

    offset_y = (
        target_h - new_h
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


# --------------------------------------------------
# Auditoría
# --------------------------------------------------

audit_items = []


# --------------------------------------------------
# Procesamiento
# --------------------------------------------------

for _, row in df.iterrows():

    token_id = int(row["id"])
    dorsal = str(row["dorsal"])

    mask_file = (
        masks_path /
        f"dorsal_{token_id:02d}.png"
    )

    mask = cv2.imread(
        str(mask_file),
        cv2.IMREAD_GRAYSCALE
    )

    if mask is None:
        print(
            f"ID {token_id:02d}: "
            "máscara inexistente"
        )
        continue


    expected_digits = len(dorsal)


    # ----------------------------------------------
    # Componentes iniciales
    # ----------------------------------------------

    components = get_components(
        mask
    )


    # ----------------------------------------------
    # Eliminar componentes claramente basura
    # ----------------------------------------------

    components = [
        c
        for c in components
        if (
            c["area"] >= MIN_AREA
            or c["h"] >= MIN_HEIGHT
        )
    ]


    # ----------------------------------------------
    # Unir fragmentos cercanos
    # ----------------------------------------------

    components = merge_components(
        mask,
        components
    )


    # ----------------------------------------------
    # Eliminar componentes demasiado grandes
    # ----------------------------------------------

    filtered = []

    for component in components:

        if (
            component["w"] > 80
            and expected_digits == 1
        ):
            continue

        filtered.append(
            component
        )

    components = filtered


    # ----------------------------------------------
    # Si hay un bloque ancho y esperamos 2
    # ----------------------------------------------

    if (
        expected_digits == 2
        and len(components) == 1
        and components[0]["w"] > 60
    ):

        split = split_component(
            mask,
            components[0]
        )

        if len(split) == 2:
            components = split


    # ----------------------------------------------
    # Orden
    # ----------------------------------------------

    components.sort(
        key=lambda c: c["x"]
    )


    print(
        f"ID {token_id:02d} | "
        f"dorsal={dorsal:>2} | "
        f"esperados={expected_digits} | "
        f"finales={len(components)}"
    )


    # ----------------------------------------------
    # Guardar dígitos
    # ----------------------------------------------

    if len(components) != expected_digits:

        print(
            "    ⚠ No coincide la cantidad."
        )

        continue


    for digit_index, (
        digit,
        component
    ) in enumerate(
        zip(
            dorsal,
            components
        )
    ):

        normalized = normalize_digit(
            mask,
            component
        )

        output_file = (
            output_path /
            f"ID{token_id:02d}_"
            f"digit{digit_index}.png"
        )

        cv2.imwrite(
            str(output_file),
            normalized
        )


        # Auditoría
        audit_items.append(
            (
                token_id,
                digit,
                normalized
            )
        )


# --------------------------------------------------
# Crear auditoría
# --------------------------------------------------

if audit_items:

    cell_w = 70
    cell_h = 60

    columns = 8

    rows = int(
        np.ceil(
            len(audit_items) /
            columns
        )
    )

    audit = np.zeros(
        (
            rows * cell_h,
            columns * cell_w,
            3
        ),
        dtype=np.uint8
    )


    for index, (
        token_id,
        digit,
        normalized
    ) in enumerate(
        audit_items
    ):

        row = index // columns
        column = index % columns

        x = column * cell_w
        y = row * cell_h

        color = cv2.cvtColor(
            normalized,
            cv2.COLOR_GRAY2BGR
        )

        color = cv2.resize(
            color,
            (40, 50),
            interpolation=cv2.INTER_NEAREST
        )

        audit[
            y:y + 50,
            x:x + 40
        ] = color

        cv2.putText(
            audit,
            f"{token_id}:{digit}",
            (x + 2, y + 58),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (0, 255, 0),
            1
        )


    cv2.imwrite(
        str(audit_path),
        audit
    )


print("\n=== FIN ===")
print(
    f"Archivos guardados en: {output_path}"
)

print(
    f"Auditoría: {audit_path}"
)