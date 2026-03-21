/**
 * Migration Tool Frontend Application
 * 
 * A visual interface for component migration with:
 * - File browser
 * - Diff viewer
 * - Progress tracking
 * - One-click migration
 */

// ========================================
// State Management
// ========================================

const state = {
  connected: false,
  files: [],
  selectedFile: null,
  rules: [],
  selectedRules: [],
  transformResult: null,
  batchProgress: null,
  isProcessing: false
};

// ========================================
// WebSocket Connection
// ========================================

let ws = null;
const WS_URL = `ws://localhost:3001`;

function connect() {
  ws = new WebSocket(WS_URL);

  ws.onopen = () => {
    state.connected = true;
    updateConnectionStatus();
    requestRuleList();
  };

  ws.onclose = () => {
    state.connected = false;
    updateConnectionStatus();
    setTimeout(connect, 3000);
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    handleMessage(message);
  };
}

function send(message) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(message));
  }
}

function handleMessage(message) {
  switch (message.type) {
    case 'file:list:response':
      state.files = message.files;
      renderFileList();
      break;

    case 'transform:response':
      state.transformResult = message;
      state.isProcessing = false;
      renderTransformResult();
      break;

    case 'batch:progress':
      state.batchProgress = message;
      renderBatchProgress();
      break;

    case 'batch:complete':
      state.batchProgress = message;
      state.isProcessing = false;
      renderBatchComplete();
      break;

    case 'rule:list:response':
      state.rules = message.rules;
      state.selectedRules = message.rules.filter(r => r.enabled).map(r => r.id);
      renderRuleList();
      break;

    case 'rollback:response':
      alert(`Rollback complete: ${message.rolledBackFiles.length} files restored`);
      requestFileList();
      break;

    case 'error':
      console.error('Server error:', message);
      alert(`Error: ${message.message}`);
      state.isProcessing = false;
      break;
  }
}

// ========================================
// API Requests
// ========================================

function requestFileList(directory = 'frontend/src') {
  send({
    type: 'file:list:request',
    timestamp: Date.now(),
    id: generateId(),
    directory
  });
}

function requestRuleList() {
  send({
    type: 'rule:list:request',
    timestamp: Date.now(),
    id: generateId()
  });
}

function requestTransform(filePath, preview = true) {
  state.isProcessing = true;
  state.transformResult = null;
  renderProcessing();

  send({
    type: 'transform:request',
    timestamp: Date.now(),
    id: generateId(),
    filePath,
    rules: state.selectedRules,
    preview
  });
}

function requestBatchTransform(directory, dryRun = true) {
  state.isProcessing = true;
  state.batchProgress = null;

  send({
    type: 'batch:request',
    timestamp: Date.now(),
    id: generateId(),
    directory,
    rules: state.selectedRules,
    dryRun
  });
}

function requestRollback(filePath) {
  send({
    type: 'rollback:request',
    timestamp: Date.now(),
    id: generateId(),
    filePath
  });
}

// ========================================
// UI Rendering
// ========================================

