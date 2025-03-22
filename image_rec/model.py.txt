import cv2
import torch
import os
import string
import numpy as np
import glob
from PIL import Image
from ultralytics import YOLO
from pathlib import Path
from datetime import datetime

# confidence threshold for the YOLO model during inference and file path to weights
MODEL_CONFIG = {"conf": 0.3, "path": Path(__file__).parent
                / "best_JH.pt"}  # model trained on 50k images

device = 'cuda' if torch.cuda.is_available() else 'cpu'

id_map = {
    "10": 10,  # Bullseye
    "11": 11,  # 1
    "12": 12,  # 2
    "13": 13,  # 3
    "14": 14,  # 4
    "15": 15,  # 5
    "16": 16,  # 6
    "17": 17,  # 7
    "18": 18,  # 8
    "19": 19,  # 9
    "20": 20,  # a
    "21": 21,  # b
    "22": 22,  # c
    "23": 23,  # d
    "24": 24,  # e
    "25": 25,  # f
    "26": 26,  # g
    "27": 27,  # h
    "28": 28,  # s
    "29": 29,  # t
    "30": 30,  # u
    "31": 31,  # v
    "32": 32,  # w
    "33": 33,  # x
    "34": 34,  # y
    "35": 35,  # z
    "36": 36,  # Up Arrow
    "37": 37,  # Down Arrow
    "38": 38,  # Right Arrow
    "39": 39,  # Left Arrow
    "40": 40  # target
}


def load_model():
    model = YOLO(MODEL_CONFIG["path"])
    model.to(device)
    return model


def find_largest_or_central_bbox(bboxes, signal):
    """
    Filter and select the best bounding box based on selection mode
    """
    if not bboxes:
        return "NA", 0.0

    # Exclude 'end' class
    valid_bboxes = [bbox for bbox in bboxes if bbox["label"]
                    != "10" and bbox["confidence"] > 0.3]
    if not valid_bboxes:
        return "NA", 0.0

    # If there is only one bounding box, return it
    if len(valid_bboxes) == 1:
        return valid_bboxes[0]["label"], valid_bboxes[0]["bbox_area"]

    # Find the largest bounding box area
    max_area = max(bbox["bbox_area"] for bbox in valid_bboxes)
    # TODO test and tune the threshold accordingly
    threshold = 0.1  # bbox is of similar size if it is within 10% range of largest bbox area
    # Get all bounding boxes with similar size to the largest bbox
    largest_bboxes = [
        bbox for bbox in valid_bboxes if bbox["bbox_area"] >= (1-threshold) * max_area]

    # Tie-breaking logic using signal
    if signal == 'L':  # Obstacle is left of robot
        # Pick the leftmost object (lowest x-coordinate)
        chosen_bbox = min(largest_bboxes, key=lambda x: x["xywh"][0])
    elif signal == 'R':  # Obstacle is right of robot
        # Pick the rightmost object (highest x-coordinate)
        chosen_bbox = max(largest_bboxes, key=lambda x: x["xywh"][0])
    else:
        # Default: Pick the largest bbox in the list
        chosen_bbox = max(largest_bboxes, key=lambda x: x["bbox_area"])

    return chosen_bbox["label"], chosen_bbox["bbox_area"]


def predict_image(logger, model, image_path, output_dir, signal):
    """
    FOR TASK 1: Predict and annotate image.

    Heuristics for predict_image
    1. Ignore the bullseyes
    2. Sort by bounding box size ( take the symbol with the largest bounding box size)
    3. Filter by Signal from algorithm. signal = 'L' if obstacle is on the left of robot, signal = 'R' if obstacle is right of robot (used to break a tie)

    Code can be further modified to use a fallback model if necessary.
    """
    formatted_time = datetime.now().strftime('%d-%m_%H-%M-%S.%f')[:-3]
    img_name = f"processed_{formatted_time}.jpg"

    # Perform inference
    results = model.predict(
        source=image_path,
        conf=MODEL_CONFIG["conf"],
        imgsz=640,
        device=device,
        verbose=False
    )
    logger.debug(f"predict speed (ms): {results[0].speed}")

    bboxes = []
    if results[0].boxes:  # If there are any detected objects
        for result in results:
            for box in result.boxes:
                cls_index = int(box.cls.tolist()[0])
                label = result.names[cls_index]
                xywh = box.xywh.tolist()[0]
                bbox_area = xywh[2] * xywh[3]
                confidence = box.conf.tolist()[0]  # Extract confidence
                bboxes.append({"label": label, "xywh": xywh,
                              "bbox_area": bbox_area, "confidence": confidence})
    logger.debug(f"Bounding boxes: '{bboxes}")

    # Save YOLO-labeled image
    os.makedirs(output_dir, exist_ok=True)
    output_file_path = output_dir / img_name
    results[0].save(output_file_path)
    logger.debug(f"Saved processed image: '{output_file_path}'")

    selected_label, selected_area = find_largest_or_central_bbox(
        bboxes, signal)
    image_id = id_map.get(selected_label, "NA")

    if selected_label != "NA":
        logger.debug(
            f"Image '{image_path.name}': Detected '{selected_label}' with bbox area {selected_area:.2f} (ID: {image_id})")
    else:
        logger.debug(f"Image '{image_path.name}': No objects detected.")

    return image_id


