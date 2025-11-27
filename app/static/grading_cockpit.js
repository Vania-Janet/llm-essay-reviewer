// ============================================
// GRADING COCKPIT - NEW JUDGE EVALUATION FUNCTIONS
// ============================================

// Referencias a elementos del DOM (deben existir en main.js o declararse aquí)
const essaysLibrarySection = document.getElementById('essaysLibrarySection');
const uploadSection = document.getElementById('uploadSection');
const resultsSection = document.getElementById('resultsSection');
const judgeEvaluationSection = document.getElementById('judgeEvaluationSection');

let currentEssays = [];
let currentSelectedEssay = null;
let currentScores = {};
let currentZoom = 100;

// Initialize Grading Cockpit when judge section is shown
async function initializeGradingCockpit() {
    console.log('🎯 Initializing Grading Cockpit...');
    try {
        // Load essays list
        console.log('📚 Fetching essays from /api/essays...');
        const response = await authenticatedFetch('/api/essays');
        if (!response.ok) {
            console.error('❌ Response not OK:', response.status, response.statusText);
            throw new Error('Error al cargar ensayos');
        }
        
        currentEssays = await response.json();
        console.log('✅ Essays loaded:', currentEssays.length, 'essays');
        
        renderEssayQueue();
        updateQueueProgress();
        
        // Setup event listeners
        setupScoreSegments();
        setupZoomControls();
        setupFormSubmit();
        
        console.log('✅ Grading Cockpit initialized successfully');
    } catch (error) {
        console.error('❌ Error initializing grading cockpit:', error);
        if (typeof showNotification === 'function') {
            showNotification('Error al cargar ensayos', 'error');
        } else {
            alert('Error al cargar ensayos: ' + error.message);
        }
    }
}

// Render essay queue in left panel
function renderEssayQueue() {
    console.log('🎨 Rendering essay queue...');
    const queueList = document.getElementById('queueList');
    if (!queueList) {
        console.error('❌ queueList element not found!');
        return;
    }
    
    console.log('📝 Queue list element found, essays count:', currentEssays.length);
    
    if (currentEssays.length === 0) {
        queueList.innerHTML = `
            <div class="queue-loading">
                <p>No hay ensayos disponibles</p>
            </div>
        `;
        return;
    }
    
    queueList.innerHTML = currentEssays.map(essay => {
        const author = extractAuthor(essay.nombre_archivo_original || essay.nombre_archivo);
        const title = extractTitle(essay.nombre_archivo_original || essay.nombre_archivo);
        
        // Check if essay has been evaluated by current judge
        const isDone = essay.evaluado_por_jurado || false;
        const statusClass = isDone ? 'done' : 'pending';
        const statusIndicator = isDone 
            ? `<div class="status-indicator success">✓</div>`
            : `<div class="status-indicator pending"></div>`;
        
        const scoreDisplay = isDone && essay.puntuacion_jurado 
            ? `<span class="essay-score">${essay.puntuacion_jurado.toFixed(1)}/5.0</span>` 
            : '';
        
        return `
            <div class="queue-item ${statusClass}" data-essay-id="${essay.id}">
                ${statusIndicator}
                <div class="meta">
                    <span class="student-name">${author}</span>
                    <span class="essay-topic">${title.substring(0, 30)}...</span>
                    ${scoreDisplay}
                </div>
            </div>
        `;
    }).join('');
    
    console.log('✅ Queue HTML rendered');
    
    // Add click listeners
    document.querySelectorAll('.queue-item').forEach(item => {
        item.addEventListener('click', () => {
            const essayId = parseInt(item.dataset.essayId);
            console.log('📄 Loading essay:', essayId);
            loadEssayForGrading(essayId);
        });
    });
    
    console.log('✅ Click listeners attached to', document.querySelectorAll('.queue-item').length, 'items');
}

// Load essay for grading
async function loadEssayForGrading(essayId) {
    try {
        const response = await authenticatedFetch(`/api/essays/${essayId}`);
        if (!response.ok) throw new Error('Error al cargar ensayo');
        
        const essay = await response.json();
        currentSelectedEssay = essay;
        
        // Update active state in queue
        document.querySelectorAll('.queue-item').forEach(item => {
            item.classList.remove('active');
            if (parseInt(item.dataset.essayId) === essayId) {
                item.classList.add('active');
            }
        });
        
        // Load PDF
        loadPdfInViewer(essayId);
        
        // Reset form
        resetGradingForm();
        
    } catch (error) {
        console.error('Error loading essay:', error);
        showNotification('Error al cargar ensayo', 'error');
    }
}

