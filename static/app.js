document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements - Chat
    const outputArea = document.getElementById('output-area');

    // DOM Elements - Upload
    const uploadForm = document.getElementById('upload-form');
    const venuEmailInput = document.getElementById('venu-email');
    const venuPasswordInput = document.getElementById('venu-password');
    const excelFileInput = document.getElementById('excel-file');
    const uploadBtn = document.getElementById('upload-btn');
    const dropArea = document.getElementById('drop-area');

    // WebSocket
    let ws;
    connectWebSocket();

    // Event Listeners - Chat


    // Event Listeners - Upload
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleUpload);
    }

    if (dropArea) {
        dropArea.addEventListener('click', () => excelFileInput.click());
        dropArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropArea.classList.add('drag-over');
        });
        dropArea.addEventListener('dragleave', () => dropArea.classList.remove('drag-over'));
        dropArea.addEventListener('drop', (e) => {
            e.preventDefault();
            dropArea.classList.remove('drag-over');
            if (e.dataTransfer.files.length) {
                excelFileInput.files = e.dataTransfer.files;
                updateFileMsg(e.dataTransfer.files[0].name);
            }
        });

        excelFileInput.addEventListener('change', () => {
            if (excelFileInput.files.length) {
                updateFileMsg(excelFileInput.files[0].name);
            }
        });
    }

    function updateFileMsg(name) {
        dropArea.querySelector('.file-msg').textContent = name;
    }

    // WebSocket Connection
    function connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

        ws.onopen = () => {
            console.log('WebSocket connected');
        };

        ws.onmessage = (event) => {
            const message = event.data;
            // Treat as AI log
            addMessage('ai', `<em>[LOG]</em> ${message}`);
            scrollToBottom();
        };

        ws.onclose = () => {
            console.log('WebSocket disconnected. Reconnecting in 3s...');
            setTimeout(connectWebSocket, 3000);
        };
    }

    // Handlers
    async function handleUpload(e) {
        e.preventDefault();

        const email = venuEmailInput.value.trim();
        const password = venuPasswordInput.value.trim();
        const file = excelFileInput.files[0];

        if (!email || !password || !file) {
            alert("Barcha maydonlarni to'ldiring va fayl tanlang!");
            return;
        }

        const formData = new FormData();
        formData.append('email', email);
        formData.append('password', password);
        formData.append('file', file);

        uploadBtn.disabled = true;
        uploadBtn.textContent = 'Yuklanmoqda...';

        addMessage('user', `📂 Excel yuklash boshlandi: ${file.name}`);

        try {
            const response = await fetch('/upload-excel', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                addMessage('ai', `✅ Fayl qabul qilindi. Jarayonni kuzatib boring...`);
            } else {
                addMessage('ai', `⚠️ Xatolik: ${data.detail || 'Noma\'lum xatolik'}`);
            }

        } catch (error) {
            addMessage('ai', `⚠️ Tarmoq xatoligi: ${error.message}`);
        } finally {
            uploadBtn.disabled = false;
            uploadBtn.textContent = 'Boshlash';
        }
    }



    function displayResult(data) {
        let contentHtml = `
            <strong>Muvaffaqiyatli yaratildi! ✅</strong><br><br>
            <strong>Nom (UZ):</strong> ${data.name_uz}<br>
            <strong>Nom (RU):</strong> ${data.name_ru}<br><br>
            <strong>Tavsif (UZ):</strong><br>${data.description_uz.substring(0, 100)}...<br><br>
            <strong>Meta Teglar:</strong> ${data.meta_tags.join(', ')}
        `;

        if (data.shop_response) {
            contentHtml += `<br><br><em>Do'kon holati: ${data.shop_response}</em>`;
        }

        if (data.product_images && data.product_images.length > 0) {
            contentHtml += `<div class="product-images">`;
            data.product_images.forEach(imgUrl => {
                contentHtml += `<img src="${imgUrl}" alt="Product Image" onclick="window.open('${imgUrl}', '_blank')">`;
            });
            contentHtml += `</div>`;
        }

        addMessage('ai', contentHtml);
    }

    function addMessage(sender, htmlContent) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = sender === 'ai' ? '🤖' : '👤';

        const content = document.createElement('div');
        content.className = 'content';
        content.innerHTML = htmlContent;

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(content);

        outputArea.appendChild(msgDiv);
        scrollToBottom();
        return msgDiv.id = 'msg-' + Date.now();
    }

    function addLoadingIndicator() {
        const id = 'loading-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ai`;
        msgDiv.id = id;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = '🤖';

        const content = document.createElement('div');
        content.className = 'content typing-indicator';
        content.innerHTML = '<span></span><span></span><span></span>';

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(content);

        outputArea.appendChild(msgDiv);
        return id;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function setLoading(isLoading) {
        // No-op or remove if unused elsewhere, but kept for compatibility just in case
        /*
        sendBtn.disabled = isLoading;
        if (productNameInput) productNameInput.disabled = isLoading;
        if (productBrandInput) productBrandInput.disabled = isLoading;

        if (isLoading) {
            sendBtn.innerHTML = '<span>Jarayonda...</span>';
        } else {
            sendBtn.innerHTML = '<span>Yaratish</span><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>';
        }
        */
    }

    function scrollToBottom() {
        if (outputArea) {
            outputArea.scrollTop = outputArea.scrollHeight;
        }
    }
});
