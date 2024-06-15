import time
import os
import glob
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from jinja2 import Template

script_dir = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(script_dir, 'images')
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta property="og:image" content="https://neonlightning.github.io/srefpage/back.png">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Gallery</title>
    <style>
        button {
            position: fixed;
            bottom: 20px;
            left: 20px;
            z-index: 9998;
            font-size: 20px;
        }
        p {
            cursor: pointer;
        }
        body {
            color: rgba(255, 255, 255, 0.8);
            background: black;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
        }

        th, td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        img {
            max-width: 100%;
            height: auto;
            cursor: pointer;
        }
        .fullsize {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: rgba(0, 0, 0, 0.8);
            display: none;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding-top: 5px;
            box-sizing: border-box;
            z-index: 9999;
        }
        .fullsize img {
            width: 100vw;
            height: calc(100vh - 70px);
            object-fit: contain;
            padding-bottom: 20px;
        }
        .fullsize .sref-number {
            margin-bottom: 5px;
            font-size: 20px;
            color: white;
            cursor: pointer;
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
        <p id="fullsizeSref" class="sref-number"></p>
        <img id="fullsizeImg" src="" alt="Fullsize Image">
    </div>
    <button onclick="scrollToRandomCell()">Go to Random Cell</button>
    <h1>"" --v 6.0 --ar 16:9 --sw 1000 --sref</h1>
    <table id="imageTable">
        {% for row in rows %}
        <tr>
            {% for item in row %}
            <td>
                <p class="copy-text">--sref {{ item.number }}</p>
                <img class="thumbnail lozad" data-src="images/sref_{{ item.number }}.png" alt="sref_{{ item.number }}">
            </td>
            {% endfor %}
        </tr>
        {% endfor %}
    </table>
    <div class="total" id="total"></div>
    <script src="https://cdn.jsdelivr.net/npm/lozad/dist/lozad.min.js"></script>
    <script>
        function scrollToRandomCell() {
            let table = document.getElementById('imageTable');
            let rows = table.rows;
            let randomRowIndex = Math.floor(Math.random() * rows.length);
            let randomRow = rows[randomRowIndex];
            let randomCellIndex = Math.floor(Math.random() * randomRow.cells.length);
            let randomCell = randomRow.cells[randomCellIndex];
            randomCell.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        document.addEventListener('DOMContentLoaded', function() {
            const observer = lozad('.lozad', {
                rootMargin: '200px 0px',
            });
            observer.observe();

            let thumbnails = document.querySelectorAll('.thumbnail');
            let fullsizeImg = document.getElementById('fullsizeImg');
            let fullsizeSref = document.getElementById('fullsizeSref');
            let fullsize = document.getElementById('fullsize');
            let total = document.getElementById('total');
            let copyTexts = document.querySelectorAll('.copy-text');
            let currentImage = null;
            let images = Array.from(thumbnails);

            thumbnails.forEach(function(thumbnail) {
                thumbnail.addEventListener('click', function() {
                    currentImage = thumbnail;
                    fullsizeImg.src = thumbnail.src;
                    fullsizeSref.textContent = thumbnail.previousElementSibling.textContent;
                    fullsize.style.display = 'flex';
                    fullsizeImg.style.maxWidth = '100vw';
                    fullsizeImg.style.maxHeight = '100vh';
                    fullsizeImg.classList.add('fade-in');
                });
            });

            fullsize.addEventListener('click', function(event) {
                if (event.target !== fullsizeSref) {
                    fullsize.style.display = 'none';
                    currentImage = null;
                }
            });

            document.addEventListener('keydown', function(event) {
                if (currentImage && event.key === 'Escape') {
                    fullsize.style.display = 'none';
                    currentImage = null;
                } else if (currentImage && event.key === 'ArrowLeft') {
                    navigateImage('left');
                } else if (currentImage && event.key === 'ArrowRight') {
                    navigateImage('right');
                } else if (event.key === ' ') {
                    event.preventDefault(); // Prevent the default spacebar behavior
                    scrollToRandomCell();
                }
            });

            function navigateImage(direction) {
                var currentIndex = images.indexOf(currentImage);
                var newIndex;
                if (!currentImage) {
                    if (direction === 'left') {
                        newIndex = images.length - 1;
                    } else if (direction === 'right') {
                        newIndex = 0;
                    }
                } else {
                    if (direction === 'left') {
                        newIndex = (currentIndex - 1 + images.length) % images.length;
                    } else if (direction === 'right') {
                        newIndex = (currentIndex + 1) % images.length;
                    }
                }
                var newImage = images[newIndex];
                toggleFullsize({ target: newImage });
            }

            function toggleFullsize(event) {
                currentImage = event.target;
                fullsizeImg.src = currentImage.src;
                fullsizeSref.textContent = currentImage.previousElementSibling.textContent;
                fullsize.style.display = 'flex';
                fullsizeImg.style.maxWidth = '100vw';
                fullsizeImg.style.maxHeight = '100vh';
                fullsizeImg.classList.add('fade-in');
            }

            let table = document.getElementById('imageTable');
            let rowCount = table.rows.length;
            let cellCount = 0;
            for (let i = 0; i < rowCount; i++) {
                cellCount += table.rows[i].cells.length;
            }
            total.innerText = 'Total cells: ' + cellCount;

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
            fullsizeSref.addEventListener('click', function() {
                let textToCopy = fullsizeSref.textContent;
                navigator.clipboard.writeText(textToCopy).then(function() {
                    alert('Copied to clipboard: ' + textToCopy);
                }).catch(function(error) {
                    console.error('Failed to copy text: ', error);
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
    rows = [image_data[i:i+4] for i in range(0, len(image_data), 4)]
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