// Load PDF in center viewer
function loadPdfInViewer(essayId) {
    const pdfFrame = document.getElementById('pdfFrame');
    const pdfPlaceholder = document.querySelector('.pdf-placeholder');
    const pageIndicator = document.getElementById('pageIndicator');
    
    if (!pdfFrame) return;
    
    // Show PDF, hide placeholder
    pdfFrame.style.display = 'block';
    if (pdfPlaceholder) pdfPlaceholder.style.display = 'none';
    
    // Load PDF
    pdfFrame.src = `/api/essays/${essayId}/pdf`;
    
    // Update indicator
    if (pageIndicator && currentSelectedEssay) {
        const author = extractAuthor(currentSelectedEssay.nombre_archivo_original || currentSelectedEssay.nombre_archivo);
        pageIndicator.textContent = `Ensayo de ${author}`;
    }
}

// Setup score segment buttons
function setupScoreSegments() {
    document.querySelectorAll('.score-segments').forEach(segmentGroup => {
        const criterion = segmentGroup.dataset.criterion;
        
        segmentGroup.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Remove selected class from siblings
                segmentGroup.querySelectorAll('button').forEach(b => {
                    b.classList.remove('selected');
                });
                
                // Add selected class to clicked button
                btn.classList.add('selected');
                
                // Store score
                const score = parseInt(btn.dataset.score);
                currentScores[criterion] = score;
                
                // Update total score
                updateLiveScore();
            });
        });
    });
}

// Update live score display
function updateLiveScore() {
    const weights = {
        'calidad_tecnica': 0.25,
        'creatividad': 0.20,
        'vinculacion_tematica': 0.15,
        'bienestar_colectivo': 0.20,
        'uso_responsable_ia': 0.10,
        'potencial_impacto': 0.10
    };
    
    let total = 0;
    let count = 0;
    
    for (const [criterion, score] of Object.entries(currentScores)) {
        if (weights[criterion]) {
            total += score * weights[criterion];
            count++;
        }
    }
    
    const totalSpan = document.getElementById('currentTotal');
    if (totalSpan) {
        totalSpan.textContent = total.toFixed(1);
        
        // Color coding
        const liveScore = totalSpan.parentElement;
        if (total >= 4.5) {
            liveScore.style.background = 'linear-gradient(135deg, #059669 0%, #10b981 100%)';
        } else if (total >= 4.0) {
            liveScore.style.background = 'linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%)';
        } else if (total >= 3.5) {
            liveScore.style.background = 'linear-gradient(135deg, #d97706 0%, #f59e0b 100%)';
        } else {
            liveScore.style.background = 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)';
        }
    }
}

// Setup zoom controls
function setupZoomControls() {
    const zoomInBtn = document.getElementById('zoomInBtn');
    const zoomOutBtn = document.getElementById('zoomOutBtn');
    const zoomLevel = document.getElementById('zoomLevel');
    const pdfFrame = document.getElementById('pdfFrame');
    
    if (zoomInBtn) {
        zoomInBtn.addEventListener('click', () => {
            currentZoom = Math.min(currentZoom + 10, 200);
            applyZoom();
        });
    }
    
    if (zoomOutBtn) {
        zoomOutBtn.addEventListener('click', () => {
            currentZoom = Math.max(currentZoom - 10, 50);
            applyZoom();
        });
    }
    
    function applyZoom() {
        if (zoomLevel) zoomLevel.textContent = `${currentZoom}%`;
        if (pdfFrame) {
            pdfFrame.style.transform = `scale(${currentZoom / 100})`;
            pdfFrame.style.transformOrigin = 'top left';
        }
    }
}

// Setup form submit
function setupFormSubmit() {
    const form = document.getElementById('rubricForm');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await submitEvaluation();
    });
    
    // Save draft button
    const saveDraftBtn = document.getElementById('saveDraftBtn');
    if (saveDraftBtn) {
        saveDraftBtn.addEventListener('click', async () => {
            await saveDraft();
        });
    }
}

