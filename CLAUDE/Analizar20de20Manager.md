# Analizar partido de Football Manager

<!-- Conversión completa del PDF a Markdown. Se conserva el orden de lectura: columna izquierda y luego columna derecha de cada hoja. -->

<!-- Hojas físicas sin texto en el PDF, omitidas del contenido MD: 6-203. -->


---

## Página 1 (hoja física 1, columna izquierda)


domingo 22:31


/idea Quiero eh, hacer un, un grabador de pantalla para


vídeos de eh, Football Manager 24. Eh, este va a ver el


partido, o sea, va a grabar la pantalla y eh, desde después


del partido va a... Eh, Primero va a analizar a todos los


jugadores, ¿no? Va a ver cuáles son los jugadores que, que 
están en el campo. Eh, yo lo que quiero hacer es eh, hacer 
como que, bueno, antes de iniciar un partido, como que


empiezo a grabar la pantalla y este eh, lo que hace es, eh, 
eh, es más que nada un... un eh, Ay, no sé cómo decirlo.


Este lo que hace es empezar a grabar la pantalla y este va 
eh, andando todo, todo. No, no, no, no. No hace, no hace


Mostrar más


Sí. Ahora entendí bastante mejor lo que querés hacer. Y, de hecho, no lo llamaría


simplemente “grabador de pantalla”. Sería más bien un analizador automático de


partidos de Football Manager 24 a partir de una grabación de pantalla.


La idea podría ser esta:


Antes del partido


El programa empieza una “sesión de análisis”. No necesita intervenir en FM24.


Simplemente empieza a capturar la pantalla.


En ese momento intenta detectar y guardar:


rival


formación del rival


tu formación


once inicial


suplentes


posiciones


roles/instrucciones


capitán


jugadores lesionados o sancionados si aparecen


condición física


estado anímico


---

## Página 2 (hoja física 1, columna derecha)


Explorar planes
familiaridad con la posición


cualquier dato visible en las pantallas previas


Después arranca el partido.


Durante el partido


Acá está la parte interesante.


El programa no tendría que “entender Football Manager” directamente. Primero tendría


que ver la pantalla y reconstruir el estado del partido.


Por ejemplo, en cada instante podría obtener algo como:


00:00


Racing 4-3-3


Maravilla: ST


Nardoni: MC


Sosa: MC


...


00:17


Pelota: sector derecho


Jugador detectado: extremo derecho


Carrilero derecho avanzando


Extremo derecho cerrándose


00:24


Pérdida de pelota


Equipo comienza presión


5 jugadores por delante de la pelota


Y así sucesivamente.


No hace falta guardar absolutamente cada frame del vídeo para eso. Sería una manera


magnífica de fabricar un archivo gigantesco porque, aparentemente, los discos duros


también merecen sufrir.


Podría analizar el vídeo cada X milisegundos y reconstruir una secuencia temporal.


Por ejemplo:


00:00


00:01


00:02


00:03


...


90:00


---

## Página 3 (hoja física 2, columna izquierda)


Y para cada momento registrar dónde está cada jugador.


Entonces podrías terminar con algo parecido a:


Jugador: Nardoni


00:15 → posición (x=42,y=61)


00:20 → posición (x=47,y=59)


00:25 → posición (x=52,y=54)


00:30 → posición (x=58,y=49)


De ahí podés calcular:


distancia recorrida


zonas ocupadas


altura media


amplitud


movimientos hacia adelante


movimientos hacia atrás


movimientos laterales


cuánto tiempo pasó en cada zona


relación con compañeros


distancia respecto de otros jugadores


participación en presión


retrocesos


desmarques


ocupación de espacios


Y ahí tu proyecto empieza a parecerse muchísimo más a un sistema de análisis táctico


que a un simple grabador.


Y después viene lo realmente interesante


Una vez terminado el partido, el programa podría combinar tres fuentes:


1. Lo que vio durante el partido


Movimiento de jugadores, pelota, sustituciones, goles, tarjetas, cambios tácticos, etc.


2. Lo que leyó de la interfaz


Por ejemplo:


Sistema: 4-3-3


Mentalidad: Positiva


Presión: Alta


---

## Página 4 (hoja física 2, columna derecha)


Línea defensiva: Alta


Ritmo: Alto


3. Las estadísticas finales de FM


Por ejemplo:


Posesión: 61%


Tiros: 17


Tiros al arco: 8


Pases completados: 89%


xG: 1.84


Entonces podría generar un informe.


Por ejemplo:


Nardoni


Posición nominal: MC


Posición observada promedio: interior derecho


Altura media: 58% del campo rival


Tendencia: desplazamiento hacia derecha


Interacción frecuente: carrilero derecho + extremo derecho


Durante pérdida: participó en presión en 8 ocasiones


Retroceso defensivo: alto


Conclusión táctica: el jugador terminó ocupando zonas más adelantadas que las
indicadas por su posición nominal.


Eso ya es otra cosa.


Incluso podrías reconstruir la táctica


Esta parte me parece especialmente buena para lo que veníamos haciendo con tu idea


futbolística.


El programa podría decir:


FORMA CON PELOTA


           ST


---

## Página 5 (hoja física 3, columna izquierda)


     LW          RW


       MEZ      MEZ


           MC


LBI     DFC   DFC     LD


Y después comparar eso con lo configurado en FM.


Porque una cosa es:


“Estoy jugando 4-3-3.”


Y otra muy distinta es:


“Mi 4-3-3 realmente se convierte en 3-2-5 cuando tengo la pelota.”


El programa podría detectar justamente eso.


Por ejemplo:


Sistema configurado:


4-3-3


Estructura observada:


3-2-5


Motivo probable:


LI se cierra


LD avanza


MC se posiciona entre líneas


Extremo izquierdo mantiene amplitud


Extremo derecho ataca zona interior


Y eso encaja muchísimo con tu filosofía de FM que estuvimos armando.


Hay una parte que tenemos que separar


No todo lo que querés obtener se puede ver directamente en la pantalla del partido.


Por ejemplo:


“¿Por qué este jugador está suplente?”


Eso es complicado.


La pantalla puede decir:


---

## Página 6 (hoja física 3, columna derecha)


Suplente


Condición 82%


Pero no necesariamente:


Está suplente porque el entrenador considera que X es mejor.


Eso el programa tendría que inferirlo, y una inferencia no debe presentarse como un


hecho.


Podría decir:


“Posibles motivos: menor condición física, rotación, rendimiento reciente o decisión


táctica.”


Mientras que para otras cosas sí puede ser mucho más directo:


Jugador en banco: sí


Titular habitual: sí


Condición: 78%


Lesionado: no


Posición natural: MC


Posición elegida por DT: MC


Yo dividiría el proyecto en 5 módulos


              GRABADOR


                 │


                 ▼


        CAPTURA DE PANTALLA


                 │


                 ▼


        VISIÓN + OCR + CV


                 │


        ┌────────┼────────┐


        ▼        ▼        ▼


    JUGADORES  PELOTA   INTERFAZ


        │        │        │


        └────────┼────────┘


                 ▼


          MOTOR DEL PARTIDO


                 │


                 ▼


          DATOS TÁCTICOS


                 │


---

## Página 7 (hoja física 4, columna izquierda)


                 ▼


             INFORME


Donde:


Grabador


guarda la sesión completa.


OCR


lee textos de FM24.


Computer Vision


detecta jugadores, pelota, líneas, posiciones, etc.


Motor del partido


reconstruye estados:


ataque


defensa


transición ofensiva


transición defensiva


pelota parada


cambio táctico


sustitución


Analizador


convierte todo eso en estadísticas y conclusiones.


Y hay una decisión MUY importante


Para la primera versión yo no intentaría analizar el 3D.


Empezaría con el modo 2D de FM24.


Porque ahí tenés una representación mucho más limpia del campo y de los jugadores. Si


conseguís detectar correctamente:


campo


equipo A


equipo B


pelota


el problema pasa a ser relativamente manejable.


Después, cuando eso funcione, podrías intentar 3D.


El MVP que realmente construiría


---

## Página 8 (hoja física 4, columna derecha)


No intentaría hacer de entrada:


“analizar absolutamente todo lo que ocurre en un partido”.


Haría algo mucho más acotado:


1. Iniciar grabación


2. Detectar formación


3. Detectar 11 titulares


4. Detectar sus posiciones


5. Seguir jugadores durante el partido


6. Detectar pelota


7. Detectar sustituciones


8. Guardar coordenadas de jugadores


9. Generar mapa de movimiento


10. Crear informe postpartido


Y recién después:


presión


bloques


ocupación de espacios


transiciones


altura defensiva


distancias entre líneas


comportamiento individual


comparación con la táctica configurada


Porque hay una diferencia enorme entre:


“detectar dónde está Nardoni”


y


“entender por qué Nardoni está ahí”.


Lo primero es visión por computadora. Lo segundo ya es análisis táctico.


Y justamente ahí está la parte más divertida del proyecto: hacer que una grabación de


FM24 se convierta en una representación estructurada del partido, algo parecido a crear


tus propios datos de tracking cuando FM no te los entrega directamente.


Hasta podría terminar existiendo un archivo interno así:


JSON


{


  "match": "Racing vs Independiente",


---

## Página 9 (hoja física 5, columna izquierda)


  "formation": "4-3-3",


  "players": {


    "Nardoni": {


      "role": "MC",


      "positions": [],


      "average_position": {},


      "heatmap": [],


      "transitions": [],


      "pressing_actions": []


    }


  }


}


Y desde ahí podrías construir una interfaz tipo Racing 360, pero alimentada


automáticamente por lo que ocurrió realmente en FM24. Ahí ya deja de ser una idea


simpática y empieza a convertirse en un proyecto de programación bastante serio.


---

## Página 10 (hoja física 204, columna izquierda)


Sí. El informe anterior terminó repitiendo varias veces las mismas ideas: el pipeline, la


prueba de 31 frames, la filosofía de validación y el estado actual aparecían en demasiadas


secciones. Lo compacté agrupando conceptos y dejando las métricas en una sola sección


