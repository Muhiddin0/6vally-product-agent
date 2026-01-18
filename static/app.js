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
            <div class="space-y-4">
                <p class="font-semibold text-emerald-400 flex items-center gap-2">
                    <span class="text-lg">✅</span> Muvaffaqiyatli yaratildi!
                </p>
                <div class="space-y-1">
                    <p><span class="text-slate-400">Nom (UZ):</span> ${data.name_uz}</p>
                    <p><span class="text-slate-400">Nom (RU):</span> ${data.name_ru}</p>
                </div>
                <div class="p-3 bg-black/20 rounded-lg border border-white/5 text-sm">
                    <span class="text-slate-400">Tavsif (UZ):</span><br>
                    <p class="mt-1">${data.description_uz.substring(0, 150)}...</p>
                </div>
                <div>
                    <span class="text-slate-400 text-sm">Meta Teglar:</span>
                    <div class="flex flex-wrap gap-2 mt-2">
                        ${data.meta_tags.map(tag => `<span class="px-2 py-0.5 bg-primary/10 border border-primary/20 rounded-md text-xs text-primary-400">${tag}</span>`).join('')}
                    </div>
                </div>
            </div>
        `;

        if (data.shop_response) {
            contentHtml += `<div class="mt-4 pt-4 border-t border-white/5 text-xs italic text-slate-500 text-right">Do'kon holati: ${data.shop_response}</div>`;
        }

        if (data.product_images && data.product_images.length > 0) {
            contentHtml += `<div class="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-4">`;
            data.product_images.forEach(imgUrl => {
                contentHtml += `
                    <div class="aspect-square overflow-hidden rounded-lg border border-white/10 group cursor-pointer hover:border-primary transition-all">
                        <img src="${imgUrl}" alt="Product" class="w-full h-full object-cover group-hover:scale-110 transition-transform" onclick="window.open('${imgUrl}', '_blank')">
                    </div>
                `;
            });
            contentHtml += `</div>`;
        }

        addMessage('ai', contentHtml);
    }

    function addMessage(sender, htmlContent) {
        const isAi = sender === 'ai';
        const msgDiv = document.createElement('div');
        msgDiv.className = `flex gap-4 max-w-[90%] animate-in fade-in slide-in-from-bottom-4 duration-300 ${!isAi ? 'flex-row-reverse ml-auto' : ''}`;

        const avatar = document.createElement('div');
        avatar.className = `w-10 h-10 rounded-full flex items-center justify-center text-xl flex-shrink-0 shadow-lg ${isAi ? 'bg-accent shadow-accent/20' : 'bg-primary shadow-primary/20'}`;
        avatar.textContent = isAi ? '🤖' : '👤';

        const content = document.createElement('div');
        content.className = `border rounded-2xl p-4 leading-relaxed text-[0.95rem] ${
            isAi 
            ? 'bg-white/5 border-white/10 rounded-tl-none' 
            : 'bg-primary/20 border-primary/30 rounded-tr-none text-white'
        }`;
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
        msgDiv.className = `flex gap-4 max-w-[90%] animate-in fade-in slide-in-from-bottom-4 duration-300`;
        msgDiv.id = id;

        const avatar = document.createElement('div');
        avatar.className = 'w-10 h-10 rounded-full bg-accent flex items-center justify-center text-xl flex-shrink-0 shadow-lg shadow-accent/20';
        avatar.textContent = '🤖';

        const content = document.createElement('div');
        content.className = 'bg-white/5 border border-white/10 rounded-2xl rounded-tl-none p-4 flex gap-1';
        content.innerHTML = `
            <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
            <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
            <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></span>
        `;

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(content);

        outputArea.appendChild(msgDiv);
        scrollToBottom();
        return id;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function setLoading(isLoading) {
        // Kept for compatibility if used by other parts of the app
    }

    function scrollToBottom() {
        if (outputArea) {
            outputArea.scrollTo({
                top: outputArea.scrollHeight,
                behavior: 'smooth'
            });
        }
    }
});
