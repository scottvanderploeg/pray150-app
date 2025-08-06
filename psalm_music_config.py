# Psalm Music Configuration
# YouTube Video IDs from your curated playlist: https://youtube.com/playlist?list=PLlAZONCUO1iQr2m19nFmRLyTWdey-iXuh

# Instructions for adding videos:
# 1. Go to your YouTube playlist
# 2. Click on a video
# 3. Copy the video ID from the URL (part after "v=" or "watch?v=")
# 4. Add it to the dictionary below with the psalm number as the key

PSALM_MUSIC_VIDEOS = {
    # Example format:
    # 1: 'VIDEO_ID_HERE',  # "Song Title" by Artist
    
    # Psalms 1-10
    1: '',   # Psalm 1 - "Blessed is the man"
    2: '',   # Psalm 2
    3: '',   # Psalm 3
    4: '',   # Psalm 4
    5: '',   # Psalm 5
    6: '',   # Psalm 6
    7: '',   # Psalm 7
    8: '',   # Psalm 8
    9: '',   # Psalm 9
    10: '',  # Psalm 10
    
    # Psalms 11-20
    11: '',  # Psalm 11
    12: '',  # Psalm 12
    13: '',  # Psalm 13
    14: '',  # Psalm 14
    15: '',  # Psalm 15
    16: '',  # Psalm 16
    17: '',  # Psalm 17
    18: '',  # Psalm 18
    19: '',  # Psalm 19
    20: '',  # Psalm 20
    
    # Psalms 21-30
    21: '',  # Psalm 21
    22: '',  # Psalm 22
    23: '',  # Psalm 23 - "The Lord is my shepherd"
    24: '',  # Psalm 24
    25: '',  # Psalm 25
    26: '',  # Psalm 26
    27: '',  # Psalm 27
    28: '',  # Psalm 28
    29: '',  # Psalm 29
    30: '',  # Psalm 30
    
    # Psalms 31-40
    31: '',  # Psalm 31
    32: '',  # Psalm 32
    33: '',  # Psalm 33
    34: '',  # Psalm 34
    35: '',  # Psalm 35
    36: '',  # Psalm 36
    37: '',  # Psalm 37
    38: '',  # Psalm 38
    39: '',  # Psalm 39
    40: '',  # Psalm 40
    
    # Psalms 41-50
    41: '',  # Psalm 41
    42: '',  # Psalm 42
    43: '',  # Psalm 43
    44: '',  # Psalm 44
    45: '',  # Psalm 45
    46: '',  # Psalm 46
    47: '',  # Psalm 47
    48: '',  # Psalm 48
    49: '',  # Psalm 49
    50: '',  # Psalm 50
    
    # Psalms 51-60
    51: '',  # Psalm 51
    52: '',  # Psalm 52
    53: '',  # Psalm 53
    54: '',  # Psalm 54
    55: '',  # Psalm 55
    56: '',  # Psalm 56
    57: '',  # Psalm 57
    58: '',  # Psalm 58
    59: '',  # Psalm 59
    60: '',  # Psalm 60
    
    # Psalms 61-70
    61: '',  # Psalm 61
    62: '',  # Psalm 62
    63: '',  # Psalm 63
    64: '',  # Psalm 64
    65: '',  # Psalm 65
    66: '',  # Psalm 66
    67: '',  # Psalm 67
    68: '',  # Psalm 68
    69: '',  # Psalm 69
    70: '',  # Psalm 70
    
    # Psalms 71-80
    71: '',  # Psalm 71
    72: '',  # Psalm 72
    73: '',  # Psalm 73
    74: '',  # Psalm 74
    75: '',  # Psalm 75
    76: '',  # Psalm 76
    77: '',  # Psalm 77
    78: '',  # Psalm 78
    79: '',  # Psalm 79
    80: '',  # Psalm 80
    
    # Psalms 81-90
    81: '',  # Psalm 81
    82: '',  # Psalm 82
    83: '',  # Psalm 83
    84: '',  # Psalm 84
    85: '',  # Psalm 85
    86: '',  # Psalm 86
    87: '',  # Psalm 87
    88: '',  # Psalm 88
    89: '',  # Psalm 89
    90: '',  # Psalm 90
    
    # Psalms 91-100
    91: '',  # Psalm 91
    92: '',  # Psalm 92
    93: '',  # Psalm 93
    94: '',  # Psalm 94
    95: '',  # Psalm 95
    96: '',  # Psalm 96
    97: '',  # Psalm 97
    98: '',  # Psalm 98
    99: '',  # Psalm 99
    100: '', # Psalm 100
    
    # Psalms 101-103
    101: '', # Psalm 101
    102: '', # Psalm 102
    103: '', # Psalm 103
}

# Multiple videos for the same psalm (if you have more than one song for a psalm)
PSALM_ALTERNATE_VIDEOS = {
    # Example:
    # 23: ['VIDEO_ID_1', 'VIDEO_ID_2'],  # Multiple versions of Psalm 23
}

def get_psalm_video_id(psalm_number):
    """Get the primary video ID for a psalm"""
    return PSALM_MUSIC_VIDEOS.get(psalm_number, '')

def get_psalm_alternate_videos(psalm_number):
    """Get alternate video IDs for a psalm"""
    return PSALM_ALTERNATE_VIDEOS.get(psalm_number, [])

def has_psalm_music(psalm_number):
    """Check if a psalm has any music configured"""
    primary = get_psalm_video_id(psalm_number)
    alternates = get_psalm_alternate_videos(psalm_number)
    return bool(primary) or bool(alternates)