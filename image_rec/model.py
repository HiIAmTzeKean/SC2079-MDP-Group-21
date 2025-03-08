import cv2
import random
import torch
import os
import time
import string
import numpy as np
import glob
from PIL import Image
from ultralytics import YOLO
from pathlib import Path
from datetime import datetime

MODEL_CONFIG = {"conf": 0.3, "path": Path(__file__).parent / "bestv2.pt"}
# confidence threshold for the YOLO model during inderence.

device = 'cuda' if torch.cuda.is_available() else 'cpu'

id_map = {
    "end": 10,
    "one": 11,
    "two": 12,
    "three": 13,
    "four": 14,
    "five": 15,
    "six": 16,
    "seven": 17,
    "eight": 18,
    "nine": 19,
    "a": 20,
    "b": 21,
    "c": 22,
    "d": 23,
    "e": 24,
    "f": 25,
    "g": 26,
    "h": 27,
    "s": 28,
    "t": 29,
    "u": 30,
    "v": 31,
    "w": 32,
    "x": 33,
    "y": 34,
    "z": 35,
    "up": 36,
    "down": 37,
    "right": 38,
    "left": 39,
    "dot": 40,
    # Id Map 2
    "10": 10, # Bullseye 
    "11": 11, # 1 
    "12": 12, # 2
    "13": 13, # 3 
    "14": 14, # 4
    "15": 15, # 5
    "16": 16, # 6 
    "17": 17, # 7 
    "18": 18, # 8
    "19": 19, # 9
    "20": 20, # a 
    "21": 21, # b
    "22": 22, # c
    "23": 23, # d 
    "24": 24, # e
    "25": 25, # f
    "26": 26, # g
    "27": 27, # h
    "28": 28, # s
    "29": 29, # t 
    "30": 30, # u
    "31": 31, # v
    "32": 32, # w
    "33": 33, # x 
    "34": 34, # y
    "35": 35, # z 
    "36": 36, # Up Arrow  
    "37": 37, # Down Arrow
    "38": 38, # Right Arrow 
    "39": 39, # Left Arrow 
    "40": 40  # target 
}

def load_model():
    model = YOLO(MODEL_CONFIG["path"])
    model.to(device)
    return model

def get_random_string(length):
    result = ''.join(random.choice(string.ascii_letters) for i in range(length))
    return result

# Filter and select the best bounding box based on selection mode
def find_largest_or_central_bbox(bboxes, signal):
    if not bboxes:
        return "NA", 0.0

    # Exclude 'end' class
    valid_bboxes = [bbox for bbox in bboxes if bbox["label"] != "10" or bbox["label"] != "end" and bbox["confidence"] > 0.3]

    if not valid_bboxes:
        return "NA", 0.0

    # Find the largest bounding box area
    max_area = max(bbox["bbox_area"] for bbox in valid_bboxes)
    largest_bboxes = [bbox for bbox in valid_bboxes if bbox["bbox_area"] == max_area]

    # If there is only one largest bounding box, return it
    if len(largest_bboxes) == 1:
        return largest_bboxes[0]["label"], largest_bboxes[0]["bbox_area"]

    # Tie-breaking logic using signal
    if signal == 'L':  
        # Pick the rightmost object (higher x-coordinate)
        chosen_bbox = max(largest_bboxes, key=lambda x: x["xywh"][0])
    elif signal == 'R':  
        # Pick the leftmost object (lower x-coordinate)
        chosen_bbox = min(largest_bboxes, key=lambda x: x["xywh"][0])
    else:
        # Default: Pick the first bbox in the list
        chosen_bbox = largest_bboxes[0]

    return chosen_bbox["label"], chosen_bbox["bbox_area"]
    
# Heuristics 
# 1. Ignore the bullseyes 
# 2. Filter by bounding box size ( take the symbol with the largest bounding box size)
# 3. Filter by Signal from algorithm, If car is on the left singal is Left. If car is on the right, signal on the right. (used to break a tie)