central.


FM24Analyzer - Informe Técnico de Estado del Proyecto


FM24Analyzer


Informe técnico de estado, arquitectura y metodología


Proyecto: FM24Analyzer


Objetivo: análisis automatizado de partidos de Football Manager 24 mediante visión


por computadora


Estado: prototipo funcional en validación de tracking


Entorno: Windows · Python 3.13 · OpenCV 5.0.0


Última prueba: 31 frames observados, 30 transiciones de tracking


1. Objetivo y alcance


FM24Analyzer busca transformar una grabación de Football Manager 24 en datos


estructurados capaces de representar el comportamiento de los jugadores y,


posteriormente, permitir análisis táctico.


El objetivo final es obtener:


posición e identidad de cada jugador;


equipo, dorsal y rol;


movimiento y trayectorias;


formación y estructura posicional;


presión, bloque y transiciones;


cambios tácticos;


análisis automático del partido.


El proyecto se desarrolla por capas:


Video


 ↓


ROI


 ↓


---

## Página 11 (hoja física 204, columna derecha)


Detección


↓


Clasificación


↓


Dorsal


↓


Identidad


↓


Tracking


↓


Trayectorias


↓


Eventos


↓


Análisis táctico


La prioridad actual sigue siendo la percepción y el tracking. El análisis táctico se


incorporará cuando los datos subyacentes sean suficientemente estables.


2. Estrategia técnica


Se decidió comenzar con una solución específica para FM24 utilizando OpenCV y


algoritmos clásicos de visión por computadora, en lugar de depender inicialmente


de modelos genéricos como YOLO.


La decisión se basa en que el entorno presenta características muy controladas:


campo visual estable;


fichas circulares;


tamaño relativamente constante;


colores diferenciables;


dorsales ubicados en una zona predecible;


interfaz y cámara con poca variabilidad.


La arquitectura podrá incorporar posteriormente deep learning si las pruebas


muestran que la solución clásica no alcanza la robustez necesaria.


3. Entorno y estructura


Entorno


---

## Página 12 (hoja física 205, columna izquierda)


Sistema:        Windows


Python:         3.13


OpenCV:         5.0.0


Bibliotecas:    NumPy, Pandas, SciPy


Procesamiento:  local


Video de prueba


Archivo:        partido_prueba.mp4


FPS:            30


Frames totales: 2172


Resolución:     1280 × 720


Duración:       72,40 s


A 30 FPS, cada frame representa aproximadamente 33,3 ms.


Estructura principal


FM24Analyzer/


├── videos/


├── output/


│   ├── dorsals_v2/


│   ├── templates/


│   └── match/


└── src/


    ├── detect_*


    ├── classify_tokens.py


    ├── extract_*


    ├── benchmark_templates.py


    ├── build_match_json.py


    ├── track_step.py


    └── batch_tracker.py


La organización actual es experimental. La refactorización modular queda para una


etapa posterior.


4. Detección y clasificación


4.1. Región de interés


La cancha se aisló mediante:


X = 183


Y = 48


---

## Página 13 (hoja física 205, columna derecha)


Ancho = 913


Alto = 623


ROI es la región de la imagen que realmente procesa el sistema.


4.2. Detección de jugadores


La detección utiliza HoughCircles sobre el ROI, complementado por una segunda


detección sensible para casos difíciles.


Características observadas de los tokens:


Radio mínimo: 7 px


Radio máximo: 8 px


Radio medio:  7,26 px


Mediana:      7 px


En la prueba inicial:


22 jugadores válidos


0 falsos positivos


0 duplicados


Radio: tamaño visual estimado de la ficha.


Falso positivo: círculo detectado que no corresponde a un jugador.


Duplicado: dos detecciones para una misma ficha.


4.3. Arqueros


Los arqueros presentan una apariencia más desaturada, por lo que requieren un


detector específico basado en CLAHE, Hough y restricción espacial a las áreas de


penal.


Se recuperaron:


2 arqueros


0 falsos positivos


Su comportamiento temporal todavía requiere validación.


4.4. Clasificación por equipo


---

## Página 14 (hoja física 206, columna izquierda)


Se utilizaron características HSV.


S < 30


    → ARQUERO


V > 180


    → RIVAL


V <= 180 y S >= 50


    → RACING


H: tono.


S: saturación.


V: luminosidad.


Los valores anteriores son umbrales de clasificación, no métricas de calidad.


5. Identificación mediante dorsal


La extracción del dorsal se realizó específicamente para el formato visual de FM24:


token


 ↓


recorte


 ↓


reescalado


 ↓


máscara


 ↓


zona interior


 ↓


componentes


 ↓


separación de dígitos


Se procesaron correctamente los 22 tokens de la muestra y se identificaron 26


dígitos debido a la existencia de dorsales de dos cifras.


Banco de templates


Se construyó un banco de:


21 templates


---

## Página 15 (hoja física 206, columna derecha)


Un template es una imagen de referencia de un determinado dígito.


Benchmark


Se utilizó:


cv2.matchTemplate


TM_CCOEFF_NORMED


Se calcularon:


Winner score: mejor similitud encontrada.


Second-best score: segunda mejor similitud.


Gap: diferencia entre ambas.


gap = winner - second-best


Un gap alto implica una decisión más separada; uno bajo, mayor ambigüedad.


Umbral experimental:


gap < 0,10 → LOW


Esto indica ambigüedad, no necesariamente error.


Resultado


23 / 26 dígitos correctos


Exactitud del benchmark: 88,46 %


Los errores se concentraron en muestras visualmente degradadas.


6. Modelo de identidad


Se estableció una separación fundamental:


token_id


Identifica una detección concreta dentro de un frame.


track_id


Identifica al jugador persistente a través del tiempo.


Esto permite que una detección pueda cambiar de token_id  sin perder la identidad


representada por track_id .


---

## Página 16 (hoja física 207, columna izquierda)


7. Tracking


El tracking utiliza:


Hungarian Algorithm;


linear_sum_assignment ;


gating espacial;


asociación separada para Racing, Rival y GK.


Parámetros actuales:


MAX_DISTANCE = 15 px


LARGE_COST = 10000


MAX_DISTANCE: distancia máxima permitida para una asociación.


LARGE_COST: costo artificialmente elevado para impedir asociaciones consideradas


inválidas.


7.1. Movimiento entre frames


Se calcula:


dx = x_actual - x_anterior


dy = y_actual - y_anterior


distance = sqrt(dx² + dy²)


La distancia se expresa en píxeles.


Por ejemplo:


dx = -2


dy = +2


distance ≈ 2,83 px


Esto representa desplazamiento visual entre dos frames, no metros ni velocidad real.


8. Primera validación del tracking


---

## Página 17 (hoja física 207, columna derecha)


Entre frame_0000  y frame_0001  se obtuvieron:


Tracks:            22


Distancia media:   ≈ 0,31 px


Distancia máxima:  ≈ 2,83 px


La mayoría de las identidades mantuvieron posiciones prácticamente constantes y


no se observaron intercambios evidentes entre jugadores de campo.


Esta prueba validó el mecanismo básico de asociación.


9. Validación temporal: 31 frames


La prueba siguiente procesó:


frame_0000


...


frame_0030


Esto representa:


31 frames observados


30 transiciones de tracking


1 segundo de video


La diferencia es importante:


3 frames → 2 transiciones


31 frames → 30 transiciones


Cada transición compara un frame con el inmediatamente anterior.


Resultados


22 matches → 12 transiciones


21 matches → 13 transiciones


20 matches →  5 transiciones


Con 22 tracks:


22/22 = 100 %


21/22 ≈ 95,45 %


20/22 ≈ 90,91 %


Estos valores representan cobertura de asociación, no accuracy global.


---

## Página 18 (hoja física 208, columna izquierda)


10. Métricas del tracking


Métrica
Significado


Frames
Cantidad de imágenes observadas


Transiciones
Comparaciones entre frames consecutivos


Detecciones
Candidatos encontrados por el detector


Matches
Asociaciones aceptadas entre tracks y detecciones


Match coverage
Matches / tracks activos


Distance
Desplazamiento de un jugador entre dos frames


Mean distance
Promedio de desplazamiento de los matches de una transición


Max distance
Mayor desplazamiento registrado en una transición


dist_total
Suma de las distancias de todos los matches de una transición


Distancia acumulada
Suma de desplazamientos de un track durante toda la prueba


Winner score
Mejor similitud entre un dígito y los templates


Second-best
Segunda mejor similitud


Gap
Diferencia entre las dos mejores similitudes


ROI
Región de la imagen analizada


Radio
Tamaño visual estimado de una ficha


MAX_DISTANCE
Límite de distancia utilizado para aceptar asociaciones


Ninguna de las métricas de distancia representa todavía distancia física en metros.


Para eso será necesaria una calibración espacial de la cancha.


11. Resultado de la prueba de 31 frames


El sistema generó:


---

## Página 19 (hoja física 208, columna derecha)


output/trajectory_30frames.jpg


y:


frame_0001.json


...


frame_0030.json


Las mayores distancias acumuladas registradas fueron:


RACING #01 → 33,31 px


RIVAL  #01 → 16,49 px


Estos valores indican mayor desplazamiento de la detección durante la ventana,


pero todavía no permiten determinar si se trata de movimiento real, jitter del


detector o una combinación de ambos.


12. Metodología de trabajo


El desarrollo se realiza mediante un ciclo controlado:


Problema


↓


Hipótesis


↓


Experimento


↓


Medición


↓


Inspección visual


↓


Diagnóstico


↓


Cambio mínimo


↓


Revalidación


↓


Escalamiento


Los principios centrales son:


Evidencia antes que hipótesis.


Una sospecha no se considera diagnóstico hasta ser comprobada.


---

## Página 20 (hoja física 209, columna izquierda)


Una capa por vez.


No se analiza tácticamente algo que todavía no puede detectarse o seguirse de


forma fiable.


Una métrica para cada problema.


Detección, identificación y tracking se validan con métricas diferentes.


No cambiar varias variables simultáneamente.


