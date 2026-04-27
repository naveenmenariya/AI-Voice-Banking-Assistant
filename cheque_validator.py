"""
Robust cheque validation using OpenCV heuristics.
"""

import os
import cv2
import numpy as np

BLANK_STD_THRESHOLD = 10.0
TEXT_RATIO_THRESHOLD = 0.005


# ── Path cleaning ─────────────────────────────────────────────────────────────

def _clean_path(path: str) -> str:
    return os.path.normpath(path.strip().strip('"').strip("'"))


# ── Core checks ───────────────────────────────────────────────────────────────

def _check_readable(path):
    if not os.path.exists(path):
        return None, f"File not found at path: {path}"

    img = cv2.imread(path)
    if img is None:
        return None, "Invalid image file."

    return img, None


def _check_aspect_ratio(img):
    h, w = img.shape[:2]
    ratio = w / h

    if ratio < 2.0 or ratio > 5.0:
        return False, f"Aspect ratio {ratio:.2f} not cheque-like."

    return True, ""


def _check_not_blank(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if np.std(gray) < BLANK_STD_THRESHOLD:
        return False, "Image appears blank."
    return True, ""


def _check_text_regions(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)

    ratio = np.sum(binary > 0) / binary.size
    if ratio < TEXT_RATIO_THRESHOLD:
        return False, "Too little text detected."

    return True, ""


def _check_horizontal_lines(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=60,
        minLineLength=img.shape[1] // 4,
        maxLineGap=25
    )

    if lines is None:
        return False, "No structural lines detected."

    horizontal = sum(1 for l in lines if abs(l[0][1] - l[0][3]) < 20)

    if horizontal < 1:
        return False, "No horizontal structure."

    return True, ""


# ── MICR CHECK (Strong filter) ──────────────────────────────────────────

def _check_micr_region(img):
    """
    Detect MICR-like numeric band using edge pattern (not just darkness).
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    bottom = gray[int(h * 0.8):h, :]

    edges = cv2.Canny(bottom, 50, 150)

    # column-wise edge density
    col_density = np.sum(edges > 0, axis=0) / bottom.shape[0]

    # count columns that resemble digit strokes
    valid_cols = np.sum((col_density > 0.1) & (col_density < 0.6))

    if valid_cols < w * 0.12:
        return False, "No MICR-like numeric pattern detected."

    return True, ""


# ── Main validation ───────────────────────────────────────────────────────────

def is_valid_cheque(image_path):
    image_path = _clean_path(image_path)

    img, err = _check_readable(image_path)
    if err:
        return False, err

    checks = [
        _check_aspect_ratio,
        _check_not_blank,
        _check_text_regions,
        _check_horizontal_lines,
    ]

    for check in checks:
        ok, msg = check(img)
        if not ok:
            return False, msg

    # 🔥 STRICT final gate
    micr_ok, micr_msg = _check_micr_region(img)

    if not micr_ok:
        return False, micr_msg

    return True, "Cheque validated successfully (MICR detected)."


# ── Voice handler ─────────────────────────────────────────────────────────────

def handle_cheque(speak, listen):
    speak("Please enter the cheque image path.")

    path = input(">>> ")
    path = _clean_path(path)

    print(f"[DEBUG] Path: {path}")
    print(f"[DEBUG] Exists: {os.path.exists(path)}")

    speak("Processing your cheque image. Please wait.")

    valid, msg = is_valid_cheque(path)

    if valid:
        speak("Good news! " + msg)
    else:
        speak("I'm sorry, the cheque could not be verified. " + msg)