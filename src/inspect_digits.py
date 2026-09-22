from pathlib import Path

import cv2
import pandas as pd


# --------------------------------------------------
# Rutas
# --------------------------------------------------

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
    / "digit_debug"
)

output_path.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# Configuración
# --------------------------------------------------

MIN_AREA = 3
MIN_WIDTH = 1
MIN_HEIGHT = 3


# --------------------------------------------------
# Leer etiquetas
# --------------------------------------------------

df = pd.read_csv(
    labels_path,
    dtype={"dorsal": str}
)


# --------------------------------------------------
# Analizar cada ficha
# --------------------------------------------------

for _, row in df.iterrows():

    token_id = int(row["id"])
    dorsal = str(row["dorsal"])

    mask_file = (
        masks_path
        / f"dorsal_{token_id:02d}.png"
    )

    mask = cv2.imread(
        str(mask_file),
        cv2.IMREAD_GRAYSCALE
    )

    if mask is None:

        print(
            f"ID {token_id:02d}: "
            "NO SE ENCONTRÓ LA MÁSCARA"
        )

        continue


    # ----------------------------------------------
    # Asegurar binario
    # ----------------------------------------------

    _, binary = cv2.threshold(
        mask,
        127,
        255,
        cv2.THRESH_BINARY
    )


    # ----------------------------------------------
    # Componentes
    # ----------------------------------------------

    num_labels, labels_img, stats, centroids = (
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

        if area < MIN_AREA:
            continue

        if w < MIN_WIDTH:
            continue

        if h < MIN_HEIGHT:
            continue

        components.append(
            {
                "x": int(x),
                "y": int(y),
                "w": int(w),
                "h": int(h),
                "area": int(area)
            }
        )


    # ----------------------------------------------
    # Ordenar izquierda → derecha
    # ----------------------------------------------

    components.sort(
        key=lambda c: c["x"]
    )


    # ----------------------------------------------
    # Mostrar
    # ----------------------------------------------

    print(
        f"ID {token_id:02d} | "
        f"dorsal={dorsal:>2} | "
        f"esperados={len(dorsal)} | "
        f"encontrados={len(components)}"
    )


    for index, component in enumerate(
        components
    ):

        print(
            f"    {index}: "
            f"x={component['x']:3d} "
            f"y={component['y']:3d} "
            f"w={component['w']:3d} "
            f"h={component['h']:3d} "
            f"area={component['area']:4d}"
        )


    # ----------------------------------------------
    # Imagen de depuración
    # ----------------------------------------------

    debug = cv2.cvtColor(
        binary,
        cv2.COLOR_GRAY2BGR
    )


    for index, component in enumerate(
        components
    ):

        x = component["x"]
        y = component["y"]
        w = component["w"]
        h = component["h"]

        cv2.rectangle(
            debug,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            debug,
            str(index),
            (x, max(y - 3, 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (0, 255, 0),
            1
        )


    debug_file = (
        output_path
        / f"debug_{token_id:02d}.png"
    )

    cv2.imwrite(
        str(debug_file),
        debug
    )


print("\n=== FIN ===")
print(
    f"Archivos de debug: {output_path}"
)