La modificación debe ser lo suficientemente acotada para poder atribuir el resultado.


No optimizar prematuramente.


La complejidad se incorpora cuando una limitación real la justifica.


No declarar resuelto más de lo demostrado.


Un resultado válido sobre una muestra pequeña no implica funcionamiento


universal.


Mantener separadas configuración, medición y conclusión.


Por ejemplo, MAX_DISTANCE = 15  es una configuración; distance = 2,83 px  es una


medición; “el tracking es estable” es una conclusión que requiere evidencia.


13. Criterio de diagnóstico


Cuando aparece un error, se analiza de abajo hacia arriba:


¿Los datos originales son correctos?


        ↓


¿La detección es correcta?


        ↓


¿La clasificación es correcta?


        ↓


¿La identidad es correcta?


        ↓


¿La asociación es correcta?


        ↓


¿La interpretación es correcta?


Esto evita corregir una capa superior cuando el problema está realmente en una


inferior.


14. Estado actual


---

## Página 21 (hoja física 209, columna derecha)


Componente
Estado


Lectura de video
Funcional


ROI
Funcional


Detección de jugadores
Funcional inicial


Recuperación de detecciones difíciles
Funcional inicial


Detección de arqueros
Funcional, requiere validación temporal


Clasificación de equipos
Funcional inicial


Extracción de dorsales
Funcional inicial


Banco de templates
Funcional


Matching de dígitos
Funcional inicial


Identidad persistente
Funcional


JSON por frame
Funcional


Tracking 1 transición
Validado


Tracking 30 transiciones / 31 frames
En validación


Predicción por velocidad
Pendiente


Coast mode
Pendiente


Tracking largo
Pendiente


Detección de eventos
Pendiente


Análisis táctico
Pendiente


Interfaz gráfica
Pendiente


15. Próximo paso


---

## Página 22 (hoja física 210, columna izquierda)


El próximo experimento no consiste todavía en agregar velocidad, coast mode ,


reidentificación ni modificar el Hungarian.


Primero debe auditarse cada transición donde:


matches < 22


para determinar:


qué track quedó sin match


qué detección quedó libre


distancia al candidato más cercano


bloque afectado:


Racing / Rival / GK


Con esa evidencia se podrá determinar si el problema está en:


detección;


arqueros;


jugadores de campo;


gating;


asociación.


Después se aplicará únicamente la corrección necesaria y se repetirá exactamente la


misma prueba antes de ampliar la ventana.


16. Roadmap


VALIDACIÓN 31 FRAMES


        ↓


AUDITORÍA DE PÉRDIDAS


        ↓


CORRECCIÓN ESPECÍFICA


        ↓


100 TRANSICIONES


        ↓


TRACKING LARGO


        ↓


CALIBRACIÓN ESPACIAL


        ↓


TRAYECTORIAS


        ↓


EVENTOS


---

## Página 23 (hoja física 210, columna derecha)


       ↓


ANÁLISIS TÁCTICO


17. Conclusión


FM24Analyzer ya cuenta con un pipeline funcional que transforma una captura de


FM24 en información estructurada sobre 22 identidades, incluyendo detección,


clasificación, dorsal y una primera capa de tracking temporal.


Los componentes básicos ya demostraron funcionar en muestras controladas. El


principal desafío actual es la robustez temporal de la asociación, no la ausencia de


infraestructura.


La metodología del proyecto permanece deliberadamente conservadora:


Primero entender. Después medir. Luego decidir. Finalmente implementar.


El siguiente avance debe surgir de la auditoría de las transiciones imperfectas, no de


introducir complejidad antes de conocer su necesidad.


hoy 16:51


bueno arma el informe del proyecto de todo lo que


hicimos, que hay que hacer y que falta para completar el 
100% del proyecto, ademas el roadmap completo


Sí. Este ya no conviene que sea otro “estado del proyecto” que repita las mismas diez


cosas con distinto sombrero. Lo correcto es convertir todo lo que hicimos en un


documento maestro del proyecto, con cuatro preguntas centrales: qué es FM24Analyzer,


qué está hecho, qué falta y qué significa llegar al 100 %.


FM24Analyzer - Informe Maestro del Proyecto, Estado, Pend…


FM24Analyzer


Informe maestro del proyecto


---

## Página 24 (hoja física 211, columna izquierda)


Proyecto: FM24Analyzer


Tipo: Sistema de visión por computadora aplicado a Football Manager 24


Objetivo final: transformar una grabación de un partido en datos estructurados,


reconstruir el comportamiento de los jugadores y generar análisis táctico


automatizado.


Estado actual: prototipo funcional en etapa de validación temporal del tracking.


Entorno: Windows · Python 3.13 · OpenCV 5.0.0 · NumPy · Pandas · SciPy


Última prueba: 31 frames observados, 30 transiciones de tracking, equivalentes a 1


segundo de video.


1. Resumen ejecutivo


FM24Analyzer nació como un proyecto para analizar partidos de Football Manager


24 a partir de video, evitando depender inicialmente de modelos de inteligencia


artificial pesados o servicios externos.


La idea central es convertir una imagen de un partido en información cada vez más


estructurada:


VIDEO


 ↓


CANCHA


 ↓


JUGADORES


 ↓


EQUIPOS


 ↓


DORSALES


 ↓


IDENTIDADES


 ↓


MOVIMIENTO


 ↓


TRAYECTORIAS


 ↓


EVENTOS


 ↓


ESTRUCTURA TÁCTICA


 ↓


ANÁLISIS


Durante el desarrollo ya se construyó y validó buena parte de las primeras capas.


---

## Página 25 (hoja física 211, columna derecha)


El sistema actualmente puede:


leer el video;


aislar la cancha;


detectar fichas de jugadores;


recuperar detecciones difíciles;


detectar arqueros mediante un detector específico;


clasificar Racing, Rival y arquero;


extraer dorsales;


reconocer dígitos mediante templates;


generar una identidad persistente mediante track_id ;


asociar jugadores entre frames mediante Hungarian + gating;


guardar estados en JSON;


generar visualizaciones de trayectorias.


Los resultados más importantes obtenidos hasta ahora son:


22 jugadores detectados en la muestra inicial


0 falsos positivos


0 duplicados


2 arqueros recuperados


26 dígitos extraídos


21 templates construidos


23/26 dígitos correctamente reconocidos


88,46 % de exactitud en el benchmark de dorsales


22/22 asociaciones correctas en la primera transición


31 frames observados en la prueba temporal


30 transiciones de tracking


El proyecto todavía no está terminado.


La principal deuda técnica actual es demostrar que el tracking es suficientemente


robusto durante períodos largos y, a partir de allí, construir la capa superior de


eventos y análisis táctico.


2. Objetivo del proyecto


El objetivo final de FM24Analyzer es producir una representación estructurada de un


partido a partir de un video.


El sistema debería terminar pudiendo responder preguntas como:


---

## Página 26 (hoja física 212, columna izquierda)


Sobre los jugadores


¿Dónde está cada jugador?


¿Cuál es su dorsal?


¿A qué equipo pertenece?


¿Qué rol tiene?


¿Dónde estuvo durante el partido?


¿Cuánto se desplazó?


¿Qué zonas ocupó?


Sobre la estructura


¿Qué formación utiliza cada equipo?


¿Cómo cambia la formación con y sin pelota?


¿Qué jugadores forman cada línea?


¿Qué amplitud tiene el equipo?


¿Qué profundidad tiene?


¿Qué tan compacto está?


Sobre el comportamiento


¿Cuándo presiona?


¿Dónde recupera?


¿Cómo inicia una transición?


¿Qué ocurre después de perder la pelota?


¿Cuándo cambia de estructura?


¿Qué jugador abandona su zona?


¿Cómo reaccionan los laterales, extremos y mediocampistas?


Sobre el partido


¿Qué patrones tácticos aparecen?


¿Cuándo cambian?


¿Qué secuencias se repiten?


¿Qué diferencias aparecen entre distintos momentos del partido?


El objetivo final no es simplemente detectar círculos. Los círculos son el principio del


problema.


3. Alcance técnico completo


---

## Página 27 (hoja física 212, columna derecha)


El proyecto se divide en ocho grandes capas.


FASE 1


Captura y preparación


       ↓


FASE 2


Percepción visual


       ↓


FASE 3


Identificación


       ↓


FASE 4


Tracking temporal


       ↓


FASE 5


Reconstrucción espacial


       ↓


FASE 6


Detección de eventos


       ↓


FASE 7


Análisis táctico


       ↓


FASE 8


Producto final


Cada fase depende de la anterior.


La metodología impide avanzar simplemente porque “se puede”. Una capa debe


alcanzar un nivel suficiente de confiabilidad antes de convertirse en fundamento de


la siguiente.


4. Lo que ya hicimos


4.1. Preparación del entorno


Se estableció el entorno de desarrollo:


Python 3.13


OpenCV 5.0.0


NumPy


Pandas


SciPy


---

## Página 28 (hoja física 213, columna izquierda)


El proyecto funciona localmente en Windows.


También se resolvió el problema inicial de las diferentes versiones de Python


instaladas, seleccionando explícitamente Python 3.13 para el proyecto.


5. Procesamiento del video


Se creó video_info.py  para inspeccionar las características del archivo.


Video actual:


Resolución: 1280 × 720


FPS: 30


Frames: 2172


Duración: 72,40 s


También se desarrolló extract_frame.py  para extraer imágenes individuales y


trabajar con frames concretos.


Esto permitió pasar de analizar el video como un objeto abstracto a trabajar sobre


imágenes controladas.


6. Aislamiento de la cancha


Se desarrolló select_field.py  para seleccionar manualmente la región útil.


ROI actual:


X = 183


Y = 48


Ancho = 913


Alto = 623


Esto fue fundamental porque eliminó gran parte de la interfaz de FM24 del


problema de detección.


La cancha pasó a ser el espacio principal de análisis.


7. Detección de jugadores


Se desarrolló un detector basado en HoughCircles.


---

## Página 29 (hoja física 213, columna derecha)


El tamaño observado de los tokens fue:


