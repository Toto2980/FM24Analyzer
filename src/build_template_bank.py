from pathlib import Path
import shutil


# ==================================================
# RUTAS
# ==================================================

project_path = Path(__file__).resolve().parent.parent

digit_debug_path = (
    project_path
    / "output"
    / "digit_debug_v3"
)

zero_source_path = (
    project_path
    / "output"
    / "templates_source"
    / "0"
)

templates_path = (
    project_path
    / "output"
    / "templates"
)


# ==================================================
# LIMPIAR / CREAR BANCO
# ==================================================

templates_path.mkdir(
    parents=True,
    exist_ok=True
)


for digit in range(10):

    digit_path = (
        templates_path
        / str(digit)
    )

    digit_path.mkdir(
        parents=True,
        exist_ok=True
    )


# ==================================================
# MAPA DE MUESTRAS LIMPIAS
# ==================================================

samples = {

    "0": [
        zero_source_path / "zero_21.png"
    ],

    "1": [
        digit_debug_path / "ID11_digit0_1.png",
        digit_debug_path / "ID12_digit0_1.png",
        digit_debug_path / "ID19_digit0_1.png",
        digit_debug_path / "ID19_digit1_1.png"
    ],

    "2": [
        digit_debug_path / "ID01_digit0_2.png",
        digit_debug_path / "ID20_digit0_2.png"
    ],

    "3": [
        digit_debug_path / "ID02_digit0_3.png",
        digit_debug_path / "ID17_digit0_3.png"
    ],

    "4": [
        digit_debug_path / "ID04_digit0_4.png",
        digit_debug_path / "ID15_digit0_4.png"
    ],

    "5": [
        digit_debug_path / "ID08_digit0_5.png",
        digit_debug_path / "ID18_digit0_5.png"
    ],

    "6": [
        digit_debug_path / "ID09_digit0_6.png",
        digit_debug_path / "ID16_digit0_6.png"
    ],

    "7": [
        digit_debug_path / "ID03_digit0_7.png",
        digit_debug_path / "ID13_digit0_7.png"
    ],

    "8": [
        digit_debug_path / "ID05_digit0_8.png",
        digit_debug_path / "ID07_digit0_8.png"
    ],

    "9": [
        digit_debug_path / "ID10_digit0_9.png",
        digit_debug_path / "ID14_digit0_9.png"
    ]
}


# ==================================================
# COPIAR
# ==================================================

print("=== CONSTRUYENDO BANCO ===\n")

total = 0

for digit, files in samples.items():

    destination = (
        templates_path
        / digit
    )

    print(f"Dígito {digit}:")

    for index, source in enumerate(files):

        if not source.exists():

            print(
                f"  ⚠ FALTA: {source.name}"
            )

            continue


        target = (
            destination
            / f"template_{index:02d}.png"
        )

        shutil.copy2(
            source,
            target
        )

        print(
            f"  ✓ {source.name}"
        )

        total += 1

    print()


# ==================================================
# RESUMEN
# ==================================================

print("================================")
print("BANCO TERMINADO")
print("================================")

for digit in range(10):

    folder = (
        templates_path
        / str(digit)
    )

    count = len(
        list(folder.glob("*.png"))
    )

    print(
        f"{digit}: {count} templates"
    )

print(
    f"\nTotal: {total} templates"
)

print(
    f"\nUbicación: {templates_path}"
)