// Submit evaluation
async function submitEvaluation() {
    if (!currentSelectedEssay) {
        showNotification('Selecciona un ensayo primero', 'error');
        return;
    }
    
    // Validate all criteria have scores
    const requiredCriteria = ['calidad_tecnica', 'creatividad', 'vinculacion_tematica', 
                              'bienestar_colectivo', 'uso_responsable_ia', 'potencial_impacto'];
    
    for (const criterion of requiredCriteria) {
        if (!currentScores[criterion]) {
            showNotification(`Por favor califica: ${criterion.replace(/_/g, ' ')}`, 'error');
            return;
        }
    }
    
    // Collect comments
    const comments = {};
    document.querySelectorAll('.criterion-comment').forEach(textarea => {
        const criterion = textarea.name.replace('_comment', '');
        comments[criterion] = textarea.value;
    });
    
    const generalComment = document.querySelector('.general-comment').value;
    
    // Calculate total
    const weights = {
        'calidad_tecnica': 0.25,
        'creatividad': 0.20,
        'vinculacion_tematica': 0.15,
        'bienestar_colectivo': 0.20,
        'uso_responsable_ia': 0.10,
        'potencial_impacto': 0.10
    };
    
    let total = 0;
    for (const [criterion, score] of Object.entries(currentScores)) {
        if (weights[criterion]) {
            total += score * weights[criterion];
        }
    }
    
    try {
        const response = await authenticatedFetch('/api/evaluaciones-jurado', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ensayo_id: currentSelectedEssay.id,
                puntajes: currentScores,
                comentarios: comments,
                comentario_general: generalComment,
                puntuacion_total: total
            })
        });
        
        if (!response.ok) throw new Error('Error al guardar evaluación');
        
        showNotification('Evaluación guardada exitosamente', 'success');
        
        // Mark as done in queue
        const queueItem = document.querySelector(`.queue-item[data-essay-id="${currentSelectedEssay.id}"]`);
        if (queueItem) {
            queueItem.classList.add('done');
            queueItem.classList.remove('pending');
            queueItem.querySelector('.status-indicator').outerHTML = `<div class="status-indicator success">✓</div>`;
            const meta = queueItem.querySelector('.meta');
            if (!meta.querySelector('.essay-score')) {
                meta.innerHTML += `<span class="essay-score">${total.toFixed(1)}/5.0</span>`;
            }
        }
        
        // Reset form and load next essay
        resetGradingForm();
        loadNextUngradedEssay();
        updateQueueProgress();
        
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al guardar evaluación', 'error');
    }
}

// Save draft
async function saveDraft() {
    showNotification('Borrador guardado localmente', 'success');
    // TODO: Implement local storage draft save
}

// Reset grading form
function resetGradingForm() {
    currentScores = {};
    document.querySelectorAll('.score-segments button').forEach(btn => {
        btn.classList.remove('selected');
    });
    document.querySelectorAll('.criterion-comment, .general-comment').forEach(textarea => {
        textarea.value = '';
    });
    updateLiveScore();
}

// Load next ungraded essay
function loadNextUngradedEssay() {
    const nextItem = document.querySelector('.queue-item.pending');
    if (nextItem) {
        nextItem.click();
    }
}

// Update queue progress
function updateQueueProgress() {
    const done = document.querySelectorAll('.queue-item.done').length;
    const total = document.querySelectorAll('.queue-item').length;
    const progress = document.getElementById('queueProgress');
    if (progress) {
        progress.textContent = `${done}/${total}`;
    }
}

// Search in queue
function setupQueueSearch() {
    const searchInput = document.getElementById('queueSearchInput');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        document.querySelectorAll('.queue-item').forEach(item => {
            const name = item.querySelector('.student-name').textContent.toLowerCase();
            const topic = item.querySelector('.essay-topic').textContent.toLowerCase();
            
            if (name.includes(query) || topic.includes(query)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    });
}

// Update showJudgeEvaluation function to use new cockpit
async function showJudgeEvaluation() {
    console.log('🎬 Showing Judge Evaluation section...');
    
    // Ocultar todas las secciones
    if (essaysLibrarySection) essaysLibrarySection.style.display = 'none';
    if (uploadSection) uploadSection.style.display = 'none';
    if (resultsSection) resultsSection.style.display = 'none';
    
    const criteriaSection = document.getElementById('criteriaManagementSection');
    if (criteriaSection) criteriaSection.style.display = 'none';
    
    const comparisonSection = document.getElementById('comparisonSection');
    if (comparisonSection) comparisonSection.style.display = 'none';
    
    const essaysHistorySection = document.getElementById('essaysHistorySection');
    if (essaysHistorySection) essaysHistorySection.style.display = 'none';
    
    // Mostrar sección de evaluación manual
    if (judgeEvaluationSection) {
        console.log('✅ Judge evaluation section found, displaying...');
        judgeEvaluationSection.style.display = 'block';
    } else {
        console.error('❌ Judge evaluation section NOT FOUND!');
    }
    
    // Initialize Grading Cockpit
    await initializeGradingCockpit();
    setupQueueSearch();
    
    console.log('✅ Judge Evaluation section initialization complete');
}
