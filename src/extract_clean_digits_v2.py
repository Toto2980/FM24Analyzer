import cv2
import numpy as np


def get_components(mask):
    num_labels, labels, stats, _ = (
        cv2.connectedComponentsWithStats(
            mask,
            connectivity=8
        )
    )

    components = []

    for i in range(1, num_labels):

        x, y, w, h, area = stats[i]

        components.append({
            "x": int(x),
            "y": int(y),
            "w": int(w),
            "h": int(h),
            "area": int(area)
        })

    return components


def center_of(component):

    return (
        component["x"] + component["w"] / 2,
        component["y"] + component["h"] / 2
    )


def distance_between(a, b):

    ax, ay = center_of(a)
    bx, by = center_of(b)

    return np.sqrt(
        (ax - bx) ** 2 +
        (ay - by) ** 2
    )


def close_to_main(component, main):

    distance = distance_between(
        component,
        main
    )

    return distance <= 45


def looks_like_digit(component):

    return (
        35 <= component["h"] <= 70
        and 15 <= component["w"] <= 55
        and component["area"] >= 300
    )


def looks_like_fragment(component):

    return (
        component["area"] >= 20
        and component["h"] >= 8
    )