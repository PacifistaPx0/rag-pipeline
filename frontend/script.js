// Global variables
let uploadedFile = null;
let isProcessing = false;

// DOM elements - will be initialized after DOM loads
let uploadArea, fileInput, fileName, fileSize, uploadBtn;
let querySection, queryInput, queryBtn, resultsSection, answerText, sourcesList;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing elements');
    
    // Initialize DOM elements
    uploadArea = document.getElementById('uploadArea');
    fileInput = document.getElementById('fileInput');
    fileName = document.getElementById('fileName');
    fileSize = document.getElementById('fileSize');
    uploadBtn = document.getElementById('uploadBtn');
    querySection = document.getElementById('querySection');
    queryInput = document.getElementById('queryInput');
    queryBtn = document.getElementById('queryBtn');
    resultsSection = document.getElementById('resultsSection');
    answerText = document.getElementById('answerText');
    sourcesList = document.getElementById('sourcesList');
    
    console.log('Upload area:', uploadArea);
    console.log('File input:', fileInput);
    console.log('File details:', document.getElementById('fileDetails'));
    console.log('fileName element:', fileName);
    console.log('fileSize element:', fileSize);
    console.log('uploadBtn element:', uploadBtn);
    
    setupEventListeners();
});

function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // File upload events
    if (uploadArea) {
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);
        console.log('Drag and drop events added to upload area');
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
        console.log('Change event listener added to file input');
        
        // Test if the file input is clickable
        fileInput.addEventListener('click', function() {
            console.log('File input clicked!');
        });
    }
    
    if (uploadBtn) {
        uploadBtn.addEventListener('click', uploadFile);
        console.log('Click event added to upload button');
    }
    
    // Query events
    if (queryBtn) {
        queryBtn.addEventListener('click', submitQuery);
    }
    if (queryInput) {
        queryInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                submitQuery();
            }
        });
    }
    
    console.log('All event listeners set up');
}

// Drag and drop handlers
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelection(files[0]);
    }
}

function handleFileSelect(e) {
    console.log('File select event triggered');
    const file = e.target.files[0];
    console.log('Selected file:', file);
    if (file) {
        handleFileSelection(file);
    }
}

function handleFileSelection(file) {
    console.log('handleFileSelection called with:', file);
    
    // Validate file type
    if (!file.name.toLowerCase().endsWith('.md')) {
        showError('Please select a Markdown (.md) file');
        return;
    }
    
    // Validate file size (2MB limit)
    const maxSize = 2 * 1024 * 1024; // 2MB in bytes
    if (file.size > maxSize) {
        showError('File size must be under 2MB');
        return;
    }
    
    uploadedFile = file;
    console.log('File validated, updating UI');
    
    // Update UI
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    
    // Show file details
    const fileDetails = document.getElementById('fileDetails');
    console.log('File details element:', fileDetails);
    fileDetails.style.display = 'block';
    
    uploadBtn.disabled = false;
    uploadBtn.textContent = 'Process File';
    console.log('UI updated, file details should be visible');
}

async function uploadFile() {
    if (!uploadedFile || isProcessing) return;
    
    isProcessing = true;
    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Processing...';
    
    try {
        const formData = new FormData();
        formData.append('file', uploadedFile);
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('File processed successfully!');
            querySection.style.display = 'block';
            queryInput.focus();
        } else {
            throw new Error(result.message || 'Upload failed');
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        showError(`Upload failed: ${error.message}`);
    } finally {
        isProcessing = false;
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Process File';
    }
}

async function submitQuery() {
    const query = queryInput.value.trim();
    if (!query || isProcessing) return;
    
    isProcessing = true;
    queryBtn.disabled = true;
    queryBtn.textContent = 'Searching...';
    
    // Show loading state
    resultsSection.style.display = 'block';
    answerText.innerHTML = '<div class="loading">Searching for relevant information...</div>';
    sourcesList.innerHTML = '';
    
    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });
        
        if (!response.ok) {
            throw new Error(`Query failed: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            displayResults(result.answer, result.sources || []);
        } else {
            throw new Error(result.message || 'Query failed');
        }
        
    } catch (error) {
        console.error('Query error:', error);
        answerText.innerHTML = `<div class="error">Query failed: ${error.message}</div>`;
    } finally {
        isProcessing = false;
        queryBtn.disabled = false;
        queryBtn.textContent = 'Ask Question';
    }
}

function displayResults(answer, sources) {
    // Display answer
    answerText.innerHTML = formatAnswer(answer);
    
    // Display sources
    sourcesList.innerHTML = '';
    if (sources && sources.length > 0) {
        sources.forEach((source, index) => {
            const sourceItem = document.createElement('div');
            sourceItem.className = 'source-item';
            sourceItem.innerHTML = `
                <div class="source-header">
                    <strong>Source ${index + 1}</strong>
                    <span class="source-score">Relevance: ${(source.score * 100).toFixed(1)}%</span>
                </div>
                <div class="source-content">${formatText(source.content)}</div>
            `;
            sourcesList.appendChild(sourceItem);
        });
    } else {
        sourcesList.innerHTML = '<div class="no-sources">No specific sources found</div>';
    }
}

function formatAnswer(answer) {
    // Convert markdown-like formatting to HTML
    return answer
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');
}

function formatText(text) {
    // Basic text formatting for source content
    return text
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>');
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showError(message) {
    // Create or update error message
    let errorDiv = document.getElementById('errorMessage');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.id = 'errorMessage';
        errorDiv.className = 'error-message';
        document.querySelector('.container').insertBefore(errorDiv, document.querySelector('.upload-section'));
    }
    
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

function showSuccess(message) {
    // Create or update success message
    let successDiv = document.getElementById('successMessage');
    if (!successDiv) {
        successDiv = document.createElement('div');
        successDiv.id = 'successMessage';
        successDiv.className = 'success-message';
        document.querySelector('.container').insertBefore(successDiv, document.querySelector('.upload-section'));
    }
    
    successDiv.textContent = message;
    successDiv.style.display = 'block';
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        successDiv.style.display = 'none';
    }, 3000);
}

// Utility function to reset the application state
function resetApp() {
    uploadedFile = null;
    fileInput.value = '';
    fileName.textContent = '';
    fileSize.textContent = '';
    
    // Hide file details
    const fileDetails = document.getElementById('fileDetails');
    fileDetails.style.display = 'none';
    
    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Select File First';
    querySection.style.display = 'none';
    resultsSection.style.display = 'none';
    queryInput.value = '';
    
    // Hide messages
    const errorDiv = document.getElementById('errorMessage');
    const successDiv = document.getElementById('successMessage');
    if (errorDiv) errorDiv.style.display = 'none';
    if (successDiv) successDiv.style.display = 'none';
}
