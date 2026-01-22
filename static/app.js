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

    // State
    let isProcessing = false;

    // WebSocket
    let ws;
    connectWebSocket();

    // Prevent Accidental Exit
    window.addEventListener('beforeunload', (e) => {
        if (isProcessing) {
            e.preventDefault();
            e.returnValue = ''; // Required for some browsers
            return '';
        }
    });

    // Event Listeners - Upload
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleUpload);
    }

    if (dropArea) {
        // Enable pointer events on drop-area for drag and drop
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

            // Detect completion or failure
            if (message.includes('🏁') || message.includes('❌') || message.includes('⚠️')) {
                // If it's a critical error before even starting one item, or final finish
                if (message.includes('🏁') || (message.includes('❌') && !message.includes('Qatorni ishlashda'))) {
                    setProcessingState(false);
                }
            }
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

        setProcessingState(true);

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
                setProcessingState(false);
            }

        } catch (error) {
            addMessage('ai', `⚠️ Tarmoq xatoligi: ${error.message}`);
            setProcessingState(false);
        }
    }

    function setProcessingState(processing, status = 'Ishlanmoqda...') {
        isProcessing = processing;
        
        if (processing) {
            uploadBtn.disabled = true;
            uploadBtn.textContent = 'Jarayon...';
        } else {
            uploadBtn.disabled = false;
            uploadBtn.textContent = 'Boshlash';
        }
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

    function scrollToBottom() {
        if (outputArea) {
            outputArea.scrollTo({
                top: outputArea.scrollHeight,
                behavior: 'smooth'
            });
        }
    }
});