function render() {
  const app = document.getElementById('app');
  app.innerHTML = `
    <div class="flex flex-col h-screen">
      <!-- Header -->
      <header class="cyber-bg cyber-border p-4 flex items-center justify-between">
        <h1 class="text-xl font-bold cyber-text flex items-center gap-2">
          <span class="text-2xl">⚡</span>
          Component Migration Tool
        </h1>
        <div class="flex items-center gap-4">
          <span id="connection-status" class="flex items-center gap-2 text-sm">
            <span class="w-2 h-2 rounded-full bg-red-500"></span>
            Disconnected
          </span>
          <button onclick="requestFileList()" class="px-4 py-2 cyber-border cyber-text hover:bg-cyan-900/30 transition">
            🔄 Refresh Files
          </button>
        </div>
      </header>

      <!-- Main Content -->
      <div class="flex flex-1 overflow-hidden">
        <!-- Sidebar: File Browser -->
        <aside class="w-80 cyber-bg cyber-border flex flex-col">
          <div class="p-4 border-b border-cyan-900/50">
            <h2 class="font-semibold cyber-text mb-2">📁 Files</h2>
            <input type="text" id="search-input" placeholder="Search files..." 
                   class="w-full px-3 py-2 bg-black/50 cyber-border text-sm focus:outline-none focus:border-cyan-400"
                   oninput="filterFiles(this.value)">
          </div>
          <div id="file-list" class="flex-1 overflow-y-auto">
            <div class="p-4 text-gray-500 text-sm">Loading...</div>
          </div>
        </aside>

        <!-- Main Panel -->
        <main class="flex-1 flex flex-col">
          <!-- Rules Selection -->
          <div class="cyber-bg cyber-border p-4">
            <h2 class="font-semibold cyber-text mb-2">🔧 Migration Rules</h2>
            <div id="rule-list" class="flex flex-wrap gap-2">
              <span class="text-gray-500 text-sm">Loading rules...</span>
            </div>
          </div>

          <!-- Diff Viewer -->
          <div class="flex-1 flex overflow-hidden">
            <!-- Original Code -->
            <div class="flex-1 flex flex-col border-r border-cyan-900/50">
              <div class="p-2 bg-black/30 text-sm font-semibold border-b border-cyan-900/50">
                📄 Original
              </div>
              <pre id="original-code" class="flex-1 overflow-auto p-4 text-sm bg-black/20"></pre>
            </div>

            <!-- Transformed Code -->
            <div class="flex-1 flex flex-col">
              <div class="p-2 bg-black/30 text-sm font-semibold border-b border-cyan-900/50">
                ✨ Transformed
              </div>
              <pre id="transformed-code" class="flex-1 overflow-auto p-4 text-sm bg-black/20"></pre>
            </div>
          </div>

          <!-- Changes Summary -->
          <div id="changes-summary" class="cyber-bg cyber-border p-4 max-h-48 overflow-y-auto">
            <div class="text-gray-500 text-sm">Select a file to preview changes</div>
          </div>
        </main>
      </div>

      <!-- Footer: Actions & Progress -->
      <footer class="cyber-bg cyber-border p-4">
        <div class="flex items-center justify-between mb-2">
          <div class="flex gap-2">
            <button id="preview-btn" onclick="previewSelected()" disabled
                    class="px-4 py-2 cyber-border cyber-text hover:bg-cyan-900/30 transition disabled:opacity-50 disabled:cursor-not-allowed">
              👁️ Preview
            </button>
            <button id="apply-btn" onclick="applySelected()" disabled
                    class="px-4 py-2 bg-cyan-900/50 cyber-border cyber-text hover:bg-cyan-900/70 transition disabled:opacity-50 disabled:cursor-not-allowed">
              ✅ Apply Migration
            </button>
            <button id="batch-btn" onclick="batchTransform()"
                    class="px-4 py-2 bg-purple-900/50 border border-purple-500 text-purple-300 hover:bg-purple-900/70 transition">
              🚀 Batch Transform
            </button>
            <button id="rollback-btn" onclick="rollbackAll()"
                    class="px-4 py-2 bg-red-900/50 border border-red-500 text-red-300 hover:bg-red-900/70 transition">
              ↩️ Rollback All
            </button>
          </div>
          <div id="progress-info" class="text-sm text-gray-400"></div>
        </div>
        <div id="progress-bar" class="progress-bar hidden">
          <div id="progress-fill" class="progress-fill" style="width: 0%"></div>
        </div>
      </footer>
    </div>
  `;
}

function updateConnectionStatus() {
  const statusEl = document.getElementById('connection-status');
  if (!statusEl) return;

  if (state.connected) {
    statusEl.innerHTML = `
      <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse-slow"></span>
      <span class="text-green-400">Connected</span>
    `;
  } else {
    statusEl.innerHTML = `
      <span class="w-2 h-2 rounded-full bg-red-500"></span>
      <span class="text-red-400">Disconnected</span>
    `;
  }
}

function renderFileList() {
  const listEl = document.getElementById('file-list');
  if (!listEl) return;

  if (state.files.length === 0) {
    listEl.innerHTML = '<div class="p-4 text-gray-500 text-sm">No files found</div>';
    return;
  }

  const filesWithMigration = state.files.filter(f => f.hasMigration);
  const filesWithoutMigration = state.files.filter(f => !f.hasMigration);

  let html = '';

  if (filesWithMigration.length > 0) {
    html += '<div class="p-2 text-xs text-yellow-400 bg-yellow-900/20 border-b border-yellow-900/50">⚠️ Files needing migration</div>';
    filesWithMigration.forEach(file => {
      html += renderFileItem(file, true);
    });
  }

  if (filesWithoutMigration.length > 0) {
    html += '<div class="p-2 text-xs text-gray-400 bg-gray-900/20 border-b border-gray-900/50">📁 Other files</div>';
    filesWithoutMigration.slice(0, 50).forEach(file => {
      html += renderFileItem(file, false);
    });
  }

  listEl.innerHTML = html;
}

