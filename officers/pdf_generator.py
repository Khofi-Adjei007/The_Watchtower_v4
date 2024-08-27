from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_pdf(data):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y_position = height - 40
    for key, value in data.items():
        p.drawString(40, y_position, f"{key}: {value}")
        y_position -= 20

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
