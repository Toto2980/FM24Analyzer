import sys, cv2, numpy as np
sys.path.insert(0, "src")
from tracking_core import X_FIELD, Y_FIELD, detect_players
v = cv2.VideoCapture("videos/partido_prueba.mp4")
for f in range(31):
    ok, fr = v.read()
    hsv = cv2.cvtColor(fr, cv2.COLOR_BGR2HSV)
    dets = detect_players(fr)
    out = []
    for d in dets:
        for (tx, ty, tag) in [(581, 622, "T21"), (651, 292, "T06"), (667, 272, "T05")]:
            if np.hypot(d["x"]-tx, d["y"]-ty) < 20:
                r = d["radius"]; x, y = d["x"], d["y"]
                p = hsv[int(y-r*0.5):int(y+r*0.5), int(x-r*0.5):int(x+r*0.5)]
                out.append(f"{tag}@({x},{y}) r={r} {d['source'][:4]} {d.get('team')} medS={np.median(p[:,:,1]):.0f} medV={np.median(p[:,:,2]):.0f}")
    print(f"{f:02d}", " | ".join(out))
