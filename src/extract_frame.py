from pathlib import Path
import cv2

project_path = Path(__file__).resolve().parent.parent

video_path = project_path / "videos" / "partido_prueba.mp4"
output_path = project_path / "output" / "primer_frame.jpg"

video = cv2.VideoCapture(str(video_path))

if not video.isOpened():
    print("No se pudo abrir el video.")
    exit()

success, frame = video.read()

if not success:
    print("No se pudo leer el primer frame.")
    video.release()
    exit()

cv2.imwrite(str(output_path), frame)

video.release()

print("Frame extraído correctamente.")
print(f"Guardado en: {output_path}")