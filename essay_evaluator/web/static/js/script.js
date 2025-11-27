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
const chatToggle = document.getElementById('chatToggle'); // Mantener para compatibilidad
const chatWidgetBtn = document.getElementById('chatWidgetTrigger');
const closeChatBtn = document.getElementById('closeChatBtn');
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

// Judge evaluation elements
const judgeEvaluationBtn = document.getElementById('judgeEvaluationBtn');
const judgeEvaluationSection = document.getElementById('judgeEvaluationSection');
const backFromJudgeBtn = document.getElementById('backFromJudgeBtn');
const essaySelectForEval = document.getElementById('essaySelectForEval');
const criteriaCardsDisplay = document.getElementById('criteriaCardsDisplay');
const criteriaFieldsContainer = document.getElementById('criteriaFieldsContainer');
const refreshCriteriaPdfBtn = document.getElementById('refreshCriteriaPdfBtn');
const aiAssistBtn = document.getElementById('aiAssistBtn');
const saveEvaluationBtn = document.getElementById('saveEvaluationBtn');
const totalScoreValue = document.getElementById('totalScoreValue');
const manualEvaluationForm = document.getElementById('manualEvaluationForm');
const editGeneralCommentBtn = document.getElementById('editGeneralCommentBtn');

// History and comparison elements
const essaysHistorySection = document.getElementById('essaysHistorySection');
const essaysLibrarySection = document.getElementById('essaysLibrarySection');
const libraryList = document.getElementById('libraryList');
const compareLibraryBtn = document.getElementById('compareLibraryBtn');
const uploadNewBtn = document.getElementById('uploadNewBtn');
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

// ============= AUTENTICACIÓN =============
const AUTH_TOKEN_KEY = 'auth_token';
const USER_KEY = 'user';

function getAuthToken() {
    return localStorage.getItem(AUTH_TOKEN_KEY);
}

function getUser() {
    const userStr = localStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
}

function setAuthToken(token) {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
}

function clearAuth() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
}

function logout() {
    clearAuth();
    window.location.href = '/login.html';
}

// Verificar autenticación al cargar la página
async function checkAuth() {
    const token = getAuthToken();
    
    if (!token) {
        window.location.href = '/login.html';
        return false;
    }
    
    try {
        const response = await fetch('/api/verify-token', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            clearAuth();
            window.location.href = '/login.html';
            return false;
        }
        
        return true;
    } catch (error) {
        console.error('Error verificando autenticación:', error);
        clearAuth();
        window.location.href = '/login.html';
        return false;
    }
}

// Función helper para hacer requests autenticados
async function authenticatedFetch(url, options = {}) {
    const token = getAuthToken();
    
    if (!token) {
        window.location.href = '/login.html';
        throw new Error('No autenticado');
    }
    
    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    
    if (response.status === 401) {
        clearAuth();
        window.location.href = '/login.html';
        throw new Error('Sesión expirada');
    }
    
    return response;
}

// Verificar autenticación al cargar
window.addEventListener('DOMContentLoaded', async () => {
    const isAuth = await checkAuth();
    if (isAuth) {
        const user = getUser();
        console.log('Usuario autenticado:', user?.username);
        
        // Mostrar nombre de usuario
        const userName = document.getElementById('userName');
        if (userName && user) {
            userName.textContent = `Hola, ${user.nombre_completo || user.username}`;
        }
        
        // Configurar botón de logout
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', logout);
        }
        
        // Cargar la biblioteca de ensayos
        loadEssaysLibrary();
    }
});

// ============= FIN AUTENTICACIÓN =============

// ============= PROTECCIÓN XSS =============

/**
 * Escapa caracteres HTML para prevenir ataques XSS
 * @param {string} text - Texto a escapar
 * @returns {string} - Texto seguro para insertar en HTML
 */
