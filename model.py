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

MODEL_CONFIG = {"conf": 0.3, "path": Path("best.pt")}
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
    "dot": 40
}

def get_random_string(length):
    result = ''.join(random.choice(string.ascii_letters) for i in range(length))
    return result

def find_largest_or_central_bbox(bboxes, selection_mode='largest', confidence_adjustment=False):
    if not bboxes:
        return "NA", 0.0

    valid_bboxes = []

    # Filter bboxes based on initial confidence threshold
    for bbox in bboxes:
            valid_bboxes.append(bbox)

    if not valid_bboxes:
        return "NA", 0.0

    if selection_mode == 'largest':
        return max(valid_bboxes, key=lambda x: x["bbox_area"])["label"], max(valid_bboxes, key=lambda x: x["bbox_area"])["bbox_area"]

    # Example central detection (adjust as needed)
    center_x = 320
    return min(valid_bboxes, key=lambda x: abs(x["xywh"][0] - center_x))["label"], min(valid_bboxes, key=lambda x: abs(x["xywh"][0] - center_x))["bbox_area"]

# Predict and Annotate image .
def predict_image(model, image_path, output_dir, selection_mode='largest'):
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

    selected_label, selected_area = find_largest_or_central_bbox(bboxes, selection_mode)
    
    image_id = id_map.get(selected_label, "NA")

    if selected_label != "NA":
        print(f"Image '{image_path.name}': Detected '{selected_label}' with bbox area {selected_area:.2f} (ID: {image_id})")
    else:
        print(f"Image '{image_path.name}': No objects detected.")

    return image_id

# WIP For Task 2 ( Left and Right )
# def predict_image_t2(image, model):
#     img = Image.open(os.path.join('uploads', image))
#     results = model(img)
#     results.save('runs')
#     df = results.pandas().xyxy[0]
   
#     df['boxHeight'] = df['ymax'] - df['ymin']
#     df['bboxWt'] = df['xmax'] - df['xmin']
#     df['boxArea'] = df['boxHeight'] * df['boxWidth']

#     df = df.sort_values('boxArea', ascending=False)
#     pred_list = df 
#     pred = 'NA'
#     if pred_list.size != 0:
#         for _, row in pred_list.iterrows():
#             if row['name'] != 'Bullseye' and row['confidence'] > 0.3:
#                 pred = row    
#                 break

#         if not isinstance(pred,str):
#             draw_box(np.array(img), pred['xmin'], pred['ymin'], pred['xmax'], pred['ymax'], pred['name'])
        
#     id_map = {
#         "NA": 'NA',
#         "Bullseye": 10,
#         "Right": 38,
#         "Left": 39,
#         "Right-Arrow": 38,
#         "Left-Arrow": 39,
#     }
#     if not isinstance(pred,str):
#         image_id = str(id_map[pred['name']])
#         print(f"Final result: {image_id}")
#     else:
#         ## fail case is go left
#         image_id = '39'
#     return image_id

def stitch_image(): ## WIP
    ## stitch the images together
    imageFolder = 'our_results'
    imagePaths = glob.glob(os.path.join(imageFolder+"/annotated_image_*.jpg"))
    imgTimestamps = [imgPath.split("_")[-1][:-4] for imgPath in imagePaths]
    timestampImages = sorted(zip(imagePaths, imgTimestamps), key=lambda x: x[1])
    images = [Image.open(x[0]) for x in timestampImages]
    width, height = zip(*(i.size for i in images))
    x_offset = 0
    total_width = sum(width)
    max_height = max(height)
    stitchedImg = Image.new('RGB', (total_width, max_height))
    for im in images:
        stitchedImg.paste(im, (x_offset, 0))
        x_offset += im.size[0]
    stitchedImg.save(os.path.join(imageFolder, f'stitched-{int(time.time())}.jpeg'))
    return stitchedImg


# ## Testing With Images From Folder##
# # Comment out Later # 
# model = YOLO(MODEL_CONFIG["path"])
# model.to(device)

# # Input folder and Output Folder # 
# test_images_folder = Path("test_images")
# output_dir = Path("output")
# os.makedirs(output_dir, exist_ok=True)

# for image_file in test_images_folder.glob("*.*"):  # This will match all files with image extensions
#     if image_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:  # Check if it's a valid image format
#         # Call the prediction function
#         image_id = predict_image(model, image_file, output_dir)
 