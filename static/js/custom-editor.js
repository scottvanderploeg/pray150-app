// Custom Rich Text Editor Functions
console.log('Loading custom rich text editor...');

// Global variables
let currentActiveEditor = null;
let autoSaveTimeout = null;

// Format text using document.execCommand
window.formatText = function(command, value = null) {
    console.log('Format command:', command, 'Value:', value);
    
    // Get the currently focused editor
    const activeEditor = document.activeElement;
    
    if (!activeEditor || !activeEditor.classList.contains('custom-editor-content')) {
        console.log('No active editor found');
        return;
    }
    
    // Prevent the editor from losing focus
    activeEditor.focus();
    
    try {
        // Special handling for font size
        if (command === 'fontSize') {
            // Use CSS style instead of document.execCommand for better control
            const selection = window.getSelection();
            if (selection.rangeCount > 0) {
                const range = selection.getRangeAt(0);
                
                if (range.collapsed) {
                    // No selection - set for next typing
                    const span = document.createElement('span');
                    span.style.fontSize = value;
                    span.appendChild(document.createTextNode('\u200B')); // Zero-width space
                    range.insertNode(span);
                    range.setStart(span.firstChild, 1);
                    range.collapse(true);
                    selection.removeAllRanges();
                    selection.addRange(range);
                } else {
                    // Has selection - wrap it
                    const contents = range.extractContents();
                    const span = document.createElement('span');
                    span.style.fontSize = value;
                    span.appendChild(contents);
                    range.insertNode(span);
                }
            }
        }
        // Special handling for highlight removal
        else if (command === 'hiliteColor' && value === 'transparent') {
            document.execCommand('hiliteColor', false, 'transparent');
            document.execCommand('removeFormat', false, null);
        }
        // Standard formatting commands
        else {
            document.execCommand(command, false, value);
        }
        
        console.log('Applied formatting:', command, value);
        
        // Update button states
        updateButtonStates(activeEditor);
        
        // Auto-save after formatting
        scheduleAutoSave();
        
        // Close any open dropdowns
        closeAllDropdowns();
        
        // Keep focus on editor
        activeEditor.focus();
        
    } catch (error) {
        console.error('Error applying format:', error);
    }
};

// Toggle dropdown visibility
window.toggleDropdown = function(dropdownId) {
    console.log('Toggling dropdown:', dropdownId);
    
    // Close all other dropdowns first
    closeAllDropdowns(dropdownId);
    
    const dropdown = document.getElementById(dropdownId);
    if (dropdown) {
        const isVisible = dropdown.classList.contains('show');
        dropdown.classList.toggle('show', !isVisible);
        console.log('Dropdown', dropdownId, isVisible ? 'closed' : 'opened');
    }
};

// Close all dropdowns
function closeAllDropdowns(exceptId = null) {
    const dropdowns = document.querySelectorAll('.format-dropdown-content');
    dropdowns.forEach(dropdown => {
        if (!exceptId || dropdown.id !== exceptId) {
            dropdown.classList.remove('show');
        }
    });
}

// Update button states based on current formatting
function updateButtonStates(editor) {
    if (!editor) return;
    
    // Find the global toolbar
    const toolbar = document.querySelector('.global-toolbar .custom-editor-toolbar');
    if (!toolbar) return;
    
    // Get current formatting
    const isBold = document.queryCommandState('bold');
    const isItalic = document.queryCommandState('italic');
    const isUnderline = document.queryCommandState('underline');
    const isStrikethrough = document.queryCommandState('strikethrough');
    
    // Update button appearance
    const boldBtn = toolbar.querySelector('[data-format="bold"]');
    const italicBtn = toolbar.querySelector('[data-format="italic"]');
    const underlineBtn = toolbar.querySelector('[data-format="underline"]');
    const strikethroughBtn = toolbar.querySelector('[data-format="strikethrough"]');
    
    if (boldBtn) boldBtn.classList.toggle('active', isBold);
    if (italicBtn) italicBtn.classList.toggle('active', isItalic);
    if (underlineBtn) underlineBtn.classList.toggle('active', isUnderline);
    if (strikethroughBtn) strikethroughBtn.classList.toggle('active', isStrikethrough);
}

// Auto-save functionality
function scheduleAutoSave() {
    if (autoSaveTimeout) {
        clearTimeout(autoSaveTimeout);
    }
    
    autoSaveTimeout = setTimeout(() => {
        saveJournalEntries();
    }, 2000); // Save 2 seconds after last change
}

// Save journal entries
function saveJournalEntries() {
    console.log('Auto-saving journal entries...');
    
    const editors = document.querySelectorAll('.custom-editor-content');
    const data = {};
    
    editors.forEach(editor => {
        const prompt = editor.getAttribute('data-prompt');
        if (prompt) {
            data[prompt] = editor.innerHTML;
        }
    });
    
    // Add psalm ID
    const psalmMatch = window.location.pathname.match(/\/psalm\/(\d+)/);
    if (psalmMatch) {
        data.psalm_id = parseInt(psalmMatch[1]);
    }
    
    console.log('Saving data:', data);
    
    fetch('/save_journal', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            console.log('Journal entries saved successfully');
            showSaveIndicator();
        } else {
            console.error('Failed to save journal entries:', result.error);
        }
    })
    .catch(error => {
        console.error('Error saving journal entries:', error);
    });
}

// Show save indicator
function showSaveIndicator() {
    const indicator = document.createElement('div');
    indicator.textContent = 'Saved ✓';
    indicator.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 14px;
        z-index: 1000;
        opacity: 0;
        transition: opacity 0.3s;
    `;
    
    document.body.appendChild(indicator);
    
    // Fade in
    setTimeout(() => {
        indicator.style.opacity = '1';
    }, 10);
    
    // Fade out and remove
    setTimeout(() => {
        indicator.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(indicator);
        }, 300);
    }, 2000);
}

// Initialize custom editors
function initializeCustomEditors() {
    console.log('Initializing custom editors...');
    
    const editors = document.querySelectorAll('.custom-editor-content');
    
    editors.forEach(editor => {
        // Handle input changes
        editor.addEventListener('input', function() {
            scheduleAutoSave();
            updateButtonStates(this);
        });
        
        // Handle selection changes
        editor.addEventListener('mouseup', function() {
            updateButtonStates(this);
        });
        
        editor.addEventListener('keyup', function() {
            updateButtonStates(this);
        });
        
        // Handle focus
        editor.addEventListener('focus', function() {
            currentActiveEditor = this;
            updateButtonStates(this);
        });
        
        // Prevent default formatting shortcuts and handle them ourselves
        editor.addEventListener('keydown', function(e) {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key.toLowerCase()) {
                    case 'b':
                        e.preventDefault();
                        formatText('bold');
                        break;
                    case 'i':
                        e.preventDefault();
                        formatText('italic');
                        break;
                    case 'u':
                        e.preventDefault();
                        formatText('underline');
                        break;
                }
            }
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.format-dropdown')) {
            closeAllDropdowns();
        }
    });
    
    console.log('Custom editors initialized');
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing custom editors...');
    initializeCustomEditors();
});

console.log('Custom rich text editor loaded');