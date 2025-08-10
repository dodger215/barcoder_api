from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import qrcode
import io
import re

app = FastAPI(
    title="QR Code Generator API",
    description="API for generating QR code images from text input",
    version="1.0.0",
    contact={
        "name": "Ked",
        "email": "kelvinenosdzah2@gmail.com"
    },
    license_info={
        "name": "MIT License",
    },
    docs_url=None,
    redoc_url="/"
)

def sanitize_filename(filename: str) -> str:
    """Sanitize the filename by removing special characters and limiting length."""
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    return filename[:100]

@app.get("/qrcode", summary="Generate QR Code")
async def generate_qrcode(
    data: str = Query(..., min_length=1, description="Data to encode in QR code"),
    size: int = Query(10, ge=1, le=40, description="Box size (pixels per module)"),
    border: int = Query(4, ge=1, description="Border size (in modules)"),
    fill_color: str = Query("black", description="QR code color"),
    back_color: str = Query("white", description="Background color"),
    version: int = Query(1, ge=1, le=40, description="QR code version (1-40)"),
    error_correction: str = Query("L", description="Error correction level (L, M, Q, H)")
):
    """
    Generate a QR code image from the provided data.
    
    Parameters:
    - data: The text/data to encode in the QR code
    - size: Controls how many pixels each "box" of the QR code is
    - border: How thick the quiet zone around the QR code should be
    - fill_color: Color of the QR code (name or hex value)
    - back_color: Background color (name or hex value)
    - version: QR code version (1-40) that controls data capacity
    - error_correction: Error correction level (L=7%, M=15%, Q=25%, H=30%)
    """
    # Sanitize input filename
    clean_data = sanitize_filename(data)
    
    # Map error correction string to constant
    error_map = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H
    }
    
    # Create QR code instance
    qr = qrcode.QRCode(
        version=version,
        error_correction=error_map.get(error_correction.upper(), qrcode.constants.ERROR_CORRECT_L),
        box_size=size,
        border=border,
    )
    
    # Add data and make QR code
    qr.add_data(clean_data)
    qr.make(fit=True)
    
    # Create image with specified colors
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    
    # Save to bytes buffer
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename=qrcode_{clean_data}.png"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)