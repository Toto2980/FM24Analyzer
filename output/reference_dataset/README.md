# Dataset de referencia (HU-04, CU-09)

`build_reference_dataset.py` propone posiciones y equipo para frames
con movimiento. Falta la parte de Toto: validar cada detección y
completar el dorsal (el sistema todavía no lee números — no hay OCR).

## Cómo validar un frame

1. Abrí `frame_XXXXXX.jpg`: cada ficha detectada tiene un círculo
   (celeste = RACING, naranja = RIVAL) con un número de índice al lado.
2. Abrí `frame_XXXXXX.json`: por cada `index` hay un objeto con
   `x, y, team, team_v, dorsal, validated`.
3. Para cada detección real: completá `"dorsal"` con el número de
   camiseta que se ve en la imagen, corregí `"team"` si está mal, y
   poné `"validated": true`.
4. Para una detección que NO es un jugador (ver falsos positivos
   abajo): borrá esa entrada del JSON, o dejala con
   `"validated": false` y agregá `"note": "falso positivo"`.
5. Si falta un jugador real que el sistema no detectó, agregalo a mano
   con un `index` nuevo, sus `x, y`, `team` y `dorsal`.

## Falsos positivos conocidos

- **Ícono "A" de instrucción táctica**: FM24 dibuja un círculo oscuro
  con una "A" sobre el jugador al que se le está por dar una
  instrucción rápida (gritos). Hough lo confunde con una ficha.
  Se reconoce porque `team_v` da muy bajo (< 20) comparado con el
  resto — ninguna camiseta real es tan oscura.
- **Arquero duplicado**: a veces el mismo arquero sale detectado dos
  veces con clasificaciones de equipo distintas (colores de arquero
  ambiguos). Quedate con una sola detección.
- **Jugadores muy juntos** (disputando la pelota): el detector a veces
  separa mal un grupo apretado. Revisá que el número de detecciones
  cerca de la pelota coincida con lo que se ve.
- **Frames con un cartel superpuesto** (ej. "X entra a Y" en una
  sustitución): el texto puede generar detecciones falsas alrededor.
  Si un frame cae justo en ese momento, mejor pedir otro frame en vez
  de pelear con el cartel.

## Formato final

Cuando los 5 (o más) frames estén validados, esto se convierte en la
línea base contra la que corre el benchmark de HU-11/RF-72. No hace
falta un solo archivo consolidado: los `frame_XXXXXX.json` con
`validated: true` en todas sus detecciones son el dataset.