Radio mínimo: 7 px


Radio máximo: 8 px


Media:        7,26 px


Mediana:      7 px


En la muestra inicial:


22 detecciones válidas


0 falsos positivos


0 duplicados


Se añadió además un segundo detector sensible para recuperar fichas difíciles.


Esto resolvió el caso particular del jugador parcialmente cubierto por elementos


gráficos.


8. Detección específica de arqueros


Los arqueros presentan características visuales diferentes a los jugadores de campo.


Se desarrolló un detector específico utilizando:


CLAHE;


Hough;


restricciones espaciales sobre las áreas de penal.


Resultado inicial:


2 arqueros recuperados


0 falsos positivos


Este detector funciona como componente independiente, pero todavía debe


demostrar estabilidad temporal durante secuencias largas.


9. Clasificación de equipos


Se analizaron los colores mediante HSV.


Se observaron patrones diferentes para:


Racing;


---

## Página 30 (hoja física 214, columna izquierda)


Rival;


arqueros.


Se construyó una primera clasificación por reglas:


S < 30


→ Arquero


V > 180


→ Rival


V <= 180 y S >= 50


→ Racing


En el frame inicial se obtuvo:


10 jugadores de campo Racing


10 jugadores de campo Rival


2 arqueros


También se evitó asumir que el lado de la cancha define permanentemente al


equipo, porque durante un partido los equipos cambian de lado.


10. Extracción de dorsales


En lugar de utilizar OCR genérico como primera solución, se diseñó un extractor


específico para las fichas de FM24.


El proceso pasó por varias iteraciones hasta alcanzar una máscara suficientemente


estable:


recorte


→ reescalado


→ HSV


→ máscara interior


→ componentes


→ separación de dígitos


La versión final de extracción permitió trabajar con los 22 tokens de la muestra.


Se identificaron:


18 dorsales de un dígito


4 dorsales de dos dígitos


---

## Página 31 (hoja física 214, columna derecha)


26 dígitos en total


Esto estableció la base para construir reconocimiento por template.


11. Banco de templates


Se construyó un banco curado de:


21 templates


La selección fue deliberada.


Se descartaron muestras contaminadas o deformadas y se conservaron únicamente


ejemplos suficientemente limpios.


Se recuperó específicamente una muestra confiable del 0 , descartando otra que


presentaba contaminación.


12. Reconocimiento de dorsales


El sistema utiliza:


cv2.matchTemplate


TM_CCOEFF_NORMED


y calcula:


winner score


second-best score


gap


El gap  permite conocer cuánto mejor es la mejor coincidencia respecto de la


segunda.


Esto permite distinguir:


coincidencia clara


de:


coincidencia ambigua


Benchmark actual:


---

## Página 32 (hoja física 215, columna izquierda)


23 / 26 correctos


88,46 % de exactitud


Los errores quedaron concentrados en muestras visualmente degradadas.


La decisión metodológica fue no seguir perfeccionando indefinidamente esta capa


antes de construir el tracking.


13. Modelo de identidad


Se estableció una distinción arquitectónica fundamental:


token_id


representa una detección concreta dentro de un frame.


track_id


representa la identidad persistente del jugador a lo largo del tiempo.


Esta separación permite que el detector entregue identificadores diferentes sin


destruir la identidad temporal.


Esto es una de las bases estructurales del proyecto.


14. JSON estructurado


Se creó build_match_json.py  para transformar las detecciones en una


representación estructurada.


Cada jugador puede contener:


identity


state


detection


Dentro de identity :


team


role


number


confidence


---

## Página 33 (hoja física 215, columna derecha)


Dentro de state :


frame


timestamp


x


y


radius


dx


dy


distance


Esto permite pasar de imágenes a datos que posteriormente pueden ser analizados


matemáticamente.


15. Primer tracking


Se implementó un tracker basado en:


Hungarian Algorithm


linear_sum_assignment


gating por distancia


El sistema separa las asociaciones en:


Racing


Rival


GK


Parámetros actuales:


MAX_DISTANCE = 15 px


LARGE_COST = 10000


La primera prueba fue:


frame 0 → frame 1


Resultado:


22 tracks


22 asociaciones


Distancia media:


≈ 0,31 px


---

## Página 34 (hoja física 216, columna izquierda)


Distancia máxima:


≈ 2,83 px


El resultado validó el mecanismo básico.


16. Primera prueba temporal


Después del primer paso se realizó una prueba más larga.


Se procesaron:


frame_0000


hasta


frame_0030


Esto significa:


31 frames observados


30 transiciones


1 segundo de video


La distribución fue:


22 matches → 12 transiciones


21 matches → 13 transiciones


20 matches →  5 transiciones


Esto demuestra que la asociación funciona durante una ventana corta, pero también


muestra que existen transiciones en las que uno o dos tracks no se asocian.


Todavía no se determinó cuál es exactamente la causa.


17. Qué está terminado


Dentro del alcance actual, las siguientes piezas pueden considerarse construidas y


funcionales:


Componente
Estado


Entorno de desarrollo
✅


Lectura de video
✅


---

## Página 35 (hoja física 216, columna derecha)


Extracción de frames
✅


ROI de cancha
✅


Detección general
✅


Recuperación de detecciones difíciles
✅


Detector específico de arqueros
✅ inicial


Clasificación por equipo
✅ inicial


Extracción de dorsales
✅ inicial


Banco de templates
✅


Reconocimiento de dígitos
✅ inicial


Modelo token_id  / track_id
✅


JSON estructurado
✅


Hungarian + gating
✅


Tracking frame a frame
✅ inicial


Visualización de trayectorias
✅ inicial


La palabra importante en algunos casos es inicial. Significa que el componente existe


y funciona, pero todavía no se considera suficientemente validado para cualquier


situación de un partido completo.


18. Qué NO está terminado


Todavía falta construir y validar una cantidad importante de trabajo.


Tracking robusto


Falta:


auditar las pérdidas de asociación;


resolver las causas demostradas;


validar o ajustar el gating;


---

## Página 36 (hoja física 217, columna izquierda)


determinar si realmente hace falta predicción;


implementar coast mode  si las pruebas lo justifican;


manejar oclusiones;


recuperar tracks después de pérdidas prolongadas;


probar durante ventanas mucho mayores;


validar un partido completo.


Identificación robusta


Falta mejorar:


reconocimiento de dorsales difíciles;


confianza de identidad;


reidentificación después de oclusiones;


situaciones donde el dorsal no pueda leerse.


Coordenadas del campo


Actualmente trabajamos con píxeles.


Falta:


definir coordenadas normalizadas del campo;


mapear posiciones a una representación consistente;


establecer una relación con dimensiones reales;


resolver posibles distorsiones de perspectiva.


Eventos


Todavía falta detectar automáticamente:


movimientos relevantes;


cambios de posición;


agrupamientos;


separación de líneas;


recuperaciones;


transiciones;


situaciones de presión;


cambios estructurales.


Análisis táctico


Falta construir el sistema capaz de inferir:


---

## Página 37 (hoja física 217, columna derecha)


formación;


estructura ofensiva;


estructura defensiva;


roles espaciales;


altura del bloque;


amplitud;


profundidad;


compactación;


presión;


ocupación de espacios;


cambios tácticos.


Producto final


También falta:


interfaz;


configuración de análisis;


procesamiento de partidos completos;


visualizaciones;


informes;


almacenamiento organizado;


manejo de errores;


documentación de usuario.


19. Qué significa realmente "100 %"


El 100 % del proyecto no significa simplemente:


“el programa detecta jugadores”.


El sistema estará completo cuando exista un flujo integrado:


video


↓


detección


↓


identificación


↓


tracking estable


↓


---

## Página 38 (hoja física 218, columna izquierda)


coordenadas normalizadas


 ↓


eventos


 ↓


estructura táctica


 ↓


análisis


 ↓


informe final


Además, una versión completa debe poder procesar un partido largo de forma


reproducible, no solamente una captura corta.


Por lo tanto, el 100 % requiere tanto funcionalidad como robustez, validación y


usabilidad.


20. Criterios de finalización del proyecto


Para declarar FM24Analyzer terminado, cada capa debería cumplir cuatro


condiciones:


1. Funcionalidad


La función existe y produce el resultado esperado.


2. Validación


Fue probada en una cantidad suficiente de datos.


3. Robustez


No depende de una única captura favorable.


4. Integración


Forma parte del pipeline completo.


Una herramienta que funciona perfectamente durante 30 frames pero falla al


procesar un partido de 90 minutos no se considera terminada.


21. Roadmap completo


---

## Página 39 (hoja física 218, columna derecha)


Fase 0. Fundaciones


Objetivo: establecer entorno y estructura.


Python


OpenCV


dependencias


estructura de carpetas


video de prueba


Estado: completado.


Fase 1. Percepción visual básica


Objetivo: detectar correctamente las fichas.


Tareas


ROI;


Hough general;


detector sensible;


detector de arqueros;


eliminación de falsos positivos;


combinación de detectores.


Estado: funcional inicial.


Criterio de salida


Detectar de manera estable los 22 jugadores en una variedad razonable de frames.


Fase 2. Clasificación e identificación


Objetivo: saber quién es cada ficha.


Tareas


clasificación Racing/Rival/GK;


extracción de dorsales;


templates;


reconocimiento;


confidence;


---

## Página 40 (hoja física 219, columna izquierda)


manejo de casos ambiguos.


Estado: funcional inicial.


Criterio de salida


Identidad suficientemente estable para usarla como entrada del tracker.


Fase 3. Tracking robusto


Objetivo: mantener la identidad durante todo el video.


Tareas inmediatas


1. Auditar tracks sin match.


2. Identificar detecciones libres.


3. Identificar bloque afectado.


4. Determinar causa.


5. Corregir solamente esa causa.


6. Repetir benchmark.


Después


100 transiciones;


ventanas largas;


coast mode si hace falta;


predicción por velocidad si hace falta;


manejo de oclusiones;


reidentificación.


Estado: etapa actual.


Criterio de salida


