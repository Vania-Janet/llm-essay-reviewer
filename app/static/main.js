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
// const editReportBtn = document.getElementById('editReportBtn'); // Eliminado del HTML
const downloadReportBtn = document.getElementById('downloadReportBtn');
const scoreEditor = document.getElementById('scoreEditor');
const closeScoreEditor = document.getElementById('closeScoreEditor');
const editTotalScore = document.getElementById('editTotalScore');
const saveScoreBtn = document.getElementById('saveScoreBtn');

// Judge evaluation elements
const navTabIA = document.getElementById('navTabIA');
const navTabManual = document.getElementById('navTabManual');
const judgeEvaluationBtn = document.getElementById('judgeEvaluationBtn'); // Mantener para compatibilidad
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

// Queue and PDF viewer elements (for manual evaluation)
const queueList = document.getElementById('queueList');
const pdfFrame = document.getElementById('pdfFrame');
const pdfContainer = document.getElementById('pdfContainer');
const rubricForm = document.getElementById('rubricForm');
const currentTotal = document.getElementById('currentTotal');

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
// Nota: El token ahora se almacena en cookies HttpOnly (más seguro)
// Solo mantenemos el usuario en localStorage para estado de UI
const USER_KEY = 'user';

function getUser() {
    const userStr = localStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
}

function setUser(user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function clearAuth() {
    localStorage.removeItem(USER_KEY);
    // Limpiar cualquier otro dato de sesión
    sessionStorage.clear();
    // El token se limpiará automáticamente al expirar la cookie
}

function logout() {
    clearAuth();
    // Llamar al endpoint de logout para limpiar la cookie
    fetch('/api/logout', {
        method: 'POST',
        credentials: 'same-origin'
    }).finally(() => {
        // Forzar redirección completa para limpiar estado
        window.location.replace('/login');
        // Prevenir navegación hacia atrás
        window.history.pushState(null, '', '/login');
    });
}

// Verificar autenticación al cargar la página
async function checkAuth() {
    try {
        const response = await fetch('/api/verify-token', {
            credentials: 'same-origin'  // Incluir cookies automáticamente
        });
        
        if (!response.ok) {
            clearAuth();
            window.location.href = '/login';
            return false;
        }
        
        return true;
    } catch (error) {
        console.error('Error verificando autenticación:', error);
        clearAuth();
        window.location.href = '/login';
        return false;
    }
}

// Función helper para hacer requests autenticados
async function authenticatedFetch(url, options = {}) {
    // No necesitamos agregar token manualmente, las cookies se envían automáticamente
    const response = await fetch(url, {
        ...options,
        credentials: 'same-origin'  // Asegurar que se incluyan las cookies
    });
    
    if (response.status === 401) {
        clearAuth();
        window.location.href = '/login';
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
        
        // Prevenir navegación hacia atrás después de autenticación
        window.history.pushState(null, '', window.location.href);
        window.addEventListener('popstate', function() {
            window.history.pushState(null, '', window.location.href);
        });
    }
});

// ============= FIN AUTENTICACIÓN =============

// ============= UTILITY FUNCTIONS =============

/**
 * Extract a clean title from the filename
 * @param {string} filename - The filename to process
 * @returns {string} - The extracted title
 */
function extractTitle(filename) {
    // Remove extension
    let title = filename.replace('.pdf', '').replace('.txt', '');
    
    // Format: "Ensayo_Autor_Titulo..."
    const parts = title.split('_');
    
    if (parts.length >= 3 && parts[0] === 'Ensayo') {
        // Join all parts after author to form the title
        const titleParts = parts.slice(2);
        title = titleParts.join(' ');
        
        // Limit length and capitalize
        if (title.length > 60) {
            title = title.substring(0, 60) + '...';
        }
    } else if (title.length > 60) {
        // If it doesn't follow expected format, simply truncate
        title = title.substring(0, 60) + '...';
    }
    
    return title;
}

/**
 * Extract the author from the filename
 * @param {string} filename - The filename to process
 * @returns {string} - The extracted author name
 */
function extractAuthor(filename) {
    const parts = filename.replace('.pdf', '').replace('.txt', '').split('_');
    if (parts.length >= 2 && parts[0] === 'Ensayo') {
        return parts[1];
    }
    return 'Desconocido';
}

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
// editReportBtn.addEventListener('click', toggleEditMode); // Botón eliminado
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

