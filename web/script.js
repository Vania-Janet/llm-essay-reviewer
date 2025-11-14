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

// Edit and download elements
const editReportBtn = document.getElementById('editReportBtn');
const downloadReportBtn = document.getElementById('downloadReportBtn');
const scoreEditor = document.getElementById('scoreEditor');
const closeScoreEditor = document.getElementById('closeScoreEditor');
const editTotalScore = document.getElementById('editTotalScore');
const saveScoreBtn = document.getElementById('saveScoreBtn');
const editGeneralCommentBtn = document.getElementById('editGeneralCommentBtn');

// History and comparison elements
const essaysHistorySection = document.getElementById('essaysHistorySection');
const viewHistoryBtn = document.getElementById('viewHistoryBtn');
const closeHistoryBtn = document.getElementById('closeHistoryBtn');
const essaysList = document.getElementById('essaysList');
const compareSelectedBtn = document.getElementById('compareSelectedBtn');
const comparisonSection = document.getElementById('comparisonSection');
const closeComparisonBtn = document.getElementById('closeComparisonBtn');
const comparisonContent = document.getElementById('comparisonContent');

let selectedFile = null;
// Variables globales para almacenar la evaluación actual
let currentEvaluation = null;
let currentEssayText = null;
let isEditMode = false;
let selectedEssays = new Set();

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

// Edit and download event listeners
editReportBtn.addEventListener('click', toggleEditMode);
downloadReportBtn.addEventListener('click', downloadReport);
document.getElementById('totalScore').addEventListener('click', openScoreEditor);
closeScoreEditor.addEventListener('click', () => {
    scoreEditor.style.display = 'none';
});
saveScoreBtn.addEventListener('click', saveTotalScore);
editGeneralCommentBtn.addEventListener('click', toggleGeneralCommentEdit);

// History and comparison event listeners
viewHistoryBtn.addEventListener('click', showEssaysHistory);
closeHistoryBtn.addEventListener('click', hideEssaysHistory);
compareSelectedBtn.addEventListener('click', compareEssays);
closeComparisonBtn.addEventListener('click', hideComparison);

