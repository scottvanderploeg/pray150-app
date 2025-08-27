// Psalm-specific JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    const psalmText = document.getElementById('psalmText');
    const translationSelect = document.getElementById('translationSelect');
    const highlightBtn = document.getElementById('highlightBtn');
    const noteBtn = document.getElementById('noteBtn');
    const toggleMarkupsBtn = document.getElementById('toggleMarkupsBtn');
    
    // Journal auto-save functionality
    const journalForm = document.getElementById('journalForm');
    const journalEditors = document.querySelectorAll('.journal-editor');
    const saveStatus = document.getElementById('saveStatus');
    
    // Initialize Quill editors
    const quillInstances = {};
    
    // Register custom fonts with Quill
    const Font = Quill.import('formats/font');
    Font.whitelist = [
        'playfair', 'merriweather', 'lora', 'crimson', 'baskerville', 
        'source-serif', 'cormorant', 'vollkorn', 'alegreya', 'spectral',
        'neuton', 'linden', 'cardo', 'gentium', 'domine', 'bitter',
        'arvo', 'rokkitt', 'georgia', 'times', 'arial', 'helvetica',
        'opensans', 'roboto'
    ];
    Quill.register(Font, true);
    
    const toolbarOptions = [
        [{ 'size': ['small', false, 'large', 'huge'] }],
        [{ 'color': [] }, { 'background': [] }],
        ['bold', 'italic', 'underline', 'strike'],
        [{ 'align': [] }],
        [{ 'list': 'ordered'}, { 'list': 'bullet' }],
        [{ 'indent': '-1'}, { 'indent': '+1' }],
        ['clean']
    ];
    
    // Font name mapping for display
    const fontNames = {
        false: 'Default Font',
        'playfair': 'Playfair Display',
        'merriweather': 'Merriweather', 
        'lora': 'Lora',
        'crimson': 'Crimson Text',
        'baskerville': 'Libre Baskerville',
        'source-serif': 'Source Serif Pro',
        'cormorant': 'Cormorant Garamond',
        'vollkorn': 'Vollkorn',
        'alegreya': 'Alegreya',
        'spectral': 'Spectral',
        'neuton': 'Neuton',
        'linden': 'Linden Hill',
        'cardo': 'Cardo',
        'gentium': 'Gentium Basic',
        'domine': 'Domine',
        'bitter': 'Bitter',
        'arvo': 'Arvo',
        'rokkitt': 'Rokkitt',
        'georgia': 'Georgia',
        'times': 'Times New Roman',
        'arial': 'Arial',
        'helvetica': 'Helvetica Neue',
        'opensans': 'Open Sans',
        'roboto': 'Roboto'
    };
    
    let isHighlightMode = false;
    let isNoteMode = false;
    let markupsVisible = true;
    let saveTimeout = null;
    let lastSaveData = {};
    let currentEmotion = null;
    let currentHighlightColor = 'yellow';
    let pendingNoteSelection = null;
    let currentTranslation = 'NIV'; // Track current translation for markups

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
            
            // Update user preference and current translation tracking
            updateUserPreference('translation', selectedTranslation);
            currentTranslation = selectedTranslation.toUpperCase();
            
            // Clear existing markups when switching translations
            clearAllMarkups();
            
            // Load markups for the new translation after a brief delay
            setTimeout(() => {
                loadExistingMarkups();
            }, 500);
        });
    }

    // Create global toolbar
    const globalToolbar = new Quill('#global-toolbar', {
        theme: 'snow',
        modules: {
            toolbar: toolbarOptions
        }
    });
    
    console.log('Global toolbar created:', globalToolbar.container);
    
    // Simple approach - override the global toolbar to work with active editor
    function connectGlobalToolbar() {
        console.log('Setting up simple toolbar connection');
        
        // Track which editor is active
        let currentActiveEditor = null;
        
        // Update active editor tracking
        Object.values(quillInstances).forEach(quill => {
            quill.on('selection-change', function(range) {
                if (range) {
                    currentActiveEditor = quill;
                    console.log('Active editor changed to:', quill.container.id);
                }
            });
        });
        
        // Override the global toolbar's editor and handlers
        const toolbar = globalToolbar.getModule('toolbar');
        if (toolbar) {
            // Replace the toolbar's quill reference
            const originalQuill = toolbar.quill;
            
            // Create a proxy that redirects to the active editor
            toolbar.quill = new Proxy(originalQuill, {
                get: function(target, prop) {
                    if (currentActiveEditor) {
                        return currentActiveEditor[prop] && typeof currentActiveEditor[prop] === 'function' 
                            ? currentActiveEditor[prop].bind(currentActiveEditor) 
                            : currentActiveEditor[prop];
                    }
                    return target[prop];
                }
            });
            
            // Override specific format handlers
            const originalHandlers = toolbar.handlers;
            
            // Override color handler
            toolbar.addHandler('color', function(value) {
                console.log('Color handler called with value:', value);
                if (currentActiveEditor) {
                    const selection = currentActiveEditor.getSelection();
                    if (selection && selection.length > 0) {
                        currentActiveEditor.format('color', value);
                        console.log('Color applied:', value);
                    } else {
                        console.log('No text selected for color');
                    }
                } else {
                    console.log('No active editor for color');
                }
            });
            
            // Override background handler
            toolbar.addHandler('background', function(value) {
                console.log('Background handler called with value:', value);
                if (currentActiveEditor) {
                    const selection = currentActiveEditor.getSelection();
                    if (selection && selection.length > 0) {
                        currentActiveEditor.format('background', value);
                        console.log('Background applied:', value);
                    } else {
                        console.log('No text selected for background');
                    }
                } else {
                    console.log('No active editor for background');
                }
            });
            
            // Override other formatting handlers
            ['bold', 'italic', 'underline', 'strike'].forEach(format => {
                toolbar.addHandler(format, function(value) {
                    console.log(`${format} handler called`);
                    if (currentActiveEditor) {
                        const currentFormat = currentActiveEditor.getFormat();
                        currentActiveEditor.format(format, !currentFormat[format]);
                    }
                });
            });
            
            console.log('All toolbar handlers set up successfully');
            
            // Override the built-in Quill color buttons with our working functionality
            setTimeout(() => {
                const toolbarContainer = document.querySelector('#global-toolbar .ql-toolbar');
                if (toolbarContainer) {
                    console.log('Setting up enhanced color button overrides');
                    
                    // Replace color picker dropdowns with our enhanced versions
                    const colorPicker = toolbarContainer.querySelector('.ql-color .ql-picker-options');
                    const backgroundPicker = toolbarContainer.querySelector('.ql-background .ql-picker-options');
                    
                    if (colorPicker) {
                        colorPicker.innerHTML = `
                            <span class="ql-picker-item" data-value="black" style="background-color: black;" title="Black"></span>
                            <span class="ql-picker-item" data-value="gray" style="background-color: gray;" title="Gray"></span>
                            <span class="ql-picker-item" data-value="red" style="background-color: red;" title="Red"></span>
                            <span class="ql-picker-item" data-value="blue" style="background-color: blue;" title="Blue"></span>
                            <span class="ql-picker-item" data-value="green" style="background-color: green;" title="Green"></span>
                            <span class="ql-picker-item" data-value="purple" style="background-color: purple;" title="Purple"></span>
                            <span class="ql-picker-item" data-value="orange" style="background-color: orange;" title="Orange"></span>
                            <span class="ql-picker-item" data-value="darkblue" style="background-color: darkblue;" title="Dark Blue"></span>
                            <span class="ql-picker-item" data-value="darkgreen" style="background-color: darkgreen;" title="Dark Green"></span>
                            <span class="ql-picker-item" data-value="brown" style="background-color: brown;" title="Brown"></span>
                        `;
                        
                        // Add click handlers for color picker items
                        colorPicker.addEventListener('click', (e) => {
                            if (e.target.classList.contains('ql-picker-item')) {
                                const color = e.target.getAttribute('data-value');
                                console.log('Enhanced color picker clicked:', color);
                                applySimpleFormat('color', color);
                            }
                        });
                    }
                    
                    if (backgroundPicker) {
                        backgroundPicker.innerHTML = `
                            <span class="ql-picker-item" data-value="yellow" style="background-color: yellow;" title="Yellow Highlight"></span>
                            <span class="ql-picker-item" data-value="lightblue" style="background-color: lightblue;" title="Light Blue Highlight"></span>
                            <span class="ql-picker-item" data-value="lightgreen" style="background-color: lightgreen;" title="Light Green Highlight"></span>
                            <span class="ql-picker-item" data-value="pink" style="background-color: pink;" title="Pink Highlight"></span>
                            <span class="ql-picker-item" data-value="lavender" style="background-color: lavender;" title="Lavender Highlight"></span>
                            <span class="ql-picker-item" data-value="" style="background-color: white; border: 2px solid #ccc; position: relative;" title="Remove Highlight">
                                <span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #666; font-size: 10px;">✕</span>
                            </span>
                        `;
                        
                        // Add click handlers for background picker items
                        backgroundPicker.addEventListener('click', (e) => {
                            if (e.target.classList.contains('ql-picker-item')) {
                                const color = e.target.getAttribute('data-value');
                                console.log('Enhanced background picker clicked:', color);
                                applySimpleFormat('background', color || false);
                            }
                        });
                    }
                    
                    console.log('Enhanced color button overrides complete');
                }
            }, 3000);
            
            // Add simple color buttons that actually work
            setTimeout(() => {
                const toolbarContainer = document.querySelector('#global-toolbar .ql-toolbar');
                if (toolbarContainer) {
                    console.log('Adding simple color buttons');
                    
                    // Create a simple color section
                    const colorSection = document.createElement('span');
                    colorSection.className = 'ql-formats';
                    colorSection.innerHTML = `
                        <button type="button" class="simple-color-btn" data-color="red" style="background: red; width: 20px; height: 20px; border: 1px solid #ccc; margin: 1px;" title="Red Text"></button>
                        <button type="button" class="simple-color-btn" data-color="blue" style="background: blue; width: 20px; height: 20px; border: 1px solid #ccc; margin: 1px;" title="Blue Text"></button>
                        <button type="button" class="simple-color-btn" data-color="green" style="background: green; width: 20px; height: 20px; border: 1px solid #ccc; margin: 1px;" title="Green Text"></button>
                        <button type="button" class="simple-bg-btn" data-color="yellow" style="background: yellow; width: 20px; height: 20px; border: 1px solid #ccc; margin: 1px;" title="Yellow Highlight"></button>
                        <button type="button" class="simple-bg-btn" data-color="lightblue" style="background: lightblue; width: 20px; height: 20px; border: 1px solid #ccc; margin: 1px;" title="Blue Highlight"></button>
                    `;
                    
                    // Add to toolbar
                    toolbarContainer.appendChild(colorSection);
                    
                    // Add event listeners
                    colorSection.addEventListener('click', (e) => {
                        if (e.target.classList.contains('simple-color-btn') || e.target.classList.contains('simple-bg-btn')) {
                            e.preventDefault();
                            
                            const color = e.target.getAttribute('data-color');
                            const isBackground = e.target.classList.contains('simple-bg-btn');
                            
                            console.log('Simple color button clicked:', color, 'background:', isBackground);
                            
                            if (currentActiveEditor) {
                                const selection = currentActiveEditor.getSelection();
                                console.log('Selection:', selection);
                                
                                if (selection && selection.length > 0) {
                                    const formatType = isBackground ? 'background' : 'color';
                                    currentActiveEditor.format(formatType, color);
                                    console.log('Applied', formatType, ':', color);
                                } else {
                                    console.log('No text selected');
                                }
                            } else {
                                console.log('No active editor');
                            }
                        }
                    });
                    
                    console.log('Simple color buttons added');
                }
            }, 2500);
        }
    }
    
    // Connect toolbar after everything is initialized
    setTimeout(connectGlobalToolbar, 1000);
    
    // Function to add font selector
    function addFontSelector() {
        console.log('Attempting to add font selector...');
        
        // Try different ways to find the toolbar
        let toolbar = null;
        
        // Method 1: Look for .ql-toolbar in globalToolbar container
        if (globalToolbar && globalToolbar.container) {
            toolbar = globalToolbar.container.querySelector('.ql-toolbar');
            console.log('Method 1 - Toolbar in container:', toolbar);
        }
        
        // Method 2: Look directly in the global-toolbar element
        if (!toolbar) {
            const globalToolbarEl = document.getElementById('global-toolbar');
            if (globalToolbarEl) {
                toolbar = globalToolbarEl.querySelector('.ql-toolbar');
                console.log('Method 2 - Toolbar in global element:', toolbar);
            }
        }
        
        // Method 3: Check if the global-toolbar element itself has toolbar class
        if (!toolbar) {
            const globalToolbarEl = document.getElementById('global-toolbar');
            if (globalToolbarEl && globalToolbarEl.classList.contains('ql-toolbar')) {
                toolbar = globalToolbarEl;
                console.log('Method 3 - Global element is toolbar:', toolbar);
            }
        }
        
        // Method 4: Look for any .ql-toolbar on the page
        if (!toolbar) {
            toolbar = document.querySelector('.ql-toolbar');
            console.log('Method 4 - Any toolbar on page:', toolbar);
        }
        
        console.log('Final toolbar found:', toolbar);
        
        if (toolbar && !toolbar.querySelector('.ql-font-custom')) {
            console.log('Adding custom font selector to toolbar');
            
            // Create custom font selector
            const fontSelectContainer = document.createElement('span');
            fontSelectContainer.className = 'ql-formats';
            
            const fontSelect = document.createElement('select');
            fontSelect.className = 'ql-font-custom';
            fontSelect.style.cssText = `
                padding: 3px 6px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background: white;
                font-size: 12px;
                margin-right: 6px;
                min-width: 120px;
                max-width: 140px;
                z-index: 1100;
                position: relative;
            `;
            
            // Font options with display names
            const fontOptions = [
                ['', 'Default Font'],
                ['playfair', 'Playfair Display'],
                ['merriweather', 'Merriweather'], 
                ['lora', 'Lora'],
                ['crimson', 'Crimson Text'],
                ['baskerville', 'Libre Baskerville'],
                ['source-serif', 'Source Serif Pro'],
                ['cormorant', 'Cormorant Garamond'],
                ['vollkorn', 'Vollkorn'],
                ['alegreya', 'Alegreya'],
                ['spectral', 'Spectral'],
                ['neuton', 'Neuton'],
                ['linden', 'Linden Hill'],
                ['cardo', 'Cardo'],
                ['gentium', 'Gentium Basic'],
                ['domine', 'Domine'],
                ['bitter', 'Bitter'],
                ['arvo', 'Arvo'],
                ['rokkitt', 'Rokkitt'],
                ['georgia', 'Georgia'],
                ['times', 'Times New Roman'],
                ['arial', 'Arial'],
                ['helvetica', 'Helvetica Neue'],
                ['opensans', 'Open Sans'],
                ['roboto', 'Roboto']
            ];
            
            // Populate font selector with font previews
            fontOptions.forEach(([value, name]) => {
                const option = document.createElement('option');
                option.value = value;
                option.textContent = name;
                option.setAttribute('data-font', value);
                fontSelect.appendChild(option);
            });
            
            // Apply font family styling to the select element to show each option in its font
            fontSelect.style.fontFamily = 'Georgia, serif';
            
            // Handle font selection and apply preview
            fontSelect.addEventListener('change', function() {
                const selectedValue = this.value;
                if (selectedValue && selectedValue !== '') {
                    this.style.fontFamily = `var(--ql-font-${selectedValue}), Georgia, serif`;
                } else {
                    this.style.fontFamily = 'Georgia, serif';
                }
            });
            
            // Simpler approach - just update font selector to show current font
            fontSelect.style.fontFamily = 'Georgia, serif';
            
            // Handle font changes
            fontSelect.addEventListener('change', function() {
                const selectedFont = this.value || false;
                
                // Find currently active/focused editor
                let activeEditor = null;
                Object.values(quillInstances).forEach(quill => {
                    const selection = quill.getSelection();
                    if (selection) {
                        activeEditor = quill;
                    }
                });
                
                if (activeEditor) {
                    const selection = activeEditor.getSelection();
                    if (selection && selection.length > 0) {
                        // Format selected text
                        activeEditor.format('font', selectedFont);
                    } else {
                        // Format new text at cursor
                        activeEditor.format('font', selectedFont);
                    }
                } else {
                    console.log('No active editor found for font change');
                }
            });
            
            fontSelectContainer.appendChild(fontSelect);
            
            // Insert at the beginning of the toolbar
            toolbar.insertBefore(fontSelectContainer, toolbar.firstChild);
            console.log('Custom font selector added successfully');
        } else {
            console.log('Font selector already exists or toolbar not found');
            if (!toolbar) {
                console.log('Toolbar is null - checking DOM structure...');
                const globalEl = document.getElementById('global-toolbar');
                console.log('Global toolbar element:', globalEl);
                if (globalEl) {
                    console.log('Global toolbar HTML:', globalEl.innerHTML);
                }
            }
        }
    }
    
    // Try multiple times to add font selector with longer delays
    setTimeout(addFontSelector, 200);
    setTimeout(addFontSelector, 800);
    setTimeout(addFontSelector, 2000);
    
    // Also try when page is fully loaded
    document.addEventListener('DOMContentLoaded', addFontSelector);
    window.addEventListener('load', addFontSelector);
    
    // Initialize Quill editors with shared toolbar
    journalEditors.forEach((editorElement, index) => {
        const promptNumber = editorElement.getAttribute('data-prompt');
        const placeholder = editorElement.getAttribute('data-placeholder');
        
        // Get initial content
        const initialContent = editorElement.innerHTML.trim();
        
        // Clear the div content before initializing Quill
        editorElement.innerHTML = '';
        
        const quill = new Quill(editorElement, {
            theme: 'bubble', // Use bubble theme for editors (no individual toolbars)
            placeholder: placeholder,
            modules: {
                toolbar: false // No individual toolbar
            }
        });
        
        // Set initial content if exists
        if (initialContent && initialContent !== '') {
            // Check if content is HTML or plain text
            if (initialContent.includes('<') && initialContent.includes('>')) {
                quill.root.innerHTML = initialContent;
            } else {
                quill.setText(initialContent);
            }
        }
        
        // Store quill instance
        quillInstances[promptNumber] = quill;
        
        // Add focus tracking for this editor
        quill.on('selection-change', function(range, oldRange, source) {
            if (range) {
                // This editor is now active
                console.log(`Editor ${promptNumber} is now active`);
                
                // Update font selector to reflect current formatting
                const format = quill.getFormat(range);
                const fontSelect = document.querySelector('.ql-font-custom');
                if (fontSelect && format.font) {
                    fontSelect.value = format.font;
                } else if (fontSelect) {
                    fontSelect.value = '';
                }
            }
        });
        
        // Add change listener for auto-save
        quill.on('text-change', function(delta, oldDelta, source) {
            if (source === 'user') {
                scheduleAutoSave();
            }
        });
        
        // Connect editor to global toolbar
        quill.on('selection-change', function(range) {
            if (range) {
                // When this editor gets focus, connect it to the global toolbar
                globalToolbar.setContents(quill.getContents());
                
                // Sync toolbar state with current editor
                const toolbar = globalToolbar.getModule('toolbar');
                toolbar.quill = quill;
                
                // Override toolbar handlers to work with focused editor
                const toolbarContainer = globalToolbar.container.querySelector('.ql-toolbar');
                const buttons = toolbarContainer.querySelectorAll('button, select');
                
                buttons.forEach(button => {
                    // Remove existing listeners and add new ones for focused editor
                    button.onclick = null;
                    
                    if (button.classList.contains('ql-bold')) {
                        button.onclick = () => quill.format('bold', !quill.getFormat().bold);
                    } else if (button.classList.contains('ql-italic')) {
                        button.onclick = () => quill.format('italic', !quill.getFormat().italic);
                    } else if (button.classList.contains('ql-underline')) {
                        button.onclick = () => quill.format('underline', !quill.getFormat().underline);
                    } else if (button.classList.contains('ql-strike')) {
                        button.onclick = () => quill.format('strike', !quill.getFormat().strike);
                    }
                    // Add more format handlers as needed
                });
                
                // Handle dropdowns (font, size, etc.)
                const selects = toolbarContainer.querySelectorAll('select');
                selects.forEach(select => {
                    select.onchange = function() {
                        const format = this.classList[0].replace('ql-', '');
                        const value = this.value || false;
                        quill.format(format, value);
                    };
                });
            }
        });
    });

    // Journal auto-save functionality
    if (journalForm && journalEditors.length > 0) {
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
            
            // Collect data from Quill editors
            Object.keys(quillInstances).forEach(promptNum => {
                const quill = quillInstances[promptNum];
                const content = quill.getLength() > 1 ? quill.root.innerHTML.trim() : '';
                if (content && content !== '<p><br></p>') {
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
        
        // Note: Auto-save is now handled by Quill text-change events above
        // Each Quill editor calls scheduleAutoSave() when content changes
        
        // Function to schedule auto-save with debouncing
        function scheduleAutoSave() {
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
        }

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
            
            // Target all markup elements including the new classes
            const highlights = psalmText.querySelectorAll('.highlight, .note-marker, .highlight-marker');
            console.log('Found', highlights.length, 'markup elements to toggle');
            
            highlights.forEach(element => {
                if (markupsVisible) {
                    // Show markups with their styling
                    element.style.display = 'inline';
                    if (element.classList.contains('highlight') || element.classList.contains('highlight-marker')) {
                        const savedColor = element.dataset.highlightColor || 'yellow';
                        element.style.backgroundColor = savedColor;
                        element.style.padding = '1px 2px';
                        element.style.borderRadius = '2px';
                        element.style.border = 'none';
                        element.style.textDecoration = 'none';
                    }
                    if (element.classList.contains('note-marker')) {
                        element.style.backgroundColor = 'transparent';
                        element.style.textDecoration = 'underline dotted';
                        element.style.textDecorationColor = '#007bff';
                        element.style.cursor = 'help';
                        element.style.border = 'none';
                        element.style.padding = '';
                    }
                } else {
                    // Hide markup styling completely but keep the text visible
                    element.style.display = 'inline';
                    element.style.backgroundColor = 'transparent';
                    element.style.textDecoration = 'none';
                    element.style.cursor = 'default';
                    element.style.border = 'none';
                    element.style.padding = '';
                    element.style.borderRadius = '';
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
        
        // Show modal with proper cleanup for new notes  
        const noteModalElement = document.getElementById('noteModal');
        
        // Clean up any existing modal instances
        const existingModal = bootstrap.Modal.getInstance(noteModalElement);
        if (existingModal) {
            existingModal.dispose();
        }
        
        // Remove any leftover backdrop elements
        document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
            backdrop.remove();
        });
        
        // Reset body classes
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
        
        // Create fresh modal instance
        const noteModal = new bootstrap.Modal(noteModalElement, {
            backdrop: true,
            keyboard: true
        });
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
        
        // Show modal with proper cleanup for editing existing notes
        const noteModalElement = document.getElementById('noteModal');
        
        // Clean up any existing modal instances
        const existingModal = bootstrap.Modal.getInstance(noteModalElement);
        if (existingModal) {
            existingModal.dispose();
        }
        
        // Remove any leftover backdrop elements
        document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
            backdrop.remove();
        });
        
        // Reset body classes
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
        
        // Create fresh modal instance
        const noteModal = new bootstrap.Modal(noteModalElement, {
            backdrop: true,
            keyboard: true
        });
        noteModal.show();
    }

    // Add event delegation for existing note markers
    psalmText.addEventListener('click', function(e) {
        if (e.target.classList.contains('note-marker')) {
            e.preventDefault();
            editNote(e.target);
        }
    });

    // Clear all markups from the text
    function clearAllMarkups() {
        const allMarkups = psalmText.querySelectorAll('.highlight-marker, .note-marker, .highlight');
        allMarkups.forEach(markup => {
            // Replace markup span with just the text content
            const textNode = document.createTextNode(markup.textContent);
            markup.parentNode.replaceChild(textNode, markup);
        });
        
        // Merge adjacent text nodes that were split by markups
        psalmText.normalize();
        
        console.log('Cleared all existing markups');
    }

    // Load existing markups via AJAX to avoid HTML attribute truncation
    function loadExistingMarkups() {
        const psalmId = psalmText.getAttribute('data-psalm-id');
        if (!psalmId) {
            console.log('No psalm ID found');
            return;
        }
        
        console.log('Loading markups via AJAX for psalm', psalmId, 'translation:', currentTranslation);
        
        fetch(`/get_markups/${psalmId}?translation=${currentTranslation}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error loading markups:', data.error);
                    return;
                }
                
                const markups = data.markups || [];
                console.log('Successfully loaded', markups.length, 'markups via AJAX');
                
                // Group markups by text for better handling
                const markupsByText = {};
                markups.forEach((markup, index) => {
                    const markupData = markup['markup-data'] || markup.markup_data;
                    if (markupData && markupData.text) {
                        if (!markupsByText[markupData.text]) {
                            markupsByText[markupData.text] = [];
                        }
                        markupsByText[markupData.text].push({...markupData, dbId: markup.id});
                    }
                });
                
                // Apply markups grouped by text
                Object.keys(markupsByText).forEach(text => {
                    const textMarkups = markupsByText[text];
                    console.log(`Processing ${textMarkups.length} markup(s) for text: "${text.substring(0, 30)}..."`);
                    
                    const textContent = psalmText.textContent || psalmText.innerText;
                    if (textContent.includes(text)) {
                        applyMultipleMarkupsToText(text, textMarkups);
                        console.log(`Successfully applied ${textMarkups.length} markup(s)`);
                    } else {
                        console.log('Text not found in current psalm content');
                    }
                });
                
                console.log('Finished loading all markups');
            })
            .catch(error => {
                console.error('Failed to load markups:', error);
            });
    }
    
    // Apply multiple markups to the same text
    function applyMultipleMarkupsToText(textToFind, markupsArray) {
        const walker = document.createTreeWalker(
            psalmText,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        let node;
        let appliedCount = 0;
        
        while (node = walker.nextNode()) {
            const text = node.textContent;
            const index = text.indexOf(textToFind);
            
            if (index !== -1) {
                try {
                    const range = document.createRange();
                    range.setStart(node, index);
                    range.setEnd(node, index + textToFind.length);
                    
                    // Create wrapper span for multiple markups
                    const wrapperSpan = document.createElement('span');
                    wrapperSpan.dataset.markupGroup = `group-${Date.now()}`;
                    
                    // Collect all markup styles
                    let hasHighlight = false;
                    let highlightColor = 'yellow';
                    const notes = [];
                    
                    markupsArray.forEach((markupData, idx) => {
                        if (markupData.markup_type === 'highlight') {
                            hasHighlight = true;
                            highlightColor = markupData.color || 'yellow';
                        } else if (markupData.markup_type === 'note') {
                            notes.push(markupData);
                        }
                    });
                    
                    // Apply highlight if present
                    if (hasHighlight) {
                        wrapperSpan.style.backgroundColor = highlightColor;
                        wrapperSpan.style.padding = '1px 2px';
                        wrapperSpan.style.borderRadius = '2px';
                        wrapperSpan.dataset.highlightColor = highlightColor;
                        wrapperSpan.classList.add('highlight-marker');
                    }
                    
                    // Apply notes if present
                    if (notes.length > 0) {
                        // Combine all note texts
                        const combinedNotes = notes.map((note, idx) => 
                            `Note ${idx + 1}: ${note.note_text || 'No text'}`
                        ).join('\n\n');
                        
                        wrapperSpan.style.textDecoration = hasHighlight ? 'underline dotted' : 'underline dotted';
                        wrapperSpan.style.textDecorationColor = '#007bff';
                        wrapperSpan.style.cursor = 'help';
                        wrapperSpan.title = combinedNotes;
                        wrapperSpan.classList.add('note-marker');
                        wrapperSpan.dataset.noteText = combinedNotes;
                        wrapperSpan.dataset.noteCount = notes.length;
                        
                        // Add visual indicator for multiple notes
                        if (notes.length > 1) {
                            wrapperSpan.style.borderLeft = '3px solid #007bff';
                        }
                        
                        // Add click handler for editing (will edit the first note)
                        wrapperSpan.addEventListener('click', function(e) {
                            e.preventDefault();
                            editNote(this);
                        });
                        
                        // Initialize tooltip
                        new bootstrap.Tooltip(wrapperSpan, {
                            title: combinedNotes,
                            placement: 'top',
                            html: true
                        });
                    }
                    
                    // Apply the wrapper span
                    range.surroundContents(wrapperSpan);
                    appliedCount++;
                    break; // Successfully applied, stop searching
                    
                } catch (error) {
                    console.warn('Could not apply markups to text:', textToFind, 'at position', index, error);
                }
            }
        }
        
        if (appliedCount === 0) {
            console.log('Could not find or apply markups for text:', textToFind.substring(0, 50) + '...');
        }
    }

    // Save markup to server
    function saveMarkup(type, text, color, noteText = null) {
        const psalmId = psalmText.getAttribute('data-psalm-id');
        const translation = currentTranslation || (translationSelect ? translationSelect.value : 'NIV');
        
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

    // Initialize translation tracking from the page
    if (translationSelect && translationSelect.value) {
        currentTranslation = translationSelect.value.toUpperCase();
    }
    
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