function renderFileItem(file, hasMigration) {
  const selected = state.selectedFile?.path === file.path;
  const icon = file.extension === '.tsx' ? '⚛️' : file.extension === '.ts' ? '📘' : '📄';
  
  return `
    <div class="file-item ${selected ? 'selected' : ''} ${hasMigration ? 'has-migration' : ''}"
         onclick="selectFile('${file.path}')">
      <div class="flex items-center gap-2">
        <span>${icon}</span>
        <span class="truncate text-sm">${file.name}</span>
        ${hasMigration ? `<span class="text-xs text-yellow-400">[${file.migrationType}]</span>` : ''}
      </div>
      <div class="text-xs text-gray-500 truncate mt-1">${file.path}</div>
    </div>
  `;
}

function renderRuleList() {
  const ruleListEl = document.getElementById('rule-list');
  if (!ruleListEl) return;

  ruleListEl.innerHTML = state.rules.map(rule => `
    <label class="flex items-center gap-2 px-3 py-1 cyber-border cursor-pointer hover:bg-cyan-900/30 transition
                 ${state.selectedRules.includes(rule.id) ? 'bg-cyan-900/50' : ''}">
      <input type="checkbox" ${state.selectedRules.includes(rule.id) ? 'checked' : ''}
             onchange="toggleRule('${rule.id}')"
             class="accent-cyan-500">
      <span class="text-sm">${rule.name}</span>
    </label>
  `).join('');
}

function renderTransformResult() {
  const result = state.transformResult;
  if (!result) return;

  // Render original code
  const originalEl = document.getElementById('original-code');
  if (originalEl) {
    originalEl.innerHTML = escapeHtml(result.originalCode || '');
  }

  // Render transformed code
  const transformedEl = document.getElementById('transformed-code');
  if (transformedEl) {
    transformedEl.innerHTML = renderDiff(result.originalCode, result.transformedCode);
  }

  // Render changes summary
  const summaryEl = document.getElementById('changes-summary');
  if (summaryEl) {
    if (result.changes.length === 0) {
      summaryEl.innerHTML = '<div class="text-gray-500 text-sm">No changes detected</div>';
    } else {
      summaryEl.innerHTML = `
        <h3 class="font-semibold cyber-text mb-2">Changes (${result.changes.length})</h3>
        <div class="space-y-2">
          ${result.changes.map(change => `
            <div class="flex items-start gap-2 text-sm">
              <span class="text-cyan-400">•</span>
              <div>
                <span class="text-gray-400">[${change.type}]</span>
                <span>${change.description}</span>
                ${change.before && change.after ? `
                  <div class="text-xs mt-1">
                    <span class="text-red-400">- ${escapeHtml(change.before)}</span>
                    <br>
                    <span class="text-green-400">+ ${escapeHtml(change.after)}</span>
                  </div>
                ` : ''}
              </div>
            </div>
          `).join('')}
        </div>
        ${result.warnings.length > 0 ? `
          <div class="mt-4 p-2 bg-yellow-900/30 border border-yellow-900/50 rounded">
            <h4 class="text-yellow-400 font-semibold mb-1">⚠️ Warnings</h4>
            ${result.warnings.map(w => `<div class="text-sm text-yellow-300">${w}</div>`).join('')}
          </div>
        ` : ''}
        ${result.errors.length > 0 ? `
          <div class="mt-4 p-2 bg-red-900/30 border border-red-900/50 rounded">
            <h4 class="text-red-400 font-semibold mb-1">❌ Errors</h4>
            ${result.errors.map(e => `<div class="text-sm text-red-300">${e}</div>`).join('')}
          </div>
        ` : ''}
      `;
    }
  }

  // Enable buttons
  const previewBtn = document.getElementById('preview-btn');
  const applyBtn = document.getElementById('apply-btn');
  if (previewBtn) previewBtn.disabled = false;
  if (applyBtn) applyBtn.disabled = !result.success;
}

function renderBatchProgress() {
  const progress = state.batchProgress;
  if (!progress) return;

  const progressBar = document.getElementById('progress-bar');
  const progressFill = document.getElementById('progress-fill');
  const progressInfo = document.getElementById('progress-info');

  if (progressBar) progressBar.classList.remove('hidden');
  if (progressFill) {
    const percent = (progress.processedFiles / progress.totalFiles) * 100;
    progressFill.style.width = `${percent}%`;
  }
  if (progressInfo) {
    progressInfo.textContent = `Processing: ${progress.currentFile} (${progress.processedFiles}/${progress.totalFiles})`;
  }
}

