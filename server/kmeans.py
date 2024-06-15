import io
import numpy as np
import cv2
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import tempfile
from   weights.kmeans_model import segment_image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8081"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

logging.basicConfig(level=logging.DEBUG)

@app.post("/segment")
async def segment_image_endpoint(file: UploadFile = File(...)):
    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_path = os.path.join(tmpdirname, file.filename)
            
            with open(tmp_path, "wb") as tmp_file:
                tmp_file.write(await file.read())

            segmented_image = segment_image(tmp_path)

        logging.info("Image segmented successfully")

        retval, buffer = cv2.imencode('.jpg', cv2.cvtColor(segmented_image, cv2.COLOR_RGB2BGR))
        segmented_image_bytes = buffer.tobytes()

        return StreamingResponse(io.BytesIO(segmented_image_bytes), media_type="image/jpeg")
    
    except Exception as e:
        logging.error(f"Error during segmentation: {e}")
        return {"error": str(e)}

