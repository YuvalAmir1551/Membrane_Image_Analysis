# Yuval Amir
import math
from typing import List, Dict
import cv2
import numpy as np
from pathlib import Path


def detect_colored_circles(image_path: str) -> list[dict]:
    """
    Detects colored circles on the membrane.

    Input:
    image_path (str): The path to an image file (JPEG or PNG) of the membrane.

    Output:
    A list of dictionaries, where each dictionary represents a detected circle
    with the keys: "x", "y", "radius", "color"
    """

    # Check extension
    filepath = Path(image_path)
    ext = filepath.suffix.lower()
    if ext not in ['.png', '.jpeg', '.jpg']:
        raise ValueError(f"The image must have an extension of png, jpg, or jpeg, given extension: {ext}")

    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not load image from {image_path}")

    # White balance
    balanced = gray_world_white_balance(image)

    # Reduce noise using bilateral filter
    denoised = cv2.bilateralFilter(balanced, 9, 75, 75)

    # Enhance contrast using CLAHE in LAB color space
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)
    enhanced_lab = cv2.merge((l_enhanced, a, b))
    enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    # Convert to HSV
    hsv = cv2.cvtColor(enhanced, cv2.COLOR_BGR2HSV)

    # Color ranges
    color_ranges = {
        "blue": ([100, 65, 60], [130, 255, 255]),
        "red1": ([0, 60, 50], [10, 255, 255]),
        "red2": ([170, 50, 50], [180, 255, 255]),
        "yellow1": ([25, 100, 70], [35, 255, 255]),
        "yellow2": ([40, 35, 50], [90, 255, 255]),
        "black": ([70, 40, 0], [120, 98, 90])
    }

    circles = []

    # Detect masks and contours for each color
    for color_name, (lower, upper) in color_ranges.items():
        # Special handling for red and yellow (split into two ranges)
        if color_name == "red1":
            mask1 = cv2.inRange(hsv, np.array(lower), np.array(upper))
            continue
        elif color_name == "red2":
            mask2 = cv2.inRange(hsv, np.array(lower), np.array(upper))
            mask = cv2.bitwise_or(mask1, mask2)
            c_name = "red"
        elif color_name == "yellow1":
            mask1 = cv2.inRange(hsv, np.array(lower), np.array(upper))
            continue
        elif color_name == "yellow2":
            mask2 = cv2.inRange(hsv, np.array(lower), np.array(upper))
            mask = cv2.bitwise_or(mask1, mask2)
            c_name = "yellow"
        else:
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            c_name = color_name

        # Morphological operations to improve the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (39, 39))
        closed_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        opened_mask = cv2.morphologyEx(closed_mask, cv2.MORPH_OPEN, kernel)

        # Detect contours
        contours, _ = cv2.findContours(opened_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Process contours into circles
        for contour in contours:
            # Fit a circle
            (x, y), radius = cv2.minEnclosingCircle(contour)

            # Append to the list of circles
            circles.append({
                "x": int(x),
                "y": int(y),
                "radius": int(radius),
                "color": c_name
            })

    filtered_circles = []
    for circle in circles:
        duplicate_circles = []
        x1, y1, r1, color1 = circle["x"], circle["y"], circle["radius"], circle["color"]
        is_duplicate = False

        for existing in filtered_circles:
            x2, y2, r2, color2 = existing["x"], existing["y"], existing["radius"], existing["color"]

            distance = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

            if distance < r1 + r2:
                is_duplicate = True
                duplicate_circles.append(existing)

        if is_duplicate:
            largest_circle = circle
            largest_radius = circle["radius"]
            for duplicate in duplicate_circles:
                if duplicate["radius"] > largest_radius:
                    if largest_circle in filtered_circles:
                        filtered_circles.remove(largest_circle)
                    largest_circle = duplicate
                elif duplicate in filtered_circles:
                    filtered_circles.remove(duplicate)
            if largest_circle not in filtered_circles:
                filtered_circles.append(largest_circle)
        else:
            filtered_circles.append(circle)

    return filtered_circles


def track_circles_over_time(image_paths: List[str]) -> Dict:
    """
    Input:
        image_paths (list[str]): A list of image file paths representing the sequence of images over time.
    Output:
        A dictionary:
            - "table": A list of records (dictionaries) where each record includes:
                • image (int): The sequence number of the image.
                • circle_id (int): The identifier for the circle.
                • x (int): The x-coordinate of the circle’s center.
                • y (int): The y-coordinate of the circle’s center.
                • radius (int): The radius of the circle.
                • color (str): The color of the circle.
    """

    # Table to store all final records
    table = []

    # "Database" of already detected circles: circle_id -> (x, y, color, radius)
    # This will be updated for each frame
    known_circles = {}

    # Counter for creating a unique circle_id when a new circle is detected
    next_circle_id = 1

    # Iterate over all images in order
    for i, image_path in enumerate(image_paths, start=1):
        # Step 1: Detect circles in the current image
        circles = detect_colored_circles(image_path)

        # Keep a set of circles that have not yet been assigned an ID (after comparing to known_circles)
        unmatched_circle_ids = set(known_circles.keys())

        # Match new circles to existing circles.
        # For each detected circle, search for a previous circle (in known_circles) that is closest.
        assignments = {}  # circle_index -> circle_id

        for circle_idx, circle in enumerate(circles):
            x_new = circle["x"]
            y_new = circle["y"]
            color_new = circle["color"]
            radius_new = circle["radius"]

            best_id = None
            best_dist = float('inf')

            for circle_id in unmatched_circle_ids:
                x_old, y_old, color_old, radius_old = known_circles[circle_id]

                # Calculate distance between centers
                dist = math.sqrt((x_new - x_old) ** 2 + (y_new - y_old) ** 2)

                # Keep the closest circle
                if dist < best_dist:
                    best_dist = dist
                    best_id = circle_id

            distance_threshold = 200

            if best_id is not None and best_dist < distance_threshold:
                # Found a previous circle that matches the new circle
                assignments[circle_idx] = best_id
                unmatched_circle_ids.remove(best_id)

                # Update the position and radius in the database
                known_circles[best_id] = (x_new, y_new, color_new, radius_new)
            else:
                # Completely new circle - assign a new circle_id
                assignments[circle_idx] = next_circle_id
                known_circles[next_circle_id] = (x_new, y_new, color_new, radius_new)
                next_circle_id += 1

        # Now, add the records for the current image to the table
        for circle_idx, circle in enumerate(circles):
            circle_id = assignments[circle_idx]
            record = {
                "image": i,
                "circle_id": circle_id,
                "x": circle["x"],
                "y": circle["y"],
                "radius": circle["radius"],
                "color": circle["color"]
            }
            table.append(record)

        # Circles that were not matched (unmatched_circle_ids) remain in known_circles;
        # We keep them in case they reappear in a subsequent frame.

    return {"table": table}


def gray_world_white_balance(image, correction_factor=0.7):
    result = image.copy().astype(np.float32)

    # Calculate the average for each channel
    avg_b = np.mean(result[:, :, 0])
    avg_g = np.mean(result[:, :, 1])
    avg_r = np.mean(result[:, :, 2])
    # Global average (expected if all channels are balanced)
    avg_gray = (avg_b + avg_g + avg_r) / 3.0

    # Calculate partial correction for each channel
    # Formula: new_value = value * (1 + correction_factor * ((avg_gray / avg_channel) - 1))
    result[:, :, 0] = result[:, :, 0] * (1 + correction_factor * ((avg_gray / avg_b) - 1))
    result[:, :, 1] = result[:, :, 1] * (1 + correction_factor * ((avg_gray / avg_g) - 1))
    result[:, :, 2] = result[:, :, 2] * (1 + correction_factor * ((avg_gray / avg_r) - 1))

    # Clip the values to the range [0, 255] and convert to uint8
    result = np.clip(result, 0, 255).astype(np.uint8)
    return result
