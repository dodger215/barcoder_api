from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import qrcode
import io
import re
from datetime import datetime
import json
from typing import Optional
import uuid

app = FastAPI(
    title="QR Code Generator API",
    description="API for generating QR code images from text input with enhanced vehicle data support",
    version="2.0.0",
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

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def sanitize_filename(filename: str) -> str:
    """Sanitize the filename by removing special characters and limiting length."""
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    return filename[:100]

def validate_vehicle_data(data: dict) -> bool:
    """Validate required vehicle data fields."""
    required_fields = [
        'brandid', 'vehiclename', 'modelnumber', 'regnumber',
        'vehicletype', 'vehiclesubtype', 'varient', 'transmission',
        'chasisnum', 'enginenumber'
    ]
    return all(field in data and data[field] for field in required_fields)

def generate_vehicle_qr_data(data: dict) -> str:
    """Generate structured QR data from vehicle information."""
    qr_data = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "vehicle": {
            "brand": data.get('brandid', ''),
            "name": data.get('vehiclename', ''),
            "model": data.get('modelnumber', ''),
            "reg": data.get('regnumber', ''),
            "type": data.get('vehicletype', ''),
            "subtype": data.get('vehiclesubtype', ''),
            "variant": data.get('varient', ''),
            "transmission": data.get('transmission', ''),
            "chassis": data.get('chasisnum', ''),
            "engine": data.get('enginenumber', ''),
            "description": data.get('description', '')
        },
        "system": {
            "generated_by": "QR Code API",
            "version": "2.0"
        }
    }
    return json.dumps(qr_data)

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
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {str(e)}")

@app.post("/qrcode/vehicle", summary="Generate Vehicle QR Code")
async def generate_vehicle_qrcode(
    brandid: str = Query(..., description="Brand ID"),
    vehiclename: str = Query(..., description="Vehicle name"),
    modelnumber: str = Query(..., description="Model number"),
    regnumber: str = Query(..., description="Registration number"),
    vehicletype: str = Query(..., description="Vehicle type"),
    vehiclesubtype: str = Query(..., description="Vehicle subtype"),
    varient: str = Query(..., description="Variant"),
    transmission: str = Query(..., description="Transmission type"),
    chasisnum: str = Query(..., description="Chassis number"),
    enginenumber: str = Query(..., description="Engine number"),
    description: Optional[str] = Query("", description="Vehicle description"),
    size: int = Query(10, ge=1, le=40, description="Box size (pixels per module)"),
    border: int = Query(4, ge=1, description="Border size (in modules)"),
    fill_color: str = Query("black", description="QR code color"),
    back_color: str = Query("white", description="Background color"),
    version: int = Query(1, ge=1, le=40, description="QR code version (1-40)"),
    error_correction: str = Query("L", description="Error correction level (L, M, Q, H)")
):
    """
    Generate a QR code for vehicle information with structured data.
    Returns both the QR code image and the encoded data.
    """
    try:
        vehicle_data = {
            'brandid': brandid,
            'vehiclename': vehiclename,
            'modelnumber': modelnumber,
            'regnumber': regnumber,
            'vehicletype': vehicletype,
            'vehiclesubtype': vehiclesubtype,
            'varient': varient,
            'transmission': transmission,
            'chasisnum': chasisnum,
            'enginenumber': enginenumber,
            'description': description
        }
        
        if not validate_vehicle_data(vehicle_data):
            raise HTTPException(status_code=400, detail="Missing required vehicle data fields")
        
        qr_data = generate_vehicle_qr_data(vehicle_data)
        clean_data = sanitize_filename(f"{vehicle_data['vehiclename']}_{vehicle_data['regnumber']}")
        
        # Generate QR code
        error_map = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H
        }
        
        qr = qrcode.QRCode(
            version=version,
            error_correction=error_map.get(error_correction.upper(), qrcode.constants.ERROR_CORRECT_L),
            box_size=size,
            border=border,
        )
        
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        return {
            "qr_code": StreamingResponse(
                buffer,
                media_type="image/png",
                headers={"Content-Disposition": f"attachment; filename=vehicle_qr_{clean_data}.png"}
            ),
            "qr_data": qr_data,
            "vehicle_info": vehicle_data,
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "api_version": "2.0"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vehicle QR generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