function escapeHtml(text) {
    if (!text) return text;
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Sanitiza texto para uso seguro en innerHTML
 * @param {string} text - Texto a sanitizar
 * @returns {string} - Texto sanitizado
 */
function sanitizeText(text) {
    if (!text) return '';
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// ============= FIN PROTECCIÓN XSS =============

let currentFileName = '';  // Para almacenar el nombre del archivo evaluado
let allEssays = [];  // Para almacenar todos los ensayos cargados

// Event Listeners
selectFileBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
evaluateBtn.addEventListener('click', evaluateEssay);
newEvaluationBtn.addEventListener('click', resetEvaluation);

// Chat event listeners - Nuevo sistema flotante
if (chatWidgetBtn) chatWidgetBtn.addEventListener('click', toggleChat);
if (closeChatBtn) closeChatBtn.addEventListener('click', toggleChat);
if (chatToggle) chatToggle.addEventListener('click', toggleChat); // Mantener compatibilidad

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
if (viewHistoryBtn) viewHistoryBtn.addEventListener('click', showEssaysHistory);
if (closeHistoryBtn) closeHistoryBtn.addEventListener('click', hideEssaysHistory);
if (compareSelectedBtn) compareSelectedBtn.addEventListener('click', compareEssays);
if (closeComparisonBtn) closeComparisonBtn.addEventListener('click', hideComparison);
if (compareLibraryBtn) compareLibraryBtn.addEventListener('click', compareEssays);
if (uploadNewBtn) uploadNewBtn.addEventListener('click', showUploadSection);

// Back button event listeners
const backFromUploadBtn = document.getElementById('backFromUploadBtn');
const backFromResultsBtn = document.getElementById('backFromResultsBtn');
const backFromHistoryBtn = document.getElementById('backFromHistoryBtn');
const backFromComparisonBtn = document.getElementById('backFromComparisonBtn');

if (backFromUploadBtn) backFromUploadBtn.addEventListener('click', returnToLibrary);
if (backFromResultsBtn) backFromResultsBtn.addEventListener('click', returnToLibrary);
if (backFromHistoryBtn) backFromHistoryBtn.addEventListener('click', returnToLibrary);
if (backFromComparisonBtn) backFromComparisonBtn.addEventListener('click', returnToLibrary);

// Judge evaluation event listeners
if (judgeEvaluationBtn) judgeEvaluationBtn.addEventListener('click', showJudgeEvaluation);
if (backFromJudgeBtn) backFromJudgeBtn.addEventListener('click', returnToLibrary);
if (refreshCriteriaPdfBtn) refreshCriteriaPdfBtn.addEventListener('click', loadJudgeCriteria);
if (aiAssistBtn) aiAssistBtn.addEventListener('click', requestAIAssistance);
if (saveEvaluationBtn) saveEvaluationBtn.addEventListener('click', saveManualEvaluation);
if (essaySelectForEval) essaySelectForEval.addEventListener('change', onEssaySelectedForEval);

// Botón de descarga Excel
const downloadExcelBtn = document.getElementById('downloadExcelBtn');
if (downloadExcelBtn) downloadExcelBtn.addEventListener('click', downloadExcel);

// Botón de estadísticas
const showStatsBtn = document.getElementById('showStatsBtn');
if (showStatsBtn) showStatsBtn.addEventListener('click', showStatsDashboard);

// Botón de cerrar PDF
const closePdfBtn = document.getElementById('closePdfBtn');
if (closePdfBtn) closePdfBtn.addEventListener('click', () => {
    const pdfViewerContainer = document.getElementById('pdfViewerContainer');
    if (pdfViewerContainer) {
        pdfViewerContainer.style.display = 'none';
    }
});

// Cargar biblioteca al iniciar
window.addEventListener('DOMContentLoaded', loadEssaysLibrary);

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
    currentFileName = file.name.replace('.pdf', '');  // Guardar nombre sin extensión
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

        // Enviar al backend con autenticación
        const response = await authenticatedFetch('/evaluate', {
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

    // Mostrar título del ensayo
    const essayTitle = document.getElementById('essayTitle');
    const essayMetadata = document.getElementById('essayMetadata');
    
    if (evaluation.nombre_archivo) {
        // Extraer el nombre del archivo sin la extensión
        let displayName = evaluation.nombre_archivo.replace('_procesado.txt', '').replace('.txt', '');
        // Reemplazar guiones bajos por espacios y capitalizar
        displayName = displayName.split('_').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
        ).join(' ');
        
        essayTitle.textContent = displayName;
        
        // Mostrar metadatos si están disponibles
        if (evaluation.fecha_evaluacion) {
            const fecha = new Date(evaluation.fecha_evaluacion);
            essayMetadata.innerHTML = `
                <span class="metadata-item">📅 Evaluado: ${fecha.toLocaleDateString('es-MX', { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                })}</span>
                ${evaluation.tiene_anexo ? '<span class="metadata-item">📎 Con Anexo IA</span>' : ''}
            `;
        }
    }

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

    // Criterio 5: Uso Responsable de IA
    if (evaluation.uso_responsable_ia) {
        document.getElementById('score5').textContent = 
            `${evaluation.uso_responsable_ia.calificacion}/5`;
        document.getElementById('comment5').textContent = 
            evaluation.uso_responsable_ia.comentario;
        displayFragments('fragments5', evaluation.uso_responsable_ia.fragmentos_destacados);
    }
    
    // Mostrar advertencia si no tiene anexo
    const anexoWarning = document.getElementById('anexoWarning');
    if (anexoWarning) {
        if (evaluation.tiene_anexo === false) {
            anexoWarning.style.display = 'block';
        } else {
            anexoWarning.style.display = 'none';
        }
    }

    // Criterio 6: Potencial de Impacto
    if (evaluation.potencial_impacto) {
        document.getElementById('score6').textContent = 
            `${evaluation.potencial_impacto.calificacion}/5`;
        document.getElementById('comment6').textContent = 
            evaluation.potencial_impacto.comentario;
        displayFragments('fragments6', evaluation.potencial_impacto.fragmentos_destacados);
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
    currentEvaluation = null;
    currentEssayText = null;
    currentFileName = '';
    
    // Volver a mostrar la biblioteca
    essaysLibrarySection.style.display = 'block';
    uploadSection.style.display = 'none';
    dropZone.style.display = 'block';
    fileInfo.style.display = 'none';
    processingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    
    // Recargar biblioteca
    loadEssaysLibrary();
    
    // Limpiar resultados
    document.getElementById('totalScore').textContent = '0.00';
    document.getElementById('scoreFill').style.width = '0%';
    
    for (let i = 1; i <= 6; i++) {
        document.getElementById(`score${i}`).textContent = '-';
        document.getElementById(`comment${i}`).textContent = '';
    }
    
    // Ocultar advertencia de anexo
    const anexoWarning = document.getElementById('anexoWarning');
    if (anexoWarning) {
        anexoWarning.style.display = 'none';
    }
    
    document.getElementById('generalComment').style.display = 'none';
    document.getElementById('generalCommentText').textContent = '';
    
    // Deshabilitar y limpiar chat
    disableChat();
    
    // Scroll al inicio
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Chat functionality - Nuevo sistema flotante
function toggleChat() {
    chatPanel.classList.toggle('active');
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
    
    if (!message) return;
    
    // Determinar qué ensayos están en contexto
    let essayIds = [];
    if (selectedEssays.size > 0) {
        // Si hay ensayos seleccionados, usar esos
        essayIds = Array.from(selectedEssays);
    } else if (currentEvaluation && currentEvaluation.id) {
        // Si hay un ensayo individual visualizado, usar ese
        essayIds = [currentEvaluation.id];
    }
    
    if (essayIds.length === 0) {
        addChatMessage('assistant', 
            'Por favor, seleccione al menos un ensayo de la biblioteca para poder responder sus consultas.'
        );
        return;
    }
    
    // Agregar mensaje del usuario
    addChatMessage('user', message);
    chatInput.value = '';
    
    // Mostrar estado de carga
    chatSendBtn.disabled = true;
    chatStatus.style.display = 'flex';
    
    try {
        const response = await authenticatedFetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                essay_ids: essayIds
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
    
    // Actualizar evaluación desde el DOM
    updateEvaluationFromDOM();
    
    // Función helper para limpiar texto y evitar problemas de codificación
    const cleanTextForPDF = (text) => {
        if (!text) return '';
        return text
            .normalize('NFD') // Descomponer caracteres acentuados
            .replace(/[\u0300-\u036f]/g, '') // Eliminar marcas diacríticas
            .replace(/[^\x00-\x7F]/g, '') // Eliminar caracteres no ASCII restantes
            .replace(/\s+/g, ' ') // Normalizar espacios
            .trim();
    };
    
    // Crear el PDF con jsPDF
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF('p', 'mm', 'a4');
    
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 20;
    const maxWidth = pageWidth - (2 * margin);
    let yPos = margin;
    
    // Función para agregar nueva página si es necesario
    const checkPageBreak = (neededSpace) => {
        if (yPos + neededSpace > pageHeight - margin) {
            doc.addPage();
            yPos = margin;
            return true;
        }
        return false;
    };
    
    // Función para texto con wrap
    const addText = (text, fontSize, isBold = false, color = [0, 0, 0]) => {
        const cleanText = cleanTextForPDF(text);
        
        doc.setFontSize(fontSize);
        doc.setFont('helvetica', isBold ? 'bold' : 'normal');
        doc.setTextColor(...color);
        const lines = doc.splitTextToSize(cleanText, maxWidth);
        
        lines.forEach((line) => {
            checkPageBreak(fontSize * 0.5 + 2);
            doc.text(line, margin, yPos);
            yPos += fontSize * 0.5;
        });
        yPos += 3;
    };
    
    // Encabezado
    doc.setFillColor(41, 52, 109);
    doc.rect(0, 0, pageWidth, 40, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(22);
    doc.setFont('helvetica', 'bold');
    doc.text('Reporte de Evaluacion de Ensayo', pageWidth / 2, 20, { align: 'center' });
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    const date = new Date().toLocaleDateString('es-MX', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    doc.text(`Generado el ${date}`, pageWidth / 2, 30, { align: 'center' });
    
    yPos = 50;
    
    // Nombre del archivo
    doc.setTextColor(0, 0, 0);
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text(`Ensayo: ${currentFileName || 'Sin nombre'}`, margin, yPos);
    yPos += 10;
    
    // Puntuación total con fondo
    checkPageBreak(30);
    doc.setFillColor(221, 218, 54);
    doc.roundedRect(margin, yPos, maxWidth, 25, 3, 3, 'F');
    doc.setFontSize(16);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(41, 52, 109);
    doc.text('Puntuacion Total', pageWidth / 2, yPos + 8, { align: 'center' });
    doc.setFontSize(28);
    doc.text(`${currentEvaluation.puntuacion_total.toFixed(2)}/5.00`, pageWidth / 2, yPos + 20, { align: 'center' });
    yPos += 35;
    
    // Criterios de evaluación (sin emojis para mejor compatibilidad PDF)
    const criterios = [
        { nombre: 'Calidad Tecnica y Rigor Academico', data: currentEvaluation.calidad_tecnica, peso: '25%' },
        { nombre: 'Creatividad y Originalidad', data: currentEvaluation.creatividad, peso: '20%' },
        { nombre: 'Vinculacion con Ejes Tematicos', data: currentEvaluation.vinculacion_tematica, peso: '15%' },
        { nombre: 'Bienestar Colectivo', data: currentEvaluation.bienestar_colectivo, peso: '20%' },
        { nombre: 'Potencial de Impacto', data: currentEvaluation.potencial_impacto, peso: '20%' }
    ];
    
    criterios.forEach((criterio, index) => {
        checkPageBreak(40);
        
        // Línea separadora
        if (index > 0) {
            doc.setDrawColor(200, 200, 200);
            doc.line(margin, yPos, pageWidth - margin, yPos);
            yPos += 8;
        }
        
        // Título del criterio
        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(41, 52, 109);
        doc.text(cleanTextForPDF(criterio.nombre), margin, yPos);
        
        // Peso y calificación
        doc.setFontSize(12);
        doc.setTextColor(100, 100, 100);
        doc.text(`Peso: ${criterio.peso}`, pageWidth - margin - 30, yPos, { align: 'right' });
        
        doc.setFontSize(16);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(221, 218, 54);
        doc.text(`${criterio.data.calificacion}/5`, pageWidth - margin, yPos, { align: 'right' });
        yPos += 8;
        
        // Comentario
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(60, 60, 60);
        const comentarioLines = doc.splitTextToSize(cleanTextForPDF(criterio.data.comentario), maxWidth);
        comentarioLines.forEach(line => {
            checkPageBreak(5);
            doc.text(line, margin, yPos);
            yPos += 5;
        });
        yPos += 5;
    });
    
    // Comentario general
    if (currentEvaluation.comentario_general) {
        checkPageBreak(30);
        doc.setDrawColor(221, 218, 54);
        doc.setLineWidth(0.5);
        doc.line(margin, yPos, pageWidth - margin, yPos);
        yPos += 8;
        
        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(41, 52, 109);
        doc.text('Comentario General', margin, yPos);
        yPos += 8;
        
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(60, 60, 60);
        const generalLines = doc.splitTextToSize(cleanTextForPDF(currentEvaluation.comentario_general), maxWidth);
        generalLines.forEach(line => {
            checkPageBreak(5);
            doc.text(line, margin, yPos);
            yPos += 5;
        });
    }
    
    // Pie de página en todas las páginas
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(150, 150, 150);
        doc.setFont('helvetica', 'normal');
        doc.text('Sistema de Evaluacion de Ensayos con IA', pageWidth / 2, pageHeight - 10, { align: 'center' });
        doc.text(`Pagina ${i} de ${pageCount}`, pageWidth - margin, pageHeight - 10, { align: 'right' });
    }
    
    // Descargar con el nombre del archivo
    const cleanFileName = cleanTextForPDF(currentFileName || 'Sin_nombre');
    const pdfFileName = `Evaluacion_${cleanFileName}.pdf`.replace(/\s+/g, '_');
    doc.save(pdfFileName);
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
        const response = await authenticatedFetch('/essays');
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
                    <div class="essay-name">${escapeHtml(essay.nombre_archivo)}</div>
                    <div class="essay-meta">
                        <span>📅 ${new Date(essay.fecha_evaluacion).toLocaleString('es-MX')}</span>
                        <span>📄 ${escapeHtml(essay.texto_preview || '')}</span>
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
        essaysList.innerHTML = `<p style="color: red; text-align: center;">Error al cargar ensayos: ${escapeHtml(error.message)}</p>`;
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
        const response = await authenticatedFetch('/compare', {
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
        const essaysSummary = result.ensayos
            .sort((a, b) => b.puntuacion_total - a.puntuacion_total)
            .map((essay, index) => `
            <div class="essay-comparison-card" style="border-left: 4px solid ${index === 0 ? '#ddd436' : index === 1 ? '#29346d' : '#d65a31'}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4>${index + 1}. ${essay.nombre_archivo.replace('.txt', '').replace('Ensayo_', '').substring(0, 40)}...</h4>
                    <div class="comparison-score" style="font-size: 1.5rem; padding: 0.5rem 1rem;">${essay.puntuacion_total.toFixed(2)}</div>
                </div>
                <p style="margin: 0.5rem 0; color: #6b7280;">📎 ${essay.tiene_anexo ? 'Con Anexo IA' : 'Sin Anexo IA'}</p>
            </div>
        `).join('');
        
        // Convertir markdown a HTML mejorado
        const comparisonHTML = result.comparacion
            .replace(/^### (.+)$/gm, '<h4>$1</h4>')
            .replace(/^## (.+)$/gm, '<h3>$1</h3>')
            .replace(/^# (.+)$/gm, '<h2>$1</h2>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/^\d+\.\s+(.+)/gm, '<li>$1</li>')
            .replace(/^-\s+(.+)/gm, '<li>$1</li>')
            .replace(/(<li>.*?<\/li>\s*)+/gs, '<ul>$&</ul>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');
        
        comparisonContent.innerHTML = `
            <div class="essays-summary">
                <h3>🏆 Ranking de Ensayos</h3>
                <div class="essays-grid" style="gap: 0.75rem;">
                    ${essaysSummary}
                </div>
            </div>
            <div class="comparison-analysis">
                <h3>📝 Análisis Comparativo</h3>
                <div class="analysis-content">${comparisonHTML}</div>
            </div>
        `;
        
    } catch (error) {
        console.error('Error:', error);
        comparisonContent.innerHTML = `<p style="color: red; text-align: center;">Error: ${escapeHtml(error.message)}</p>`;
    }
}

function hideComparison() {
    comparisonSection.style.display = 'none';
    essaysHistorySection.style.display = 'block';
}

// Funciones para la biblioteca de ensayos
async function loadEssaysLibrary() {
    try {
        // Mostrar skeleton loading
        libraryList.innerHTML = `
            <div class="skeleton-card">
                <div class="skeleton-text" style="width: 60%;"></div>
                <div class="skeleton-text" style="width: 40%;"></div>
                <div class="skeleton-text" style="width: 50%;"></div>
            </div>
            <div class="skeleton-card">
                <div class="skeleton-text" style="width: 55%;"></div>
                <div class="skeleton-text" style="width: 45%;"></div>
                <div class="skeleton-text" style="width: 35%;"></div>
            </div>
            <div class="skeleton-card">
                <div class="skeleton-text" style="width: 50%;"></div>
                <div class="skeleton-text" style="width: 60%;"></div>
                <div class="skeleton-text" style="width: 40%;"></div>
            </div>
        `;
        
        const response = await authenticatedFetch('/essays');
        if (!response.ok) throw new Error('Error al cargar ensayos');
        
        allEssays = await response.json();
        
        if (allEssays.length === 0) {
            libraryList.innerHTML = `
                <div style="text-align: center; padding: 3rem; grid-column: 1/-1;">
                    <p style="font-size: 1.2rem; color: #6b7280; margin-bottom: 1rem;">
                        📭 No hay ensayos en la biblioteca
                    </p>
                    <p style="color: #9ca3af;">
                        Sube un nuevo ensayo o ejecuta el script de procesamiento batch
                    </p>
                </div>
            `;
            return;
        }
        
        displayEssaysLibrary(allEssays);
        
    } catch (error) {
        console.error('Error:', error);
        libraryList.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: red; grid-column: 1/-1;">
                Error al cargar la biblioteca: ${error.message}
            </div>
        `;
    }
}

function displayEssaysLibrary(essays) {
    // Función para extraer un título limpio del nombre del archivo
    const extractTitle = (filename) => {
        // Eliminar extensión
        let title = filename.replace('.pdf', '').replace('.txt', '');
        
        // Formato: "Ensayo_Autor_Titulo..."
        const parts = title.split('_');
        
        if (parts.length >= 3 && parts[0] === 'Ensayo') {
            // Unir todas las partes después del autor para formar el título
            const titleParts = parts.slice(2);
            title = titleParts.join(' ');
            
            // Limitar longitud y capitalizar
            if (title.length > 60) {
                title = title.substring(0, 60) + '...';
            }
        } else if (title.length > 60) {
            // Si no sigue el formato esperado, simplemente recortar
            title = title.substring(0, 60) + '...';
        }
        
        return title;
    };
    
    // Función para extraer el autor
    const extractAuthor = (filename) => {
        const parts = filename.replace('.pdf', '').replace('.txt', '').split('_');
        if (parts.length >= 2 && parts[0] === 'Ensayo') {
            return parts[1];
        }
        return 'Desconocido';
    };
    
    libraryList.innerHTML = essays.map(essay => {
        const anexoIndicator = essay.tiene_anexo 
            ? '<span class="anexo-indicator anexo-ok">✓ Anexo IA</span>'
            : '<span class="anexo-indicator anexo-missing">⚠️ Sin Anexo IA</span>';
        
        const title = escapeHtml(extractTitle(essay.nombre_archivo));
        const author = escapeHtml(extractAuthor(essay.nombre_archivo));
        
        return `
            <div class="essay-card" data-id="${essay.id}">
                <div class="essay-card-header">
                    <input type="checkbox" class="essay-card-checkbox" data-id="${essay.id}">
                    <div class="essay-card-title">${title}</div>
                </div>
                <div class="essay-card-author">Por: ${author}</div>
                <div class="essay-card-score">${essay.puntuacion_total.toFixed(2)}/5.00</div>
                ${anexoIndicator}
                <div class="essay-card-meta">
                    <div class="essay-card-date">
                        📅 ${new Date(essay.fecha_evaluacion).toLocaleDateString('es-MX', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                        })}
                    </div>
                </div>
                <div class="essay-card-preview">${escapeHtml(essay.texto_preview || '')}</div>
                <div class="essay-card-actions">
                    <button class="btn-view-essay" onclick="viewEssayDetails(${essay.id}); event.stopPropagation();">
                        Ver Detalles
                    </button>
                </div>
            </div>
        `;
    }).join('');
    
    // Agregar event listeners a los checkboxes y tarjetas
    document.querySelectorAll('.essay-card').forEach(card => {
        const checkbox = card.querySelector('.essay-card-checkbox');
        const essayId = parseInt(checkbox.dataset.id);
        
        // Click en toda la tarjeta para seleccionar
        card.addEventListener('click', (e) => {
            // Ignorar clics en botones o enlaces
            if (e.target.closest('.btn-view-essay') || e.target.closest('.essay-card-checkbox')) {
                return;
            }
            
            // Toggle el checkbox
            checkbox.checked = !checkbox.checked;
            checkbox.dispatchEvent(new Event('change'));
        });
        
        // Prevenir propagación del checkbox
        checkbox.addEventListener('click', (e) => e.stopPropagation());
        checkbox.addEventListener('change', handleLibrarySelection);
    });
}

function handleLibrarySelection(e) {
    e.stopPropagation();
    const essayId = parseInt(e.target.dataset.id);
    const essayCard = e.target.closest('.essay-card');
    
    if (e.target.checked) {
        selectedEssays.add(essayId);
        essayCard.classList.add('selected');
    } else {
        selectedEssays.delete(essayId);
        essayCard.classList.remove('selected');
    }
    
    compareLibraryBtn.disabled = selectedEssays.size < 2;
    
    // Actualizar el chatbot con los ensayos seleccionados
    updateChatbotContext();
}

async function viewEssayDetails(essayId) {
    try {
        const response = await authenticatedFetch(`/essays/${essayId}`);
        if (!response.ok) throw new Error('Error al cargar ensayo');
        
        const essay = await response.json();
        
        // Actualizar variables globales con la estructura de la base de datos
        currentEvaluation = {
            id: essay.id,
            ...essay.evaluacion,  // Extraer la evaluación del objeto
            nombre_archivo: essay.nombre_archivo,
            fecha_evaluacion: essay.fecha_evaluacion,
            tiene_anexo: essay.tiene_anexo
        };
        currentEssayText = essay.texto_completo;
        currentFileName = essay.nombre_archivo.replace('.pdf', '');
        
        // Seleccionar solo este ensayo
        selectedEssays.clear();
        selectedEssays.add(essayId);
        
        // Actualizar UI
        document.querySelectorAll('.essay-card').forEach(card => {
            card.classList.remove('selected');
        });
        document.querySelectorAll('.essay-card-checkbox').forEach(cb => {
            cb.checked = cb.dataset.id == essayId;
        });
        document.querySelector(`[data-id="${essayId}"]`).closest('.essay-card').classList.add('selected');
        
        // Mostrar resultados - displayResults espera el objeto de evaluación
        displayResults(currentEvaluation);
        
        // Cargar PDF
        loadPDF(essayId);
        
        // Ocultar biblioteca y mostrar resultados
        essaysLibrarySection.style.display = 'none';
        uploadSection.style.display = 'none';
        resultsSection.style.display = 'block';
        
        // Habilitar chat
        enableChat();
        
        // Actualizar contexto del chatbot
        updateChatbotContext();
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error al cargar los detalles del ensayo');
    }
}

async function loadPDF(essayId) {
    const pdfViewerContainer = document.getElementById('pdfViewerContainer');
    const pdfViewer = document.getElementById('pdfViewer');
    const pdfError = document.getElementById('pdfError');
    
    try {
        // Construir URL del PDF
        const pdfUrl = `/essays/${essayId}/pdf`;
        
        // Verificar que el PDF existe
        const response = await authenticatedFetch(pdfUrl, { method: 'HEAD' });
        
        if (response.ok) {
            // Cargar PDF en el iframe
            pdfViewer.src = pdfUrl;
            pdfViewerContainer.style.display = 'block';
            pdfError.style.display = 'none';
        } else {
            // Mostrar error
            pdfViewerContainer.style.display = 'block';
            pdfViewer.style.display = 'none';
            pdfError.style.display = 'flex';
        }
    } catch (error) {
        console.error('Error al cargar PDF:', error);
        pdfViewerContainer.style.display = 'block';
        pdfViewer.style.display = 'none';
        pdfError.style.display = 'flex';
    }
}

function showUploadSection() {
    essaysLibrarySection.style.display = 'none';
    uploadSection.style.display = 'block';
    resultsSection.style.display = 'none';
}

function returnToLibrary() {
    // Hide all sections
    uploadSection.style.display = 'none';
    resultsSection.style.display = 'none';
    essaysHistorySection.style.display = 'none';
    comparisonSection.style.display = 'none';
    judgeEvaluationSection.style.display = 'none';
    
    // Ocultar gestión de criterios si existe
    const criteriaSection = document.getElementById('criteriaManagementSection');
    if (criteriaSection) criteriaSection.style.display = 'none';
    
    // Show library
    essaysLibrarySection.style.display = 'block';
    
    // Reload library to refresh data
    loadEssaysLibrary();
}

function updateChatbotContext() {
    // Esta función actualiza el contexto del chatbot según los ensayos seleccionados
    const numSelected = selectedEssays.size;
    
    if (numSelected === 0) {
        chatInput.placeholder = "Selecciona un ensayo para hacer consultas...";
    } else if (numSelected === 1) {
        chatInput.placeholder = "Pregunta sobre este ensayo...";
    } else {
        chatInput.placeholder = `Pregunta sobre estos ${numSelected} ensayos...`;
    }
}

// Función para descargar Excel con todos los ensayos
async function downloadExcel() {
    try {
        const downloadBtn = document.getElementById('downloadExcelBtn');
        const originalText = downloadBtn.innerHTML;
        
        // Mostrar estado de descarga
        downloadBtn.disabled = true;
        downloadBtn.innerHTML = '⏳ Descargando...';
        
        const response = await authenticatedFetch('/essays/export/csv');
        
        if (!response.ok) {
            throw new Error('Error al generar el archivo');
        }
        
        // Obtener el blob del archivo
        const blob = await response.blob();
        
        // Crear un enlace temporal para descargar
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        
        // Obtener el nombre del archivo desde el header o usar uno por defecto
        const contentDisposition = response.headers.get('content-disposition');
        let filename = 'ensayos_evaluados.csv';
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (filenameMatch && filenameMatch[1]) {
                filename = filenameMatch[1].replace(/['"]/g, '');
            }
        }
        
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        // Limpiar
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        // Restaurar botón
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = originalText;
        
        // Mostrar mensaje de éxito
        showNotification('✅ Excel descargado exitosamente', 'success');
        
    } catch (error) {
        console.error('Error al descargar Excel:', error);
        
        const downloadBtn = document.getElementById('downloadExcelBtn');
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = '📊 Descargar Excel';
        
        showNotification('❌ Error al descargar Excel: ' + error.message, 'error');
    }
}

// Función auxiliar para mostrar notificaciones
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#dcfce7' : type === 'error' ? '#fee2e2' : '#e0f2fe'};
        color: ${type === 'success' ? '#166534' : type === 'error' ? '#991b1b' : '#0c4a6e'};
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        z-index: 10000;
        font-weight: 500;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ============================================
// STATISTICS DASHBOARD
// ============================================

let scoresChartInstance = null;
let criteriaRadarChartInstance = null;

async function showStatsDashboard() {
    if (!allEssays || allEssays.length === 0) {
        showNotification('❌ No hay ensayos disponibles para mostrar estadísticas', 'error');
        return;
    }

    // Mostrar modal
    const statsModal = document.getElementById('statsModal');
    statsModal.style.display = 'block';

    // Calcular estadísticas
    const scores = allEssays
        .map(e => e.evaluacion?.puntuacion_total || e.puntuacion_total)
        .filter(s => s !== null && s !== undefined);

    if (scores.length === 0) {
        showNotification('❌ No hay calificaciones disponibles', 'error');
        statsModal.style.display = 'none';
        return;
    }

    const total = scores.length;
    const sum = scores.reduce((a, b) => a + b, 0);
    const avg = sum / total;
    const max = Math.max(...scores);
    const min = Math.min(...scores);

    // Actualizar tarjetas de resumen
    document.getElementById('totalEssays').textContent = total;
    document.getElementById('avgScore').textContent = avg.toFixed(2);
    document.getElementById('highestScore').textContent = max.toFixed(2);
    document.getElementById('lowestScore').textContent = min.toFixed(2);

    // Crear gráficos
    createScoresChart(scores);
    await createCriteriaRadarChart();
}

function createScoresChart(scores) {
    const ctx = document.getElementById('scoresChart');
    
    // Destruir gráfico anterior si existe
    if (scoresChartInstance) {
        scoresChartInstance.destroy();
    }

    // Contar ensayos por rango
    const ranges = [
        { label: '0-1', min: 0, max: 1, color: '#ef4444' },
        { label: '1-2', min: 1, max: 2, color: '#f97316' },
        { label: '2-3', min: 2, max: 3, color: '#f59e0b' },
        { label: '3-4', min: 3, max: 4, color: '#3b82f6' },
        { label: '4-5', min: 4, max: 5, color: '#10b981' }
    ];

    const data = ranges.map(range => 
        scores.filter(s => s >= range.min && s < range.max).length
    );
    
    // Agregar los que tienen exactamente 5
    data[data.length - 1] += scores.filter(s => s === 5).length;

    scoresChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ranges.map(r => r.label),
            datasets: [{
                label: '# de Ensayos',
                data: data,
                backgroundColor: ranges.map(r => r.color),
                borderColor: ranges.map(r => r.color),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

async function createCriteriaRadarChart() {
    const ctx = document.getElementById('criteriaRadarChart');
    
    // Destruir gráfico anterior si existe
    if (criteriaRadarChartInstance) {
        criteriaRadarChartInstance.destroy();
    }

    // Intentar obtener datos reales de criterios
    try {
        const criteriaAverages = calculateCriteriaAverages();
        
        if (criteriaAverages.labels.length === 0) {
            // Si no hay datos de criterios, usar datos de ejemplo
            createExampleRadarChart(ctx);
            return;
        }

        criteriaRadarChartInstance = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: criteriaAverages.labels,
                datasets: [{
                    label: 'Promedio de la Generación',
                    data: criteriaAverages.data,
                    backgroundColor: 'rgba(59, 130, 246, 0.2)',
                    borderColor: '#3b82f6',
                    borderWidth: 2,
                    pointBackgroundColor: '#3b82f6',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#3b82f6'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 5,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creando gráfico de radar:', error);
        createExampleRadarChart(ctx);
    }
}

function calculateCriteriaAverages() {
    const criteriaMap = new Map();
    let essayCount = 0;

    // Iterar sobre todos los ensayos y acumular puntajes por criterio
    allEssays.forEach(essay => {
        const evaluacion = essay.evaluacion || essay;
        const criterios = evaluacion.criterios || [];
        
        if (criterios.length > 0) {
            essayCount++;
            criterios.forEach(criterio => {
                if (criterio.calificacion !== null && criterio.calificacion !== undefined) {
                    const nombre = criterio.nombre || criterio.criterio;
                    if (!criteriaMap.has(nombre)) {
                        criteriaMap.set(nombre, []);
                    }
                    criteriaMap.get(nombre).push(criterio.calificacion);
                }
            });
        }
    });

    // Calcular promedios
    const labels = [];
    const data = [];

    criteriaMap.forEach((values, name) => {
        const avg = values.reduce((a, b) => a + b, 0) / values.length;
        labels.push(name);
        data.push(parseFloat(avg.toFixed(2)));
    });

    return { labels, data };
}

function createExampleRadarChart(ctx) {
    criteriaRadarChartInstance = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Técnica', 'Creatividad', 'Temática', 'Bienestar', 'IA', 'Impacto'],
            datasets: [{
                label: 'Promedio de la Generación',
                data: [3.8, 4.2, 3.5, 4.0, 2.9, 3.6],
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                borderColor: '#3b82f6',
                borderWidth: 2,
                pointBackgroundColor: '#3b82f6',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#3b82f6'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 5,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                title: {
                    display: true,
                    text: '(Datos de ejemplo)',
                    font: {
                        size: 11,
                        style: 'italic'
                    }
                }
            }
        }
    });
}

// ============================================
// JUDGE EVALUATION FUNCTIONS
// ============================================

let currentJudgeCriteria = [];
let currentEssayForEval = null;

// Mostrar sección de evaluación manual
async function showJudgeEvaluation() {
    essaysLibrarySection.style.display = 'none';
    uploadSection.style.display = 'none';
    resultsSection.style.display = 'none';
    criteriaSectionDiv.style.display = 'none';
    judgeEvaluationSection.style.display = 'block';
    
    // Cargar criterios y ensayos
    await loadJudgeCriteria();
    await loadEssaysForSelection();
}

// Cargar criterios del usuario
async function loadJudgeCriteria() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/criterios', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) throw new Error('Error al cargar criterios');
        
        const data = await response.json();
        currentJudgeCriteria = data.criterios || [];
        
        renderJudgeCriteriaDisplay();
        generateEvaluationFields();
        
    } catch (error) {
        console.error('Error al cargar criterios:', error);
        showNotification('Error al cargar criterios personalizados', 'error');
    }
}

// Renderizar criterios en el panel izquierdo
function renderJudgeCriteriaDisplay() {
    if (!criteriaCardsDisplay) return;
    
    if (currentJudgeCriteria.length === 0) {
        criteriaCardsDisplay.innerHTML = `
            <div class="empty-state">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="width: 48px; height: 48px; color: #94a3b8; margin-bottom: 1rem;">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 style="color: #64748b; margin: 0 0 0.5rem 0;">No hay criterios personalizados</h3>
                <p style="color: #94a3b8; font-size: 0.9rem;">Define tus criterios de evaluación primero para poder usar esta función.</p>
            </div>
        `;
        return;
    }
    
    criteriaCardsDisplay.innerHTML = currentJudgeCriteria
        .sort((a, b) => a.orden - b.orden)
        .map(criterio => `
            <div class="criteria-view-card">
                <div class="criteria-view-header">
                    <div class="criteria-view-title">
                        <span>${criterio.icono || '📋'}</span>
                        <span>${criterio.nombre}</span>
                    </div>
                    <div class="criteria-view-weight">${criterio.peso}%</div>
                </div>
                <div class="criteria-view-description">${criterio.descripcion || 'Sin descripción'}</div>
            </div>
        `).join('');
}

// Generar campos de evaluación dinámicamente
function generateEvaluationFields() {
    if (!criteriaFieldsContainer) return;
    
    if (currentJudgeCriteria.length === 0) {
        criteriaFieldsContainer.innerHTML = `
            <div class="empty-state" style="text-align: center; padding: 2rem;">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="width: 64px; height: 64px; color: #cbd5e1; margin: 0 auto 1rem;">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <h3 style="color: #64748b; margin: 0 0 0.5rem 0; font-size: 1.1rem;">No hay criterios definidos</h3>
                <p style="color: #94a3b8; margin-bottom: 1.5rem;">Define tus criterios personalizados para poder evaluar ensayos manualmente.</p>
                <button onclick="document.getElementById('criteriaManagementSection').style.display='block'; document.getElementById('judgeEvaluationSection').style.display='none'; essaysLibrarySection.style.display='none';" class="btn-primary" style="padding: 0.75rem 1.5rem; font-size: 0.95rem;">
                    ⚙️ Configurar Criterios Ahora
                </button>
            </div>
        `;
        return;
    }
    
    criteriaFieldsContainer.innerHTML = currentJudgeCriteria
        .sort((a, b) => a.orden - b.orden)
        .map(criterio => `
            <div class="criterion-field" data-criterion-id="${criterio.id}">
                <div class="criterion-field-header">
                    <div class="criterion-field-title">
                        <span>${criterio.icono || '📋'}</span>
                        <span>${criterio.nombre}</span>
                    </div>
                    <div class="criterion-field-max">Máx: ${criterio.peso} pts</div>
                </div>
                <div class="criterion-field-input-group">
                    <input 
                        type="number" 
                        class="score-input" 
                        data-criterion-id="${criterio.id}"
                        data-max="${criterio.peso}"
                        min="0" 
                        max="${criterio.peso}" 
                        step="0.1"
                        placeholder="0.0"
                        required
                    />
                    <textarea 
                        class="criterion-comments" 
                        data-criterion-id="${criterio.id}"
                        placeholder="Comentarios sobre ${criterio.nombre}..."
                    ></textarea>
                </div>
            </div>
        `).join('');
    
    // Agregar listeners para calcular total automáticamente
    const scoreInputs = criteriaFieldsContainer.querySelectorAll('.score-input');
    scoreInputs.forEach(input => {
        input.addEventListener('input', calculateTotalScore);
    });
}

// Calcular puntuación total
function calculateTotalScore() {
    const scoreInputs = criteriaFieldsContainer.querySelectorAll('.score-input');
    let total = 0;
    
    scoreInputs.forEach(input => {
        const value = parseFloat(input.value) || 0;
        const max = parseFloat(input.dataset.max) || 0;
        
        // Validar que no exceda el máximo
        if (value > max) {
            input.value = max;
            showNotification(`La puntuación no puede exceder ${max} puntos`, 'warning');
        }
        
        total += parseFloat(input.value) || 0;
    });
    
    if (totalScoreValue) {
        totalScoreValue.textContent = total.toFixed(2);
        
        // Cambiar color según la puntuación
        if (total >= 80) {
            totalScoreValue.style.color = '#22c55e';
        } else if (total >= 60) {
            totalScoreValue.style.color = '#0ea5e9';
        } else {
            totalScoreValue.style.color = '#ef4444';
        }
    }
}

// Cargar ensayos para el selector
async function loadEssaysForSelection() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/ensayos', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) throw new Error('Error al cargar ensayos');
        
        const data = await response.json();
        const essays = data.ensayos || [];
        
        if (essaySelectForEval) {
            essaySelectForEval.innerHTML = '<option value="">-- Seleccione un ensayo --</option>' + 
                essays.map(essay => `
                    <option value="${essay.id}">${essay.autor || 'Autor desconocido'} - ${essay.titulo || 'Sin título'}</option>
                `).join('');
        }
        
    } catch (error) {
        console.error('Error al cargar ensayos:', error);
        showNotification('Error al cargar la lista de ensayos', 'error');
    }
}

// Al seleccionar un ensayo
function onEssaySelectedForEval() {
    const essayId = essaySelectForEval.value;
    if (essayId) {
        currentEssayForEval = parseInt(essayId);
        // Aquí podrías cargar información adicional del ensayo si es necesario
    } else {
        currentEssayForEval = null;
    }
}

// Solicitar asistencia de IA
async function requestAIAssistance() {
    if (!currentEssayForEval) {
        showNotification('Selecciona un ensayo primero', 'warning');
        return;
    }
    
    if (currentJudgeCriteria.length === 0) {
        showNotification('Define criterios personalizados antes de usar la IA', 'warning');
        return;
    }
    
    try {
        aiAssistBtn.disabled = true;
        aiAssistBtn.innerHTML = `
            <svg class="spinner" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" width="20" height="20">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Procesando...
        `;
        
        const token = localStorage.getItem('token');
        
        // Preparar datos de los criterios
        const criteriosData = currentJudgeCriteria.map(c => ({
            id: c.id,
            nombre: c.nombre,
            descripcion: c.descripcion,
            peso: c.peso
        }));
        
        const response = await fetch(`/api/evaluar_con_criterios/${currentEssayForEval}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ criterios: criteriosData })
        });
        
        if (!response.ok) throw new Error('Error en la evaluación con IA');
        
        const data = await response.json();
        
        // Rellenar los campos con las sugerencias de la IA
        if (data.evaluacion) {
            data.evaluacion.forEach(evalItem => {
                const input = criteriaFieldsContainer.querySelector(`.score-input[data-criterion-id="${evalItem.criterio_id}"]`);
                const textarea = criteriaFieldsContainer.querySelector(`.criterion-comments[data-criterion-id="${evalItem.criterio_id}"]`);
                
                if (input) input.value = evalItem.puntuacion || 0;
                if (textarea) textarea.value = evalItem.comentario || '';
            });
            
            calculateTotalScore();
            showNotification('Evaluación asistida por IA completada', 'success');
        }
        
    } catch (error) {
        console.error('Error en asistencia de IA:', error);
        showNotification('Error al obtener asistencia de IA', 'error');
    } finally {
        aiAssistBtn.disabled = false;
        aiAssistBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="20" height="20">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            IA
        `;
    }
}

// Guardar evaluación manual
async function saveManualEvaluation() {
    if (!currentEssayForEval) {
        showNotification('Selecciona un ensayo para evaluar', 'warning');
        return;
    }
    
    if (currentJudgeCriteria.length === 0) {
        showNotification('No hay criterios definidos', 'warning');
        return;
    }
    
    // Validar que todos los campos estén llenos
    const scoreInputs = criteriaFieldsContainer.querySelectorAll('.score-input');
    let allFilled = true;
    
    scoreInputs.forEach(input => {
        if (!input.value || input.value === '') {
            allFilled = false;
            input.style.borderColor = '#ef4444';
        } else {
            input.style.borderColor = '';
        }
    });
    
    if (!allFilled) {
        showNotification('Completa todas las puntuaciones antes de guardar', 'warning');
        return;
    }
    
    try {
        saveEvaluationBtn.disabled = true;
        saveEvaluationBtn.innerHTML = `
            <svg class="spinner" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" width="20" height="20">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Guardando...
        `;
        
        // Recopilar datos de la evaluación
        const evaluaciones = [];
        scoreInputs.forEach(input => {
            const criterioId = parseInt(input.dataset.criterionId);
            const puntuacion = parseFloat(input.value);
            const textarea = criteriaFieldsContainer.querySelector(`.criterion-comments[data-criterion-id="${criterioId}"]`);
            const comentario = textarea ? textarea.value : '';
            
            evaluaciones.push({
                criterio_id: criterioId,
                puntuacion: puntuacion,
                comentario: comentario
            });
        });
        
        const generalComments = document.getElementById('generalComments').value;
        const totalScore = parseFloat(totalScoreValue.textContent);
        
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/guardar_evaluacion_manual/${currentEssayForEval}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                evaluaciones: evaluaciones,
                comentario_general: generalComments,
                puntuacion_total: totalScore
            })
        });
        
        if (!response.ok) throw new Error('Error al guardar evaluación');
        
        showNotification('Evaluación guardada exitosamente', 'success');
        
        // Limpiar formulario
        manualEvaluationForm.reset();
        calculateTotalScore();
        
    } catch (error) {
        console.error('Error al guardar evaluación:', error);
        showNotification('Error al guardar la evaluación', 'error');
    } finally {
        saveEvaluationBtn.disabled = false;
        saveEvaluationBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="20" height="20">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Guardar
        `;
    }
}