# Predict and Annotate image .
def predict_image(model, image_path, output_dir, signal):
    """Predict and annotate image."""
    formatted_time = datetime.now().strftime('%d-%m_%H-%M-%S.%f')[:-3]
    img_name = f"processed_{formatted_time}.jpg"

    # Perform inference
    results = model.predict(
        source=image_path,
        save=True,
        conf=MODEL_CONFIG["conf"],
        imgsz=640,
        device=device
    )

    # Save YOLO-labeled image
    labeled_img_path = Path(results[0].save_dir) / image_path.name
    output_file_path = output_dir / img_name

    os.makedirs(output_dir, exist_ok=True)
    labeled_img_path.rename(output_file_path)

    # Extract bounding boxes
    bboxes = []
    if results[0].boxes:  # If there are any detected objects
        for result in results:
            for box in result.boxes:
                cls_index = int(box.cls.tolist()[0])
                label = result.names[cls_index]
                xywh = box.xywh.tolist()[0]
                bbox_area = xywh[2] * xywh[3]
                confidence = box.conf.tolist()[0]  # Extract confidence
                bboxes.append({"label": label, "xywh": xywh, "bbox_area": bbox_area, "confidence": confidence})
    else:
        # No Objects Deteced Null Check, set confidence to 0
        bboxes.append({"label": "NA", "xywh": [0, 0, 0, 0], "bbox_area": 0.0, "confidence": 0.0})

    selected_label, selected_area = find_largest_or_central_bbox(bboxes,signal)
    
    image_id = id_map.get(selected_label, "NA")

    if selected_label != "NA":
        print(f"Image '{image_path.name}': Detected '{selected_label}' with bbox area {selected_area:.2f} (ID: {image_id})")
    else:
        print(f"Image '{image_path.name}': No objects detected.")

    return image_id

## Task 2
def predict_image_t2(model, image_path, output_dir, signal):
    """Predict and annotate image, identifying only 'left' or 'right'.
       Defaults to 'left' (39) if no valid detection is found.
    """
    formatted_time = datetime.now().strftime('%d-%m_%H-%M-%S.%f')[:-3]
    img_name = f"processed_{formatted_time}.jpg"

    id_map = {
        "end": 10,
        "right": 38,
        "left": 39,
        "38":38,
        "39":39,
        "10":10
    }

    # Perform inference
    results = model.predict(
        source=image_path,
        save=True,
        conf=MODEL_CONFIG["conf"],
        imgsz=640,
        device=device
    )

    # Save YOLO-labeled image
    labeled_img_path = Path(results[0].save_dir) / image_path.name 
    output_file_path = output_dir / img_name

    os.makedirs(output_dir, exist_ok=True)
    if labeled_img_path.exists():
        labeled_img_path.rename(output_file_path)
    else:
        print(f"Warning: Labeled image not found at {labeled_img_path}")

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
                if label in ["38","39","left", "right"] and confidence > 0.3:
                    bboxes.append({"label": label, "xywh": xywh, "bbox_area": bbox_area, "confidence": confidence})

    # Select the largest bounding box
    selected_label, selected_area = find_largest_or_central_bbox(bboxes, signal)

    # If no valid detection, default to "left" (39)

    if selected_label != "38" or selected_label != "39" or selected_label != "left" or selected_label != "right":

        image_id = 39
    else:
        image_id = id_map.get(selected_label, 39)  # Default to left if key is missing

    print(f"Image '{image_path.name}': Detected '{selected_label}' with bbox area {selected_area:.2f} (ID: {image_id})")

    return image_id


def resize_image(image_path, output_dir):
    """
    Resize the image at the given path to 640x640 pixels and overwrite the original image.
    Args:
        image_path (str or Path): Path to the image file.
    """
    try:
        # Open the image
        img = Image.open(image_path)
        # Original image size is 640x480 (picamera1) or 3280x2464 (picamera2)
        # Resize the image while maintaining aspect ratio
        ratio = 0.1952 # scale 3280x2464 to 640x480
        resized_img = img.resize([int(ratio * s)
                                 for s in img.size], Image.LANCZOS)
        output_path = output_dir / image_path.name.replace("processed", "resized")
        resized_img.save(output_path)

    except Exception as e:
        print(f"Error resizing image {image_path}: {e}")


def resize_all_images(output_dir, fullsize_dir):
    """
    Resize all images in the given directory before stitching.
    Args:
        output_dir (Path): Directory containing images.
    """
    for img_path in fullsize_dir.iterdir():
        if img_path.is_file() and img_path.suffix.lower() in ('.png', '.jpg', '.jpeg'):
            resize_image(img_path, output_dir)


def stitch_image(output_dir, fullsize_dir):
    output_filename = "concatenated.jpg"
    output_path = output_dir / output_filename

    try:
        # Resize all images before proceeding
        resize_all_images(output_dir, fullsize_dir)

        # Get all image files
        image_files = [
            path for path in output_dir.iterdir()
            if path.is_file()
            and path.suffix.lower() in ('.png', '.jpg', '.jpeg')
            and path.name.lower() != output_filename  # Exclude stitched image
        ]
        if not image_files:
            print(f"No image files found in '{output_dir}'.")
            return

        images = []
        for img_path in image_files:
            try:
                img = Image.open(img_path)
                images.append(img)
            except Exception as e:
                print(f"Skipping image {img_path.name} due to error: {e}")
                continue  # Skip faulty images instead of returning

        if not images:  # Check if any images were successfully loaded
            print("No valid images to stitch.")
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
        print(f"Concatenated image saved to: {output_path}")

        return new_img

    except Exception as e:
        print(f"An error occurred: {e}")
