from pathlib import Path
import re

import cv2
import numpy as np
import pandas as pd


# ==================================================
# RUTAS
# ==================================================

project_path = Path(__file__).resolve().parent.parent

templates_path = (
    project_path
    / "output"
    / "templates"
)

digits_path = (
    project_path
    / "output"
    / "digit_debug_v3"
)

output_path = (
    project_path
    / "output"
    / "benchmark"
)

output_path.mkdir(
    parents=True,
    exist_ok=True
)


results_csv = (
    output_path
    / "results.csv"
)

matrix_self_csv = (
    output_path
    / "confusion_self.csv"
)

matrix_blind_csv = (
    output_path
    / "confusion_blind.csv"
)


# ==================================================
# MUESTRAS UTILIZADAS PARA CONSTRUIR EL BANCO
# ==================================================
#
# Cada tupla:
# (ID de ficha, índice del dígito)
#

TRAIN_SAMPLES = {
    (11, 0),
    (12, 0),
    (19, 0),
    (19, 1),

    (1, 0),
    (20, 0),

    (2, 0),
    (17, 0),

    (4, 0),
    (15, 0),

    (8, 0),
    (18, 0),

    (9, 0),
    (16, 0),

    (3, 0),
    (13, 0),

    (5, 0),
    (7, 0),

    (10, 0),
    (14, 0),

    # Único 0 del banco
    (21, 1)
}


# Esta muestra NO puede considerarse ciega porque
# es exactamente la fuente usada como template 0.
LEAKED_SAMPLES = {
    (21, 1)
}


LOW_GAP = 0.10


# ==================================================
# CARGAR TEMPLATES
# ==================================================

templates = {}


for digit in range(10):

    digit_dir = (
        templates_path
        / str(digit)
    )

    templates[digit] = []

    if not digit_dir.exists():
        continue

    for file in sorted(
        digit_dir.glob("template_*.png")
    ):

        image = cv2.imread(
            str(file),
            cv2.IMREAD_GRAYSCALE
        )

        if image is None:
            continue

        templates[digit].append(
            {
                "file": file.name,
                "image": image
            }
        )


print("=== BANCO DE TEMPLATES ===")

total_templates = 0

for digit in range(10):

    count = len(
        templates[digit]
    )

    total_templates += count

    print(
        f"{digit}: {count}"
    )

print(
    f"TOTAL: {total_templates}"
)


if total_templates == 0:

    print(
        "\nERROR: "
        "no se encontraron templates."
    )

    exit()


# ==================================================
# RECONOCEDOR 1-NN
# ==================================================

