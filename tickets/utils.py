import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

def generate_ticket_qr(ticket_data):
    """
    Generates a QR code image from the given data string.
    Returns a ContentFile for Django ImageField.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(ticket_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    file_name = f'qr_ticket_{ticket_data[:10]}.png'
    
    return ContentFile(buffer.getvalue(), file_name)
