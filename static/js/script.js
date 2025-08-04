// Pray150 Psalm Display Script
document.addEventListener('DOMContentLoaded', function() {
    loadPsalm1();
});

async function loadPsalm1() {
    const psalmTitle = document.getElementById('psalm-title');
    const psalmText = document.getElementById('psalm-text');
    const youtubeContainer = document.getElementById('youtube-container');
    
    try {
        // Fetch Psalm 1 data from API
        const response = await fetch('/api/psalms/1');
        const result = await response.json();
        
        if (result.success && result.data) {
            const psalm = result.data;
            
            // Update title
            psalmTitle.textContent = `Psalm ${psalm.psalm_number}`;
            
            // Update text with NIV translation
            if (psalm.text_niv) {
                psalmText.innerHTML = formatPsalmText(psalm.text_niv);
            } else {
                psalmText.innerHTML = '<p class="text-gray-500 italic">Psalm text not available</p>';
            }
            
            // Load YouTube video if music_url exists
            if (psalm.music_url) {
                loadYouTubeVideo(psalm.music_url, youtubeContainer);
            } else {
                youtubeContainer.innerHTML = '<div class="flex justify-center items-center h-full bg-gray-100 text-gray-500">No worship music available</div>';
            }
            
        } else {
            // Handle error
            psalmTitle.textContent = 'Psalm 1';
            psalmText.innerHTML = '<p class="text-red-500">Error loading psalm content</p>';
            youtubeContainer.innerHTML = '<div class="flex justify-center items-center h-full bg-gray-100 text-gray-500">Unable to load music</div>';
        }
        
    } catch (error) {
        console.error('Error fetching psalm:', error);
        psalmTitle.textContent = 'Psalm 1';
        psalmText.innerHTML = '<p class="text-red-500">Network error loading psalm</p>';
        youtubeContainer.innerHTML = '<div class="flex justify-center items-center h-full bg-gray-100 text-gray-500">Unable to load music</div>';
    }
}

function formatPsalmText(text) {
    // Format the psalm text with proper spacing and verse numbers
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
        // Create YouTube iframe after psalm is loaded
        const iframe = document.createElement('iframe');
        iframe.className = 'youtube-iframe';
        iframe.src = `https://www.youtube.com/embed/${videoId}?rel=0&modestbranding=1`;
        iframe.allowFullscreen = true;
        iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
        
        // Clear loading message and add iframe
        container.innerHTML = '';
        container.appendChild(iframe);
    } else {
        container.innerHTML = '<div class="flex justify-center items-center h-full bg-gray-100 text-gray-500">Invalid music URL format</div>';
    }
}

// Export functions for potential use elsewhere
window.Pray150Psalm = {
    loadPsalm1,
    extractYouTubeVideoId,
    formatPsalmText
};