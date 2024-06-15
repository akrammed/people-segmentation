import io  # Add this import statement

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import torch
import albumentations as albu
from iglovikov_helper_functions.utils.image_utils import load_rgb, pad, unpad
from iglovikov_helper_functions.dl.pytorch.utils import tensor_from_rgb_image
from people_segmentation.pre_trained_models import create_model
import logging
import os
import tempfile

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8081"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

model = create_model("Unet_2020-07-20")
model.eval()

def segment(image):
    transform = albu.Compose([albu.Normalize(p=1)], p=1)
    padded_image, pads = pad(image, factor=32, border=cv2.BORDER_CONSTANT)

    x = transform(image=padded_image)["image"]
    x = torch.unsqueeze(tensor_from_rgb_image(x), 0)

    with torch.no_grad():
        prediction = model(x)[0][0]

    mask = (prediction > 0).cpu().numpy().astype(np.uint8)
    mask = unpad(mask, pads)

    dst = cv2.addWeighted(image, 1, (cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB) * (0, 255, 0)).astype(np.uint8), 0.5, 0)

    return dst

logging.basicConfig(level=logging.DEBUG)

@app.post("/segment")
async def segment_image(file: UploadFile = File(...)):
    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_path = os.path.join(tmpdirname, file.filename)
            
            with open(tmp_path, "wb") as tmp_file:
                tmp_file.write(await file.read())

            image = load_rgb(tmp_path)

        logging.info("Image loaded successfully")

        segmented_image = segment(image)

        logging.info("Image segmented successfully")

        retval, buffer = cv2.imencode('.jpg', segmented_image)
        segmented_image_bytes = buffer.tobytes()

        return StreamingResponse(io.BytesIO(segmented_image_bytes), media_type="image/jpeg")
    except Exception as e:
        logging.error(f"Error during segmentation: {e}")
        return {"error": str(e)}
