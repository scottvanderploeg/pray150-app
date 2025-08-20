// Psalm-specific JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    const psalmText = document.getElementById('psalmText');
    const translationSelect = document.getElementById('translationSelect');
    const highlightBtn = document.getElementById('highlightBtn');
    const noteBtn = document.getElementById('noteBtn');
    const toggleMarkupsBtn = document.getElementById('toggleMarkupsBtn');
    
    // Journal auto-save functionality
    const journalForm = document.getElementById('journalForm');
    const journalTextareas = document.querySelectorAll('.journal-textarea');
    const saveStatus = document.getElementById('saveStatus');
    
    let isHighlightMode = false;
    let isNoteMode = false;
    let markupsVisible = true;
    let saveTimeout = null;
    let lastSaveData = {};
    let currentEmotion = null;
    let currentHighlightColor = 'yellow';
    let pendingNoteSelection = null;

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
            } else {
                // If translation text doesn't exist, this means we're using the new Bible API
                // Trigger the Bible API translation change function
                if (typeof changeTranslation === 'function') {
                    // Set the value and trigger the change
                    const headerSelect = document.getElementById('translationSelect');
                    if (headerSelect) {
                        headerSelect.value = selectedTranslation.toUpperCase();
                        changeTranslation();
                    }
                }
                console.log('Using Bible API for translation switching');
            }
            
            // Update user preference (could be saved via AJAX)
            updateUserPreference('translation', selectedTranslation);
        });
    }

    // Journal auto-save functionality
    if (journalForm && journalTextareas.length > 0) {
        // Initialize with empty save status
        if (saveStatus) {
            saveStatus.textContent = 'Ready';
            saveStatus.className = 'text-muted';
        }

        // Create persistent emotion indicator
        function createEmotionIndicator() {
            if (!currentEmotion) return;
            
            // Remove any existing indicator
            const existingIndicator = document.querySelector('.emotion-indicator');
            if (existingIndicator) {
                existingIndicator.remove();
            }
            
            // Create new indicator
            const indicator = document.createElement('div');
            indicator.className = 'emotion-indicator alert alert-info d-flex align-items-center justify-content-between mb-2';
            indicator.style.cssText = 'position: sticky; top: 0px; z-index: 100; margin-bottom: 1rem; background: rgba(217, 237, 247, 0.95); backdrop-filter: blur(5px);';
            
            const emotionEmojis = {
                'terrible': '😞',
                'bad': '😟', 
                'okay': '😐',
                'good': '😊',
                'great': '😄'
            };
            
            const emotionLabels = {
                'terrible': 'Awful',
                'bad': 'Bad',
                'okay': 'Okay', 
                'good': 'Good',
                'great': 'Great'
            };
            
            indicator.innerHTML = `
                <div>
                    <i class="fas fa-heart text-primary me-2"></i>
                    <strong>Your heart today: ${emotionLabels[currentEmotion] || currentEmotion}</strong>
                    <span style="font-size: 1.2em; margin-left: 8px;">${emotionEmojis[currentEmotion] || '❤️'}</span>
                </div>
                <small class="text-muted">Being saved with your journal</small>
            `;
            
            // Insert at the top of the journal form, right after the form element
            const journalForm = document.getElementById('journalForm');
            if (journalForm) {
                journalForm.insertBefore(indicator, journalForm.firstChild);
            }
        }
        
        // Initialize emotion data from DOM on page load
        function initializeEmotion() {
            if (currentEmotion) {
                createEmotionIndicator();
                return; // Already initialized
            }
            
            try {
                const emotionAlert = document.querySelector('.alert-info img[src*="emoji-"]');
                if (emotionAlert) {
                    const emotionSrc = emotionAlert.getAttribute('src');
                    const emotionMatch = emotionSrc.match(/emoji-([^.]+)\.png/);
                    if (emotionMatch) {
                        currentEmotion = emotionMatch[1];
                        console.log('Initialized emotion from image:', currentEmotion);
                        // Store in localStorage for persistence
                        localStorage.setItem('currentEmotion_' + journalForm.dataset.psalmId, currentEmotion);
                        createEmotionIndicator();
                        return;
                    }
                }
                
                // Also check for emotion text in the DOM
                const emotionText = document.querySelector('.alert-info strong');
                if (emotionText && !currentEmotion) {
                    const emotionValue = emotionText.textContent.toLowerCase().trim();
                    if (emotionValue === 'awful') currentEmotion = 'terrible';
                    else if (['bad', 'okay', 'good', 'great'].includes(emotionValue)) {
                        currentEmotion = emotionValue;
                        console.log('Initialized emotion from text:', currentEmotion);
                        // Store in localStorage for persistence
                        localStorage.setItem('currentEmotion_' + journalForm.dataset.psalmId, currentEmotion);
                        createEmotionIndicator();
                        return;
                    }
                }
                
                // Try to load from localStorage if DOM methods failed
                const storedEmotion = localStorage.getItem('currentEmotion_' + journalForm.dataset.psalmId);
                if (storedEmotion) {
                    currentEmotion = storedEmotion;
                    console.log('Loaded emotion from localStorage:', currentEmotion);
                    createEmotionIndicator();
                }
            } catch (error) {
                console.error('Error initializing emotion:', error);
            }
        }
        
        // Function to collect all journal data
        function getJournalData() {
            const psalmId = journalForm.dataset.psalmId;
            const promptResponses = {};
            
            journalTextareas.forEach(textarea => {
                const promptNum = textarea.dataset.prompt;
                const content = textarea.value.trim();
                if (content) {
                    promptResponses[promptNum] = content;
                }
            });
            
            // Always include emotion data if we have it
            if (currentEmotion) {
                promptResponses['emotion'] = currentEmotion;
                console.log('Including emotion in journal data:', currentEmotion);
            }
            
            return {
                psalm_id: psalmId,
                prompt_responses: promptResponses
            };
        }

        // Function to save journal data
        function saveJournal() {
            const data = getJournalData();
            
            // Don't save if no content
            if (Object.keys(data.prompt_responses).length === 0) {
                if (saveStatus) {
                    saveStatus.textContent = 'Ready';
                    saveStatus.className = 'text-muted';
                }
                return;
            }

            // Check if data has changed
            const dataString = JSON.stringify(data);
            if (dataString === JSON.stringify(lastSaveData)) {
                return; // No changes
            }

            if (saveStatus) {
                saveStatus.textContent = 'Auto-saving journal entry...';
                saveStatus.className = 'text-info';
            }

            console.log('Auto-saving journal entry...');

            fetch('/save_journal', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || ''
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    lastSaveData = data;
                    if (saveStatus) {
                        saveStatus.textContent = 'Journal entry saved successfully';
                        saveStatus.className = 'text-success';
                    }
                    console.log('Journal entry saved successfully');
                } else {
                    if (saveStatus) {
                        saveStatus.textContent = 'Error saving entry';
                        saveStatus.className = 'text-danger';
                    }
                    console.error('Error saving journal entry:', result.error);
                }
            })
            .catch(error => {
                if (saveStatus) {
                    saveStatus.textContent = 'Error saving entry';
                    saveStatus.className = 'text-danger';
                }
                console.error('Error saving journal entry:', error);
            });
        }

        // Initialize emotion data from DOM
        initializeEmotion();
        
        // Periodic emotion re-initialization to handle DOM changes
        setInterval(function() {
            if (!currentEmotion) {
                initializeEmotion();
            } else {
                // Ensure the indicator is still visible
                const indicator = document.querySelector('.emotion-indicator');
                if (!indicator) {
                    createEmotionIndicator();
                }
            }
        }, 3000);
        
        // Add event listeners for auto-save
        journalTextareas.forEach(textarea => {
            textarea.addEventListener('input', function() {
                // Clear existing timeout
                if (saveTimeout) {
                    clearTimeout(saveTimeout);
                }
                
                // Set new timeout for auto-save (2 seconds after user stops typing)
                saveTimeout = setTimeout(saveJournal, 2000);
                
                if (saveStatus) {
                    saveStatus.textContent = 'Typing...';
                    saveStatus.className = 'text-muted';
                }
            });

            // Save on blur (when user clicks away)
            textarea.addEventListener('blur', function() {
                if (saveTimeout) {
                    clearTimeout(saveTimeout);
                }
                saveTimeout = setTimeout(saveJournal, 500);
            });
        });

        // Save before page unload
        window.addEventListener('beforeunload', function() {
            if (saveTimeout) {
                clearTimeout(saveTimeout);
            }
            // Attempt synchronous save (may not work in all browsers)
            const data = getJournalData();
            if (Object.keys(data.prompt_responses).length > 0) {
                navigator.sendBeacon('/save_journal', JSON.stringify(data));
            }
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
                if (markupsVisible) {
                    // Show markups with their styling
                    element.style.display = 'inline';
                    if (element.classList.contains('highlight')) {
                        const savedColor = element.dataset.highlightColor || 'yellow';
                        element.style.backgroundColor = savedColor;
                        element.style.border = 'none';
                        element.style.textDecoration = 'none';
                    }
                    if (element.classList.contains('note-marker')) {
                        element.style.backgroundColor = 'transparent';
                        element.style.textDecoration = 'underline dotted';
                        element.style.textDecorationColor = '#007bff';
                        element.style.cursor = 'help';
                        element.style.border = 'none';
                    }
                } else {
                    // Hide markup styling completely but keep the text visible
                    element.style.display = 'inline';
                    element.style.backgroundColor = 'transparent';
                    element.style.textDecoration = 'none';
                    element.style.cursor = 'default';
                    element.style.border = 'none';
                    element.style.textDecorationColor = 'transparent';
                    // Hide tooltips when markups are hidden
                    if (element.hasAttribute('data-bs-toggle')) {
                        const tooltip = bootstrap.Tooltip.getInstance(element);
                        if (tooltip) {
                            tooltip.hide();
                        }
                    }
                }
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
                
                // Apply highlight styling
                span.style.backgroundColor = currentHighlightColor;
                span.style.padding = '1px 2px';
                span.dataset.highlightColor = currentHighlightColor;
                
                // Save highlight (would typically be sent to server)
                saveMarkup('highlight', span.textContent, currentHighlightColor);
                
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
        // Store selection for later use
        pendingNoteSelection = {
            selection: selection,
            selectedText: selectedText,
            range: selection.getRangeAt(0).cloneRange()
        };
        
        // Update modal content
        document.getElementById('noteModalLabel').textContent = 'Add Your Note';
        document.getElementById('selectedTextPreview').textContent = selectedText.length > 50 ? selectedText.substring(0, 50) + '...' : selectedText;
        document.getElementById('noteTextInput').value = '';
        
        // Hide delete button and edit help for new notes
        const deleteBtn = document.getElementById('deleteNoteBtn');
        const editHelp = document.getElementById('editNoteHelp');
        if (deleteBtn) deleteBtn.style.display = 'none';
        if (editHelp) editHelp.style.display = 'none';
        
        // Show modal
        const noteModal = new bootstrap.Modal(document.getElementById('noteModal'));
        noteModal.show();
    }
    
    // Handle note saving from modal
    const saveNoteBtn = document.getElementById('saveNoteBtn');
    if (saveNoteBtn) {
            saveNoteBtn.addEventListener('click', function() {
                const noteText = document.getElementById('noteTextInput').value.trim();
                
                // Check if we're editing an existing note
                if (this.dataset.editingElement === 'true') {
                    if (noteText && this.tempNoteElement) {
                        // Update existing note
                        this.tempNoteElement.title = noteText;
                        
                        // Destroy and recreate tooltip with new content
                        const existingTooltip = bootstrap.Tooltip.getInstance(this.tempNoteElement);
                        if (existingTooltip) {
                            existingTooltip.dispose();
                        }
                        new bootstrap.Tooltip(this.tempNoteElement);
                        
                        // Save updated note
                        saveMarkup('note', this.tempSelectedText, null, noteText);
                        
                        // Reset editing state
                        this.dataset.editingElement = 'false';
                        this.tempNoteElement = null;
                        this.tempSelectedText = null;
                        document.getElementById('noteModalLabel').textContent = 'Add Your Note';
                        
                        // Close modal and ensure screen responsiveness
                        const modalInstance = bootstrap.Modal.getInstance(document.getElementById('noteModal'));
                        if (modalInstance) {
                            modalInstance.hide();
                        }
                        
                        // Force remove modal backdrop and restore document interaction
                        setTimeout(() => {
                            const backdrop = document.querySelector('.modal-backdrop');
                            if (backdrop) {
                                backdrop.remove();
                            }
                            document.body.classList.remove('modal-open');
                            document.body.style.overflow = '';
                            document.body.style.paddingRight = '';
                        }, 300);
                        
                        window.Pray150.showNotification('Note updated successfully!', 'success');
                    }
                } else if (noteText && pendingNoteSelection) {
                    // Create new note (existing functionality)
                    const span = document.createElement('span');
                    span.className = 'note-marker';
                    span.title = noteText;
                    span.setAttribute('data-bs-toggle', 'tooltip');
                    span.setAttribute('data-bs-placement', 'top');
                    
                    try {
                        // Clear current selection and restore the saved range
                        window.getSelection().removeAllRanges();
                        window.getSelection().addRange(pendingNoteSelection.range);
                        
                        pendingNoteSelection.range.surroundContents(span);
                        window.getSelection().removeAllRanges();
                        
                        // Apply note styling
                        span.style.textDecoration = 'underline dotted';
                        span.style.textDecorationColor = '#007bff';
                        span.style.cursor = 'help';
                        
                        // Add click handler for editing notes
                        span.addEventListener('click', function(e) {
                            e.preventDefault();
                            editNote(this);
                        });
                        
                        // Initialize tooltip for the new note
                        new bootstrap.Tooltip(span);
                        
                        // Save note (would typically be sent to server)
                        saveMarkup('note', pendingNoteSelection.selectedText, null, noteText);
                        
                        // Reset note mode
                        isNoteMode = false;
                        noteBtn.classList.remove('active');
                        noteBtn.innerHTML = '<i class="fas fa-sticky-note me-1"></i>Add Note';
                        psalmText.style.cursor = 'default';
                        
                        // Close modal and ensure screen responsiveness
                        const modalInstance = bootstrap.Modal.getInstance(document.getElementById('noteModal'));
                        if (modalInstance) {
                            modalInstance.hide();
                        }
                        
                        // Force remove modal backdrop and restore document interaction
                        setTimeout(() => {
                            const backdrop = document.querySelector('.modal-backdrop');
                            if (backdrop) {
                                backdrop.remove();
                            }
                            document.body.classList.remove('modal-open');
                            document.body.style.overflow = '';
                            document.body.style.paddingRight = '';
                        }, 300);
                        
                        window.Pray150.showNotification('Note added successfully!', 'success');
                    } catch (error) {
                        console.error('Note addition failed:', error);
                        window.Pray150.showNotification('Could not add note to selected text', 'warning');
                    }
                    
                    pendingNoteSelection = null;
                }
            });
    }

    // Handle note deletion
    const deleteNoteBtn = document.getElementById('deleteNoteBtn');
    if (deleteNoteBtn) {
        deleteNoteBtn.addEventListener('click', function() {
            const saveNoteBtn = document.getElementById('saveNoteBtn');
            if (saveNoteBtn.dataset.editingElement === 'true' && saveNoteBtn.tempNoteElement) {
                if (confirm('Are you sure you want to delete this note?')) {
                    // Remove the note element
                    const noteElement = saveNoteBtn.tempNoteElement;
                    const textContent = noteElement.textContent;
                    
                    // Replace the note element with just the text
                    const textNode = document.createTextNode(textContent);
                    noteElement.parentNode.replaceChild(textNode, noteElement);
                    
                    // Reset editing state
                    saveNoteBtn.dataset.editingElement = 'false';
                    saveNoteBtn.tempNoteElement = null;
                    saveNoteBtn.tempSelectedText = null;
                    document.getElementById('noteModalLabel').textContent = 'Add Your Note';
                    
                    // Close modal and ensure screen responsiveness
                    const modalInstance = bootstrap.Modal.getInstance(document.getElementById('noteModal'));
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                    
                    // Force remove modal backdrop and restore document interaction
                    setTimeout(() => {
                        const backdrop = document.querySelector('.modal-backdrop');
                        if (backdrop) {
                            backdrop.remove();
                        }
                        document.body.classList.remove('modal-open');
                        document.body.style.overflow = '';
                        document.body.style.paddingRight = '';
                    }, 300);
                    
                    window.Pray150.showNotification('Note deleted successfully!', 'success');
                }
            }
        });
    }

    // Add color picker functionality
    document.querySelectorAll('.highlight-color-option').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const color = this.dataset.color;
            currentHighlightColor = color;
            
            // Update the main highlight button
            if (highlightBtn) {
                highlightBtn.dataset.color = color;
            }
            
            // Update dropdown selection visual feedback
            const dropdownItems = document.querySelectorAll('.highlight-color-option');
            dropdownItems.forEach(item => item.classList.remove('active'));
            this.classList.add('active');
            
            // If highlight mode is active, show feedback
            if (isHighlightMode) {
                window.Pray150.showNotification(`Highlight color set to ${color}`, 'info');
            }
        });
    });

    // Function to edit existing notes
    function editNote(noteElement) {
        const currentNoteText = noteElement.title;
        const selectedText = noteElement.textContent;
        
        // Update modal content for editing
        document.getElementById('noteModalLabel').textContent = 'Edit Your Note';
        document.getElementById('selectedTextPreview').textContent = selectedText.length > 50 ? selectedText.substring(0, 50) + '...' : selectedText;
        document.getElementById('noteTextInput').value = currentNoteText;
        
        // Show delete button and edit help for editing mode
        const deleteBtn = document.getElementById('deleteNoteBtn');
        const editHelp = document.getElementById('editNoteHelp');
        if (deleteBtn) deleteBtn.style.display = 'inline-block';
        if (editHelp) editHelp.style.display = 'block';
        
        // Store reference to the note element being edited
        const saveNoteBtn = document.getElementById('saveNoteBtn');
        saveNoteBtn.dataset.editingElement = 'true';
        saveNoteBtn.tempNoteElement = noteElement;
        saveNoteBtn.tempSelectedText = selectedText;
        
        // Show modal
        const noteModal = new bootstrap.Modal(document.getElementById('noteModal'));
        noteModal.show();
    }

    // Add event delegation for existing note markers
    psalmText.addEventListener('click', function(e) {
        if (e.target.classList.contains('note-marker')) {
            e.preventDefault();
            editNote(e.target);
        }
    });

    // Load existing markups on page load
    function loadExistingMarkups() {
        const markupsData = psalmText.getAttribute('data-markups');
        console.log('Raw markups data length:', markupsData ? markupsData.length : 'null');
        
        if (!markupsData || markupsData === '[]' || markupsData.length === 0) {
            console.log('No markups to load');
            return;
        }
        
        try {
            // The data might be large, so let's be more careful with parsing
            const markups = JSON.parse(markupsData);
            console.log('Successfully parsed', markups.length, 'markups');
            
            markups.forEach((markup, index) => {
                console.log(`Processing markup ${index + 1}/${markups.length}`);
                
                // The database uses 'markup-data' column (with hyphen)
                const data = markup['markup-data'] || markup.markup_data;
                if (!data) {
                    console.log('No markup data found for markup', index);
                    return;
                }
                
                console.log('Applying markup:', data.markup_type, 'for text:', data.text.substring(0, 30) + '...');
                
                // Find and apply the markup to the text
                const textContent = psalmText.textContent || psalmText.innerText;
                if (textContent.includes(data.text)) {
                    applyMarkup(data);
                    console.log('Successfully applied markup');
                } else {
                    console.log('Text not found in current psalm content');
                }
            });
            
            console.log('Finished loading all markups');
        } catch (error) {
            console.error('JSON parsing error:', error);
            console.log('First 200 chars of data:', markupsData ? markupsData.substring(0, 200) : 'null');
        }
    }
    
    // Apply a markup to the psalm text
    function applyMarkup(markupData) {
        const textToFind = markupData.text;
        const walker = document.createTreeWalker(
            psalmText,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        let node;
        while (node = walker.nextNode()) {
            const text = node.textContent;
            const index = text.indexOf(textToFind);
            
            if (index !== -1) {
                const range = document.createRange();
                range.setStart(node, index);
                range.setEnd(node, index + textToFind.length);
                
                const span = document.createElement('span');
                
                if (markupData.markup_type === 'highlight') {
                    span.style.backgroundColor = markupData.color || 'yellow';
                    span.style.padding = '1px 2px';
                    span.dataset.highlightColor = markupData.color || 'yellow';
                } else if (markupData.markup_type === 'note') {
                    span.style.textDecoration = 'underline dotted';
                    span.style.textDecorationColor = '#007bff';
                    span.style.cursor = 'help';
                    span.title = markupData.note_text || '';
                    span.classList.add('note-marker');
                    
                    // Add click handler for editing notes
                    span.addEventListener('click', function(e) {
                        e.preventDefault();
                        editNote(this);
                    });
                    
                    // Initialize tooltip
                    new bootstrap.Tooltip(span);
                }
                
                try {
                    range.surroundContents(span);
                    break; // Found and applied, stop searching
                } catch (error) {
                    console.warn('Could not apply markup to text:', textToFind, error);
                }
            }
        }
    }

    // Save markup to server
    function saveMarkup(type, text, color, noteText = null) {
        const psalmId = psalmText.getAttribute('data-psalm-id');
        const translation = translationSelect ? translationSelect.value : 'NIV';
        
        const markupData = {
            psalm_id: psalmId,
            translation: translation,
            markup_type: type,
            text: text,
            color: color,
            note_text: noteText
        };
        
        console.log('Saving markup:', markupData);
        
        // Send markup data to server
        fetch('/save_markup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(markupData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Markup saved successfully');
            } else {
                console.error('Failed to save markup:', data.error);
                window.Pray150.showNotification('Failed to save markup. Please try again.', 'error');
            }
        })
        .catch(error => {
            console.error('Error saving markup:', error);
            window.Pray150.showNotification('Error saving markup. Please try again.', 'error');
        });
    }

    // Update user preference
    function updateUserPreference(key, value) {
        // Save to localStorage for immediate use
        localStorage.setItem(`pray150_${key}`, value);
        console.log(`Updating preference: ${key} = ${value}`);
        
        // This would typically be an AJAX call to update user preferences
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
            console.log('Auto-saving journal entry...');
            
            // Show auto-save indicator
            const saveBtn = form.querySelector('button[type="submit"]');
            const originalText = saveBtn.innerHTML;
            saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Auto-saving...';
            saveBtn.disabled = true;
            
            // Make AJAX call to save journal entry
            // First try the regular endpoint, then fall back to API endpoint if needed
            fetch('/save_journal', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    saveBtn.innerHTML = '<i class="fas fa-check me-1"></i>Saved';
                    console.log('Journal entry saved successfully');
                } else {
                    saveBtn.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>Error';
                    console.error('Failed to save journal entry');
                }
            })
            .catch(error => {
                console.error('Error saving journal entry:', error);
                saveBtn.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>Error';
            })
            .finally(() => {
                // Reset button after 2 seconds
                setTimeout(() => {
                    saveBtn.innerHTML = originalText;
                    saveBtn.disabled = false;
                }, 2000);
            });
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

    // Load existing markups after DOM is ready
    setTimeout(loadExistingMarkups, 100);
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
