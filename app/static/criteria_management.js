// ============================================================================
// GESTIÓN DE CRITERIOS PERSONALIZADOS
// ============================================================================

const criteriaManagementSection = document.getElementById('criteriaManagementSection');
const manageCriteriaBtn = document.getElementById('manageCriteriaBtn');
const backFromCriteriaBtn = document.getElementById('backFromCriteriaBtn');
const addCriterionBtn = document.getElementById('addCriterionBtn');
const criterionModal = document.getElementById('criterionModal');
const closeCriterionModal = document.getElementById('closeCriterionModal');
const cancelCriterionBtn = document.getElementById('cancelCriterionBtn');
const criterionForm = document.getElementById('criterionForm');
const criteriaList = document.getElementById('criteriaList');

let currentCriteria = [];
let editingCriterionId = null;

// Event listeners
if (manageCriteriaBtn) {
    manageCriteriaBtn.addEventListener('click', showCriteriaManagement);
}

if (backFromCriteriaBtn) {
    backFromCriteriaBtn.addEventListener('click', returnToLibrary);
}

if (addCriterionBtn) {
    addCriterionBtn.addEventListener('click', openNewCriterionModal);
}

if (closeCriterionModal) {
    closeCriterionModal.addEventListener('click', closeCriterionModalFn);
}

if (cancelCriterionBtn) {
    cancelCriterionBtn.addEventListener('click', closeCriterionModalFn);
}

if (criterionForm) {
    criterionForm.addEventListener('submit', saveCriterion);
}

// Funciones principales
async function showCriteriaManagement() {
    // Ocultar otras secciones
    const uploadSection = document.getElementById('uploadSection');
    const resultsSection = document.getElementById('resultsSection');
    const essaysLibrarySection = document.getElementById('essaysLibrarySection');
    const essaysHistorySection = document.getElementById('essaysHistorySection');
    const comparisonSection = document.getElementById('comparisonSection');
    
    if (uploadSection) uploadSection.style.display = 'none';
    if (resultsSection) resultsSection.style.display = 'none';
    if (essaysLibrarySection) essaysLibrarySection.style.display = 'none';
    if (essaysHistorySection) essaysHistorySection.style.display = 'none';
    if (comparisonSection) comparisonSection.style.display = 'none';
    
    // Mostrar sección de criterios
    criteriaManagementSection.style.display = 'block';
    
    // Cargar criterios
    await loadCriteria();
}

async function loadCriteria() {
    try {
        const response = await authenticatedFetch('/api/criterios');
        if (!response.ok) throw new Error('Error al cargar criterios');
        
        const data = await response.json();
        currentCriteria = data.criterios || [];
        
        renderCriteriaList();
        updateCriteriaStats();
        
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al cargar criterios', 'error');
    }
}

function renderCriteriaList() {
    if (currentCriteria.length === 0) {
        criteriaList.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">📝</span>
                <p>No tienes criterios personalizados aún</p>
                <p class="empty-subtitle">Haz clic en "Agregar Criterio" para crear tu primer criterio de evaluación</p>
            </div>
        `;
        return;
    }
    
    criteriaList.innerHTML = currentCriteria.map(criterion => `
        <div class="criterion-item" data-id="${criterion.id}">
            <div class="criterion-item-header">
                <div class="criterion-title">
                    <span class="criterion-icon-large">${criterion.icono}</span>
                    <h4>${escapeHtml(criterion.nombre)}</h4>
                </div>
                <span class="criterion-weight-badge">${criterion.peso}%</span>
            </div>
            <p class="criterion-description">${escapeHtml(criterion.descripcion)}</p>
            <div class="criterion-actions">
                <button class="btn-icon btn-edit-criterion" data-id="${criterion.id}" title="Editar">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                </button>
                <button class="btn-icon btn-delete btn-delete-criterion" data-id="${criterion.id}" title="Eliminar">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                </button>
            </div>
        </div>
    `).join('');
    
    // Agregar event listeners
    document.querySelectorAll('.btn-edit-criterion').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = parseInt(e.currentTarget.dataset.id);
            editCriterion(id);
        });
    });
    
    document.querySelectorAll('.btn-delete-criterion').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = parseInt(e.currentTarget.dataset.id);
            deleteCriterion(id);
        });
    });
}

function updateCriteriaStats() {
    const totalCount = currentCriteria.length;
    const totalWeight = currentCriteria.reduce((sum, c) => sum + c.peso, 0);
    
    document.getElementById('totalCriteriaCount').textContent = totalCount;
    document.getElementById('totalWeightSum').textContent = totalWeight.toFixed(1);
    
    const warningEl = document.getElementById('weightWarning');
    if (Math.abs(totalWeight - 100) > 0.1 && totalCount > 0) {
        warningEl.style.display = 'inline';
    } else {
        warningEl.style.display = 'none';
    }
}

function openNewCriterionModal() {
    editingCriterionId = null;
    document.getElementById('criterionModalTitle').textContent = 'Nuevo Criterio';
    document.getElementById('criterionId').value = '';
    document.getElementById('criterionName').value = '';
    document.getElementById('criterionDescription').value = '';
    document.getElementById('criterionWeight').value = '20';
    document.getElementById('criterionIcon').value = '📝';
    criterionModal.style.display = 'flex';
}

function editCriterion(id) {
    const criterion = currentCriteria.find(c => c.id === id);
    if (!criterion) return;
    
    editingCriterionId = id;
    document.getElementById('criterionModalTitle').textContent = 'Editar Criterio';
    document.getElementById('criterionId').value = id;
    document.getElementById('criterionName').value = criterion.nombre;
    document.getElementById('criterionDescription').value = criterion.descripcion;
    document.getElementById('criterionWeight').value = criterion.peso;
    document.getElementById('criterionIcon').value = criterion.icono;
    criterionModal.style.display = 'flex';
}

function closeCriterionModalFn() {
    criterionModal.style.display = 'none';
    editingCriterionId = null;
}

async function saveCriterion(e) {
    e.preventDefault();
    
    const criterionData = {
        nombre: document.getElementById('criterionName').value.trim(),
        descripcion: document.getElementById('criterionDescription').value.trim(),
        peso: parseFloat(document.getElementById('criterionWeight').value),
        icono: document.getElementById('criterionIcon').value
    };
    
    try {
        let response;
        
        if (editingCriterionId) {
            // Actualizar
            response = await authenticatedFetch(`/api/criterios/${editingCriterionId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(criterionData)
            });
        } else {
            // Crear
            response = await authenticatedFetch('/api/criterios', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(criterionData)
            });
        }
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al guardar criterio');
        }
        
        showNotification(editingCriterionId ? 'Criterio actualizado' : 'Criterio creado', 'success');
        closeCriterionModalFn();
        await loadCriteria();
        
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message, 'error');
    }
}

async function deleteCriterion(id) {
    if (!confirm('¿Estás seguro de eliminar este criterio?')) return;
    
    try {
        const response = await authenticatedFetch(`/api/criterios/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Error al eliminar criterio');
        
        showNotification('Criterio eliminado', 'success');
        await loadCriteria();
        
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al eliminar criterio', 'error');
    }
}