def predict_image_t2(logger, model, image_path, output_dir, signal):
    """FOR TASK 2: Predict and annotate image, identifying only 'left' or 'right'.
       Defaults to 'left' (39) if no valid detection is found.
    """
    formatted_time = datetime.now().strftime('%d-%m_%H-%M-%S.%f')[:-3]
    img_name = f"processed_{formatted_time}.jpg"

    id_map = {
        "38": 38,   # Right Arrow
        "39": 39,   # Left Arrow
        "10": 10    # Bullseye
    }

    # Perform inference
    results = model.predict(
        source=image_path,
        conf=MODEL_CONFIG["conf"],
        imgsz=640,
        device=device,
        verbose=False
    )
    logger.debug(f"predict speed (ms): {results[0].speed}")

    # Extract bounding boxes
    bboxes = []
    if results[0].boxes:  # If there are any detected objects
        for result in results:
            for box in result.boxes:
                cls_index = int(box.cls.tolist()[0])
                label = result.names[cls_index]
                xywh = box.xywh.tolist()[0]
                bbox_area = xywh[2] * xywh[3]
                confidence = box.conf.tolist()[0]

                # Only consider 'left' and 'right' with confidence > 0.3
                if label in ["38", "39"] and confidence > 0.3:
                    bboxes.append(
                        {"label": label, "xywh": xywh, "bbox_area": bbox_area, "confidence": confidence})

    logger.debug(f"Bounding boxes: '{bboxes}")

    # Save YOLO-labeled image
    os.makedirs(output_dir, exist_ok=True)
    output_file_path = output_dir / img_name
    results[0].save(output_file_path)
    logger.debug(f"Saved processed image: '{output_file_path}'")

    # Select the largest bounding box
    selected_label, selected_area = find_largest_or_central_bbox(
        bboxes, signal)

    # If no valid detection, default to "left" (39)
    if selected_label == "38":
        image_id = 38
        logger.debug(
            f"Image '{image_path.name}': Detected '{selected_label}' with bbox area {selected_area:.2f} (ID: {image_id})")
    elif selected_label == "39":
        image_id = 39
        logger.debug(
            f"Image '{image_path.name}': Detected '{selected_label}' with bbox area {selected_area:.2f} (ID: {image_id})")
    else:
        # Default to left if key is missing
        image_id = id_map.get(selected_label, 39)
        logger.debug(
            f"Image '{image_path.name}': Detected '{selected_label}' with bbox area {selected_area:.2f} (ID: Defaulting to {image_id})")

    return image_id


def resize_image(logger, image_path, output_dir):
    """
    Resize the 3280px x 2464px image at the given path to 640px x 480px.
    Args:
        image_path (str or Path): Path to the image file.
    """
    try:
        # Open the image
        img = Image.open(image_path)
        # Original image size is 640x480 (picamera1) or 3280x2464 (picamera2)
        # Resize the image while maintaining aspect ratio
        ratio = 0.1952  # scale 3280x2464 to 640x480
        resized_img = img.resize([int(ratio * s)
                                 for s in img.size], Image.LANCZOS)
        output_path = output_dir / \
            image_path.name.replace("processed", "resized")
        resized_img.save(output_path)

    except Exception as e:
        logger.debug(f"Error resizing image '{image_path}: {e}'")


def resize_all_images(logger, output_dir, fullsize_dir):
    """
    Resize all images in the given directory while maintaining aspect ratio before stitching.
    Args:
        output_dir (Path): Directory containing images.
    """
    for img_path in fullsize_dir.iterdir():
        if img_path.is_file() and img_path.suffix.lower() in ('.png', '.jpg', '.jpeg'):
            resize_image(logger, img_path, output_dir)


def stitch_image(logger, output_dir, fullsize_dir):
    output_filename = "concatenated"
    output_path = output_dir / f"{output_filename}.jpg"

    try:
        logger.debug(f"Resizing images in folder: '{fullsize_dir}'")
        # Resize all images (while maintaining aspect ratio) before concatenation, since large images take longer to process
        resize_all_images(logger, output_dir, fullsize_dir)
        logger.debug(f"Saved resized images to folder: '{output_dir}'")

        # Get all image files
        image_files = [
            path for path in output_dir.iterdir()
            if path.is_file()
            and path.suffix.lower() in ('.png', '.jpg', '.jpeg')
            and output_filename not in path.name.lower()  # Exclude stitched image
        ]
        if not image_files:
            logger.debug(f"No image files found in '{output_dir}'.")
            return

        images = []
        for img_path in image_files:
            try:
                img = Image.open(img_path)
                images.append(img)
            except Exception as e:
                logger.debug(
                    f"Skipping image {img_path.name} due to error: {e}")
                continue  # Skip faulty images instead of returning

        if not images:  # Check if any images were successfully loaded
            logger.debug("No valid images to stitch.")
            return

        # Get total width and max height
        widths, heights = zip(*(i.size for i in images))
        total_width = sum(widths)
        max_height = max(heights)

        # Create new blank image
        new_img = Image.new('RGB', (total_width, max_height))

        # Stitch images side by side
        x_offset = 0
        for img in images:
            new_img.paste(img, (x_offset, 0))
            x_offset += img.width

        # Save output
        new_img.save(output_path)
        logger.debug(f"Concatenated image saved to: '{output_path}'")

        return new_img

    except Exception as e:
        logger.debug(f"An error occurred: {e}")
