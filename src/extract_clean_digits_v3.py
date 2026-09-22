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
    / "digit_debug_v3"
)

audit_path = (
    project_path
    / "output"
    / "digit_debug_audit_v3.jpg"
)

output_path.mkdir(
    parents=True,
    exist_ok=True
)


# ==================================================
# CONFIGURACIÓN
# ==================================================

# Un fragmento y otro pertenecen al mismo dígito
# si sus centros X están suficientemente cerca.
MAX_CENTER_X_GAP = 15

# Distancia máxima desde el centro de la ficha.
MAX_CENTER_DISTANCE = 65

# Fragmentos diminutos que claramente son ruido.
MIN_COMPONENT_AREA = 10
MIN_COMPONENT_HEIGHT = 5

# Un bloque de este ancho probablemente contiene
# dos dígitos fusionados.
FUSED_WIDTH = 60

# Normalización final
TARGET_WIDTH = 32
TARGET_HEIGHT = 40


# ==================================================
# CARGAR ETIQUETAS
# ==================================================

df = pd.read_csv(
    labels_path,
    dtype={"dorsal": str}
)


# ==================================================
# FUNCIONES
# ==================================================

def component_center(component):
    """
    Devuelve el centro X/Y de un componente.
    """

    return (
        component["x"] + component["w"] / 2,
        component["y"] + component["h"] / 2
    )


def vertical_gap(a, b):
    """
    Distancia vertical entre dos cajas.
    Si se superponen, devuelve 0.
    """

    a_bottom = a["y"] + a["h"]
    b_bottom = b["y"] + b["h"]

    return max(
        0,
        max(
            b["y"] - a_bottom,
            a["y"] - b_bottom
        )
    )


def x_overlap(a, b):
    """
    Cantidad de píxeles que se superponen en X.
    """

    left = max(
        a["x"],
        b["x"]
    )

    right = min(
        a["x"] + a["w"],
        b["x"] + b["w"]
    )

    return max(
        0,
        right - left
    )


def should_belong_to_same_digit(a, b):
    """
    Decide si dos componentes son probablemente
    fragmentos del mismo dígito.
    """

    ax, ay = component_center(a)
    bx, by = component_center(b)

    x_gap = abs(ax - bx)

    if x_gap > MAX_CENTER_X_GAP:
        return False

    overlap = x_overlap(a, b)

    gap_y = vertical_gap(a, b)

    # Comparten bastante X.
    aligned_x = (
        overlap >= min(a["w"], b["w"]) * 0.35
        or x_gap <= 8
    )

    # Están juntos verticalmente.
    aligned_y = (
        gap_y <= 15
    )

    return aligned_x and aligned_y


def get_components(mask):
    """
    Obtiene componentes conectados de la máscara.
    """

    binary = (
        mask > 127
    ).astype(np.uint8) * 255

    num_labels, labels_img, stats, _ = (
        cv2.connectedComponentsWithStats(
            binary,
            connectivity=8
        )
    )

    components = []

    for label_id in range(
        1,
        num_labels
    ):

        x, y, w, h, area = (
            stats[label_id]
        )

        if area < MIN_COMPONENT_AREA:
            continue

        if h < MIN_COMPONENT_HEIGHT:
            continue

        components.append(
            {
                "label": int(label_id),
                "x": int(x),
                "y": int(y),
                "w": int(w),
                "h": int(h),
                "area": int(area)
            }
        )

    return components, labels_img


def merge_component_groups(
    components,
    labels_img
):
    """
    Agrupa componentes que parecen pertenecer
    al mismo dígito.

    Importante:
    no usamos transitividad ciega.

    Dos componentes tienen que ser compatibles
    directamente por su posición.
    """

    groups = []

    for component in components:

        placed = False

        for group in groups:

            # Comparamos únicamente contra el
            # componente más cercano del grupo,
            # no hacemos una cadena infinita.
            best = min(
                group,
                key=lambda c: abs(
                    component_center(c)[0]
                    - component_center(component)[0]
                )
            )

            if should_belong_to_same_digit(
                best,
                component
            ):

                group.append(
                    component
                )

                placed = True
                break

        if not placed:

            groups.append(
                [component]
            )


    # ==================================================
    # Construir datos de cada grupo
    # ==================================================

    digit_groups = []

    for group in groups:

        x1 = min(
            c["x"]
            for c in group
        )

        y1 = min(
            c["y"]
            for c in group
        )

        x2 = max(
            c["x"] + c["w"]
            for c in group
        )

        y2 = max(
            c["y"] + c["h"]
            for c in group
        )

        area = sum(
            c["area"]
            for c in group
        )

        width = x2 - x1
        height = y2 - y1

        center_x = (
            x1 + width / 2
        )

        center_y = (
            y1 + height / 2
        )

        digit_groups.append(
            {
                "components": group,
                "x": x1,
                "y": y1,
                "w": width,
                "h": height,
                "area": area,
                "center_x": center_x,
                "center_y": center_y
            }
        )

    return digit_groups


