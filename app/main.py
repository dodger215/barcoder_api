from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import barcode
from barcode.writer import ImageWriter
import io
import re

app = FastAPI(
    title="Barcode Generate API",  
    description="This API allows User to generate barcode image", 
    version="1.0.0",
    contact={
        "name": "Ked",
        "email": "kelvinenosdzah2@gmail.com"
    },
    docs_url=None, 
    redoc_url="/"
)

def sanitize_filename(filename):
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    return filename[:100]

@app.get("/barcode")
def generate_barcode(id: str = Query(..., min_length=1)):
    clean_id = sanitize_filename(id)

    Code128 = barcode.get_barcode_class('code128')
    barcode_obj = Code128(clean_id, writer=ImageWriter())

    buffer = io.BytesIO()
    barcode_obj.write(buffer)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename=barcode_{clean_id}.png"}
    )
