import barcode
from barcode.writer import ImageWriter


id_value = "1234"


Code128 = barcode.get_barcode_class('code128')


barcode_obj = Code128(id_value, writer=ImageWriter())


filename = barcode_obj.save("id_barcode")

print(f"✅ Barcode saved as {filename}.png (ID only)")
