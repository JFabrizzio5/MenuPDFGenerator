from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from fpdf import FPDF
import re

app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json

    # Imprimir los datos recibidos para depuración
    print("Datos recibidos:")
    print("Imagen (inicio):", data.get('image', '')[:50], "...")  # Mostrar una parte del inicio de los datos de la imagen
    print("Artículos:", data.get('items', []))
    print("Etiquetas:", data.get('labels', []))

    image_data = data['image']
    items = data['items']
    labels = data['labels']

    image_data = image_data.split(",")[1]
    image_bytes = base64.b64decode(image_data)

    image = Image.open(io.BytesIO(image_bytes))
    image_path = 'uploaded_image.png'

    # Crear un único PDF con todas las etiquetas
    output_path = 'output.pdf'
    pdf = FPDF()

    # Filtrar etiquetas que contienen números
    filtered_labels = [label for label in labels if re.match(r'\d+', label['text'])]

    # Dividir los artículos en grupos según la cantidad de etiquetas por página
    items_per_page = len(filtered_labels)
    num_pages = (len(items) + items_per_page - 1) // items_per_page

    for page in range(num_pages):
        pdf.add_page()

        # Crear una nueva imagen base para cada página para evitar sobreescritura
        img_with_labels = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        draw = ImageDraw.Draw(img_with_labels)
        font = ImageFont.load_default()

        # Obtener el índice de inicio y fin para los artículos actuales
        start_index = page * items_per_page
        end_index = min(start_index + items_per_page, len(items))

        print(f"Página {page + 1}: Asignando artículos de índice {start_index} a {end_index - 1}")

        for index, label in enumerate(filtered_labels):
            if start_index + index >= len(items):
                break
            x, y = label['x'], label['y']
            text = items[start_index + index]
            print(f"Etiqueta {index}: {text} en posición ({x}, {y})")  # Imprimir texto y posición de cada etiqueta
            draw.text((x, y), text, font=font, fill='black')

        # Guardar la imagen con etiquetas para cada página
        temp_image_path = f"temp_image_with_labels_page_{page + 1}.png"
        img_with_labels.save(temp_image_path)
        pdf.image(temp_image_path, 0, 0, 210, 297)

    pdf.output(output_path)

    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(port=5000)
