
# ----- DELETE THIS FILE AND `api_test_img/` FOLDER WHEN DONE TESTING -----

import requests

API_IP = "" # TODO: replace with your PC's local IPv4 address
API_PORT = 5000

url = f"http://{API_IP}:{API_PORT}"

# put image to rec in `api_test_img/` folder
image_filename = f"1739516818_1_C.jpg" # RPI sends image in format: f"{int(time.time())}_{obstacle_id}_{signal}.jpg"
image_path = f"api_test_img\\{image_filename}"
response = requests.post(
    f'{url}/image', files={"file": (image_filename, open(image_path, 'rb'))})
if response.status_code != 200:
    print("Something went wrong with /image endpoint.")

# # WIP, stitch function not ready yet
# response = requests.get(f'{url}/stitch')
# if response.status_code != 200:
#     print("Something went wrong with /stitch endpoint")
