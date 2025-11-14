// Elementos del DOM
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const selectFileBtn = document.getElementById('selectFileBtn');
const uploadSection = document.getElementById('uploadSection');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const evaluateBtn = document.getElementById('evaluateBtn');
const processingSection = document.getElementById('processingSection');
const resultsSection = document.getElementById('resultsSection');
const newEvaluationBtn = document.getElementById('newEvaluationBtn');

// Chat elements
const chatPanel = document.getElementById('chatPanel');
const chatToggle = document.getElementById('chatToggle');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const chatSendBtn = document.getElementById('chatSendBtn');
const chatStatus = document.getElementById('chatStatus');

let selectedFile = null;
let currentEvaluation = null;
let currentEssayText = null;

// Event Listeners
selectFileBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
evaluateBtn.addEventListener('click', evaluateEssay);
newEvaluationBtn.addEventListener('click', resetEvaluation);

// Chat event listeners
chatToggle.addEventListener('click', toggleChat);
chatSendBtn.addEventListener('click', sendChatMessage);
chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendChatMessage();
    }
});

// Drag and Drop
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type === 'application/pdf') {
        handleFile(files[0]);
    } else {
        alert('Por favor, selecciona un archivo PDF válido.');
    }
});

// Manejo de archivos
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
        handleFile(file);
    } else {
        alert('Por favor, selecciona un archivo PDF válido.');
    }
}