// Edit criterion buttons
document.addEventListener('click', (e) => {
    if (e.target.closest('.btn-edit-criterion')) {
        const btn = e.target.closest('.btn-edit-criterion');
        const criterionNum = btn.dataset.criterion;
        toggleCriterionEdit(criterionNum);
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
        currentEssayText = result.texto_completo || '';
        
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
        displayFragments('fragments1', evaluation.calidad_tecnica.fragmentos_destacados);
    }

    // Criterio 2: Creatividad
    if (evaluation.creatividad) {
        document.getElementById('score2').textContent = 
            `${evaluation.creatividad.calificacion}/5`;
        document.getElementById('comment2').textContent = 
            evaluation.creatividad.comentario;
        displayFragments('fragments2', evaluation.creatividad.fragmentos_destacados);
    }

    // Criterio 3: Vinculación Temática
    if (evaluation.vinculacion_tematica) {
        document.getElementById('score3').textContent = 
            `${evaluation.vinculacion_tematica.calificacion}/5`;
        document.getElementById('comment3').textContent = 
            evaluation.vinculacion_tematica.comentario;
        displayFragments('fragments3', evaluation.vinculacion_tematica.fragmentos_destacados);
    }

    // Criterio 4: Bienestar Colectivo
    if (evaluation.bienestar_colectivo) {
        document.getElementById('score4').textContent = 
            `${evaluation.bienestar_colectivo.calificacion}/5`;
        document.getElementById('comment4').textContent = 
            evaluation.bienestar_colectivo.comentario;
        displayFragments('fragments4', evaluation.bienestar_colectivo.fragmentos_destacados);
    }

    // Criterio 5: Potencial de Impacto
    if (evaluation.potencial_impacto) {
        document.getElementById('score5').textContent = 
            `${evaluation.potencial_impacto.calificacion}/5`;
        document.getElementById('comment5').textContent = 
            evaluation.potencial_impacto.comentario;
        displayFragments('fragments5', evaluation.potencial_impacto.fragmentos_destacados);
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

// Función para mostrar fragmentos destacados
function displayFragments(containerId, fragments) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Limpiar contenedor
    container.innerHTML = '';
    
    if (!fragments || fragments.length === 0) {
        container.style.display = 'none';
        return;
    }
    
    container.style.display = 'block';
    
    fragments.forEach(fragment => {
        const fragmentDiv = document.createElement('div');
        fragmentDiv.className = `fragment fragment-${fragment.impacto}`;
        
        const icon = fragment.impacto === 'positivo' ? '✓' : '✗';
        const label = fragment.impacto === 'positivo' ? 'Aspecto Positivo' : 'Área de Mejora';
        
        fragmentDiv.innerHTML = `
            <div class="fragment-header">
                <span class="fragment-icon">${icon}</span>
                <span class="fragment-label">${label}</span>
            </div>
            <blockquote class="fragment-text">"${fragment.texto}"</blockquote>
            <p class="fragment-reason">${fragment.razon}</p>
        `;
        
        container.appendChild(fragmentDiv);
    });
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
        // Enviar al backend con el texto del ensayo
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                evaluation: currentEvaluation,
                essay_text: currentEssayText
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

// Edit and Download Functions
function toggleEditMode() {
    isEditMode = !isEditMode;
    
    if (isEditMode) {
        editReportBtn.textContent = '💾 Guardar Edición';
        editReportBtn.style.background = 'var(--gradient)';
        editReportBtn.style.color = 'white';
        editReportBtn.style.borderColor = 'transparent';
        
        // Enable all editable fields
        document.querySelectorAll('.criterion-comment').forEach(el => {
            el.contentEditable = 'true';
            el.classList.add('editing');
        });
        
        const generalCommentText = document.getElementById('generalCommentText');
        if (generalCommentText) {
            generalCommentText.contentEditable = 'true';
        }
    } else {
        editReportBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Editar Reporte
        `;
        editReportBtn.style.background = 'white';
        editReportBtn.style.color = 'var(--primary-blue)';
        editReportBtn.style.borderColor = 'var(--primary-blue)';
        
        // Disable all editable fields
        document.querySelectorAll('.criterion-comment').forEach(el => {
            el.contentEditable = 'false';
            el.classList.remove('editing');
        });
        
        const generalCommentText = document.getElementById('generalCommentText');
        if (generalCommentText) {
            generalCommentText.contentEditable = 'false';
        }
        
        // Update evaluation object with edited values
        updateEvaluationFromDOM();
    }
}

function toggleCriterionEdit(criterionNum) {
    const comment = document.getElementById(`comment${criterionNum}`);
    const card = document.querySelector(`[data-criterion="${criterionNum}"]`);
    
    if (comment.contentEditable === 'true') {
        comment.contentEditable = 'false';
        card.classList.remove('editing');
    } else {
        comment.contentEditable = 'true';
        card.classList.add('editing');
        comment.focus();
    }
}

function toggleGeneralCommentEdit() {
    const commentText = document.getElementById('generalCommentText');
    
    if (commentText.contentEditable === 'true') {
        commentText.contentEditable = 'false';
    } else {
        commentText.contentEditable = 'true';
        commentText.focus();
    }
}

function openScoreEditor() {
    if (!currentEvaluation) return;
    
    editTotalScore.value = currentEvaluation.puntuacion_total.toFixed(2);
    scoreEditor.style.display = 'block';
    editTotalScore.focus();
}

function saveTotalScore() {
    const newScore = parseFloat(editTotalScore.value);
    
    if (isNaN(newScore) || newScore < 0 || newScore > 5) {
        alert('Por favor, ingrese una puntuación válida entre 0.00 y 5.00');
        return;
    }
    
    currentEvaluation.puntuacion_total = newScore;
    document.getElementById('totalScore').textContent = newScore.toFixed(2);
    
    const percentage = (newScore / 5) * 100;
    document.getElementById('scoreFill').style.width = percentage + '%';
    
    scoreEditor.style.display = 'none';
}

function updateEvaluationFromDOM() {
    // Update comments from DOM
    const criterios = ['calidad_tecnica', 'creatividad', 'vinculacion_tematica', 'bienestar_colectivo', 'potencial_impacto'];
    
    criterios.forEach((criterio, index) => {
        const commentEl = document.getElementById(`comment${index + 1}`);
        if (commentEl && currentEvaluation[criterio]) {
            currentEvaluation[criterio].comentario = commentEl.textContent;
        }
    });
    
    // Update general comment
    const generalCommentEl = document.getElementById('generalCommentText');
    if (generalCommentEl) {
        currentEvaluation.comentario_general = generalCommentEl.textContent;
    }
}

function downloadReport() {
    if (!currentEvaluation) {
        alert('No hay reporte disponible para descargar.');
        return;
    }
    
    // Update evaluation from current DOM state
    updateEvaluationFromDOM();
    
    // Generate HTML report
    const html = generateHTMLReport(currentEvaluation);
    
    // Create blob and download
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `evaluacion_ensayo_${new Date().toISOString().split('T')[0]}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function generateHTMLReport(evaluation) {
    const date = new Date().toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    
    return `<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Evaluación - ${date}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            background: #f8f9fa;
            padding: 2rem;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 3rem;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 3rem;
            padding-bottom: 2rem;
            border-bottom: 3px solid #ddda36;
        }
        .header h1 {
            color: #29346d;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .header .date {
            color: #6c757d;
            font-size: 1rem;
        }
        .score-summary {
            background: linear-gradient(135deg, #29346d 0%, #ddda36 100%);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 2rem;
        }
        .score-summary h2 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            opacity: 0.95;
        }
        .score-summary .total {
            font-size: 4rem;
            font-weight: 700;
        }
        .criterion {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            border-left: 4px solid #ddda36;
        }
        .criterion-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid #e0e0e0;
        }
        .criterion-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #29346d;
        }
        .criterion-score {
            font-size: 1.5rem;
            font-weight: 700;
            color: #29346d;
        }
        .criterion-comment {
            color: #6c757d;
            line-height: 1.7;
        }
        .general-comment {
            background: #f8f9fa;
            padding: 2rem;
            border-radius: 8px;
            border-left: 4px solid #29346d;
            margin-top: 2rem;
        }
        .general-comment h3 {
            color: #29346d;
            margin-bottom: 1rem;
        }
        .footer {
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #6c757d;
            font-size: 0.9rem;
        }
        @media print {
            body { padding: 0; background: white; }
            .container { box-shadow: none; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Reporte de Evaluación de Ensayo</h1>
            <p class="date">Generado el ${date}</p>
        </div>
        
        <div class="score-summary">
            <h2>Puntuación Total</h2>
            <div class="total">${evaluation.puntuacion_total.toFixed(2)}/5.00</div>
        </div>
        
        <div class="criterion">
            <div class="criterion-header">
                <span class="criterion-title">📝 Calidad Técnica y Rigor Académico</span>
                <span class="criterion-score">${evaluation.calidad_tecnica.calificacion}/5</span>
            </div>
            <p class="criterion-comment">${evaluation.calidad_tecnica.comentario}</p>
        </div>
        
        <div class="criterion">
            <div class="criterion-header">
                <span class="criterion-title">🎨 Creatividad y Originalidad</span>
                <span class="criterion-score">${evaluation.creatividad.calificacion}/5</span>
            </div>
            <p class="criterion-comment">${evaluation.creatividad.comentario}</p>
        </div>
        
        <div class="criterion">
            <div class="criterion-header">
                <span class="criterion-title">🎯 Vinculación con Ejes Temáticos</span>
                <span class="criterion-score">${evaluation.vinculacion_tematica.calificacion}/5</span>
            </div>
            <p class="criterion-comment">${evaluation.vinculacion_tematica.comentario}</p>
        </div>
        
        <div class="criterion">
            <div class="criterion-header">
                <span class="criterion-title">🌍 Bienestar Colectivo y Responsabilidad Social</span>
                <span class="criterion-score">${evaluation.bienestar_colectivo.calificacion}/5</span>
            </div>
            <p class="criterion-comment">${evaluation.bienestar_colectivo.comentario}</p>
        </div>
        
        <div class="criterion">
            <div class="criterion-header">
                <span class="criterion-title">✨ Potencial de Impacto y Publicación</span>
                <span class="criterion-score">${evaluation.potencial_impacto.calificacion}/5</span>
            </div>
            <p class="criterion-comment">${evaluation.potencial_impacto.comentario}</p>
        </div>
        
        ${evaluation.comentario_general ? `
        <div class="general-comment">
            <h3>Comentario General</h3>
            <p>${evaluation.comentario_general}</p>
        </div>
        ` : ''}
        
        <div class="footer">
            <p>Sistema de Evaluación Inteligente de Ensayos</p>
            <p>Powered by IA · ${date}</p>
        </div>
    </div>
</body>
</html>
    `;

    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reporte_evaluacion_${date}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Funciones para historial y comparación
async function showEssaysHistory() {
    essaysHistorySection.style.display = 'block';
    uploadSection.style.display = 'none';
    resultsSection.style.display = 'none';
    comparisonSection.style.display = 'none';
    
    essaysList.innerHTML = '<div class="loader"></div><p>Cargando ensayos...</p>';
    selectedEssays.clear();
    compareSelectedBtn.disabled = true;
    
    try {
        const response = await fetch('/essays');
        if (!response.ok) throw new Error('Error al cargar ensayos');
        
        const essays = await response.json();
        
        if (essays.length === 0) {
            essaysList.innerHTML = '<p style="text-align: center; color: #6b7280;">No hay ensayos evaluados aún.</p>';
            return;
        }
        
        essaysList.innerHTML = essays.map(essay => `
            <div class="essay-item" data-id="${essay.id}">
                <input type="checkbox" class="essay-checkbox" data-id="${essay.id}">
                <div class="essay-info">
                    <div class="essay-name">${essay.nombre_archivo}</div>
                    <div class="essay-meta">
                        <span>📅 ${new Date(essay.fecha_evaluacion).toLocaleString('es-MX')}</span>
                        <span>📄 ${essay.texto_preview}</span>
                    </div>
                </div>
                <div class="essay-score">${essay.puntuacion_total.toFixed(2)}/5.00</div>
            </div>
        `).join('');
        
        // Agregar event listeners a los checkboxes
        document.querySelectorAll('.essay-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', handleEssaySelection);
        });
        
    } catch (error) {
        console.error('Error:', error);
        essaysList.innerHTML = `<p style="color: red; text-align: center;">Error al cargar ensayos: ${error.message}</p>`;
    }
}

function hideEssaysHistory() {
    essaysHistorySection.style.display = 'none';
    uploadSection.style.display = 'block';
}

function handleEssaySelection(e) {
    const essayId = parseInt(e.target.dataset.id);
    const essayItem = e.target.closest('.essay-item');
    
    if (e.target.checked) {
        selectedEssays.add(essayId);
        essayItem.classList.add('selected');
    } else {
        selectedEssays.delete(essayId);
        essayItem.classList.remove('selected');
    }
    
    compareSelectedBtn.disabled = selectedEssays.size < 2;
}

async function compareEssays() {
    if (selectedEssays.size < 2) {
        alert('Debe seleccionar al menos 2 ensayos para comparar');
        return;
    }
    
    essaysHistorySection.style.display = 'none';
    comparisonSection.style.display = 'block';
    comparisonContent.innerHTML = '<div class="loader"></div><p>Generando análisis comparativo...</p>';
    
    try {
        const response = await fetch('/compare', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                essay_ids: Array.from(selectedEssays)
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al comparar ensayos');
        }
        
        const result = await response.json();
        
        // Mostrar resumen de ensayos comparados
        const essaysSummary = result.ensayos.map((essay, index) => `
            <div class="essay-comparison-card">
                <h4>Ensayo ${index + 1}: ${essay.nombre_archivo}</h4>
                <p><strong>Puntuación Total:</strong> ${essay.puntuacion_total.toFixed(2)}/5.00</p>
                <p><strong>Fecha:</strong> ${new Date(essay.fecha_evaluacion).toLocaleString('es-MX')}</p>
            </div>
        `).join('');
        
        // Convertir markdown a HTML básico
        const comparisonHTML = result.comparacion
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');
        
        comparisonContent.innerHTML = `
            <div class="essays-summary">
                <h3>Ensayos Comparados</h3>
                ${essaysSummary}
            </div>
            <div class="comparison-analysis">
                <h3>Análisis Comparativo</h3>
                <p>${comparisonHTML}</p>
            </div>
        `;
        
    } catch (error) {
        console.error('Error:', error);
        comparisonContent.innerHTML = `<p style="color: red; text-align: center;">Error: ${error.message}</p>`;
    }
}

function hideComparison() {
    comparisonSection.style.display = 'none';
    essaysHistorySection.style.display = 'block';
}
