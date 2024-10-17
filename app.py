from flask import Flask, redirect, render_template, request, send_file
import os
import yt_dlp

# Setting up the app
app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"

# Configue main
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/downloads", methods=["GET", "POST"])
def downloads():
    link = request.form.get("link")
    format = request.form.get("format").lower()
    ydl_opts = get_options(format=format)

    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            video_file = ydl.prepare_filename(info_dict)

            if format == "audio":
                video_file = video_file.replace(".webm", ".mp3")  # or the appropriate extension
            
            if os.path.exists(video_file):
                return send_file(video_file, as_attachment=True)
            else:
                return render_template("index.html", error="File not found after download.")

    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return render_template("index.html", error="An error occurred while processing the download.")


def get_options(format):
    ydl_opts = {
    'format': 'best',  # 'best' or 'worst', 'bestaudio', etc.
    'outtmpl': os.path.join(DOWNLOAD_FOLDER,'%(title)s.%(ext)s'),  # save as title.ext (ext refers to file format)
    }

    if format == "low":
        ydl_opts["format"] = "worst"
    elif format == "audio":

        ydl_opts["format"] = "bestaudio"
        ydl_opts["postprocessors"] = [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
        }]
    return ydl_opts