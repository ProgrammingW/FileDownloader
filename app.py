import yt_dlp
from flask import Flask, request, render_template, Response
import io

app = Flask(__name__)

def stream_youtube_video(url):
    try:
        # Configura las opciones de yt-dlp para transmitir el video
        ydl_opts = {
            'format': 'best',  # Descargar el mejor formato disponible
            'quiet': True,     # No mostrar mensajes de progreso
            'outtmpl': '-',    # Salida estándar, lo que significa no guardar el archivo
            'noplaylist': True, # Para evitar descargar listas de reproducción
            'extractaudio': False # Si no queremos solo el audio
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extrae la información y descarga el video
            info_dict = ydl.extract_info(url, download=True)  # download=True para obtener el video
            video_title = info_dict.get('title', 'video')  # Nombre del video

            # Obtiene la URL de la mejor calidad del video
            video_url = info_dict.get('url')
            
            if not video_url:
                raise Exception('No se pudo obtener la URL del video.')

            # Usar yt-dlp para obtener el video en formato de flujo y enviarlo
            with ydl.urlopen(video_url) as video_data:
                return Response(video_data.read(), content_type='video/mp4', headers={
                    'Content-Disposition': f'attachment; filename={video_title}.mp4'
                })

    except Exception as e:
        return str(e), 500

@app.route("/", methods=["GET", "POST"])
def home():
    message = None
    if request.method == "POST":
        youtube_url = request.form.get("url")
        if youtube_url:
            try:
                return stream_youtube_video(youtube_url)
            except Exception as e:
                message = f"Error: {e}"
    return render_template("index.html", message=message)

if __name__ == "__main__":
    app.run(debug=True)