def recognize(image):

    class_scores = {}

    best_template_for_class = {}

    for digit in range(10):

        scores = []

        for template in templates[digit]:

            tpl = template["image"]

            if (
                image.shape !=
                tpl.shape
            ):
                raise ValueError(
                    "Input y template "
                    "tienen tamaños diferentes."
                )

            result = cv2.matchTemplate(
                image,
                tpl,
                cv2.TM_CCOEFF_NORMED
            )

            score = float(
                result[0, 0]
            )

            scores.append(score)


        if scores:

            best_index = int(
                np.argmax(scores)
            )

            class_scores[digit] = (
                scores[best_index]
            )

            best_template_for_class[digit] = (
                templates[digit][best_index]["file"]
            )


    ranked = sorted(
        class_scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    if len(ranked) == 0:
        return None

    winner_digit = ranked[0][0]
    winner_score = ranked[0][1]

    if len(ranked) > 1:

        second_digit = ranked[1][0]
        second_score = ranked[1][1]

    else:

        second_digit = None
        second_score = None


    gap = (
        winner_score - second_score
        if second_score is not None
        else None
    )


    return {
        "prediction": winner_digit,
        "score": winner_score,
        "second": second_digit,
        "second_score": second_score,
        "gap": gap,
        "template": best_template_for_class[
            winner_digit
        ]
    }


# ==================================================
# DESCUBRIR MUESTRAS
# ==================================================

pattern = re.compile(
    r"ID(\d+)_digit(\d+)_(\d+)\.png"
)

samples = []


for file in sorted(
    digits_path.glob("ID*_digit*_*.png")
):

    match = pattern.fullmatch(
        file.name
    )

    if not match:
        continue

    token_id = int(
        match.group(1)
    )

    digit_index = int(
        match.group(2)
    )

    expected_digit = int(
        match.group(3)
    )

    image = cv2.imread(
        str(file),
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        continue

    samples.append(
        {
            "file": file,
            "token_id": token_id,
            "digit_index": digit_index,
            "expected": expected_digit,
            "image": image
        }
    )


print(
    f"\nMuestras encontradas: "
    f"{len(samples)}"
)


# ==================================================
# BENCHMARK
# ==================================================

results = []


for sample in samples:

    token_id = sample["token_id"]
    digit_index = sample["digit_index"]
    expected = sample["expected"]

    key = (
        token_id,
        digit_index
    )

    prediction = recognize(
        sample["image"]
    )

    if prediction is None:

        continue


    predicted = prediction[
        "prediction"
    ]

    score = prediction[
        "score"
    ]

    second = prediction[
        "second"
    ]

    second_score = prediction[
        "second_score"
    ]

    gap = prediction[
        "gap"
    ]


    if key in LEAKED_SAMPLES:

        test_type = "LEAKED"

    elif key in TRAIN_SAMPLES:

        test_type = "SELF"

    else:

        test_type = "BLIND"


    correct = (
        predicted == expected
    )


    if gap is not None and gap < LOW_GAP:

        confidence = "LOW"

    else:

        confidence = "CLEAR"


    results.append(
        {
            "token_id": token_id,
            "digit_index": digit_index,
            "expected": expected,
            "predicted": predicted,
            "correct": correct,
            "score": score,
            "second": second,
            "second_score": second_score,
            "gap": gap,
            "confidence": confidence,
            "test_type": test_type,
            "template": prediction[
                "template"
            ],
            "file": sample["file"].name
        }
    )


# ==================================================
# DATAFRAME
# ==================================================

results_df = pd.DataFrame(
    results
)


# ==================================================
# MOSTRAR RESULTADOS INDIVIDUALES
# ==================================================

print(
    "\n========================================"
)

print(
    "RESULTADOS INDIVIDUALES"
)

print(
    "========================================"
)


for _, row in results_df.iterrows():

    status = (
        "OK"
        if row["correct"]
        else "ERROR"
    )


    print(
        f"{row['test_type']:6} | "
        f"ID {row['token_id']:02d} "
        f"digit {row['digit_index']} | "
        f"{row['expected']} → "
        f"{row['predicted']} | "
        f"score={row['score']:.4f} | "
        f"gap={row['gap']:.4f} | "
        f"{row['confidence']:5} | "
        f"{status}"
    )


# ==================================================
# FUNCIÓN DE RESUMEN
# ==================================================

def print_summary(
    dataframe,
    title
):

    print(
        f"\n=== {title} ==="
    )

    if len(dataframe) == 0:

        print(
            "Sin muestras."
        )

        return


    correct = int(
        dataframe["correct"].sum()
    )

    total = len(
        dataframe
    )

    accuracy = (
        correct / total * 100
    )


    print(
        f"Correctas: "
        f"{correct}/{total}"
    )

    print(
        f"Precisión: "
        f"{accuracy:.2f}%"
    )

    print(
        f"Gap promedio: "
        f"{dataframe['gap'].mean():.4f}"
    )

    print(
        f"Gap mínimo: "
        f"{dataframe['gap'].min():.4f}"
    )

    low = (
        dataframe["confidence"]
        == "LOW"
    ).sum()

    print(
        f"Casos de margen bajo: "
        f"{low}"
    )


# ==================================================
# RESÚMENES
# ==================================================

self_df = results_df[
    results_df["test_type"] == "SELF"
]

blind_df = results_df[
    results_df["test_type"] == "BLIND"
]

leaked_df = results_df[
    results_df["test_type"] == "LEAKED"
]


print_summary(
    self_df,
    "SELF TEST"
)

print_summary(
    blind_df,
    "BLIND TEST"
)

print_summary(
    leaked_df,
    "LEAKED TEST"
)


# ==================================================
# MATRIZ DE CONFUSIÓN
# ==================================================

def confusion_matrix(
    dataframe
):

    matrix = np.zeros(
        (10, 10),
        dtype=int
    )

    for _, row in dataframe.iterrows():

        true_digit = int(
            row["expected"]
        )

        predicted_digit = int(
            row["predicted"]
        )

        matrix[
            true_digit,
            predicted_digit
        ] += 1

    return pd.DataFrame(
        matrix,
        index=[
            f"real_{i}"
            for i in range(10)
        ],
        columns=[
            f"pred_{i}"
            for i in range(10)
        ]
    )


# Self
self_matrix = confusion_matrix(
    self_df
)

print(
    "\n========================================"
)

print(
    "MATRIZ DE CONFUSIÓN - SELF"
)

print(
    "========================================"
)

print(
    self_matrix
)


# Blind
blind_matrix = confusion_matrix(
    blind_df
)

print(
    "\n========================================"
)

print(
    "MATRIZ DE CONFUSIÓN - BLIND"
)

print(
    "========================================"
)

print(
    blind_matrix
)


# ==================================================
# GUARDAR
# ==================================================

results_df.to_csv(
    results_csv,
    index=False,
    encoding="utf-8"
)

self_matrix.to_csv(
    matrix_self_csv
)

blind_matrix.to_csv(
    matrix_blind_csv
)


print(
    "\n========================================"
)

print(
    "ARCHIVOS GENERADOS"
)

print(
    "========================================"
)

print(
    results_csv
)

print(
    matrix_self_csv
)

print(
    matrix_blind_csv
)