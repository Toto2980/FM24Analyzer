# Investigación: ¿FM24 ya calcula lo que queremos medir? (INV-01)

**Pregunta.** Si FM24 muestra heatmap, distancia recorrida y sprints por jugador después del partido, entonces ya calculó y guardó esos datos. ¿Se pueden leer de la pantalla o de un archivo, en vez de reconstruirlos del video?

**Respuesta corta.** Sí para las dos cosas, con distinto costo:

| Vía | Qué da | Costo | Estado |
|---|---|---|---|
| Pantallas del juego | Totales por jugador: distancia, sprints, presiones, heatmap, posición media | Bajo | Confirmado por fuentes públicas. Falta verificarlo en tu instalación |
| Exportar con Ctrl+P (Print Screen → página web) | Las mismas tablas en HTML, sin OCR | Muy bajo | Confirmado para tablas de jugadores. Falta verificar en las tablas de estadísticas del partido |
| Archivo `.pkm` del partido | Coordenadas de los 22 jugadores y la pelota a lo largo del partido: la **ground truth** que el tracker intenta reconstruir | Alto (formato propio, sin parser público) | Sin explorar. Ver la sonda más abajo |
| Leer la memoria del proceso | En teoría, todo lo anterior en vivo | Muy alto y frágil (cambia con cada parche) | Descartado para el MVP |

## 1. Lo que FM24 muestra en el juego

Según fuentes públicas sobre FM24 (Data Hub y Análisis de partido):

- **Heatmap por jugador**: muestra dónde estuvo el jugador, tuviera o no la pelota.
- **Distancia recorrida** por jugador y partido (Data Hub, informes individuales).
- **Sprints** y **presiones** (intentadas y exitosas), con un gráfico de "physical output" que cruza sprints con distancia.
- Posiciones medias, mapas de pases, pases progresivos.
- **Velocidad máxima: sin evidencia.** No encontré ninguna fuente que diga que FM24 la muestra. Hay que confirmarlo en el juego.

**Qué confirmar en tu instalación** (10 minutos, al terminar un partido):

1. Análisis de partido → Jugador → ¿hay heatmap, distancia, sprints, velocidad máxima?
2. En esas tablas, ¿funciona Ctrl+P → "Página web"? Si funciona, los totales se obtienen en HTML sin OCR.
3. Arriba a la derecha, ¿aparece "Guardar partido"? Guardá uno para la sonda del punto 3.

## 2. Qué cambia para el proyecto

- **Los totales ya los da FM.** Distancia, sprints y heatmap agregado no justifican el pipeline de video. Hay que sacarlos de FM (vía Ctrl+P) y no reconstruirlos.
- **El valor propio del tracker es la serie temporal**: posición de cada jugador en cada instante, distancias entre líneas, compactación, forma de la presión. FM no muestra nada de eso de manera exportable.
- **Oráculo de validación gratis para Sprints 5 y 6.** La distancia que FM reporta por jugador sirve para validar la conversión de píxeles a metros y la trayectoria del tracker. Criterio: error relativo de distancia por jugador contra FM.
- Dato complementario: `simatch.fmf` → `physical_constraints.jsb` contiene las velocidades de caminar, trotar y esprintar del motor. Hay un proyecto público que lo edita (FM24-matchengine-maker). Sirve como cota física para el gating del tracking.

## 3. El archivo detrás: `.pkm`

- **Qué es.** Es la repetición del partido. No es video: es un registro comprimido de coordenadas y telemetría del motor, que FM vuelve a reproducir.
- **Dónde está.** Se guarda con "Guardar partido" al terminar el partido, en `Documents\Sports Interactive\Football Manager 2024\matches\`. Las grabaciones automáticas van a `matches\automatic\` (`.pkm` y `.rec`).
- **Limitaciones.** El formato es propietario, depende de la versión del parche y no tiene documentación ni parser público conocido.

**Sonda (`src/probe_pkm.py`).** No decodifica nada: solo decide si vale la pena intentarlo.

```bash
python src/probe_pkm.py "C:/Users/<usuario>/Documents/Sports Interactive/Football Manager 2024/matches/<partido>.pkm"
```

Cómo leer el resultado:

- **Hay streams zlib/deflate descomprimibles.** Es viable: el siguiente paso es buscar en los datos descomprimidos patrones de floats que coincidan con las dimensiones de la cancha (105×68). Conviene un timebox de 1 sprint.
- **Entropía ≈ 8,0 en todo el archivo y ningún stream.** El archivo está cifrado o usa compresión propia. En ese caso se descarta y seguimos con el video.

## Decisión propuesta

1. Ahora: verificar las pantallas del punto 1 y correr la sonda sobre un `.pkm` real.
2. Si Ctrl+P funciona: agregar al backlog la ingesta de estadísticas de FM como oráculo de validación (distancia y sprints por jugador).
3. Si la sonda encuentra streams descomprimibles: hacer un spike de 1 sprint para decodificar el `.pkm`. Si sale bien, da ground truth frame a frame para medir el tracker, algo mucho mejor que auditar 31 frames a mano.
4. El pipeline de video se mantiene: es la única vía que no depende de un formato cerrado ni de la versión del parche.

## Fuentes

- [FM Scout – Match replays](https://www.fmscout.com/q-1199-Match-replays.html)
- [Strikerless – .PKM files](https://strikerless.com/2014/08/13/pkm-files-what-are-they-and-why-would-i-even-use-them/)
- [SI Community – PKM + REC files](https://community.sports-interactive.com/bugtracker/1644_football-manager-26-bugs-tracker/1872_fm26-bug-tracker-introduction/how-to-upload-pkms-rec-files-r23721/)
- [FMWonderkid – FM24 Data Hub](https://fmwonderkid.com/fm-tactics/fm24-data-hub-explanation/)
- [FootballGPT – FM24 stats](https://footballgpt.co/blog/football-manager-dominate-with-data-analytics-fm24-stats)
- [FM Scout – Export a CSV/HTML](https://www.fmscout.com/a-fm26-player-csv-export.html)
- [FM24-matchengine-maker](https://github.com/wonss737/FM24-matchengine-maker)