// Navigation tabs event listeners
if (navTabIA) navTabIA.addEventListener('click', () => switchToTab('library'));
if (navTabManual) navTabManual.addEventListener('click', () => switchToTab('judge'));

// Judge evaluation event listeners
if (judgeEvaluationBtn) judgeEvaluationBtn.addEventListener('click', showJudgeEvaluation);
if (backFromJudgeBtn) backFromJudgeBtn.addEventListener('click', returnToLibrary);
if (refreshCriteriaPdfBtn) refreshCriteriaPdfBtn.addEventListener('click', loadJudgeCriteria);
if (aiAssistBtn) aiAssistBtn.addEventListener('click', requestAIAssistance);
if (saveEvaluationBtn) saveEvaluationBtn.addEventListener('click', saveManualEvaluation);
if (essaySelectForEval) essaySelectForEval.addEventListener('change', onEssaySelectedForEval);

// Event listeners para botones de puntuación en evaluación manual
if (rubricForm) {
    rubricForm.addEventListener('click', (e) => {
        if (e.target.matches('.score-segments button')) {
            const criterion = e.target.closest('.score-segments').dataset.criterion;
            const score = parseInt(e.target.dataset.score);
            selectScoreButton(criterion, score);
        }
    });
}

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
        const response = await authenticatedFetch('/api/evaluate', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Error al procesar el archivo');
        }

        const result = await response.json();
        
        // 🚀 Verificar si fue un cache hit (respuesta inmediata)
        if (result.cache_hit) {
            showEnhancedNotification(result.mensaje_cache || '⚡ Evaluación recuperada del caché', 'success');
            console.log('⚡ CACHE HIT - Evaluación recuperada instantáneamente');
            
            // Guardar evaluación y texto para el chat
            currentEvaluation = result;
            currentEssayText = result.texto_completo || '';
            
            // Mostrar resultados inmediatamente
            displayResults(result);
            enableChat();
            return;
        }
        
        // 🔄 Si no es cache hit, es un job asíncrono - hacer polling
        if (result.job_id) {
            console.log(`🚀 Job ${result.job_id} iniciado - polling cada 2 segundos`);
            showEnhancedNotification('🔄 Procesando ensayo con IA...', 'info');
            
            // Polling para verificar el status del job
            const checkJobStatus = async () => {
                try {
                    const statusResponse = await authenticatedFetch(`/api/job-status/${result.job_id}`);
                    if (!statusResponse.ok) {
                        throw new Error('Error al verificar status del job');
                    }
                    
                    const jobStatus = await statusResponse.json();
                    console.log(`📊 Job status: ${jobStatus.status} (${jobStatus.progress}%)`);
                    
                    // Actualizar barra de progreso (si la tienes en el HTML)
                    // document.getElementById('progress').value = jobStatus.progress;
                    
                    if (jobStatus.status === 'completed') {
                        // Job completado - mostrar resultados
                        showEnhancedNotification('✅ Evaluación completada', 'success');
                        
                        currentEvaluation = jobStatus.result;
                        currentEssayText = jobStatus.result.texto_completo || '';
                        
                        displayResults(jobStatus.result);
                        enableChat();
                        
                    } else if (jobStatus.status === 'error') {
                        // Error en el procesamiento
                        throw new Error(jobStatus.error || 'Error desconocido al procesar');
                        
                    } else {
                        // Aún procesando - seguir polling
                        setTimeout(checkJobStatus, 2000);  // 2 segundos
                    }
                    
                } catch (error) {
                    console.error('Error en polling:', error);
                    showEnhancedNotification('❌ Error al procesar: ' + error.message, 'error');
                    resetEvaluation();
                }
            };
            
            // Iniciar polling después de 2 segundos
            setTimeout(checkJobStatus, 2000);
        }
        
    } catch (error) {
        console.error('Error:', error);
        showEnhancedNotification('❌ Error al enviar ensayo: ' + error.message, 'error');
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
    
    if (evaluation.nombre_archivo_original || evaluation.nombre_archivo) {
        // Usar el nombre original si está disponible
        const nombreDisplay = evaluation.nombre_archivo_original || evaluation.nombre_archivo;
        // Extraer el nombre del archivo sin la extensión
        let displayName = nombreDisplay.replace('_procesado.txt', '').replace('.txt', '').replace('.pdf', '');
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
        const response = await authenticatedFetch('/api/chat', {
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
        // editReportBtn.textContent = '💾 Guardar Edición';
        // editReportBtn.style.background = 'var(--gradient)';
        // editReportBtn.style.color = 'white';
        // editReportBtn.style.borderColor = 'transparent';
        
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
        // editReportBtn.innerHTML = `
        //     <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        //         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        //     </svg>
        //     Editar Reporte
        // `;
        // editReportBtn.style.background = 'white';
        // editReportBtn.style.color = 'var(--primary-blue)';
        // editReportBtn.style.borderColor = 'var(--primary-blue)';
        
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
    
    // Nombre del archivo con wrap para evitar recorte
    doc.setTextColor(0, 0, 0);
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    const essayTitleText = `Ensayo: ${currentFileName || 'Sin nombre'}`;
    const titleLines = doc.splitTextToSize(cleanTextForPDF(essayTitleText), maxWidth);
    titleLines.forEach((line) => {
        doc.text(line, margin, yPos);
        yPos += 6;
    });
    yPos += 4;
    
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
    essaysLibrarySection.style.display = 'none';
    uploadSection.style.display = 'none';
    resultsSection.style.display = 'none';
    comparisonSection.style.display = 'none';
    judgeEvaluationSection.style.display = 'none';
    
    // 🎨 SKELETON SCREEN en lugar de loader
    showSkeletonLoading(essaysList, 5);
    selectedEssays.clear();
    compareSelectedBtn.disabled = true;
    
    try {
        const response = await authenticatedFetch('/api/essays');
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
                    <div class="essay-name">${escapeHtml(essay.nombre_archivo_original || essay.nombre_archivo)}</div>
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
    essaysLibrarySection.style.display = 'block';
    uploadSection.style.display = 'none';
    resultsSection.style.display = 'none';
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
    
    // Ocultar la biblioteca y mostrar la sección de comparación
    essaysLibrarySection.style.display = 'none';
    uploadSection.style.display = 'none';
    resultsSection.style.display = 'none';
    comparisonSection.style.display = 'block';
    comparisonContent.innerHTML = '<div class="loader"></div><p>Generando análisis comparativo...</p>';
    
    try {
        const response = await authenticatedFetch('/api/compare', {
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
                    <h4>${index + 1}. ${(essay.nombre_archivo_original || essay.nombre_archivo).replace('.txt', '').replace('.pdf', '').replace('Ensayo_', '').substring(0, 40)}...</h4>
                    <div class="comparison-score" style="font-size: 1.5rem; padding: 0.5rem 1rem;">${essay.puntuacion_total.toFixed(2)}</div>
                </div>
                <p style="margin: 0.5rem 0; color: #6b7280;">📎 ${essay.tiene_anexo ? 'Con Anexo IA' : 'Sin Anexo IA'}</p>
            </div>
        `).join('');
        
        // Convertir markdown a HTML mejorado con mejor formato
        let comparisonHTML = result.comparacion;
        
        // Normalizar saltos de línea múltiples
        comparisonHTML = comparisonHTML.replace(/\n{3,}/g, '\n\n');
        
        // Convertir líneas de ranking (Ensayo N: "Título" - X.XX/5.0)
        comparisonHTML = comparisonHTML.replace(/^(Ensayo \d+): "(.*?)" - (\d+\.\d+)\/5\.0$/gm, 
            '<div class="ranking-item"><span class="ranking-number">$1</span><span class="ranking-title">"$2"</span><span class="ranking-score">$3/5.0</span></div>');
        
        // Convertir encabezados
        comparisonHTML = comparisonHTML.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
        comparisonHTML = comparisonHTML.replace(/^### (.+)$/gm, '<h3>$1</h3>');
        comparisonHTML = comparisonHTML.replace(/^## (.+)$/gm, '<h2>$1</h2>');
        comparisonHTML = comparisonHTML.replace(/^# (.+)$/gm, '<h2>$1</h2>');
        
        // Convertir negritas
        comparisonHTML = comparisonHTML.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        
        // Convertir listas numeradas - mejorado
        comparisonHTML = comparisonHTML.replace(/^(\d+\.\s+.+$(?:\n(?!\d+\.|\n|^[#-]).*$)*)/gm, (match) => {
            const items = match.split(/\n(?=\d+\.\s)/);
            const listItems = items.map(item => {
                const content = item.replace(/^\d+\.\s+/, '');
                return `<li>${content}</li>`;
            }).join('');
            return `<ol>${listItems}</ol>`;
        });
        
        // Convertir listas con viñetas - mejorado
        comparisonHTML = comparisonHTML.replace(/^(-\s+.+$(?:\n(?!-\s|\n|^[#]).*$)*)/gm, (match) => {
            const items = match.split(/\n(?=-\s)/);
            const listItems = items.map(item => {
                const content = item.replace(/^-\s+/, '');
                return `<li>${content}</li>`;
            }).join('');
            return `<ul>${listItems}</ul>`;
        });
        
        // Convertir párrafos (doble salto de línea)
        comparisonHTML = comparisonHTML.split(/\n\n+/).map(para => {
            para = para.trim();
            if (!para) return '';
            if (para.startsWith('<h') || para.startsWith('<ul') || para.startsWith('<ol')) {
                return para;
            }
            return `<p>${para.replace(/\n/g, ' ')}</p>`;
        }).join('\n');
        
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
    essaysLibrarySection.style.display = 'block';
    uploadSection.style.display = 'none';
    resultsSection.style.display = 'none';
}

// Funciones para la biblioteca de ensayos
async function loadEssaysLibrary() {
    try {
        // 🎨 SKELETON LOADING mejorado
        libraryList.innerHTML = createSkeletonCards(6);
        
        const response = await authenticatedFetch('/api/essays');
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
    libraryList.innerHTML = essays.map(essay => {
        const anexoIndicator = essay.tiene_anexo 
            ? '<span class="anexo-indicator anexo-ok">✓ Anexo IA</span>'
            : '<span class="anexo-indicator anexo-missing">⚠️ Sin Anexo IA</span>';
        
        const nombreParaDisplay = essay.nombre_archivo_original || essay.nombre_archivo;
        const title = escapeHtml(extractTitle(nombreParaDisplay));
        const author = escapeHtml(extractAuthor(nombreParaDisplay));
        
        // Determinar clase de color según puntuación
        let scoreClass = 'score-low';
        if (essay.puntuacion_total >= 4.5) {
            scoreClass = 'score-excellent';
        } else if (essay.puntuacion_total >= 4.0) {
            scoreClass = 'score-good';
        } else if (essay.puntuacion_total >= 3.5) {
            scoreClass = 'score-average';
        }
        
        return `
            <div class="essay-card" data-id="${essay.id}">
                <div class="essay-card-header">
                    <input type="checkbox" class="essay-card-checkbox" data-id="${essay.id}">
                    <div class="essay-card-title">${title}</div>
                </div>
                <div class="essay-card-author">Por: ${author}</div>
                <div class="essay-card-score ${scoreClass}">${essay.puntuacion_total.toFixed(2)}/5.00</div>
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
        const response = await authenticatedFetch(`/api/essays/${essayId}`);
        if (!response.ok) throw new Error('Error al cargar ensayo');
        
        const essay = await response.json();
        
        // Actualizar variables globales con la estructura de la base de datos
        currentEvaluation = {
            id: essay.id,
            ...essay.evaluacion,  // Extraer la evaluación del objeto
            nombre_archivo: essay.nombre_archivo,
            nombre_archivo_original: essay.nombre_archivo_original,
            fecha_evaluacion: essay.fecha_evaluacion,
            tiene_anexo: essay.tiene_anexo
        };
        currentEssayText = essay.texto_completo;
        currentFileName = (essay.nombre_archivo_original || essay.nombre_archivo).replace('.pdf', '').replace('.txt', '');
        
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
        const pdfUrl = `/api/essays/${essayId}/pdf`;
        
        // Fetch PDF with authentication - get as blob
        const response = await authenticatedFetch(pdfUrl);
        
        if (response.ok) {
            // Convert response to blob
            const blob = await response.blob();
            
            // Verificar que el blob no esté vacío
            if (blob.size === 0) {
                throw new Error('El archivo PDF está vacío');
            }
            
            // Create object URL from blob
            const objectUrl = URL.createObjectURL(blob);
            
            // Clean up previous object URL if exists
            if (pdfViewer.src && pdfViewer.src.startsWith('blob:')) {
                URL.revokeObjectURL(pdfViewer.src);
            }
            
            // Load PDF in the iframe using object URL
            pdfViewer.src = objectUrl;
            pdfViewerContainer.style.display = 'block';
            pdfViewer.style.display = 'block';
            pdfError.style.display = 'none';
            
            // Agregar listener para detectar errores de carga del PDF
            pdfViewer.onerror = () => {
                console.error('Error al cargar el PDF en el iframe');
                pdfViewerContainer.style.display = 'block';
                pdfViewer.style.display = 'none';
                pdfError.style.display = 'flex';
                pdfError.innerHTML = '<p>⚠️ Error al cargar el PDF. El archivo puede estar corrupto.</p>';
            };
        } else {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `Error ${response.status}: No se pudo cargar el PDF`);
        }
    } catch (error) {
        console.error('Error al cargar PDF:', error);
        pdfViewerContainer.style.display = 'block';
        pdfViewer.style.display = 'none';
        pdfError.style.display = 'flex';
        pdfError.innerHTML = `<p>⚠️ ${error.message || 'No se pudo cargar el PDF'}</p>`;
    }
}

function showUploadSection() {
    // Limpiar estado anterior completamente
    selectedFile = null;
    fileInput.value = '';
    currentEvaluation = null;
    currentEssayText = null;
    currentFileName = '';
    
    // Ocultar todas las secciones
    essaysLibrarySection.style.display = 'none';
    resultsSection.style.display = 'none';
    processingSection.style.display = 'none';
    judgeEvaluationSection.style.display = 'none';
    essaysHistorySection.style.display = 'none';
    comparisonSection.style.display = 'none';
    
    const criteriaSection = document.getElementById('criteriaManagementSection');
    if (criteriaSection) criteriaSection.style.display = 'none';
    
    // Mostrar sección de upload limpia
    uploadSection.style.display = 'block';
    dropZone.style.display = 'block';
    fileInfo.style.display = 'none';
    evaluateBtn.disabled = true;
    
    // Asegurarse de que la zona de drop está activa
    dropZone.classList.remove('drag-over');
    
    // Scroll to top smoothly
    window.scrollTo({ top: 0, behavior: 'smooth' });
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

// Función para descargar CSV (compatible con Excel básico)
async function downloadCSV() {
    try {
        const downloadBtn = document.getElementById('downloadCSVBtn');
        const originalText = downloadBtn.innerHTML;
        
        // Mostrar estado de descarga
        downloadBtn.disabled = true;
        downloadBtn.innerHTML = '⏳ Descargando...';
        
        const response = await authenticatedFetch('/api/essays/export/csv');
        
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
        showNotification('✅ CSV descargado exitosamente', 'success');
        
    } catch (error) {
        console.error('Error al descargar CSV:', error);
        
        const downloadBtn = document.getElementById('downloadCSVBtn');
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = '📄 Descargar CSV';
        
        showNotification('❌ Error al descargar CSV: ' + error.message, 'error');
    }
}

// Función para descargar Excel profesional con formato mejorado
async function downloadExcel() {
    try {
        const downloadBtn = document.getElementById('downloadExcelBtn');
        const originalText = downloadBtn.innerHTML;
        
        // Mostrar estado de descarga
        downloadBtn.disabled = true;
        downloadBtn.innerHTML = '⏳ Generando Excel...';
        
        const response = await authenticatedFetch('/api/essays/export/excel');
        
        if (!response.ok) {
            throw new Error('Error al generar el archivo Excel');
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
        let filename = 'ensayos_evaluados_profesional.xlsx';
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
        showNotification('✅ Excel profesional descargado exitosamente', 'success');
        
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
            // Si no hay datos, mostrar mensaje
            ctx.parentElement.innerHTML = '<p style="text-align: center; color: #6b7280; padding: 2rem;">No hay datos suficientes para generar el gráfico de criterios. Evalúa al menos un ensayo.</p>';
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
        ctx.parentElement.innerHTML = '<p style="text-align: center; color: #ef4444; padding: 2rem;">Error al generar el gráfico de criterios.</p>';
    }
}

function calculateCriteriaAverages() {
    // Mapa para acumular calificaciones por criterio desde la base de datos
    const criteriaScores = {
        'Calidad Técnica': [],
        'Creatividad': [],
        'Vinculación Temática': [],
        'Bienestar Colectivo': [],
        'Uso Responsable IA': [],
        'Potencial Impacto': []
    };

    // Iterar sobre todos los ensayos y extraer calificaciones desde evaluacion_data
    allEssays.forEach(essay => {
        // Los datos vienen de evaluacion_data que es un JSON parseado
        const evaluacionData = essay.evaluacion_data;
        
        if (!evaluacionData) return;
        
        // Extraer calificaciones de cada criterio
        if (evaluacionData.calidad_tecnica?.calificacion !== undefined) {
            criteriaScores['Calidad Técnica'].push(parseFloat(evaluacionData.calidad_tecnica.calificacion));
        }
        if (evaluacionData.creatividad?.calificacion !== undefined) {
            criteriaScores['Creatividad'].push(parseFloat(evaluacionData.creatividad.calificacion));
        }
        if (evaluacionData.vinculacion_tematica?.calificacion !== undefined) {
            criteriaScores['Vinculación Temática'].push(parseFloat(evaluacionData.vinculacion_tematica.calificacion));
        }
        if (evaluacionData.bienestar_colectivo?.calificacion !== undefined) {
            criteriaScores['Bienestar Colectivo'].push(parseFloat(evaluacionData.bienestar_colectivo.calificacion));
        }
        if (evaluacionData.uso_responsable_ia?.calificacion !== undefined) {
            criteriaScores['Uso Responsable IA'].push(parseFloat(evaluacionData.uso_responsable_ia.calificacion));
        }
        if (evaluacionData.potencial_impacto?.calificacion !== undefined) {
            criteriaScores['Potencial Impacto'].push(parseFloat(evaluacionData.potencial_impacto.calificacion));
        }
    });

    // Calcular promedios solo para criterios con datos
    const labels = [];
    const data = [];

    Object.entries(criteriaScores).forEach(([criterio, scores]) => {
        if (scores.length > 0) {
            const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
            labels.push(criterio);
            data.push(parseFloat(avg.toFixed(2)));
        }
    });

    return { labels, data };
}

// ============================================
// JUDGE EVALUATION FUNCTIONS
// ============================================

let currentJudgeCriteria = [];
let currentEssayForEval = null;

// Función para cambiar entre tabs de navegación
function switchToTab(section) {
    console.log('🔄 Switching to tab:', section);
    
    // Actualizar estado visual de los tabs
    const navTabIA = document.getElementById('navTabIA');
    const navTabManual = document.getElementById('navTabManual');
    
    if (section === 'library') {
        console.log('📚 Switching to library view');
        navTabIA.classList.add('active');
        navTabManual.classList.remove('active');
        returnToLibrary();
    } else if (section === 'judge') {
        console.log('👨‍⚖️ Switching to judge evaluation view');
        navTabManual.classList.add('active');
        navTabIA.classList.remove('active');
        showJudgeEvaluation();
    }
    
    console.log('✅ Tab switch complete');
}

// Mostrar sección de evaluación manual
// NOTA: Esta función está definida en grading-cockpit.js
// async function showJudgeEvaluation() {
//     essaysLibrarySection.style.display = 'none';
//     uploadSection.style.display = 'none';
//     resultsSection.style.display = 'none';
//     criteriaSectionDiv.style.display = 'none';
//     judgeEvaluationSection.style.display = 'block';
//     
//     // Cargar criterios y ensayos en la cola
//     await loadJudgeCriteria();
//     await loadEssaysQueue();  // Nueva función para cargar cola
// }

// Nueva función: Cargar ensayos en la cola de evaluación
async function loadEssaysQueue() {
    try {
        if (!queueList) return;
        
        queueList.innerHTML = '<div class="queue-loading"><div class="loader"></div><p>Cargando...</p></div>';
        
        const response = await authenticatedFetch('/api/essays');
        if (!response.ok) throw new Error('Error al cargar ensayos');
        
        const essays = await response.json();
        
        if (essays.length === 0) {
            queueList.innerHTML = `
                <div class="empty-queue">
                    <p style="color: #94a3b8; text-align: center; padding: 2rem;">
                        No hay ensayos para evaluar
                    </p>
                </div>
            `;
            return;
        }
        
        // Renderizar lista de ensayos
        queueList.innerHTML = essays.map(essay => {
            const filename = essay.nombre_archivo_original || essay.nombre_archivo || 'Sin nombre';
            const author = extractAuthor(filename);
            const score = essay.puntuacion_total ? essay.puntuacion_total.toFixed(2) : '—';
            
            return `
                <div class="queue-item" data-essay-id="${essay.id}" onclick="loadEssayForManualEval(${essay.id})">
                    <div class="queue-item-title">${author}</div>
                    <div class="queue-item-score">${score}/5.0</div>
                </div>
            `;
        }).join('');
        
        // Actualizar progreso
        const queueProgress = document.getElementById('queueProgress');
        if (queueProgress) {
            queueProgress.textContent = `0/${essays.length}`;
        }
        
    } catch (error) {
        console.error('Error al cargar cola:', error);
        if (queueList) {
            queueList.innerHTML = '<div class="error-queue"><p style="color: #ef4444;">Error al cargar ensayos</p></div>';
        }
    }
}

// Nueva función: Cargar ensayo específico para evaluación manual
async function loadEssayForManualEval(essayId) {
    try {
        // Marcar item como seleccionado
        document.querySelectorAll('.queue-item').forEach(item => {
            item.classList.remove('active');
        });
        const selectedItem = document.querySelector(`.queue-item[data-essay-id="${essayId}"]`);
        if (selectedItem) {
            selectedItem.classList.add('active');
        }
        
        // Cargar datos del ensayo
        const response = await authenticatedFetch(`/api/essays/${essayId}`);
        if (!response.ok) throw new Error('Error al cargar ensayo');
        
        const essay = await response.json();
        
        // Mostrar PDF en iframe
        if (pdfFrame && essay.nombre_archivo) {
            const pdfUrl = `/api/pdfs/${essay.nombre_archivo}`;
            pdfFrame.src = pdfUrl;
            pdfFrame.style.display = 'block';
            
            // Ocultar placeholder
            const placeholder = pdfContainer?.querySelector('.pdf-placeholder');
            if (placeholder) placeholder.style.display = 'none';
        }
        
        // Pre-llenar formulario con evaluación existente si la hay
        if (rubricForm && essay.evaluacion) {
            // Aquí podrías pre-llenar los campos si es una re-evaluación
            const evaluacion = essay.evaluacion;
            if (evaluacion.calidad_tecnica) {
                selectScoreButton('calidad_tecnica', evaluacion.calidad_tecnica.calificacion);
            }
            // ... repetir para otros criterios
        }
        
        // Guardar ID actual
        window.currentManualEssayId = essayId;
        
    } catch (error) {
        console.error('Error al cargar ensayo:', error);
        showEnhancedNotification('Error al cargar ensayo', 'error');
    }
}

// Helper: Seleccionar botón de puntuación
function selectScoreButton(criterion, score) {
    const buttons = document.querySelectorAll(`.score-segments[data-criterion="${criterion}"] button`);
    buttons.forEach(btn => {
        btn.classList.remove('selected');
        if (parseInt(btn.dataset.score) === score) {
            btn.classList.add('selected');
        }
    });
    updateManualTotal();
}

// Helper: Actualizar total manual
function updateManualTotal() {
    if (!currentTotal) return;
    
    let total = 0;
    const criterionBlocks = document.querySelectorAll('.criterion-block');
    
    criterionBlocks.forEach(block => {
        const selectedBtn = block.querySelector('.score-segments button.selected');
        if (selectedBtn) {
            total += parseInt(selectedBtn.dataset.score);
        }
    });
    
    // Promedio simple (ajustar según criterios)
    const average = criterionBlocks.length > 0 ? total / criterionBlocks.length : 0;
    currentTotal.textContent = average.toFixed(1);
}

// Cargar criterios del usuario
async function loadJudgeCriteria() {
    try {
        const response = await authenticatedFetch('/api/criterios');
        
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
        const response = await authenticatedFetch('/api/ensayos');
        
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
        
        // Preparar datos de los criterios
        const criteriosData = currentJudgeCriteria.map(c => ({
            id: c.id,
            nombre: c.nombre,
            descripcion: c.descripcion,
            peso: c.peso
        }));
        
        const response = await authenticatedFetch(`/api/evaluar_con_criterios/${currentEssayForEval}`, {
            method: 'POST',
            headers: {
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
        
        const response = await authenticatedFetch(`/api/guardar_evaluacion_manual/${currentEssayForEval}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                evaluaciones: evaluaciones,
                comentario_general: generalComments,
                puntuacion_total: totalScore
            })
        });
        
        if (!response.ok) throw new Error('Error al guardar evaluación');
        
        // ✅ ANIMACIÓN DE ÉXITO EN EL BOTÓN
        showButtonSuccess(saveEvaluationBtn);
        showEnhancedNotification('✓ Evaluación guardada exitosamente', 'success');
        
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

// ============================================
// 🎨 UX UTILITIES: SKELETON SCREENS & ANIMATIONS
// ============================================

/**
 * Genera un skeleton screen para tarjetas de ensayos
 * @param {number} count - Cantidad de skeletons a mostrar
 * @returns {string} HTML de skeleton cards
 */
function createSkeletonCards(count = 3) {
    const skeletons = [];
    for (let i = 0; i < count; i++) {
        skeletons.push(`
            <div class="skeleton-card">
                <div class="skeleton skeleton-title"></div>
                <div class="skeleton skeleton-text"></div>
                <div class="skeleton skeleton-text"></div>
                <div class="skeleton skeleton-text short"></div>
                <div class="skeleton skeleton-score"></div>
            </div>
        `);
    }
    return skeletons.join('');
}

/**
 * Muestra skeleton screen mientras carga contenido
 * @param {HTMLElement} container - Elemento donde mostrar los skeletons
 * @param {number} count - Cantidad de skeletons
 */
function showSkeletonLoading(container, count = 3) {
    if (!container) return;
    container.innerHTML = createSkeletonCards(count);
}

/**
 * Animación de éxito en botón (check verde por 2 segundos)
 * @param {HTMLButtonElement} button - Botón a animar
 * @param {string} originalText - Texto original del botón
 */
function showButtonSuccess(button, originalText = null) {
    if (!button) return;
    
    // Guardar contenido original
    const originalHTML = originalText || button.innerHTML;
    const originalDisabled = button.disabled;
    
    // Aplicar estado de éxito
    button.disabled = true;
    button.classList.add('btn-success-animation', 'btn-check-icon');
    button.innerHTML = '✓ Guardado';
    
    // Restaurar después de 2 segundos
    setTimeout(() => {
        button.classList.remove('btn-success-animation', 'btn-check-icon');
        button.innerHTML = originalHTML;
        button.disabled = originalDisabled;
    }, 2000);
}

/**
 * Versión mejorada de showNotification con más opciones
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - 'success', 'error', 'warning', 'info'
 * @param {number} duration - Duración en ms (default: 3000)
 */
function showEnhancedNotification(message, type = 'info', duration = 3000) {
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };
    
    const colors = {
        success: { bg: '#dcfce7', text: '#166534', border: '#10b981' },
        error: { bg: '#fee2e2', text: '#991b1b', border: '#ef4444' },
        warning: { bg: '#fef3c7', text: '#92400e', border: '#f59e0b' },
        info: { bg: '#e0f2fe', text: '#0c4a6e', border: '#0ea5e9' }
    };
    
    const color = colors[type] || colors.info;
    const icon = icons[type] || icons.info;
    
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${color.bg};
        color: ${color.text};
        padding: 1rem 1.5rem;
        border-radius: 12px;
        border-left: 4px solid ${color.border};
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        animation: slideInRight 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        max-width: 400px;
    `;
    
    notification.innerHTML = `
        <span style="font-size: 1.5em; line-height: 1;">${icon}</span>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// Agregar animaciones al CSS (si no existen)
if (!document.querySelector('#ux-animations-style')) {
    const style = document.createElement('style');
    style.id = 'ux-animations-style';
    style.textContent = `
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(100px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes slideOutRight {
            from {
                opacity: 1;
                transform: translateX(0);
            }
            to {
                opacity: 0;
                transform: translateX(100px);
            }
        }
    `;
    document.head.appendChild(style);
}
