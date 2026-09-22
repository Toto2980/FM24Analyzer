import sys, json, cv2, numpy as np
sys.path.insert(0, "src")
from tracking_core import detect_players
SP = sys.argv[1]
v = cv2.VideoCapture("videos/partido_prueba.mp4")
frames = []
for f in range(31):
    ok, fr = v.read(); frames.append(fr)
# crops: T21 frames 9/10, T06 frames 22/23/24
def crop(fr, x, y, s=40, z=6):
    c = fr[y-s:y+s, x-s:x+s]
    return cv2.resize(c, None, fx=z, fy=z, interpolation=cv2.INTER_NEAREST)
row1 = np.hstack([crop(frames[9], 581, 622, 20, 8), crop(frames[10], 581, 622, 20, 8)])
row2 = np.hstack([crop(frames[f], 665, 285, 40, 4) for f in (22, 23, 24)])
cv2.imwrite(SP + "/t21_f09_f10.png", row1)
cv2.imwrite(SP + "/t06_f22_23_24.png", row2)
# ring vs center for all field detections, frames 0,10,20
f0 = json.load(open("output/match/frame_0000.json", encoding="utf-8"))
truth = {(p["state"]["x"], p["state"]["y"]): p["identity"]["team"] for p in f0["players"] if p["identity"]["role"] == "PLAYER"}
hsv = cv2.cvtColor(frames[10], cv2.COLOR_BGR2HSV)
rows = []
for d in detect_players(frames[10]):
    if d.get("role") == "GK": continue
    x, y = d["x"], d["y"]
    t = min(truth, key=lambda k: np.hypot(k[0]-x, k[1]-y))
    if np.hypot(t[0]-x, t[1]-y) > 5: continue
    yy, xx = np.ogrid[-12:13, -12:13]
    rr = np.hypot(xx, yy)
    patch = hsv[y-12:y+13, x-12:x+13]
    ring = patch[(rr >= 4.5) & (rr <= 6.5)]
    r = d["radius"]
    c = hsv[int(y-r*0.5):int(y+r*0.5), int(x-r*0.5):int(x+r*0.5)]
    rows.append((truth[t], d["team"], r, np.median(c[:,:,1]), np.median(c[:,:,2]), np.median(ring[:,1]), np.median(ring[:,2]), np.median(ring[:,0])))
for r in sorted(rows): print("%-6s pred=%-6s r=%d | centro S=%3.0f V=%3.0f | anillo S=%3.0f V=%3.0f H=%3.0f" % r)
