// Psalm-specific JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    const psalmText = document.getElementById('psalmText');
    const translationSelect = document.getElementById('translationSelect');
    const highlightBtn = document.getElementById('highlightBtn');
    const noteBtn = document.getElementById('noteBtn');
    const toggleMarkupsBtn = document.getElementById('toggleMarkupsBtn');
    
    let isHighlightMode = false;
    let isNoteMode = false;
    let markupsVisible = true;

    // Translation switching
    if (translationSelect) {
        translationSelect.addEventListener('change', function() {
            const selectedTranslation = this.value;
            
            // Hide all translation texts
            const allTexts = psalmText.querySelectorAll('[id^="text-"]');
            allTexts.forEach(text => {
                text.style.display = 'none';
            });
            
            // Show selected translation
            const selectedText = document.getElementById(`text-${selectedTranslation}`);
            if (selectedText) {
                selectedText.style.display = 'block';
            }
            
            // Update user preference (could be saved via AJAX)
            updateUserPreference('translation', selectedTranslation);
        });
    }

    // Text selection and highlighting
    if (highlightBtn) {
        highlightBtn.addEventListener('click', function() {
            isHighlightMode = !isHighlightMode;
            isNoteMode = false;
            
            this.classList.toggle('active');
            noteBtn.classList.remove('active');
            
            if (isHighlightMode) {
                psalmText.style.cursor = 'crosshair';
                this.innerHTML = '<i class="fas fa-times me-1"></i>Cancel Highlight';
            } else {
                psalmText.style.cursor = 'default';
                this.innerHTML = '<i class="fas fa-highlighter me-1"></i>Highlight';
            }
        });
    }

    if (noteBtn) {
        noteBtn.addEventListener('click', function() {
            isNoteMode = !isNoteMode;
            isHighlightMode = false;
            
            this.classList.toggle('active');
            highlightBtn.classList.remove('active');
            
            if (isNoteMode) {
                psalmText.style.cursor = 'pointer';
                this.innerHTML = '<i class="fas fa-times me-1"></i>Cancel Note';
            } else {
                psalmText.style.cursor = 'default';
                this.innerHTML = '<i class="fas fa-sticky-note me-1"></i>Add Note';
            }
        });
    }

    // Toggle markups visibility
    if (toggleMarkupsBtn) {
        toggleMarkupsBtn.addEventListener('click', function() {
            markupsVisible = !markupsVisible;
            
            const highlights = psalmText.querySelectorAll('.highlight, .note-marker');
            highlights.forEach(element => {
                element.style.display = markupsVisible ? 'inline' : 'none';
            });
            
            this.innerHTML = markupsVisible 
                ? '<i class="fas fa-eye-slash me-1"></i>Hide Markups'
                : '<i class="fas fa-eye me-1"></i>Show Markups';
        });
    }

    // Handle text selection
    psalmText.addEventListener('mouseup', function() {
        const selection = window.getSelection();
        const selectedText = selection.toString().trim();
        
        if (selectedText.length > 0) {
            if (isHighlightMode) {
                highlightSelection(selection);
            } else if (isNoteMode) {
                addNoteToSelection(selection, selectedText);
            }
        }
    });

    // Highlight selected text
    function highlightSelection(selection) {
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            const span = document.createElement('span');
            span.className = 'highlight';
            
            try {
                range.surroundContents(span);
                selection.removeAllRanges();
                
                // Save highlight (would typically be sent to server)
                saveMarkup('highlight', span.textContent, 'yellow');
                
                // Reset highlight mode
                isHighlightMode = false;
                highlightBtn.classList.remove('active');
                highlightBtn.innerHTML = '<i class="fas fa-highlighter me-1"></i>Highlight';
                psalmText.style.cursor = 'default';
                
                window.Pray150.showNotification('Text highlighted successfully!', 'success');
            } catch (error) {
                console.error('Highlighting failed:', error);
                window.Pray150.showNotification('Could not highlight selected text', 'warning');
            }
        }
    }

    // Add note to selected text
    function addNoteToSelection(selection, selectedText) {
        const noteText = prompt('Add your note:', '');
        
        if (noteText && noteText.trim() !== '') {
            if (selection.rangeCount > 0) {
                const range = selection.getRangeAt(0);
                const span = document.createElement('span');
                span.className = 'note-marker';
                span.title = noteText;
                span.setAttribute('data-bs-toggle', 'tooltip');
                span.setAttribute('data-bs-placement', 'top');
                
                try {
                    range.surroundContents(span);
                    selection.removeAllRanges();
                    
                    // Initialize tooltip for the new note
                    new bootstrap.Tooltip(span);
                    
                    // Save note (would typically be sent to server)
                    saveMarkup('note', selectedText, null, noteText);
                    
                    // Reset note mode
                    isNoteMode = false;
                    noteBtn.classList.remove('active');
                    noteBtn.innerHTML = '<i class="fas fa-sticky-note me-1"></i>Add Note';
                    psalmText.style.cursor = 'default';
                    
                    window.Pray150.showNotification('Note added successfully!', 'success');
                } catch (error) {
                    console.error('Note addition failed:', error);
                    window.Pray150.showNotification('Could not add note to selected text', 'warning');
                }
            }
        }
    }

    // Save markup to server (placeholder function)
    function saveMarkup(type, text, color, noteText = null) {
        const psalmId = psalmText.getAttribute('data-psalm-id');
        const translation = translationSelect.value;
        
        // In a real implementation, this would send data to the server
        const markupData = {
            psalm_id: psalmId,
            translation: translation,
            markup_type: type,
            text: text,
            color: color,
            note_text: noteText
        };
        
        console.log('Saving markup:', markupData);
        
        // This would typically be an AJAX call to save the markup
        // fetch('/save_markup', {
        //     method: 'POST',
        //     headers: {'Content-Type': 'application/json'},
        //     body: JSON.stringify(markupData)
        // });
    }

    // Update user preference
    function updateUserPreference(key, value) {
        // This would typically be an AJAX call to update user preferences
        console.log(`Updating preference: ${key} = ${value}`);
        
        // fetch('/update_preference', {
        //     method: 'POST',
        //     headers: {'Content-Type': 'application/json'},
        //     body: JSON.stringify({key: key, value: value})
        // });
    }

    // Auto-save journal entries with debouncing
    const journalForms = document.querySelectorAll('.journal-form');
    journalForms.forEach((form, index) => {
        const textarea = form.querySelector('textarea');
        let timeout;
        
        textarea.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                autoSaveJournal(form);
            }, 3000); // Auto-save after 3 seconds of inactivity
        });
    });

    function autoSaveJournal(form) {
        const formData = new FormData(form);
        const content = formData.get('content');
        
        if (content && content.trim() !== '') {
            // Show auto-save indicator
            const saveBtn = form.querySelector('button[type="submit"]');
            const originalText = saveBtn.innerHTML;
            saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Auto-saving...';
            saveBtn.disabled = true;
            
            // Simulate auto-save (in real implementation, this would be an AJAX call)
            setTimeout(() => {
                saveBtn.innerHTML = '<i class="fas fa-check me-1"></i>Saved';
                setTimeout(() => {
                    saveBtn.innerHTML = originalText;
                    saveBtn.disabled = false;
                }, 1000);
            }, 1000);
        }
    }

    // Verse of the day sharing
    function shareVerse() {
        const psalmNumber = document.querySelector('h1').textContent;
        const psalmText = document.querySelector('.psalm-text').textContent.substring(0, 200) + '...';
        
        const shareText = `${psalmNumber}\n\n"${psalmText}"\n\n#Pray150 #ScriptureFed #SpiritLed`;
        
        if (navigator.share) {
            navigator.share({
                title: psalmNumber,
                text: shareText,
                url: window.location.href
            });
        } else {
            window.Pray150.copyToClipboard(shareText);
        }
    }

    // Add share button if not exists
    const psalmHeader = document.querySelector('.psalm-header');
    if (psalmHeader && !psalmHeader.querySelector('.share-btn')) {
        const shareBtn = document.createElement('button');
        shareBtn.className = 'btn btn-outline-primary btn-sm share-btn ms-2';
        shareBtn.innerHTML = '<i class="fas fa-share me-1"></i>Share';
        shareBtn.addEventListener('click', shareVerse);
        
        const title = psalmHeader.querySelector('h2');
        if (title) {
            title.appendChild(shareBtn);
        }
    }

    // Reading progress tracking
    let startTime = Date.now();
    let hasScrolledToBottom = false;
    
    // Track if user has scrolled through the psalm
    window.addEventListener('scroll', function() {
        const scrollPercent = (window.scrollY + window.innerHeight) / document.body.offsetHeight;
        if (scrollPercent > 0.9 && !hasScrolledToBottom) {
            hasScrolledToBottom = true;
            console.log('User has read through the psalm');
        }
    });

    // Track reading time
    window.addEventListener('beforeunload', function() {
        const readingTime = Math.floor((Date.now() - startTime) / 60000);
        console.log(`Reading time: ${readingTime} minutes`);
        // This data could be sent to the server for analytics
    });
});

// Keyboard shortcuts for psalm reading
document.addEventListener('keydown', function(e) {
    // 'H' for highlight mode
    if (e.key.toLowerCase() === 'h' && !e.ctrlKey && !e.metaKey) {
        const activeElement = document.activeElement;
        if (activeElement.tagName !== 'INPUT' && activeElement.tagName !== 'TEXTAREA') {
            e.preventDefault();
            document.getElementById('highlightBtn').click();
        }
    }
    
    // 'N' for note mode
    if (e.key.toLowerCase() === 'n' && !e.ctrlKey && !e.metaKey) {
        const activeElement = document.activeElement;
        if (activeElement.tagName !== 'INPUT' && activeElement.tagName !== 'TEXTAREA') {
            e.preventDefault();
            document.getElementById('noteBtn').click();
        }
    }
    
    // 'T' to toggle markups
    if (e.key.toLowerCase() === 't' && !e.ctrlKey && !e.metaKey) {
        const activeElement = document.activeElement;
        if (activeElement.tagName !== 'INPUT' && activeElement.tagName !== 'TEXTAREA') {
            e.preventDefault();
            document.getElementById('toggleMarkupsBtn').click();
        }
    }
});