function handleFile(file) {
    selectedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    
    dropZone.style.display = 'none';
    fileInfo.style.display = 'flex';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Evaluación del ensayo
async function evaluateEssay() {
    if (!selectedFile) {
        alert('Por favor, selecciona un archivo primero.');
        return;
    }

    // Mostrar sección de procesamiento
    uploadSection.style.display = 'none';
    processingSection.style.display = 'block';
    resultsSection.style.display = 'none';

    try {
        // Crear FormData para enviar el archivo
        const formData = new FormData();
        formData.append('file', selectedFile);

        // Enviar al backend
        const response = await fetch('/evaluate', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Error al procesar el archivo');
        }

        const result = await response.json();
        
        // Guardar evaluación y texto para el chat
        currentEvaluation = result;
        
        // Mostrar resultados
        displayResults(result);
        
        // Habilitar chat
        enableChat();
    } catch (error) {
        console.error('Error:', error);
        alert('Hubo un error al procesar el ensayo. Por favor, intenta nuevamente.');
        resetEvaluation();
    }
}

// Mostrar resultados
function displayResults(evaluation) {
    // Ocultar procesamiento y mostrar resultados
    processingSection.style.display = 'none';
    resultsSection.style.display = 'block';

    // Puntuación total
    const totalScore = evaluation.puntuacion_total || 0;
    document.getElementById('totalScore').textContent = totalScore.toFixed(2);
    
    // Animar barra de progreso
    const scoreFill = document.getElementById('scoreFill');
    const percentage = (totalScore / 5) * 100;
    setTimeout(() => {
        scoreFill.style.width = percentage + '%';
    }, 100);

    // Criterio 1: Calidad Técnica
    if (evaluation.calidad_tecnica) {
        document.getElementById('score1').textContent = 
            `${evaluation.calidad_tecnica.calificacion}/5`;
        document.getElementById('comment1').textContent = 
            evaluation.calidad_tecnica.comentario;
    }

    // Criterio 2: Creatividad
    if (evaluation.creatividad) {
        document.getElementById('score2').textContent = 
            `${evaluation.creatividad.calificacion}/5`;
        document.getElementById('comment2').textContent = 
            evaluation.creatividad.comentario;
    }

    // Criterio 3: Vinculación Temática
    if (evaluation.vinculacion_tematica) {
        document.getElementById('score3').textContent = 
            `${evaluation.vinculacion_tematica.calificacion}/5`;
        document.getElementById('comment3').textContent = 
            evaluation.vinculacion_tematica.comentario;
    }

    // Criterio 4: Bienestar Colectivo
    if (evaluation.bienestar_colectivo) {
        document.getElementById('score4').textContent = 
            `${evaluation.bienestar_colectivo.calificacion}/5`;
        document.getElementById('comment4').textContent = 
            evaluation.bienestar_colectivo.comentario;
    }

    // Criterio 5: Potencial de Impacto
    if (evaluation.potencial_impacto) {
        document.getElementById('score5').textContent = 
            `${evaluation.potencial_impacto.calificacion}/5`;
        document.getElementById('comment5').textContent = 
            evaluation.potencial_impacto.comentario;
    }

    // Comentario general (si existe)
    if (evaluation.comentario_general) {
        document.getElementById('generalComment').style.display = 'block';
        document.getElementById('generalCommentText').textContent = 
            evaluation.comentario_general;
    }

    // Scroll suave a los resultados
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Reiniciar evaluación
function resetEvaluation() {
    selectedFile = null;
    fileInput.value = '';
    
    uploadSection.style.display = 'block';
    dropZone.style.display = 'block';
    fileInfo.style.display = 'none';
    processingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    
    // Limpiar resultados
    document.getElementById('totalScore').textContent = '0.00';
    document.getElementById('scoreFill').style.width = '0%';
    
    for (let i = 1; i <= 5; i++) {
        document.getElementById(`score${i}`).textContent = '-';
        document.getElementById(`comment${i}`).textContent = '';
    }
    
    document.getElementById('generalComment').style.display = 'none';
    document.getElementById('generalCommentText').textContent = '';
    
    // Deshabilitar y limpiar chat
    disableChat();
    
    // Scroll al inicio
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Chat functionality
function toggleChat() {
    chatPanel.classList.toggle('minimized');
    const icon = chatToggle.querySelector('svg path');
    
    if (chatPanel.classList.contains('minimized')) {
        icon.setAttribute('d', 'M19 9l-7 7-7-7');
    } else {
        icon.setAttribute('d', 'M6 18L18 6M6 6l12 12');
    }
}

function enableChat() {
    chatInput.disabled = false;
    chatSendBtn.disabled = false;
    chatInput.placeholder = 'Escriba su consulta sobre la evaluación...';
    
    // Agregar mensaje de bienvenida contextual
    addChatMessage('assistant', 
        'La evaluación ha sido completada. Ahora puede realizar consultas específicas sobre los resultados, ' +
        'solicitar aclaraciones sobre algún criterio, o pedir recomendaciones para mejorar el ensayo.'
    );
}

function disableChat() {
    chatInput.disabled = true;
    chatSendBtn.disabled = true;
    chatInput.value = '';
    chatInput.placeholder = 'Primero debe evaluar un ensayo...';
    currentEvaluation = null;
    currentEssayText = null;
    
    // Limpiar mensajes excepto el inicial
    const messages = chatMessages.querySelectorAll('.chat-message');
    messages.forEach((msg, index) => {
        if (index > 0) msg.remove();
    });
}

function addChatMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? 'UD' : 'IA';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Parsear saltos de línea
    const paragraphs = content.split('\n').filter(p => p.trim());
    paragraphs.forEach(p => {
        const para = document.createElement('p');
        para.textContent = p;
        contentDiv.appendChild(para);
    });
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll al último mensaje
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendChatMessage() {
    const message = chatInput.value.trim();
    
    if (!message || !currentEvaluation) return;
    
    // Agregar mensaje del usuario
    addChatMessage('user', message);
    chatInput.value = '';
    
    // Mostrar estado de carga
    chatSendBtn.disabled = true;
    chatStatus.style.display = 'flex';
    
    try {
        // Enviar al backend
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                evaluation: currentEvaluation
            })
        });
        
        if (!response.ok) {
            throw new Error('Error al procesar la consulta');
        }
        
        const result = await response.json();
        
        // Agregar respuesta del asistente
        addChatMessage('assistant', result.response);
        
    } catch (error) {
        console.error('Error:', error);
        addChatMessage('assistant', 
            'Disculpe, ha ocurrido un error al procesar su consulta. Por favor, intente nuevamente.'
        );
    } finally {
        chatStatus.style.display = 'none';
        chatSendBtn.disabled = false;
        chatInput.focus();
    }
}
