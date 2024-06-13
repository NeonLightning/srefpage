import os
import glob
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from jinja2 import Template

script_dir = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(script_dir, 'external')
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Gallery</title>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: center;
            position: relative; /* Add position relative for numbering */
        }
        img {
            max-width: 100%;
            height: auto;
            cursor: pointer; /* Add cursor pointer for clickable images */
        }
        .number {
            position: absolute;
            top: 0;
            left: 0;
            background-color: rgba(255, 255, 255, 0.8);
            padding: 3px 6px;
            border-radius: 3px;
        }
        .fullsize {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }
        .fullsize img {
            max-width: 90vw;
            max-height: 90vh;
        }
    </style>
</head>
<body>
    <div class="fullsize" id="fullsize">
        <img id="fullsizeImg" src="" alt="Fullsize Image">
    </div>
    <table>
        {% for row in rows %}
        <tr>
            {% for item in row %}
            <td>
                <div class="number">{{ item.unique_number }}</div>
                <p>--sref {{ item.number }}</p>
                <img class="thumbnail" src="external/sref_{{ item.number }}.png" alt="sref_{{ item.number }}">
            </td>
            {% endfor %}
        </tr>
        {% endfor %}
    </table>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            let thumbnails = document.querySelectorAll('.thumbnail');
            let fullsizeImg = document.getElementById('fullsizeImg');
            let fullsize = document.getElementById('fullsize');

            thumbnails.forEach(function(thumbnail) {
                thumbnail.addEventListener('click', function() {
                    fullsizeImg.src = thumbnail.src;
                    fullsize.style.display = 'flex';
                });
            });

            fullsize.addEventListener('click', function() {
                fullsize.style.display = 'none';
            });
        });
    </script>
</body>
</html>
"""

def scan_folder(folder):
    images = glob.glob(os.path.join(folder, 'sref_*.png'))
    image_data = []
    for idx, img in enumerate(sorted(images, key=lambda x: int(os.path.basename(x).split('_')[1].split('.')[0]))):
        filename = os.path.basename(img)
        number = filename.split('_')[1].split('.')[0]
        image_data.append({'unique_number': idx + 1, 'number': number, 'path': img})
    return image_data

def generate_html(image_data):
    rows = [image_data[i:i+3] for i in range(0, len(image_data), 3)]
    template = Template(html_template)
    html_content = template.render(rows=rows)
    with open('index.html', 'w') as f:
        f.write(html_content)

class ImageFolderHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        image_data = scan_folder(folder_path)
        generate_html(image_data)

if __name__ == "__main__":
    image_data = scan_folder(folder_path)
    generate_html(image_data)
    event_handler = ImageFolderHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
