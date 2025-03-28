# API Server

API Server for RPI to communicate with PC over Wifi. Used by Algo & Image Rec

## Setup 

---

1. Clone the repository
2. Open the terminal and navigate to `/api` directory
3. Create a python virtual environment
    ```bash
    python -m venv .venv
    ```
4. Activate the virtual environment for the directory

    Mac:
    ```bash
    source .venv/bin/activate
    ```

    Windows:
    ```bash
    .venv/Scripts/activate
    ```

5. Install the required packages
    ```bash
    pip install -r requirements.txt
    ```

6. In `/api` directory, start the application
    ```bash
    python api.py
    ```

Server application and Swagger documentation will be running on `http://localhost:5000` or `http://{your local IP}:5000`. Make sure to point the web simulator or RPI code to the URL that this server is running on.

Image recognition files will be stored in `/api/image_rec_files`. 
`/api/image_rec_files/uploads/`: contains the images sent in the POST request to the `/image` API endpoint
`/api/image_rec_files/output/fullsize`: contains the full-size processed images with bounding boxes
`/api/image_rec_files/output/`: contains the resized processed images with bounding boxes and output concatenated image

## Credits
Thank you to Group 30 from AY24/25 S1 for the base code. We extended their code by extensive refactoring, implementing logging and Flask-RESTX for generating Swagger documentation. 