Tracking estable durante secuencias largas y, finalmente, durante un partido


completo.


Fase 4. Reconstrucción espacial


Objetivo: convertir píxeles en posiciones útiles para análisis futbolístico.


Tareas


---

## Página 41 (hoja física 219, columna derecha)


coordenadas normalizadas;


referencia del campo;


calibración;


orientación;


zonas del terreno;


coordenadas comparables entre partidos.


Estado: pendiente.


Criterio de salida


Cada jugador debe disponer de una posición consistente dentro de un sistema


espacial del campo.


Fase 5. Trayectorias y movimiento


Objetivo: transformar posiciones en comportamiento temporal.


Tareas


trayectoria individual;


velocidad aproximada;


aceleración aproximada;


distancia;


ocupación espacial;


zonas frecuentes;


cambios de posición.


Estado: pendiente.


Criterio de salida


Poder describir el movimiento de cada jugador durante cualquier segmento del


partido.


Fase 6. Detección de eventos


Objetivo: identificar cambios significativos del juego.


Tareas


---

## Página 42 (hoja física 220, columna izquierda)


cambios bruscos de posición;


avance de líneas;


retrocesos;


presión;


pérdida/recuperación;


transiciones;


agrupamientos;


cambios estructurales;


secuencias repetidas.


Estado: pendiente.


Criterio de salida


El sistema debe poder dividir el partido en segmentos relevantes en lugar de tratarlo


como una secuencia homogénea de frames.


Fase 7. Análisis táctico


Objetivo: transformar datos de movimiento en conceptos futbolísticos.


Tareas


detección de formación;


estructura con pelota;


estructura sin pelota;


líneas;


bloque;


amplitud;


profundidad;


compactación;


ocupación de espacios;


comportamiento individual;


relaciones entre jugadores;


cambios de sistema;


presión;


transiciones.


Estado: pendiente.


Criterio de salida


---

## Página 43 (hoja física 220, columna derecha)


Poder describir de forma reproducible estructuras y comportamientos tácticos


observables.


Fase 8. Motor de análisis


Objetivo: convertir eventos tácticos en conclusiones estructuradas.


Tareas


comparación entre períodos;


comparación entre equipos;


comparación entre partidos;


detección de patrones;


métricas agregadas;


indicadores tácticos;


generación de conclusiones.


Estado: pendiente.


Criterio de salida


Generar un análisis estructurado a partir de los datos procesados.


Fase 9. Visualización


Objetivo: hacer interpretable el resultado.


Tareas


mapa de posiciones;


trayectorias;


heatmaps;


líneas de equipo;


zonas ocupadas;


eventos sobre timeline;


comparativas;


reproducción sincronizada.


Estado: pendiente.


Criterio de salida


---

## Página 44 (hoja física 221, columna izquierda)


Un usuario debe poder entender visualmente qué ocurrió.


Fase 10. Informe automático


Objetivo: generar un informe final del partido.


El sistema debería poder producir:


Resumen del partido


↓


Formaciones


↓


Estructura ofensiva


↓


Estructura defensiva


↓


Presión


↓


Transiciones


↓


Cambios tácticos


↓


Comportamiento individual


↓


Conclusiones


Estado: pendiente.


Fase 11. Interfaz y producto


Objetivo: convertir el prototipo en una herramienta utilizable.


Tareas


cargar video;


seleccionar parámetros;


iniciar análisis;


mostrar progreso;


revisar resultados;


visualizar partido;


exportar informe;


---

## Página 45 (hoja física 221, columna derecha)


manejar errores;


conservar sesiones.


Estado: pendiente.


Fase 12. Validación final


Objetivo: demostrar que el sistema funciona fuera de la muestra original.


Tareas


diferentes partidos;


distintos equipos;


cambios de campo;


distintos niveles de movimiento;


oclusiones;


cambios de cámara;


diferentes interfaces;


diferentes situaciones de partido.


Estado: pendiente.


Criterio de salida


El sistema debe funcionar de forma reproducible más allá del video utilizado para


desarrollar el prototipo.


22. Roadmap resumido


[✅] ENTORNO


     ↓


[✅] VIDEO / ROI


     ↓


[✅] DETECCIÓN INICIAL


     ↓


[✅] CLASIFICACIÓN


     ↓


[✅] DORSALES


     ↓


[✅] IDENTIDAD


     ↓


---

## Página 46 (hoja física 222, columna izquierda)


[🟡] TRACKING ROBUSTO


     ↓


[⬜] COORDENADAS DEL CAMPO


     ↓


[⬜] TRAYECTORIAS


     ↓


[⬜] EVENTOS


     ↓


[⬜] ANÁLISIS TÁCTICO


     ↓


[⬜] MOTOR DE ANÁLISIS


     ↓


[⬜] VISUALIZACIÓN


     ↓


[⬜] INFORME AUTOMÁTICO


     ↓


[⬜] INTERFAZ


     ↓


[⬜] VALIDACIÓN MULTIPARTIDO


     ↓


[100 %] FM24Analyzer


23. Prioridad real de trabajo


No todas las tareas pendientes tienen la misma prioridad.


Prioridad crítica


Tracking robusto.


Sin esto no hay trayectorias confiables.


Prioridad alta


Coordenadas espaciales y trayectorias.


Son la base de todo análisis táctico.


Prioridad media


Eventos y estructuras tácticas.


Dependen de las capas anteriores.


---

## Página 47 (hoja física 222, columna derecha)


Prioridad posterior


Visualización, informes e interfaz.


Son importantes para convertir el sistema en producto, pero no solucionan


problemas de percepción.


Prioridad condicional


Deep learning, YOLO, modelos avanzados, IA generativa.


Solo deben incorporarse cuando una limitación concreta demuestre que son


necesarios.


24. Deuda técnica actual


El proyecto todavía tiene varias cuestiones pendientes que no son funcionalidades


nuevas, sino consolidación.


Código


Los scripts todavía contienen lógica experimental repetida.


Ejemplo:


detección


clasificación


tracking


aparecen parcialmente duplicados entre distintos scripts.


Más adelante conviene separar:


vision_detector.py


classifier.py


digit_reader.py


tracker.py


models.py


pipeline.py


Configuración


Parámetros como:


---

## Página 48 (hoja física 223, columna izquierda)


ROI


Hough


HSV


gating


deberían terminar centralizados y configurables.


Tests


Actualmente existe principalmente validación manual y benchmarks específicos.


Será necesario agregar:


tests unitarios;


casos de regresión;


datasets de referencia;


benchmarks repetibles.


Logs


Los scripts deberán evolucionar hacia un sistema de logging más estructurado.


Datos


Conviene definir un formato estable para:


detección;


identidad;


trayectoria;


eventos;


análisis.


25. Riesgos técnicos principales


Los principales riesgos del proyecto son:


1. Detección inestable


Puede generar errores aguas arriba.


2. Oclusiones


Un jugador puede quedar parcialmente cubierto.


---

## Página 49 (hoja física 223, columna derecha)


3. Cambios visuales


La interfaz puede variar entre situaciones.


4. Identidad incorrecta


Un error de dorsal puede contaminar el tracking.


5. Pérdida de asociación


Puede romper una trayectoria.


6. Interpretación excesiva


Un patrón geométrico no necesariamente implica automáticamente una intención


táctica.


7. Generalización


Un sistema ajustado al video de prueba puede no funcionar igual en otros partidos.


8. Complejidad creciente


El análisis táctico será considerablemente más complejo que detectar tokens.


Por eso la metodología incremental no es solamente una preferencia. Es una forma


de controlar estos riesgos.


26. Criterio de calidad del producto final


El sistema final no debería evaluarse únicamente por una única cifra.


La calidad deberá observarse en varias dimensiones:


Percepción


→ ¿Detecta correctamente?


Identidad


→ ¿Sabe quién es quién?


Tracking


→ ¿Mantiene identidades?


Espacio


---

## Página 50 (hoja física 224, columna izquierda)


→ ¿Ubica correctamente?


Eventos


→ ¿Detecta cambios significativos?


Táctica


→ ¿Describe estructuras observables?


Generalización


→ ¿Funciona fuera del video de desarrollo?


Usabilidad


→ ¿Una persona puede utilizarlo?


Solo cuando todas estas capas sean suficientemente sólidas tendrá sentido hablar de


un sistema terminado.


27. Definición de éxito del proyecto


FM24Analyzer puede considerarse terminado cuando sea capaz de recibir:


un video de un partido


y producir automáticamente:


1. jugadores detectados


2. identidades


3. posiciones


4. trayectorias


5. eventos


6. estructuras tácticas


7. análisis


8. visualizaciones


9. informe final


de forma reproducible y con un nivel de error conocido.


Ese último punto es importante.


El objetivo no es que el sistema sea mágicamente perfecto. El objetivo es que sus


resultados sean suficientemente confiables, medibles y explicables como para


utilizarlos.


---

## Página 51 (hoja física 224, columna derecha)


28. Estado global del proyecto


La situación actual puede resumirse así:


PERCEPCIÓN


██████████████████░░  ~90 %


IDENTIFICACIÓN


████████████████░░░░  ~80 %


TRACKING


████████░░░░░░░░░░░░  ~40 %


ESPACIO


██░░░░░░░░░░░░░░░░░░  ~10 %


TRAYECTORIAS


██░░░░░░░░░░░░░░░░░░  ~10 %


EVENTOS


░░░░░░░░░░░░░░░░░░░░   ~0 %


ANÁLISIS TÁCTICO


░░░░░░░░░░░░░░░░░░░░   ~0 %


PRODUCTO FINAL


░░░░░░░░░░░░░░░░░░░░   ~0 %


Estos porcentajes son estimaciones de avance por capa, no métricas científicas de


calidad ni porcentajes exactos de código completado.


La mayor parte del trabajo futuro se encuentra en las capas superiores, no en la


detección básica.


29. Próximo paso inmediato


El próximo trabajo concreto es uno solo:


Auditar las pérdidas de tracking


Para todas las transiciones con:


matches < 22


---

## Página 52 (hoja física 225, columna izquierda)


