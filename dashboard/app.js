// Necro Dashboard JavaScript

// State
let resultsData = null;

// Source code mapping for before/after comparison
const SOURCE_CODE = {
    'calculate_legacy_metrics': {
        file: 'demo_repo/src/legacy_feature.py',
        code: `def calculate_legacy_metrics(data):
    """
    Old metrics calculation - replaced by new system.
    This function computed simple averages for the v1.0 dashboard.
    No longer used anywhere in the codebase.
    """
    if not data or len(data) == 0:
        return 0
    return sum(data) / len(data)`
    },
    'format_old_date': {
        file: 'demo_repo/src/utils.py',
        code: `def format_old_date(timestamp):
    """
    CASE 2: Genuinely Dead Function #2
    Date formatter from v1.0 - no longer used.
    This was replaced by the new datetime handling system.
    Different pattern: leftover from removed feature.
    """
    from datetime import datetime
    if isinstance(timestamp, str):
        dt = datetime.fromisoformat(timestamp)
    else:
        dt = timestamp
    return dt.strftime("%d/%m/%Y")`
    },
    'track_user_event': {
        file: 'demo_repo/src/analytics.py',
        code: `def track_user_event(event_type, user_id):
    """
    Track user events for analytics.
    Called via string-based dispatch - static analysis misses it.
    """
    print(f"[ANALYTICS] Event: {event_type} for user {user_id}")
    # In a real system, this would log to a database or analytics service
    return {"event": event_type, "user": user_id, "tracked": True}`
    },
    'validate_input': {
        file: 'demo_repo/src/utils.py',
        code: `def validate_input(data):
    # CASE 4: Undocumented but clearly used
    # No docstring, no comments, but called in main.py
    if not data or not isinstance(data, dict):
        return False
    if "id" not in data or "timestamp" not in data:
        return False
    return True`
    },
    'process_request': {
        file: 'demo_repo/src/main.py',
        code: `def process_request(request_data):
    """
    Main request processor - handles incoming requests.
    
    Args:
        request_data: Dictionary containing request information
        
    Returns:
        dict: Processed response with status and data
    """
    if not validate_input(request_data):
        return {
            "status": "error",
            "message": "Invalid request data"
        }
    
    return {
        "status": "success",
        "data": request_data,
        "processed": True
    }`
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadResults();
    setupModal();
});

// Load results from JSON file
async function loadResults() {
    try {
        const response = await fetch('../results/results.json');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        resultsData = await response.json();
        renderDashboard();
        
    } catch (error) {
        showError(error.message);
    }
}

// Render the entire dashboard
function renderDashboard() {
    if (!resultsData) return;
    
    renderSummary();
    renderResultsTable();
}

// Render summary statistics
function renderSummary() {
    const results = resultsData.results;
    
    // Count verdicts - dynamically derive counts from actual data
    const verdictCounts = {
        'Safe to Delete': 0,
        'Secretly Load-Bearing': 0,
        'Undocumented but Valuable': 0,
        'Normal': 0,
        'Error': 0
    };
    
    results.forEach(result => {
        // Handle both "Normal" and "Normal - No Action" verdicts
        if (result.verdict.startsWith('Normal')) {
            verdictCounts['Normal']++;
        } else if (verdictCounts.hasOwnProperty(result.verdict)) {
            verdictCounts[result.verdict]++;
        }
    });
    
    // Update DOM
    document.getElementById('total-modules').textContent = resultsData.modules_analyzed;
    document.getElementById('delete-count').textContent = verdictCounts['Safe to Delete'];
    document.getElementById('warning-count').textContent = verdictCounts['Secretly Load-Bearing'];
    document.getElementById('docs-count').textContent = verdictCounts['Undocumented but Valuable'];
    document.getElementById('normal-count').textContent = verdictCounts['Normal'];
    
    // Update metadata
    const generatedTime = new Date(resultsData.generated_at).toLocaleString();
    document.getElementById('generated-time').textContent = `Generated: ${generatedTime}`;
    document.getElementById('bob-mode').textContent = `Mode: ${resultsData.bob_mode || 'N/A'}`;
}

// Render results table
function renderResultsTable() {
    const tbody = document.getElementById('results-body');
    tbody.innerHTML = '';
    
    resultsData.results.forEach((result, index) => {
        const row = createResultRow(result, index);
        tbody.appendChild(row);
    });
}

// Create a table row for a result
function createResultRow(result, index) {
    const row = document.createElement('tr');
    
    // Module name
    const moduleCell = document.createElement('td');
    moduleCell.innerHTML = `
        <strong>${result.module_name}</strong><br>
        <small style="color: #666;">${result.module_path}</small>
    `;
    row.appendChild(moduleCell);
    
    // Verdict
    const verdictCell = document.createElement('td');
    verdictCell.innerHTML = `<span class="verdict-badge ${getVerdictClass(result.verdict)}">${result.verdict}</span>`;
    row.appendChild(verdictCell);
    
    // Confidence
    const confidenceCell = document.createElement('td');
    confidenceCell.innerHTML = `<span class="confidence-badge ${getConfidenceClass(result.confidence)}">${result.confidence}</span>`;
    row.appendChild(confidenceCell);
    
    // Evidence
    const evidenceCell = document.createElement('td');
    evidenceCell.innerHTML = `
        <span class="evidence-toggle" onclick="showEvidence(${index})">
            View ${result.evidence.length} items
        </span>
    `;
    row.appendChild(evidenceCell);
    
    // Artifact
    const artifactCell = document.createElement('td');
    if (result.artifact_path) {
        artifactCell.innerHTML = `
            <a href="../${result.artifact_path}" class="btn btn-secondary btn-small" target="_blank">
                Download
            </a>
        `;
    } else {
        artifactCell.innerHTML = '<span style="color: #999;">None</span>';
    }
    row.appendChild(artifactCell);
    
    return row;
}

