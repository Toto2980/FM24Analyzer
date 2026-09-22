from pathlib import Path
import pandas as pd


# --------------------------------------------------
# Rutas
# --------------------------------------------------

project_path = Path(__file__).resolve().parent.parent

input_path = project_path / "output" / "token_colors.csv"
output_path = project_path / "output" / "classified_tokens.csv"


# --------------------------------------------------
# Cargar datos
# --------------------------------------------------

df = pd.read_csv(input_path)


# --------------------------------------------------
# Clasificación
# --------------------------------------------------

def classify(row):

    saturation = row["median_s"]
    value = row["median_v"]

    # Arquero
    if saturation < 30:
        return "ARQUERO"

    # Rival
    if value > 180:
        return "RIVAL"

    # Racing
    if value <= 180 and saturation >= 50:
        return "RACING"

    return "DESCONOCIDO"


df["team"] = df.apply(classify, axis=1)


# --------------------------------------------------
# Mostrar resultado
# --------------------------------------------------

print("=== CLASIFICACIÓN ===")

print(
    df[
        [
            "id",
            "x",
            "y",
            "team",
            "median_h",
            "median_s",
            "median_v",
            "source"
        ]
    ].to_string(index=False)
)


# --------------------------------------------------
# Resumen
# --------------------------------------------------

print("\n=== RESUMEN ===")

print(
    df["team"].value_counts()
)


# --------------------------------------------------
# Guardar
# --------------------------------------------------

df.to_csv(
    output_path,
    index=False,
    encoding="utf-8"
)

print("\nArchivo guardado en:")
print(output_path)