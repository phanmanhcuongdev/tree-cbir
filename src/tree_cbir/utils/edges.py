import cv2
import numpy as np


def canny(gray, low=50, high=150):
    return cv2.Canny(gray, low, high).astype(bool)


def edge_density(edges):
    return float(edges.astype(bool).mean()) if edges.size else 0.0


def hough_lines(edges, threshold=20):
    return cv2.HoughLinesP(
        edges.astype(np.uint8) * 255, 1, np.pi / 180, threshold, minLineLength=10, maxLineGap=2
    )


def total_line_length(lines):
    return (
        0.0
        if lines is None
        else float(sum(np.hypot(x2 - x1, y2 - y1) for x1, y1, x2, y2 in lines.reshape(-1, 4)))
    )