// Get CSS class for verdict
function getVerdictClass(verdict) {
    const classMap = {
        'Safe to Delete': 'verdict-delete',
        'Secretly Load-Bearing': 'verdict-warning',
        'Undocumented but Valuable': 'verdict-info',
        'Normal': 'verdict-normal',
        'Error': 'verdict-error'
    };
    return classMap[verdict] || 'verdict-normal';
}

// Get CSS class for confidence
function getConfidenceClass(confidence) {
    const classMap = {
        'High': 'confidence-high',
        'Medium': 'confidence-medium',
        'Low': 'confidence-low'
    };
    return classMap[confidence] || 'confidence-medium';
}

// Show evidence modal
function showEvidence(index) {
    const result = resultsData.results[index];
    const modal = document.getElementById('evidence-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    
    modalTitle.textContent = `Evidence: ${result.module_name}`;
    
    // Get verdict class for styling
    const verdictClass = getVerdictClass(result.verdict);
    const verdictColorMap = {
        'verdict-delete': 'var(--color-delete)',
        'verdict-warning': 'var(--color-warning)',
        'verdict-info': 'var(--color-info)',
        'verdict-normal': 'var(--color-normal)',
        'verdict-error': 'var(--color-error)'
    };
    const verdictColor = verdictColorMap[verdictClass] || 'var(--color-primary)';
    
    let html = `
        <div class="modal-verdict-header" style="border-left-color: ${verdictColor}">
            <h3>
                <span class="modal-verdict-badge ${verdictClass}">${result.verdict}</span>
            </h3>
            <div class="modal-confidence">
                <strong>Confidence:</strong>
                <span class="confidence-badge ${getConfidenceClass(result.confidence)}">${result.confidence}</span>
            </div>
            <p style="margin-top: 0.5rem; font-size: 0.9rem; color: var(--color-text-light);">
                <strong>Analyzed:</strong> ${new Date(result.timestamp).toLocaleString()}
            </p>
        </div>
    `;
    
    // Add Before/After comparison if source code is available
    const sourceInfo = SOURCE_CODE[result.module_name];
    if (sourceInfo) {
        html += `
            <div class="comparison-container">
                <div class="comparison-panel">
                    <div class="comparison-header before">📄 Original Code</div>
                    <div class="comparison-content">
                        <pre><code class="language-python">${escapeHtml(sourceInfo.code)}</code></pre>
                        <p style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--color-text-light);">
                            From: <span class="file-citation">${sourceInfo.file}</span>
                        </p>
                    </div>
                </div>
                <div class="comparison-panel">
                    <div class="comparison-header after">⚖️ Bob's Verdict</div>
                    <div class="comparison-content">
                        <div style="padding: 0.5rem 0;">
                            <div style="margin-bottom: 1rem;">
                                <strong style="color: ${verdictColor}; font-size: 1.1rem;">${result.verdict}</strong>
                            </div>
                            <div style="background: #f6f8fa; padding: 0.75rem; border-radius: 4px; margin-bottom: 0.75rem;">
                                <strong>Confidence:</strong> ${result.confidence}
                            </div>
                            <div style="line-height: 1.6; color: var(--color-text);">
                                ${escapeHtml(result.reasoning)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Evidence section with highlighted file citations
    html += `
        <div class="evidence-detail">
            <h3>🔍 Evidence Trail</h3>
            <ul class="evidence-list">
    `;
    
    result.evidence.forEach(item => {
        // Highlight file:line patterns in evidence
        const highlightedItem = highlightFileCitations(escapeHtml(item));
        html += `<li class="evidence-item">${highlightedItem}</li>`;
    });
    
    html += `
            </ul>
        </div>
    `;
    
    if (result.evidence_path) {
        html += `
            <div class="evidence-detail">
                <h3>📋 Session Logs</h3>
                <p>Full evidence available at: <span class="file-citation">${result.evidence_path}</span></p>
            </div>
        `;
    }
    
    if (result.artifact_path) {
        html += `
            <div class="evidence-detail">
                <h3>📦 Generated Artifact</h3>
                <p>
                    <a href="../${result.artifact_path}" class="btn btn-secondary" download>
                        Download Artifact
                    </a>
                </p>
            </div>
        `;
    }
    
    
    modalBody.innerHTML = html;
    
    // Apply syntax highlighting to code blocks
    modalBody.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });
    
    modal.style.display = 'flex';
}

// Highlight file:line citations in text
function highlightFileCitations(text) {
    // Match patterns like "file.py line 10" or "file.py lines 10-20"
    return text.replace(/(\w+\.py)\s+(lines?\s+\d+(-\d+)?)/gi, (match, file, lineInfo) => {
        return `<span class="file-citation">${file} ${lineInfo}</span>`;
    });
}

// Setup modal close handlers
function setupModal() {
    const modal = document.getElementById('evidence-modal');
    const closeBtn = modal.querySelector('.close');
    
    closeBtn.onclick = () => {
        modal.style.display = 'none';
    };
    
    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    };
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    const resultsTable = document.getElementById('results-table');
    
    errorText.textContent = message;
    errorDiv.style.display = 'block';
    resultsTable.style.display = 'none';
    
    // Hide summary stats
    document.getElementById('total-modules').textContent = '0';
    document.getElementById('delete-count').textContent = '0';
    document.getElementById('warning-count').textContent = '0';
    document.getElementById('docs-count').textContent = '0';
    document.getElementById('normal-count').textContent = '0';
}

// Utility: Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Made with Bob
