// Pray150 Psalm Reading Interface Script
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a psalm page
    const psalmText = document.getElementById('psalmText');
    if (psalmText) {
        const psalmNumber = psalmText.dataset.psalmNumber;
        if (psalmNumber) {
            loadPsalmData(psalmNumber);
        }
    }
    
    // Handle translation selection
    const translationSelect = document.getElementById('translationSelect');
    if (translationSelect) {
        translationSelect.addEventListener('change', function() {
            updateDisplayedTranslation(this.value);
        });
    }
});

async function loadPsalmData(psalmNumber) {
    const psalmText = document.getElementById('psalmText');
    const youtubeContainer = document.getElementById('youtube-container');
    
    try {
        // Fetch psalm data from API
        const response = await fetch(`/api/psalms/${psalmNumber}`);
        const result = await response.json();
        
        if (result.success && result.data) {
            const psalm = result.data;
            
            // Update psalm text with all translations
            updatePsalmText(psalm);
            
            // Load YouTube video if music_url exists
            if (psalm.music_url) {
                loadYouTubeVideo(psalm.music_url, youtubeContainer);
            } else {
                youtubeContainer.innerHTML = '<div class="d-flex justify-content-center align-items-center bg-light rounded h-100"><div class="text-muted">No worship music available</div></div>';
            }
            
        } else {
            // Handle error
            psalmText.innerHTML = '<p class="text-danger">Error loading psalm content</p>';
            youtubeContainer.innerHTML = '<div class="d-flex justify-content-center align-items-center bg-light rounded h-100"><div class="text-muted">Unable to load music</div></div>';
        }
        
    } catch (error) {
        console.error('Error fetching psalm:', error);
        psalmText.innerHTML = '<p class="text-danger">Network error loading psalm</p>';
        youtubeContainer.innerHTML = '<div class="d-flex justify-content-center align-items-center bg-light rounded h-100"><div class="text-muted">Unable to load music</div></div>';
    }
}

function updatePsalmText(psalm) {
    const psalmText = document.getElementById('psalmText');
    const translationSelect = document.getElementById('translationSelect');
    
    // Create containers for each translation
    const translations = {
        niv: psalm.text_niv,
        esv: psalm.text_esv,
        nlt: psalm.text_nlt,
        nkjv: psalm.text_nkjv,
        nrsv: psalm.text_nrsv
    };
    
    let html = '';
    let defaultTranslation = 'niv';
    
    for (const [key, text] of Object.entries(translations)) {
        const isVisible = key === defaultTranslation;
        const formattedText = text ? formatPsalmText(text) : '<p class="text-muted fst-italic">Translation not available</p>';
        
        html += `<div id="text-${key}" class="translation-text" style="${isVisible ? '' : 'display: none;'}">${formattedText}</div>`;
    }
    
    psalmText.innerHTML = html;
    
    // Set default translation selection
    if (translationSelect) {
        translationSelect.value = defaultTranslation;
    }
}

function updateDisplayedTranslation(translation) {
    // Hide all translations
    const allTexts = document.querySelectorAll('.translation-text');
    allTexts.forEach(text => text.style.display = 'none');
    
    // Show selected translation
    const selectedText = document.getElementById(`text-${translation}`);
    if (selectedText) {
        selectedText.style.display = 'block';
    }
}

function formatPsalmText(text) {
    // Format the psalm text with proper spacing and paragraphs
    return text
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0)
        .map(line => `<p class="mb-3">${line}</p>`)
        .join('');
}

function extractYouTubeVideoId(url) {
    // Handle various YouTube URL formats including ?si= parameters
    const patterns = [
        /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
        /youtube\.com\/watch\?.*v=([^&\n?#]+)/
    ];
    
    for (const pattern of patterns) {
        const match = url.match(pattern);
        if (match && match[1]) {
            return match[1];
        }
    }
    
    return null;
}

function loadYouTubeVideo(musicUrl, container) {
    const videoId = extractYouTubeVideoId(musicUrl);
    
    if (videoId) {
        // Create YouTube iframe
        const iframe = document.createElement('iframe');
        iframe.style.cssText = 'width: 100%; height: 100%; border: none; border-radius: 0.5rem;';
        iframe.src = `https://www.youtube.com/embed/${videoId}?rel=0&modestbranding=1`;
        iframe.allowFullscreen = true;
        iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
        iframe.title = 'Psalm Worship Music';
        
        // Clear loading message and add iframe
        container.innerHTML = '';
        container.appendChild(iframe);
    } else {
        container.innerHTML = '<div class="d-flex justify-content-center align-items-center bg-light rounded h-100"><div class="text-muted">Invalid music URL format</div></div>';
    }
}

// Export functions for potential use elsewhere
window.Pray150PsalmReader = {
    loadPsalmData,
    extractYouTubeVideoId,
    formatPsalmText,
    updateDisplayedTranslation
};