hay que registrar:


transición


track_id perdido


equipo


dorsal


rol


detección libre


distancia al candidato


bloque afectado


El objetivo es responder:


¿Qué está fallando realmente?


Solo después se decidirá si corresponde implementar:


coast mode


predicción


velocidad


reidentificación


ajuste de gating


mejora de detección


Esto mantiene exactamente la metodología que se utilizó durante todo el proyecto:


No optimizar lo que todavía no entendemos.


30. Conclusión general


FM24Analyzer dejó de ser una idea y pasó a ser un prototipo técnico funcional.


Hoy existe una cadena real que transforma:


video


en:


detecciones


→ equipos


→ dorsales


→ identidades


---

## Página 53 (hoja física 225, columna derecha)


→ tracking


→ JSON


Se resolvieron los problemas fundamentales de la primera etapa y se construyeron


las herramientas necesarias para continuar.


El proyecto todavía está lejos del 100 %, pero ahora la distancia restante está


estructurada y puede dividirse en etapas concretas.


El núcleo pendiente es pasar de:


“sé dónde está cada ficha”


a:


“sé quién es, dónde está, cómo se mueve, qué está haciendo el equipo y qué


patrón táctico representa ese comportamiento”.


El roadmap completo es, por lo tanto:


VIDEO


↓


PERCEPCIÓN


↓


IDENTIDAD


↓


TRACKING ROBUSTO


↓


CALIBRACIÓN ESPACIAL


↓


TRAYECTORIAS


↓


EVENTOS


↓


ESTRUCTURA TÁCTICA


↓


ANÁLISIS


↓


VISUALIZACIÓN


↓


INFORME


↓


INTERFAZ


↓


VALIDACIÓN MULTIPARTIDO


---

## Página 54 (hoja física 226, columna izquierda)


 ↓


FM24Analyzer 100 %


Y la regla que sigue gobernando todo el desarrollo continúa siendo:


Primero entender. Después medir. Luego decidir. Finalmente implementar.


La cosa mejor. Vamos a hacer como si fuera una aplicación 
o un software que hay que entregar en un desarrollo.


Escucha bien. De un software esto es exactamente lo que 
le entrego y los pasos que sigo de principio a fin. Primero,


SRS, especificación de requerimientos de software. Es un 
documento bastante extenso en donde se explica qué


debe hacer la aplicación y cómo debe comportarse. Fácil. 
La SRS tiene varias capas, por ejemplo, el alcance del


proyecto, los objetivos del proyecto, la introducción al 
dominio del problema del proyecto, las necesidades del


negocio, los objetivos del negocio, la descripción de los


Mostrar más


Ha pensado durante 9s


Ahora el proyecto queda planteado como corresponde a un desarrollo profesional para un


cliente. El trabajo técnico que ya hicimos no se pierde: se clasifica como una etapa previa


de descubrimiento y prueba de concepto, y a partir de acá se formaliza dentro del ciclo


de desarrollo.


FM24Analyzer - Plan Maestro de Desarrollo, Entrega y Mant…


FM24Analyzer


Plan maestro de desarrollo, entrega y mantenimiento


Proyecto: FM24Analyzer


Tipo: Software de análisis de partidos de Football Manager 24 mediante visión por


computadora


Modalidad: Desarrollo incremental con Scrum + Kanban


---

## Página 55 (hoja física 226, columna derecha)


Objetivo: construir, entregar y mantener una aplicación capaz de analizar


grabaciones de partidos y producir información estructurada y análisis táctico.


1. Propósito del documento


Este documento define el ciclo completo de desarrollo de FM24Analyzer como un


producto de software profesional.


No se limita a describir la tecnología utilizada. Define:


qué documentación debe existir;


cómo se capturan y formalizan los requerimientos;


cómo se organiza el backlog;


cómo se planifican los sprints;


cómo se desarrolla y prueba cada incremento;


cómo se define el MVP;


qué se entrega al cliente;


qué constituye el 100 % del proyecto;


y cómo continúa el producto después de la entrega mediante mantenimiento y


soporte.


El objetivo es que FM24Analyzer pueda desarrollarse con un proceso reproducible,


trazable y profesional, y no simplemente como una colección de scripts que funciona


en una computadora concreta.


2. Modelo profesional de trabajo


El ciclo completo del producto se divide en dos grandes etapas.


ETAPA 1


DESARROLLO Y ENTREGA


       ↓


ETAPA 2


MANTENIMIENTO Y SOPORTE


La primera etapa comprende:


SRS


↓


BACKLOG / TRELLO


↓


---

## Página 56 (hoja física 227, columna izquierda)


PLANIFICACIÓN DE SPRINTS


 ↓


DESARROLLO


 ↓


TESTING


 ↓


ENTREGAS INCREMENTALES


 ↓


MVP


 ↓


ENTREGA FINAL


 ↓


CÓDIGO FUENTE + DOCUMENTACIÓN


La segunda comprende:


MANTENIMIENTO


 ↓


CORRECCIÓN DE ERRORES


 ↓


SOPORTE


 ↓


NUEVOS REQUERIMIENTOS


 ↓


NUEVAS VERSIONES


Este modelo permite separar claramente el desarrollo contratado de la etapa


posterior de soporte y evolución.


3. Situación actual de FM24Analyzer


Hasta ahora se realizó una etapa de exploración técnica que debe considerarse


prototipado o prueba de concepto, no todavía desarrollo formal basado en una SRS


aprobada.


Durante esta etapa se investigó si el problema podía resolverse técnicamente y qué


herramientas serían necesarias.


Ese trabajo produjo resultados concretos:


Video


 ↓


ROI


---

## Página 57 (hoja física 227, columna derecha)


↓


detección de fichas


↓


clasificación


↓


dorsales


↓


identidades


↓


tracking inicial


↓


JSON


Entre los resultados obtenidos:


22 jugadores detectados en la muestra inicial


0 falsos positivos


0 duplicados


2 arqueros detectados


26 dígitos analizados


21 templates


23/26 dígitos reconocidos


88,46 % de exactitud en el benchmark de dorsales


22/22 asociaciones en la primera transición


31 frames observados


30 transiciones de tracking


Esta etapa fue técnicamente valiosa porque permitió reducir incertidumbre antes de


formalizar el producto.


Sin embargo, no debe confundirse un prototipo funcional con una aplicación


terminada.


El siguiente paso profesional es formalizar el producto mediante una SRS.


4. ETAPA 1 - Desarrollo y entrega


4.1. Paso 1: SRS


La Software Requirements Specification (SRS) es el documento principal del


proyecto.


Su función es definir qué debe hacer el software antes de construirlo formalmente.


---

## Página 58 (hoja física 228, columna izquierda)


La SRS funciona como los planos de la aplicación.


El principio fundamental es:


No desarrollar sobre requisitos ambiguos.


Antes de comenzar cada gran bloque de desarrollo debe existir una especificación


suficientemente precisa de lo que se espera obtener.


5. Contenido de la SRS de FM24Analyzer


La SRS deberá abarcar, como mínimo:


5.1. Introducción


propósito del documento;


propósito del sistema;


público destinatario;


definiciones;


acrónimos;


referencias;


descripción general del producto.


5.2. Alcance del proyecto


Debe definir explícitamente:


Incluido


Qué funcionalidades forman parte de FM24Analyzer.


Excluido


Qué funcionalidades no forman parte de la versión contratada.


Esto evita que el proyecto crezca indefinidamente por incorporación informal de


necesidades.


5.3. Objetivos del proyecto


Deben establecerse objetivos verificables.


---

## Página 59 (hoja física 228, columna derecha)


Por ejemplo:


procesar videos de partidos;


detectar jugadores;


identificar jugadores;


mantener identidades;


reconstruir posiciones;


identificar eventos;


producir análisis táctico;


generar un informe final.


Cada objetivo debe tener posteriormente una forma de validación.


5.4. Introducción al dominio del problema


La SRS debe explicar el dominio futbolístico y tecnológico en el que trabaja el


sistema.


Debe documentarse:


funcionamiento visual de FM24;


representación de jugadores;


equipos;


arqueros;


dorsales;


cancha;


cambios de lado;


movimiento;


conceptos tácticos relevantes;


limitaciones de la información disponible en video.


Esto permite que el equipo de desarrollo y el cliente trabajen con el mismo modelo


conceptual.


6. Necesidades del negocio


La SRS debe explicar por qué existe el sistema.


No solamente:


---

## Página 60 (hoja física 229, columna izquierda)


“Detectar jugadores.”


Sino:


“Transformar una grabación de un partido en información estructurada que


permita analizar automáticamente el comportamiento espacial y táctico de los


equipos.”


Las necesidades de negocio determinan posteriormente los objetivos y


funcionalidades del sistema.


7. Objetivos de negocio


Ejemplos para FM24Analyzer:


reducir el trabajo manual de análisis;


obtener información objetiva a partir de video;


conservar datos estructurados de los partidos;


permitir análisis posterior;


generar informes reproducibles;


facilitar comparación entre partidos;


disponer de una herramienta extensible.


Estos objetivos no son necesariamente funcionalidades. Son el motivo por el que las


funcionalidades existen.


8. Procesos de negocio


La SRS debe modelar qué ocurre desde que un usuario utiliza el sistema.


Ejemplo general:


Usuario


 ↓


Carga video


 ↓


Configura análisis


 ↓


Inicia procesamiento


 ↓


---

## Página 61 (hoja física 229, columna derecha)


Sistema procesa video


↓


Detecta jugadores


↓


Identifica jugadores


↓


Construye trayectorias


↓


Detecta eventos


↓


Analiza estructura


↓


Genera resultados


↓


Usuario revisa


↓


Exporta informe


Este flujo es el proceso de negocio que posteriormente se transforma en


funcionalidades concretas.


9. Casos de uso del negocio


Los casos de uso de negocio describen las acciones relevantes desde la perspectiva


del proceso.


Ejemplos:


CU-B01 Analizar partido


CU-B02 Consultar resultado del análisis


CU-B03 Revisar trayectoria de jugador