def group_mask(
    group,
    labels_img
):
    """
    Construye una máscara que contiene
    todos los componentes de un grupo.
    """

    mask = np.zeros(
        labels_img.shape,
        dtype=np.uint8
    )

    for component in group["components"]:

        mask[
            labels_img
            == component["label"]
        ] = 255

    return mask


def split_wide_digit(
    digit_mask,
    group
):
    """
    Divide un bloque ancho en dos dígitos
    usando el valle de la proyección vertical.
    """

    x = group["x"]
    y = group["y"]
    w = group["w"]
    h = group["h"]

    crop = digit_mask[
        y:y + h,
        x:x + w
    ]

    projection = np.sum(
        crop > 0,
        axis=0
    )

    if len(projection) < 10:
        return []

    left_limit = max(
        2,
        int(w * 0.25)
    )

    right_limit = min(
        w - 3,
        int(w * 0.75)
    )

    if right_limit <= left_limit:
        return []

    valley_relative = np.argmin(
        projection[
            left_limit:right_limit
        ]
    )

    split_x = (
        left_limit
        + valley_relative
    )

    maximum = projection.max()

    if maximum == 0:
        return []

    minimum = projection[
        split_x
    ]

    # El valle tiene que ser realmente un valle.
    if minimum > maximum * 0.55:
        return []

    left_group = {
        "x": x,
        "y": y,
        "w": split_x,
        "h": h,
        "area": int(
            np.sum(
                crop[:, :split_x] > 0
            )
        ),
        "mask": crop[
            :,
            :split_x
        ]
    }

    right_group = {
        "x": x + split_x,
        "y": y,
        "w": w - split_x,
        "h": h,
        "area": int(
            np.sum(
                crop[:, split_x:] > 0
            )
        ),
        "mask": crop[
            :,
            split_x:
        ]
    }

    return [
        left_group,
        right_group
    ]


