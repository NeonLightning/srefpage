import time
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
<meta property="og:image" content="https://neonlightning.github.io/srefpage/back.png">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Gallery</title>
    <style>
        p {
            color: rgba(255, 255, 255, 0.8);
            cursor: pointer; /* Add cursor pointer for clickable paragraphs */
        }
        body {
            background: black;
        }
		table {
			width: 100%;
			border-collapse: collapse;
			table-layout: fixed; /* Ensure fixed layout */
		}

		th, td {
			border: 1px solid #ddd;
			padding: 10px;
			text-align: center;
			position: relative; /* Add position relative for numbering */
			overflow: hidden; /* Hide overflow content */
		}
        img {
            max-width: 100%;
            height: auto;
            cursor: pointer; /* Add cursor pointer for clickable images */
        }
        .fullsize {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: rgba(0, 0, 0, 0.8);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }
		.fullsize img {
			width: 100vw;
			height: 100vh;
			object-fit: contain;
		}
        .total {
            text-align: center;
            margin-top: 10px;
            font-size: 20px;
            color: white;
        }
        .fade-in {
            animation: fadeIn 1s forwards;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="fullsize" id="fullsize">
        <img id="fullsizeImg" src="" alt="Fullsize Image">
    </div>
    <table id="imageTable">
        {% for row in rows %}
        <tr>
            {% for item in row %}
            <td>
                <p class="copy-text">--sref {{ item.number }}</p>
                <img class="thumbnail" src="external/sref_{{ item.number }}.png" alt="sref_{{ item.number }}">
            </td>
            {% endfor %}
        </tr>
        {% endfor %}
    </table>
    <div class="total" id="total"></div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            let thumbnails = document.querySelectorAll('.thumbnail');
            let fullsizeImg = document.getElementById('fullsizeImg');
            let fullsize = document.getElementById('fullsize');
            let total = document.getElementById('total');
            let copyTexts = document.querySelectorAll('.copy-text');

            thumbnails.forEach(function(thumbnail) {
                thumbnail.addEventListener('click', function() {
                    fullsizeImg.src = thumbnail.src;
                    fullsize.style.display = 'flex';
                    fullsizeImg.style.maxWidth = '100vw'; // Set max-width to 100vw
                    fullsizeImg.style.maxHeight = '100vh'; // Set max-height to 100vh
                    fullsizeImg.classList.add('fade-in');
                });
            });

            fullsize.addEventListener('click', function() {
                fullsize.style.display = 'none';
            });

            // Count cells
            let table = document.getElementById('imageTable');
            let rowCount = table.rows.length;
            let cellCount = 0;
            for (let i = 0; i < rowCount; i++) {
                cellCount += table.rows[i].cells.length;
            }
            total.innerText = 'Total cells: ' + cellCount;

            // Add event listener for copying text
            copyTexts.forEach(function(copyText) {
                copyText.addEventListener('click', function() {
                    let textToCopy = copyText.innerText;
                    navigator.clipboard.writeText(textToCopy).then(function() {
                        alert('Copied to clipboard: ' + textToCopy);
                    }).catch(function(error) {
                        console.error('Failed to copy text: ', error);
                    });
                });
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
        time.sleep(10)

if __name__ == "__main__":
    image_data = scan_folder(folder_path)
    generate_html(image_data)
    event_handler = ImageFolderHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(5)
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
