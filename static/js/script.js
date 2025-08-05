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
    
    // Translation selection is handled by psalm.js for psalm pages
    // This avoids duplicate event listeners
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

// These functions are no longer needed as psalm pages use the Bible API
// and translation switching is handled by psalm.js

function formatPsalmText(text) {
    if (!text) return '<p class="text-muted fst-italic">Translation not available</p>';
    
    // Split text into lines and process each one
    const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);
    let formattedLines = [];
    
    for (let line of lines) {
        // Check if line starts with a verse number (digit followed by space or colon)
        if (/^\d+[\s:]/.test(line)) {
            // Add verse number styling
            const verseMatch = line.match(/^(\d+)[\s:](.+)/);
            if (verseMatch) {
                const verseNum = verseMatch[1];
                const verseText = verseMatch[2].trim();
                formattedLines.push(`<p class="mb-3"><span class="verse-number text-primary fw-bold me-2">${verseNum}</span>${verseText}</p>`);
            } else {
                formattedLines.push(`<p class="mb-3">${line}</p>`);
            }
        } else if (line.match(/^Psalm \d+/i)) {
            // Title formatting
            formattedLines.push(`<h6 class="psalm-title text-center text-primary mb-4 fw-bold">${line}</h6>`);
        } else {
            // Regular verse text
            formattedLines.push(`<p class="mb-3">${line}</p>`);
        }
    }
    
    return formattedLines.join('');
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