CU-B04 Revisar estructura táctica


CU-B05 Comparar segmentos


CU-B06 Generar informe


No necesariamente representan todavía botones o ventanas.


Representan procesos que tienen valor para el usuario.


10. Casos de uso del sistema


---

## Página 62 (hoja física 230, columna izquierda)


Después se especifica cómo el software implementa esos procesos.


Ejemplos:


CU-S01 Cargar video


CU-S02 Validar formato


CU-S03 Seleccionar parámetros


CU-S04 Detectar jugadores


CU-S05 Clasificar equipos


CU-S06 Identificar dorsales


CU-S07 Crear tracks


CU-S08 Mantener identidad


CU-S09 Generar trayectorias


CU-S10 Detectar eventos


CU-S11 Detectar estructuras


CU-S12 Generar análisis


CU-S13 Exportar informe


Cada caso de uso debe incluir condiciones, flujo principal, alternativas, errores y


resultado esperado.


11. Diagramas


La SRS debe incorporar los diagramas que permitan entender el sistema.


Como mínimo:


diagrama de actores;


diagrama general de casos de uso;


diagramas de casos de uso relevantes;


diagramas de procesos;


diagramas de arquitectura cuando corresponda;


modelo de datos;


diagramas adicionales necesarios para reducir ambigüedad.


El objetivo no es llenar páginas por decoración. Cada diagrama debe aclarar una


parte del sistema.


12. Requisitos funcionales


Los requisitos funcionales indican qué debe hacer el sistema.


---

## Página 63 (hoja física 230, columna derecha)


Deben escribirse de manera inequívoca.


Ejemplo:


RF-001: El sistema deberá permitir al usuario cargar un archivo de video


compatible para iniciar un análisis.


RF-002: El sistema deberá identificar los jugadores detectados y asignarles un


identificador persistente durante el análisis.


RF-003: El sistema deberá almacenar las posiciones detectadas de cada jugador


asociadas al instante temporal correspondiente.


Cada requisito debe tener:


identificador;


descripción;


prioridad;


fuente;


criterio de aceptación;


dependencia, cuando corresponda.


13. Requisitos no funcionales


Los requisitos no funcionales especifican cómo debe comportarse el software.


Para FM24Analyzer pueden incluir:


Rendimiento


Tiempo máximo o esperado de procesamiento.


Disponibilidad


Condiciones en las que el sistema debe poder ejecutarse.


Seguridad


Protección de archivos y datos.


Usabilidad


---

## Página 64 (hoja física 231, columna izquierda)


Facilidad para cargar y analizar un partido.


Mantenibilidad


Capacidad de modificar componentes sin afectar todo el sistema.


Escalabilidad


Capacidad de procesar videos más largos o ampliar funcionalidades.


Compatibilidad


Formatos de video y sistemas operativos admitidos.


Trazabilidad


Conservación de logs y resultados.


Calidad


Precisión mínima aceptable para detección, identificación y tracking.


La SRS deberá convertir estos conceptos en valores verificables cuando corresponda.


14. Criterio fundamental de la SRS


La SRS debe evitar expresiones ambiguas como:


"rápido"


"preciso"


"fácil"


"bueno"


"inteligente"


"que detecte bien"


Deben transformarse en criterios medibles.


Por ejemplo:


Ambiguo:


"El sistema deberá detectar correctamente a los jugadores."


Especificado:


"El sistema deberá detectar al menos X de los Y jugadores


en las condiciones definidas en el conjunto de validación."


---

## Página 65 (hoja física 231, columna derecha)


El valor exacto de X e Y deberá definirse durante la especificación.


La SRS determina los criterios que después permiten aceptar o rechazar un sprint.


15. Paso 2: Trello, Backlog y metodología ágil


Una vez definidos los requisitos, se construye el backlog del proyecto.


La metodología adoptada será:


Scrum + Kanban.


Scrum aporta:


sprints;


planificación;


entregables incrementales;


objetivos de sprint;


revisión;


retrospectiva.


Kanban aporta:


flujo visual;


estados de tareas;


control del trabajo en curso;


seguimiento continuo.


16. Backlog


El backlog contiene todo lo que debe hacerse para cumplir la SRS.


Puede organizarse mediante:


Épicas


↓


Historias de usuario


↓


Tareas


↓


Subtareas


---

## Página 66 (hoja física 232, columna izquierda)


Ejemplo:


ÉPICA:


Tracking


Historia:


Como analista quiero que cada jugador conserve


su identidad durante el partido.


Tareas:


- implementar asociación;


- configurar gating;


- registrar pérdidas;


- probar 100 frames;


- validar oclusiones;


- documentar resultado.


El backlog debe ser el vínculo entre la SRS y el código.


17. Flujo de Trello


El tablero deberá permitir ver claramente el estado de cada trabajo.


Una estructura posible:


BACKLOG


   ↓


SPRINT PLANIFICADO


   ↓


EN CURSO


   ↓


TESTING


   ↓


TERMINADO / VALIDADO


   ↓


ENTREGADO


La regla fundamental es:


Una tarea no está terminada porque el código compila. Está terminada cuando


cumple el requisito y fue testeada.


---

## Página 67 (hoja física 232, columna derecha)


18. Sprints


El proyecto se divide en sprints.


Cada sprint debe tener:


objetivo;


tareas;


criterios de aceptación;


resultado esperado;


pruebas;


entregable.


Cada sprint representa un incremento real del producto.


No es simplemente una semana de programación.


19. Roadmap de Sprints de FM24Analyzer


La división definitiva dependerá de la SRS y del backlog real, pero el proyecto puede


organizarse inicialmente así.


Sprint 0 - Formalización


Objetivo: convertir el prototipo actual en proyecto formal.


Entregables:


SRS aprobada;


backlog;


arquitectura inicial;


repositorio;


criterios de aceptación;


estructura del proyecto.


Sprint 1 - Ingesta y preparación


Objetivo: recibir y preparar correctamente los videos.


Incluye:


carga de video;


---

## Página 68 (hoja física 233, columna izquierda)


validación;


lectura de metadata;


extracción de frames;


ROI;


manejo de errores.


Entregable: pipeline de entrada funcional.


Sprint 2 - Detección


Objetivo: detectar jugadores de manera estable.


Incluye:


Hough;


detección sensible;


detector GK;


filtrado;


validación.


Entregable: detección de jugadores.


Sprint 3 - Identificación


Objetivo: determinar equipo, rol y dorsal.


Incluye:


clasificación;


extracción;


templates;


reconocimiento;


confidence.


Entregable: jugadores identificables.


Sprint 4 - Tracking


Objetivo: mantener identidades a través del tiempo.


---

## Página 69 (hoja física 233, columna derecha)


Incluye:


Hungarian;


gating;


pérdida de detección;


recuperación;


oclusiones;


validación prolongada.


Entregable: tracking robusto.


Este es el sprint en el que actualmente se encuentra el prototipo técnico.


Sprint 5 - Reconstrucción espacial


Objetivo: transformar posiciones de imagen en posiciones utilizables para análisis


futbolístico.


Incluye:


coordenadas normalizadas;


orientación;


zonas;


calibración;


referencias del campo.


Entregable: mapa espacial consistente.


Sprint 6 - Trayectorias y movimiento


Objetivo: transformar posiciones en comportamiento temporal.


Incluye:


trayectoria;


velocidad;


desplazamiento;


ocupación;


zonas frecuentes.


Entregable: análisis individual de movimiento.


---

## Página 70 (hoja física 234, columna izquierda)


Sprint 7 - Eventos


Objetivo: detectar cambios relevantes.


Incluye:


presión;


transición;


recuperación;


pérdida;


movimientos estructurales;


cambios de posición.


Entregable: timeline de eventos.


Sprint 8 - Análisis táctico


Objetivo: interpretar las estructuras del equipo.


Incluye:


formación;


líneas;


bloque;


amplitud;


profundidad;


compactación;


ocupación;


estructuras con y sin pelota.


Entregable: análisis táctico estructurado.


Sprint 9 - Motor de análisis e informes


Objetivo: convertir datos y eventos en resultados útiles.


Incluye:


métricas;


comparación;


---

## Página 71 (hoja física 234, columna derecha)


patrones;


conclusiones;


informe automático.


Entregable: informe táctico.


Sprint 10 - Visualización


Objetivo: hacer comprensible el análisis.


Incluye:


mapa;


trayectorias;


heatmaps;


timeline;


estructuras;


reproducción.


Entregable: módulo visual.


Sprint 11 - Aplicación


Objetivo: convertir el sistema técnico en software utilizable.


Incluye:


interfaz;


configuración;


progreso;


resultados;


exportación;


manejo de errores.


Entregable: aplicación funcional.


Sprint 12 - Hardening y validación


Objetivo: preparar el producto para entrega.


---

## Página 72 (hoja física 235, columna izquierda)


Incluye:


pruebas;


regresión;


rendimiento;


errores;


documentación;


validación multiprueba;


empaquetado.


Entregable: release candidata.


20. Paso 3: Desarrollo


El desarrollo se realiza sprint por sprint.


El principio es:


SRS


 ↓


Backlog


 ↓


Sprint


 ↓


Desarrollo


 ↓


Testing


 ↓


Aceptación


 ↓


Entrega


No se debe construir todo el software y probarlo al final.


Cada sprint debe producir un resultado verificable.


21. Testing


El testing debe existir en varios niveles.


Test unitario


---

## Página 73 (hoja física 235, columna derecha)


Comprueba componentes individuales.


Ejemplo:


¿La función calcula correctamente la distancia?


Test de integración


Comprueba que varios componentes trabajen juntos.


Ejemplo:


detección


→ clasificación


→ identidad


→ tracking


Test funcional


Comprueba el requisito desde el punto de vista del usuario.


Test de regresión


Comprueba que una modificación no rompa funcionalidades existentes.


Validación


Comprueba que el resultado responde a lo especificado en la SRS.


22. Definition of Done


Una tarea de Trello solamente pasa a terminada cuando:


Código implementado


       +


Pruebas realizadas


       +


Resultado esperado


       +


