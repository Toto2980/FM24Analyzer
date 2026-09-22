# FM24Analyzer

Análisis automatizado de partidos de **Football Manager 24** mediante visión por computadora clásica (OpenCV). A partir de una grabación de la vista 2D del motor de partido, reconstruye la posición e identidad de cada jugador frame a frame, como base para análisis táctico medible.

> **Estado:** prototipo en validación del tracking (Sprint 0). Todavía no hay una versión usable de punta a punta.

## Qué hace hoy

```text
video → ROI de cancha → detección de fichas (Hough) → arqueros → equipo (HSV)
      → dorsal (templates) → identidad persistente (track_id) → tracking (Hungarian + gating) → JSON por frame
```

- 22/22 jugadores detectados en el frame de referencia, 0 falsos positivos.
- Dorsales: 23/26 dígitos correctos (88,46 %).
- Tracking de 30 transiciones auditado: las 23 pérdidas vienen de 2 causas identificadas (ver `CLAUDE/Auditoria 31 frames.md`).

## Documentación del proyecto

El proyecto se gestiona como una entrega de software: especificación, backlog y sprints hasta el MVP.

| Documento | Contenido |
|---|---|
| [`CLAUDE/SRS - FM24Analyzer.md`](CLAUDE/SRS%20-%20FM24Analyzer.md) | Especificación de requerimientos (alcance, casos de uso, RF/RNF, MVP) |
| [`CLAUDE/Backlog y Sprints.md`](CLAUDE/Backlog%20y%20Sprints.md) | Product backlog, Definición de Hecho y plan de sprints |
| [`CLAUDE/FM24Analyzer - Informe Maestro del Proyecto, Estado, Pendientes y Roadmap.md`](CLAUDE/) | Estado, roadmap y metodología |
| [`CLAUDE/Auditoria 31 frames.md`](CLAUDE/Auditoria%2031%20frames.md) | Auditoría de pérdidas de tracking |

## Requisitos

- Windows 11
- Python 3.13
- Dependencias con versión fija en `requirements.txt`

```bash
python -m pip install -r requirements.txt
```

## Uso (prototipo)

Los videos no se versionan. Colocá el clip en `videos/partido_prueba.mp4` (1280×720, 30 FPS, vista 2D) y corré:

```bash
python src/build_match_json.py
python src/batch_tracker.py
python src/audit_transitions.py
```

Salidas en `output/`. La línea base de regresión de 31 frames está en `output/baseline_31f/`.

## Estructura

```text
src/        scripts del pipeline (tracking_core.py = detección + asociación compartidas)
CLAUDE/     documentación del proyecto (SRS, backlog, informes)
output/     salidas generadas (solo se versiona baseline_31f/)
videos/     clips de entrada (no versionados)
```

## Metodología

> Primero entender. Después medir. Luego decidir. Finalmente implementar.

Un cambio por vez, medido contra una línea base y revalidado antes de ampliar la prueba.
