import io
import os
import base64
import json
import qrcode
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, render_template_string

app = Flask(__name__)

FONT_PATH = os.path.join(
    os.path.dirname(__file__),
    "dejavu-sans-bold.ttf"
)

def generate_qr(qr_type):
    now = datetime.now()
    refresh_time = now.replace(hour=5, minute=0, second=0, microsecond=0)

    if now < refresh_time:
        refresh_time -= timedelta(days=1)

    payload = {
        "id": 1,
        "lemdikId": 4,
        "createdAt": refresh_time.isoformat(),
        "type": qr_type
    }
    payload_json = json.dumps(payload)

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )


    qr.add_data(payload_json)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color='black', back_color='white').convert("RGB")

    title = qr_type
    padding = 50
    width, height = qr_img.size

    new_img = Image.new("RGB", (width, height + padding), 'white')
    new_img.paste(qr_img, (0, 0))

    draw = ImageDraw.Draw(new_img)
    font = ImageFont.truetype(FONT_PATH, 20)

    box = draw.textbbox((0, 0), title, font=font)
    text_width = box[2] - box[0]
    text_x = (width - text_width) / 2
    text_y = height + (padding - (box[3] - box[1])) / 2

    draw.text((text_x, text_y), title, fill='black', font=font)

    # new_img.save(f"{qr_type.lower().replace(' ', '_')}.png")

    img_io = io.BytesIO()
    new_img.save(img_io, 'PNG')
    img_io.seek(0)

    return base64.b64encode(img_io.getvalue()).decode('utf-8')


@app.route('/')
def index():
    # Generate both strings instantly on page load/refresh
    qr_datang = generate_qr("QR Datang")
    qr_pulang = generate_qr("QR Pulang")

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="refresh" content="300">
        <title>Scan QR Attendance</title>
        <style>
            body {{ font-family: system-ui, sans-serif; background: #f4f6f9; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }}
            h1 {{ color: #2c3e50; margin-bottom: 30px; }}
            .container {{ display: flex; gap: 100px; flex-wrap: wrap; justify-content: center; }}
            .qr-card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); text-align: center; }}
        </style>
        <script>
            function scheduleRefresh() {{
                const now = new Date();
                const next = new Date();

                next.setHours(5, 0, 0, 0);

                if (now >= next) {{
                    next.setDate(next.getDate() + 1);
                }}

                const delay = next - now;

                setTimeout(() => {{
                    window.location.reload();
                }}, delay);
            }}

            scheduleRefresh();
        </script>
    </head>
    <body>

        <h1>Digits QR</h1>

        <div class="container">
            <div class="qr-card">
                <img src="data:image/png;base64,{qr_datang}" alt="QR Datang">
            </div>
            <div class="qr-card">
                <img src="data:image/png;base64,{qr_pulang}" alt="QR Pulang">
            </div>
        </div>

        <!-- Single button to refresh/regenerate both QR codes with new timestamps -->

    </body>
    </html>
    """
    return render_template_string(html_template)

if __name__ == "__main__":
    app.run(debug=True)
