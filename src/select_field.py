from pathlib import Path
import cv2


# --------------------------------------------------
# Rutas
# --------------------------------------------------

project_path = Path(__file__).resolve().parent.parent
image_path = project_path / "output" / "primer_frame.jpg"
output_path = project_path / "output" / "campo.jpg"


# --------------------------------------------------
# Cargar imagen
# --------------------------------------------------

image = cv2.imread(str(image_path))

if image is None:
    print("No se pudo abrir la imagen.")
    exit()


# --------------------------------------------------
# Seleccionar cancha
# --------------------------------------------------

print("Seleccioná con el mouse SOLO el área de la cancha.")
print("Cuando termines, presioná ENTER.")
print("Para cancelar, presioná ESC.")

x, y, width, height = cv2.selectROI(
    "Seleccionar cancha",
    image,
    showCrosshair=True,
    fromCenter=False
)

cv2.destroyAllWindows()


# --------------------------------------------------
# Comprobar selección
# --------------------------------------------------

if width == 0 or height == 0:
    print("No se seleccionó ninguna región.")
    exit()


print("\n=== ROI DE LA CANCHA ===")
print(f"x: {x}")
print(f"y: {y}")
print(f"width: {width}")
print(f"height: {height}")


# --------------------------------------------------
# Recortar
# --------------------------------------------------

field = image[
    y:y + height,
    x:x + width
]


# --------------------------------------------------
# Guardar
# --------------------------------------------------

success = cv2.imwrite(str(output_path), field)

if success:
    print("\nCancha guardada correctamente.")
    print(output_path)
else:
    print("\nNo se pudo guardar la imagen.")