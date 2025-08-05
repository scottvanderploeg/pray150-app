// Pray150 Psalm Reading Interface Script
document.addEventListener('DOMContentLoaded', function() {
    // Psalm pages are now handled by the Bible API and psalm.js
    // This script provides supporting functions
});

// Function to load psalm data via Bible API - used by psalm templates
function loadPsalmData(psalmNumber, translation = 'ESV') {
    return fetch(`/api/psalms/${psalmNumber}?translation=${translation}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data.data;
            } else {
                throw new Error(data.error || 'Failed to load psalm data');
            }
        })
        .catch(error => {
            console.error('Error loading psalm data:', error);
            return null;
        });
}

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

// Legacy function placeholder - no longer used
function updateDisplayedTranslation() {
    // This function is no longer used as translation switching 
    // is handled by the Bible API and psalm.js
    console.log('Legacy function called - translation switching handled by Bible API');
}

// Export functions for potential use elsewhere
window.Pray150PsalmReader = {
    loadPsalmData,
    extractYouTubeVideoId,
    formatPsalmText,
    updateDisplayedTranslation
};