function renderBatchComplete() {
  const progress = state.batchProgress;
  if (!progress) return;

  const progressBar = document.getElementById('progress-bar');
  const progressInfo = document.getElementById('progress-info');

  if (progressBar) progressBar.classList.add('hidden');
  if (progressInfo) {
    progressInfo.innerHTML = `
      <span class="text-green-400">✓ Complete:</span>
      ${progress.successfulFiles} succeeded,
      ${progress.failedFiles} failed,
      ${progress.totalChanges} changes
    `;
  }

  // Refresh file list
  requestFileList();
}

function renderProcessing() {
  const transformedEl = document.getElementById('transformed-code');
  if (transformedEl) {
    transformedEl.innerHTML = '<div class="text-cyan-400 animate-pulse-slow">Processing...</div>';
  }
}

// ========================================
// Diff Rendering
// ========================================

function renderDiff(original, transformed) {
  const originalLines = original.split('\n');
  const transformedLines = transformed.split('\n');

  let html = '';
  const maxLines = Math.max(originalLines.length, transformedLines.length);

  for (let i = 0; i < maxLines; i++) {
    const origLine = originalLines[i] || '';
    const transLine = transformedLines[i] || '';

    if (origLine === transLine) {
      html += `<div class="diff-line">${escapeHtml(transLine)}</div>`;
    } else if (!origLine) {
      html += `<div class="diff-line diff-added">+ ${escapeHtml(transLine)}</div>`;
    } else if (!transLine) {
      html += `<div class="diff-line diff-removed">- ${escapeHtml(origLine)}</div>`;
    } else {
      html += `<div class="diff-line diff-removed">- ${escapeHtml(origLine)}</div>`;
      html += `<div class="diff-line diff-added">+ ${escapeHtml(transLine)}</div>`;
    }
  }

  return html;
}

// ========================================
// Event Handlers
// ========================================

function selectFile(path) {
  state.selectedFile = state.files.find(f => f.path === path);
  state.transformResult = null;
  renderFileList();

  // Enable preview button
  const previewBtn = document.getElementById('preview-btn');
  if (previewBtn) previewBtn.disabled = false;

  // Auto-preview if has migration
  if (state.selectedFile?.hasMigration) {
    previewSelected();
  }
}

function toggleRule(ruleId) {
  const index = state.selectedRules.indexOf(ruleId);
  if (index > -1) {
    state.selectedRules.splice(index, 1);
  } else {
    state.selectedRules.push(ruleId);
  }
  renderRuleList();
}

function filterFiles(query) {
  const lowerQuery = query.toLowerCase();
  const items = document.querySelectorAll('.file-item');
  items.forEach(item => {
    const text = item.textContent.toLowerCase();
    item.style.display = text.includes(lowerQuery) ? '' : 'none';
  });
}

function previewSelected() {
  if (!state.selectedFile || state.selectedRules.length === 0) {
    alert('Please select a file and at least one rule');
    return;
  }
  requestTransform(state.selectedFile.path, true);
}

function applySelected() {
  if (!state.selectedFile || state.selectedRules.length === 0) {
    alert('Please select a file and at least one rule');
    return;
  }
  if (confirm(`Apply migration to ${state.selectedFile.path}?`)) {
    requestTransform(state.selectedFile.path, false);
  }
}

function batchTransform() {
  const directory = prompt('Enter directory to process:', 'frontend/src');
  if (!directory) return;

  const dryRun = !confirm('This will modify files. Continue with actual changes? (Cancel for dry-run)');
  requestBatchTransform(directory, dryRun);
}

function rollbackAll() {
  if (confirm('Are you sure you want to rollback all changes?')) {
    requestRollback();
  }
}

// ========================================
// Utilities
// ========================================

function generateId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// ========================================
// Initialize
// ========================================

document.addEventListener('DOMContentLoaded', () => {
  render();
  connect();
});

// Make functions globally available
window.selectFile = selectFile;
window.toggleRule = toggleRule;
window.filterFiles = filterFiles;
window.previewSelected = previewSelected;
window.applySelected = applySelected;
window.batchTransform = batchTransform;
window.rollbackAll = rollbackAll;
window.requestFileList = requestFileList;