def normalize_digit(
    digit_mask
):
    """
    Normaliza un dígito a 32x40 manteniendo
    su proporción.
    """

    coords = cv2.findNonZero(
        digit_mask
    )

    if coords is None:
        return None

    x, y, w, h = cv2.boundingRect(
        coords
    )

    crop = digit_mask[
        y:y + h,
        x:x + w
    ]

    if crop.size == 0:
        return None

    scale = min(
        (TARGET_WIDTH - 4) / crop.shape[1],
        (TARGET_HEIGHT - 4) / crop.shape[0]
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


def quality_score(
    group,
    center_x,
    center_y
):
    """
    Puntúa un grupo según:
    - área
    - altura
    - cercanía al centro
    """

    distance = np.sqrt(
        (
            group["center_x"]
            - center_x
        ) ** 2
        +
        (
            group["center_y"]
            - center_y
        ) ** 2
    )

    return (
        group["area"]
        + group["h"] * 15
        - distance * 8
    )


# ==================================================
# PROCESAR FICHAS
# ==================================================

audit_items = []

successful = 0
failed = 0


for _, row in df.iterrows():

    token_id = int(row["id"])
    dorsal = str(row["dorsal"])

    expected_digits = len(
        dorsal
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
            f"ID {token_id:02d} "
            "→ máscara inexistente"
        )

        failed += 1
        continue


    height, width = mask.shape


    # ==================================================
    # DISCO INTERIOR
    # ==================================================

    center_x = width / 2
    center_y = height / 2

    yy, xx = np.ogrid[
        :height,
        :width
    ]

    distance = np.sqrt(
        (xx - center_x) ** 2
        +
        (yy - center_y) ** 2
    )

    inner_radius = (
        min(width, height)
        * 0.37
    )

    inner_mask = (
        distance <= inner_radius
    )


    binary = (
        mask > 127
    ).astype(np.uint8) * 255

    binary[
        ~inner_mask
    ] = 0


    # ==================================================
    # COMPONENTES
    # ==================================================

    components, labels_img = (
        get_components(
            binary
        )
    )


    # ==================================================
    # AGRUPAR FRAGMENTOS
    # ==================================================

    groups = merge_component_groups(
        components,
        labels_img
    )


    # ==================================================
    # FILTRO DE GRUPOS
    # ==================================================

    valid_groups = []

    for group in groups:

        group_distance = np.sqrt(
            (
                group["center_x"]
                - center_x
            ) ** 2
            +
            (
                group["center_y"]
                - center_y
            ) ** 2
        )

        if (
            group_distance
            > MAX_CENTER_DISTANCE
        ):
            continue

        if group["h"] < 8:
            continue

        if group["w"] > 100:
            # Solo dejamos pasar bloques grandes
            # cuando esperamos 2 dígitos.
            if expected_digits != 2:
                continue

        valid_groups.append(
            group
        )


    # ==================================================
    # ORDEN
    # ==================================================

    valid_groups.sort(
        key=lambda g: g["center_x"]
    )


    # ==================================================
    # CASO DE 1 DÍGITO
    # ==================================================

    if expected_digits == 1:

        if not valid_groups:

            print(
                f"ID {token_id:02d} | "
                f"dorsal={dorsal:>2} | "
                "SIN GRUPO"
            )

            failed += 1
            continue


        # El mejor grupo es el que más se parece
        # a un dorsal central.
        best_group = max(
            valid_groups,
            key=lambda g:
            quality_score(
                g,
                center_x,
                center_y
            )
        )

        selected_groups = [
            best_group
        ]


    # ==================================================
    # CASO DE 2 DÍGITOS
    # ==================================================

    else:

        # ----------------------------------------------
        # Si hay UN bloque muy ancho, es probable
        # que los dos dígitos estén fusionados.
        # ----------------------------------------------

        fused_groups = [
            g
            for g in valid_groups
            if g["w"] >= FUSED_WIDTH
            and g["h"] >= 35
        ]

        if fused_groups:

            best_group = max(
                fused_groups,
                key=lambda g:
                quality_score(
                    g,
                    center_x,
                    center_y
                )
            )

            selected_groups = (
                split_wide_digit(
                    binary,
                    best_group
                )
            )


        else:

            # ------------------------------------------
            # Tenemos grupos separados.
            # Elegimos los dos mejores.
            # ------------------------------------------

            ranked = sorted(
                valid_groups,
                key=lambda g:
                quality_score(
                    g,
                    center_x,
                    center_y
                ),
                reverse=True
            )

            selected_groups = ranked[:2]

            selected_groups.sort(
                key=lambda g:
                g["center_x"]
            )


    # ==================================================
    # COMPROBAR
    # ==================================================

    if len(selected_groups) != expected_digits:

        print(
            f"ID {token_id:02d} | "
            f"dorsal={dorsal:>2} | "
            f"esperados={expected_digits} | "
            f"finales={len(selected_groups)} | "
            "⚠ FALLÓ"
        )

        failed += 1
        continue


    # ==================================================
    # GUARDAR DÍGITOS
    # ==================================================

    print(
        f"ID {token_id:02d} | "
        f"dorsal={dorsal:>2} | "
        f"grupos={len(valid_groups)} | "
        f"finales={len(selected_groups)} | "
        "OK"
    )


    for digit_index, (
        expected_digit,
        group
    ) in enumerate(
        zip(
            dorsal,
            selected_groups
        )
    ):

        # ----------------------------------------------
        # Obtener máscara del grupo
        # ----------------------------------------------

        if "mask" in group:

            digit_mask = group["mask"]

        else:

            digit_mask = group_mask(
                group,
                labels_img
            )


        # ----------------------------------------------
        # Normalizar
        # ----------------------------------------------

        normalized = normalize_digit(
            digit_mask
        )

        if normalized is None:

            continue


        output_file = (
            output_path
            /
            f"ID{token_id:02d}_"
            f"digit{digit_index}_"
            f"{expected_digit}.png"
        )

        cv2.imwrite(
            str(output_file),
            normalized
        )


        # ----------------------------------------------
        # Auditoría
        # ----------------------------------------------

        audit_image = cv2.cvtColor(
            normalized,
            cv2.COLOR_GRAY2BGR
        )

        cv2.putText(
            audit_image,
            f"{token_id}:{expected_digit}",
            (2, 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.28,
            (0, 255, 0),
            1
        )

        audit_items.append(
            audit_image
        )

    successful += 1


# ==================================================
# AUDITORÍA
# ==================================================

if audit_items:

    cell_width = 50
    cell_height = 55

    columns = 10

    rows = int(
        np.ceil(
            len(audit_items)
            / columns
        )
    )

    audit = np.zeros(
        (
            rows * cell_height,
            columns * cell_width,
            3
        ),
        dtype=np.uint8
    )


    for index, image_digit in enumerate(
        audit_items
    ):

        row = index // columns
        column = index % columns

        x = (
            column
            * cell_width
        )

        y = (
            row
            * cell_height
        )

        resized = cv2.resize(
            image_digit,
            (40, 50),
            interpolation=cv2.INTER_NEAREST
        )

        audit[
            y:y + 50,
            x:x + 40
        ] = resized


    cv2.imwrite(
        str(audit_path),
        audit
    )


# ==================================================
# RESULTADO
# ==================================================

print("\n================================")
print("RESULTADO")
print("================================")

print(
    f"Correctas: {successful}/22"
)

print(
    f"Fallidas:  {failed}/22"
)

print(
    f"Archivos:  {output_path}"
)

print(
    f"Auditoría: {audit_path}"
)