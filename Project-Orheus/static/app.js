// Project Orpheus - Studio Logic
const API_BASE = 'http://localhost:8000';

// DOM Elements
const elements = {
    generateBtn: document.getElementById('generateBtn'),
    promptInput: document.getElementById('prompt'),
    normalize: document.getElementById('normalize'),
    applyFades: document.getElementById('applyFades'),
    planPanel: document.getElementById('planPanel'),
    outputPanel: document.getElementById('outputPanel'),
    audioPlayer: document.getElementById('audioPlayer'),
    downloadBtn: document.getElementById('downloadBtn'),
    metadata: document.getElementById('metadata'),
    statusBadge: document.getElementById('statusBadge')
};

// State
let currentJobId = null;

// Event Listeners
elements.generateBtn.addEventListener('click', () => handleGenerate());
elements.downloadBtn.addEventListener('click', () => {
    if (currentJobId) window.open(`${API_BASE}/download/${currentJobId}`, '_blank');
});

// Get Duration Helper
function getSelectedDuration() {
    const selected = document.querySelector('input[name="duration"]:checked');
    return selected ? selected.value : 'short';
}

// Main Generation Flow
async function handleGenerate(promptText) {
    const prompt = promptText || elements.promptInput.value.trim();

    if (!prompt) {
        alert('Please enter a description for your music.');
        return;
    }

    // Reset UI
    elements.generateBtn.disabled = true;
    elements.generateBtn.innerHTML = `
        <div class="thinking-dots">
            <span></span><span></span><span></span>
        </div>
        <span>Thinking</span>
    `;
    elements.planPanel.classList.add('hidden');
    elements.outputPanel.classList.add('hidden');
    updateStatus('processing', 'Analyzing Prompt...');

    try {
        // 1. Get Plan
        const planResponse = await fetch(`${API_BASE}/plan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
        });

        if (!planResponse.ok) throw new Error('Failed to create plan');
        const planData = await planResponse.json();

        // Render Plan
        currentPlan = planData.plan;
        elements.planPanel.innerHTML = renderPlanCard(currentPlan);
        elements.planPanel.classList.remove('hidden');

        // 2. Start Generation
        updateStatus('processing', 'Composing Audio...');
        const genResponse = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt,
                duration: getSelectedDuration(),
                use_lyrics: false,  // Always false - MusicGen can't generate vocals
                normalize: elements.normalize.checked,
                apply_fades: elements.applyFades.checked,
                plan: planData.plan
            })
        });

        if (!genResponse.ok) throw new Error('Generation failed to start');
        const genData = await genResponse.json();
        currentJobId = genData.job_id;

        // 3. Poll for Completion
        pollStatus();

    } catch (error) {
        console.error(error);
        updateStatus('failed', 'Error');
        elements.generateBtn.disabled = false;
        elements.generateBtn.innerHTML = `<span>Generate Track</span><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>`;
        alert(error.message);
    }
}

// Polling
async function pollStatus() {
    if (!currentJobId) return;

    try {
        const response = await fetch(`${API_BASE}/status/${currentJobId}`);
        const data = await response.json();

        if (data.status === 'completed') {
            handleComplete(data);
        } else if (data.status === 'failed') {
            throw new Error(data.metadata?.error || 'Generation failed');
        } else {
            // Update progress
            if (data.metadata?.progress) {
                updateStatus('processing', `Generating (${data.metadata.progress})`);
            }
            setTimeout(pollStatus, 1000);
        }
    } catch (error) {
        console.error(error);
        updateStatus('failed', 'Failed');
        elements.generateBtn.disabled = false;
        elements.generateBtn.innerHTML = `<span>Retry Generation</span>`;
    }
}

// Completion Handler
function handleComplete(data) {
    updateStatus('completed', 'Track Ready');
    elements.generateBtn.disabled = false;
    elements.generateBtn.innerHTML = `
        <div class="success-check"></div>
        <span>Generate New Track</span>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
    `;

    // Show Output
    elements.outputPanel.classList.remove('hidden');
    elements.audioPlayer.src = `${API_BASE}/download/${currentJobId}`;

    // Metadata
    elements.metadata.innerHTML = `
        <p><strong>Prompt:</strong> ${data.metadata.prompt}</p>
        <p><strong>Duration:</strong> ${data.metadata.duration_sec?.toFixed(1)}s • <strong>Sample Rate:</strong> ${data.metadata.sample_rate}Hz</p>
    `;
}

// Render Plan Card (Premium Glassmorphism)
function renderPlanCard(plan, isEditable = false) {
    if (!plan) return '';

    const structureHtml = plan.structure.map((step, index) => `
        <div class="structure-step-container">
            <div class="structure-step" ${isEditable ? `contenteditable="true" onblur="updatePlanStructure(${index}, this.innerText)"` : ''}>${step}</div>
            ${index < plan.structure.length - 1 ? '<div class="structure-line"></div>' : ''}
        </div>
    `).join('');

    const instrumentsHtml = plan.instruments.map((inst, index) => `
        <span class="inst-tag" ${isEditable ? `contenteditable="true" onblur="updatePlanInstrument(${index}, this.innerText)"` : ''}>
            <span>♪</span> ${inst}
        </span>
    `).join('');

    return `
        <div class="plan-card-glass">
            <div class="plan-header">
                <div class="plan-icon-pulse">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                        <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                        <line x1="12" y1="22.08" x2="12" y2="12"></line>
                    </svg>
                </div>
                <div style="flex:1;">
                    <h3 style="margin:0; color:white;">Sonic Blueprint</h3>
                    <p style="margin:0; color:var(--text-muted); font-size:0.9rem;">AI Generated Composition Plan</p>
                </div>
                ${!isEditable ? `<button onclick="enableEditMode()" class="btn btn-glass" style="padding:8px 16px; font-size:0.8rem;">Edit Plan</button>` : ''}
            </div>
            
            <div class="plan-stats-row">
                <div class="plan-stat-card">
                    <div class="input-label">KEY</div>
                    <div class="stat-value" ${isEditable ? `contenteditable="true" onblur="updatePlanKey(this.innerText)"` : ''}>${plan.key}</div>
                </div>
                <div class="plan-stat-card">
                    <div class="input-label">TEMPO</div>
                    <div class="stat-value"><span ${isEditable ? `contenteditable="true" onblur="updatePlanBpm(this.innerText)"` : ''}>${plan.bpm}</span> <span style="font-size:1rem; color:var(--text-muted);">BPM</span></div>
                </div>
            </div>

            <div style="margin-bottom:24px;">
                <div class="input-label">STRUCTURE FLOW ${isEditable ? '<span style="font-size:0.7rem; color:var(--accent);">(Click items to edit)</span>' : ''}</div>
                <div class="structure-flow-visual">
                    ${structureHtml}
                </div>
            </div>

            <div>
                <div class="input-label">INSTRUMENTATION ${isEditable ? '<span style="font-size:0.7rem; color:var(--accent);">(Click items to edit)</span>' : ''}</div>
                <div class="instrument-tags-cloud">
                    ${instrumentsHtml}
                </div>
            </div>
            
            ${isEditable ? `
            <div style="margin-top:24px; display:flex; justify-content:flex-end; gap:8px;">
                <button onclick="cancelEdit()" class="btn btn-glass">Cancel</button>
                <button onclick="applyEdit()" class="btn btn-primary">Apply Changes</button>
            </div>` : ''}
        </div>
    `;
}

// Edit Mode Logic
let currentPlan = null;
let originalPlan = null;

function enableEditMode() {
    if (!currentPlan) return;
    originalPlan = JSON.parse(JSON.stringify(currentPlan)); // Deep copy
    elements.planPanel.innerHTML = renderPlanCard(currentPlan, true);
}

function cancelEdit() {
    currentPlan = originalPlan;
    elements.planPanel.innerHTML = renderPlanCard(currentPlan, false);
}

function applyEdit() {
    elements.planPanel.innerHTML = renderPlanCard(currentPlan, false);
    // Re-trigger generation with new plan? Or just update UI?
    // For now, just update UI. User can hit "Generate Track" to use this plan.
    updateStatus('idle', 'Plan Updated');
}

// Update Helpers
window.updatePlanStructure = (index, value) => { if (currentPlan) currentPlan.structure[index] = value; };
window.updatePlanInstrument = (index, value) => { if (currentPlan) currentPlan.instruments[index] = value; };
window.updatePlanKey = (value) => { if (currentPlan) currentPlan.key = value; };
window.updatePlanBpm = (value) => { if (currentPlan) currentPlan.bpm = parseInt(value) || currentPlan.bpm; };
window.enableEditMode = enableEditMode;
window.cancelEdit = cancelEdit;
window.applyEdit = applyEdit;

// Status Updater
function updateStatus(status, text) {
    elements.statusBadge.className = `status-badge status-${status}`;
    elements.statusBadge.textContent = text;
}

console.log('Orpheus Studio Loaded');
