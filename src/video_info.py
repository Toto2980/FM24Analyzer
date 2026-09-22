from pathlib import Path
import cv2

# Ruta de la carpeta del proyecto
project_path = Path(__file__).resolve().parent.parent

# Ruta absoluta al video
video_path = project_path / "videos" / "partido_prueba.mp4"

print("Ruta del video:")
print(video_path)

print("\n¿Existe el archivo?")
print(video_path.exists())

if not video_path.exists():
    print("\nNo encuentro el archivo.")
    exit()

print("\nTamaño del archivo:")
print(f"{video_path.stat().st_size / (1024 * 1024):.2f} MB")

print("\nIntentando abrir el video...")

video = cv2.VideoCapture(str(video_path))

if not video.isOpened():
    print("OpenCV encontró el archivo, pero no pudo abrirlo.")
    exit()

fps = video.get(cv2.CAP_PROP_FPS)
frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

duration = frame_count / fps if fps > 0 else 0

print("\n=== INFORMACIÓN DEL VIDEO ===")
print(f"FPS: {fps}")
print(f"Frames: {frame_count}")
print(f"Resolución: {width}x{height}")
print(f"Duración: {duration:.2f} segundos")

video.release()