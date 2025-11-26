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
let currentFileName = '';  // Para almacenar el nombre del archivo evaluado
let allEssays = [];  // Para almacenar todos los ensayos cargados

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
        const response = await fetch('/chat', {
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
        comparisonContent.innerHTML = `<p style="color: red; text-align: center;">Error: ${error.message}</p>`;
    }
}

function hideComparison() {
    comparisonSection.style.display = 'none';
    essaysHistorySection.style.display = 'block';
}

// Funciones para la biblioteca de ensayos
async function loadEssaysLibrary() {
    try {
        const response = await fetch('/essays');
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
        
        const title = extractTitle(essay.nombre_archivo);
        const author = extractAuthor(essay.nombre_archivo);
        
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
                <div class="essay-card-preview">${essay.texto_preview}</div>
                <div class="essay-card-actions">
                    <button class="btn-view-essay" onclick="viewEssayDetails(${essay.id})">
                        Ver Detalles
                    </button>
                </div>
            </div>
        `;
    }).join('');
    
    // Agregar event listeners a los checkboxes
    document.querySelectorAll('.essay-card-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', handleLibrarySelection);
        checkbox.addEventListener('click', (e) => e.stopPropagation());
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
        const response = await fetch(`/essays/${essayId}`);
        if (!response.ok) throw new Error('Error al cargar ensayo');
        
        const essay = await response.json();
        
        // Actualizar variables globales con la estructura de la base de datos
        currentEvaluation = {
            id: essay.id,
            ...essay.evaluacion,  // Extraer la evaluación del objeto
            nombre_archivo: essay.nombre_archivo
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
        displayResults(essay.evaluacion);
        
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
        chatInput.placeholder = `Pregunta sobre los ${numSelected} ensayos seleccionados...`;
    }
}