Sin errores conocidos bloqueantes


       +


Documentación actualizada


       +


Criterio de aceptación cumplido


---

## Página 74 (hoja física 236, columna izquierda)


Esto evita que “terminado” signifique simplemente “dejé de trabajar en eso”.


23. Paso 4: MVP


El MVP es el Minimum Viable Product.


No es el producto final reducido de manera arbitraria.


Es la primera versión que entrega suficiente valor como producto funcional.


Para FM24Analyzer, el MVP debe definirse explícitamente en la SRS y el backlog.


Una posible definición sería:


El usuario carga un video


        ↓


el sistema detecta jugadores


        ↓


identifica equipos y dorsales


        ↓


mantiene identidades


        ↓


genera posiciones y trayectorias


        ↓


presenta un análisis básico


        ↓


exporta resultados


El contenido exacto del MVP debe quedar definido antes de empezar a construirlo.


24. MVP Value


El valor del MVP debe medirse por la utilidad que aporta al usuario, no por cantidad


de funcionalidades.


El MVP debería permitir demostrar algo importante:


Que FM24Analyzer puede transformar un video de un partido en información


útil para analizarlo.


---

## Página 75 (hoja física 236, columna derecha)


El MVP no necesita contener todavía todas las funciones avanzadas del producto


definitivo.


Pero sí debe representar claramente el valor central del sistema.


25. Paso 5: Entrega del código fuente


La entrega profesional incluye el código fuente completo.


No solamente:


.exe


o una versión ejecutable.


La entrega debe incluir:


Código fuente


+


dependencias


+


configuración


+


documentación


+


scripts


+


tests


+


recursos necesarios


Además, deberá definirse cómo reproducir el entorno.


26. Paquete de entrega final


El cierre de la primera etapa debería incluir un paquete similar a:


FM24Analyzer/


│


├── source/


├── tests/


├── docs/


---

## Página 76 (hoja física 237, columna izquierda)


│   ├── SRS


│   ├── manual técnico


│   └── manual de usuario


│


├── config/


├── data/


├── examples/


├── release/


└── README


El cliente debe recibir todo lo necesario según el alcance acordado.


27. Documentación de entrega


La entrega final debe incluir:


SRS


Documento contractual/técnico de requisitos.


Manual de usuario


Cómo utilizar el software.


Manual técnico


Cómo está construido.


Instalación


Cómo configurar el entorno.


Dependencias


Versiones necesarias.


Arquitectura


Descripción de módulos y relaciones.


Testing


Pruebas realizadas y resultados.


Limitaciones conocidas


---

## Página 77 (hoja física 237, columna derecha)


Qué casos no están cubiertos.


Código fuente


Repositorio o paquete completo.


28. Aceptación final


Antes de considerar terminado el proyecto debe realizarse una validación final


contra la SRS.


La pregunta ya no es:


“¿Nos parece que funciona?”


La pregunta es:


“¿Cumple los requisitos acordados?”


Cada requisito debe tener una situación de aceptación verificable.


Por ejemplo:


RF-014


Sistema deberá mantener la identidad de un jugador


durante una secuencia válida.


Prueba:


video X


segmento Y


resultado esperado Z


Resultado:


APROBADO / RECHAZADO


29. Criterio de 100 % del desarrollo


FM24Analyzer está al 100 % cuando:


[✓] SRS aprobada


[✓] Backlog completo


---

## Página 78 (hoja física 238, columna izquierda)


[✓] Sprints completados


[✓] Requisitos implementados


[✓] Testing completado


[✓] MVP validado


[✓] Producto final validado


[✓] Documentación terminada


[✓] Código fuente entregado


[✓] Release final generado


[✓] Criterios de aceptación cumplidos


No se define por cantidad de líneas de código ni por cantidad de scripts.


Se define por cumplimiento del alcance acordado.


30. ETAPA 2 - Mantenimiento y soporte


Una vez entregado el software comienza una etapa diferente.


No se debe confundir con el desarrollo original.


El mantenimiento puede incluir:


Correctivo


Solucionar errores.


Preventivo


Mejorar estabilidad y reducir futuros problemas.


Adaptativo


Adaptar el sistema a cambios externos.


Ejemplo:


nueva versión de FM;


cambio de interfaz;


nuevos formatos de video.


Evolutivo


Agregar funcionalidades nuevas.


Ejemplo:


---

## Página 79 (hoja física 238, columna derecha)


nueva métrica táctica;


nuevos tipos de análisis;


nuevos gráficos.


31. Nuevos requerimientos durante mantenimiento


Cuando aparece una necesidad nueva, no debería incorporarse directamente al


código.


Debe seguir nuevamente un ciclo controlado:


Nuevo requerimiento


↓


análisis


↓


impacto


↓


priorización


↓


backlog


↓


sprint


↓


desarrollo


↓


testing


↓


release


De esta manera, incluso el mantenimiento conserva la misma disciplina.


32. Modelo completo del proyecto


El proceso profesional completo de FM24Analyzer queda:


                   ┌──────────────────────┐


                   │  IDEA / NECESIDAD    │


                   └──────────┬───────────┘


                              ↓


                   ┌──────────────────────┐


                   │        SRS           │


---

## Página 80 (hoja física 239, columna izquierda)


                    │ Requisitos completos │


                    └──────────┬───────────┘


                               ↓


                    ┌──────────────────────┐


                    │  BACKLOG + TRELLO    │


                    │ Scrum + Kanban       │


                    └──────────┬───────────┘


                               ↓


                ┌──────────────────────────────┐


                │          SPRINTS              │


                │ desarrollo + testing + QA    │


                └──────────────┬───────────────┘


                               ↓


                    ┌──────────────────────┐


                    │         MVP          │


                    │ Valor funcional real │


                    └──────────┬───────────┘


                               ↓


                    ┌──────────────────────┐


                    │ VALIDACIÓN FINAL     │


                    │ contra la SRS        │


                    └──────────┬───────────┘


                               ↓


                    ┌──────────────────────┐


                    │       ENTREGA        │


                    │ Software + docs      │


                    │ + código fuente      │


                    └──────────┬───────────┘


                               ↓


                ╔══════════════════════════════╗


                ║ MANTENIMIENTO Y SOPORTE      ║


                ╚══════════════════════════════╝


33. Roadmap maestro de FM24Analyzer


El roadmap completo deja de ser únicamente técnico y pasa a ser:


ETAPA 0


Descubrimiento / PoC


        ↓


ETAPA 1


SRS


---

## Página 81 (hoja física 239, columna derecha)


       ↓


ETAPA 2


Backlog + Trello


       ↓


ETAPA 3


Arquitectura y planificación


       ↓


ETAPA 4


Sprints de desarrollo


       ↓


ETAPA 5


Testing y validación incremental


       ↓


ETAPA 6


MVP


       ↓


ETAPA 7


Desarrollo completo


       ↓


ETAPA 8


QA / Hardening


       ↓


ETAPA 9


Aceptación final


       ↓


ETAPA 10


Entrega


       ↓


ETAPA 11


Código fuente + documentación


       ↓


ETAPA 12


Mantenimiento y soporte


34. Situación real actual frente al proceso profesional


FM24Analyzer actualmente tiene:


✅ Descubrimiento técnico


✅ Prueba de concepto


✅ Investigación tecnológica


✅ Primer prototipo funcional


---

## Página 82 (hoja física 240, columna izquierda)


✅ Primeras métricas


✅ Pipeline visual inicial


✅ Tracking inicial


Todavía falta formalizar:


⬜ SRS completa


⬜ Alcance aprobado


⬜ Requisitos funcionales


⬜ Requisitos no funcionales


⬜ Casos de uso


⬜ Criterios de aceptación


⬜ Product Backlog


⬜ Organización formal de Sprints


⬜ Definition of Done


⬜ MVP definido formalmente


⬜ Desarrollo productivo


⬜ QA completo


⬜ Validación final


⬜ Release


⬜ Documentación de entrega


⬜ Paquete de código fuente


⬜ Plan de mantenimiento


Por lo tanto, no debemos considerar que el desarrollo actual sea Sprint 4 formal,


aunque técnicamente estemos trabajando sobre el problema del tracking.


Lo correcto es tratar el trabajo realizado hasta ahora como:


Discovery técnico + Proof of Concept + Prototype.


Luego se formaliza el producto y se reutiliza todo lo aprendido dentro de la SRS y el


backlog.


35. Qué hacemos ahora


El siguiente paso del proyecto cambia respecto del roadmap anterior.


No corresponde seguir agregando funcionalidades indefinidamente.


Ahora corresponde:


---

## Página 83 (hoja física 240, columna derecha)


1. Formalizar el alcance


       ↓


2. Construir la SRS


       ↓


3. Convertir los requisitos en backlog


       ↓


4. Definir Sprints


       ↓


5. Establecer criterios de aceptación


       ↓


6. Determinar qué parte del prototipo se conserva


       ↓


7. Iniciar desarrollo formal


El prototipo ya hizo su trabajo más importante: demostrar que existe una base


técnica viable y revelar cuáles son las dificultades reales.


La siguiente etapa ya no consiste principalmente en experimentar.


Consiste en convertir ese conocimiento en especificación y producto.


36. Principio rector del desarrollo profesional


La metodología completa puede resumirse así:


Primero se especifica qué debe construirse. Después se organiza cómo


construirlo. Luego se desarrolla y se prueba por incrementos. Finalmente se


entrega el producto completo con su código y documentación.


Y el principio operativo más importante:


Lo que no está especificado no forma parte automáticamente del alcance; lo


que está especificado debe poder probarse; y lo que está terminado debe


poder entregarse.


FM24Analyzer deja así de ser simplemente un proyecto de visión por computadora y


pasa a plantearse como lo que realmente queremos construir:


un producto de software especificado, planificado, desarrollado, testeado,


entregado y posteriormente mantenido.


---

## Página 84 (hoja física 241, columna izquierda)


Definí un MVP concreto y verificable
Separá el roadmap de la metodología


ChatGPT puede cometer errores. Considera verificar la información importante.
