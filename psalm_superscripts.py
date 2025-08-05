"""
Psalm Superscripts/Inscriptions Database for Pray150
Contains authorship, musical directions, and historical contexts for all 150 Psalms
"""

PSALM_SUPERSCRIPTS = {
    1: None,  # No superscript
    2: None,  # No superscript 
    3: "A psalm of David, when he fled from Absalom his son.",
    4: "To the choirmaster: with stringed instruments. A Psalm of David.",
    5: "To the choirmaster: for the flutes. A Psalm of David.",
    6: "To the choirmaster: with stringed instruments; according to The Sheminith. A Psalm of David.",
    7: "A Shiggaion of David, which he sang to the LORD concerning the words of Cush, a Benjaminite.",
    8: "To the choirmaster: according to The Gittith. A Psalm of David.",
    9: "To the choirmaster: according to Muth-labben. A Psalm of David.",
    10: None,  # No superscript (continuation of Psalm 9 in Hebrew)
    11: "To the choirmaster. Of David.",
    12: "To the choirmaster: according to The Sheminith. A Psalm of David.",
    13: "To the choirmaster. A Psalm of David.",
    14: "To the choirmaster. Of David.",
    15: "A Psalm of David.",
    16: "A Miktam of David.",
    17: "A Prayer of David.",
    18: "To the choirmaster. A Psalm of David, the servant of the LORD, who addressed the words of this song to the LORD on the day when the LORD delivered him from the hand of all his enemies, and from the hand of Saul.",
    19: "To the choirmaster. A Psalm of David.",
    20: "To the choirmaster. A Psalm of David.",
    21: "To the choirmaster. A Psalm of David.",
    22: "To the choirmaster: according to The Doe of the Dawn. A Psalm of David.",
    23: "A Psalm of David.",
    24: "Of David. A Psalm.",
    25: "Of David.",
    26: "Of David.",
    27: "Of David.",
    28: "Of David.",
    29: "A Psalm of David.",
    30: "A Psalm of David. A Song for the dedication of the temple.",
    31: "To the choirmaster. A Psalm of David.",
    32: "Of David. A Maskil.",
    33: None,  # No superscript
    34: "Of David, when he changed his behavior before Abimelech, so that he drove him out, and he went away.",
    35: "Of David.",
    36: "To the choirmaster. Of David, the servant of the LORD.",
    37: "Of David.",
    38: "A Psalm of David, for the memorial offering.",
    39: "To the choirmaster: to Jeduthun. A Psalm of David.",
    40: "To the choirmaster. Of David. A Psalm.",
    41: "To the choirmaster. A Psalm of David.",
    42: "To the choirmaster. A Maskil of the Sons of Korah.",
    43: None,  # No superscript (continuation of Psalm 42)
    44: "To the choirmaster. Of the Sons of Korah. A Maskil.",
    45: "To the choirmaster: according to Lilies. Of the Sons of Korah. A Maskil. A love song.",
    46: "To the choirmaster. Of the Sons of Korah. According to Alamoth. A Song.",
    47: "To the choirmaster. Of the Sons of Korah. A Psalm.",
    48: "A Song. A Psalm of the Sons of Korah.",
    49: "To the choirmaster. Of the Sons of Korah. A Psalm.",
    50: "A Psalm of Asaph.",
    51: "To the choirmaster. A Psalm of David, when Nathan the prophet went to him, after he had gone in to Bathsheba.",
    52: "To the choirmaster. A Maskil of David, when Doeg, the Edomite, came and told Saul, \"David has come to the house of Ahimelech.\"",
    53: "To the choirmaster: according to Mahalath. A Maskil of David.",
    54: "To the choirmaster: with stringed instruments. A Maskil of David, when the Ziphites went and told Saul, \"Is not David hiding among us?\"",
    55: "To the choirmaster: with stringed instruments. A Maskil of David.",
    56: "To the choirmaster: according to The Dove on Far-off Terebinths. Of David. A Miktam, when the Philistines seized him in Gath.",
    57: "To the choirmaster: according to Do Not Destroy. Of David. A Miktam, when he fled from Saul, in the cave.",
    58: "To the choirmaster: according to Do Not Destroy. Of David. A Miktam.",
    59: "To the choirmaster: according to Do Not Destroy. Of David. A Miktam, when Saul sent men to watch his house in order to kill him.",
    60: "To the choirmaster: according to Shushan Eduth. A Miktam of David; for instruction; when he strove with Aram-naharaim and with Aram-zobah, and when Joab on his return struck down twelve thousand of Edom in the Valley of Salt.",
    61: "To the choirmaster: with stringed instruments. Of David.",
    62: "To the choirmaster: according to Jeduthun. A Psalm of David.",
    63: "A Psalm of David, when he was in the wilderness of Judah.",
    64: "To the choirmaster. A Psalm of David.",
    65: "To the choirmaster. A Psalm of David. A Song.",
    66: "To the choirmaster. A Song. A Psalm.",
    67: "To the choirmaster: with stringed instruments. A Psalm. A Song.",
    68: "To the choirmaster. A Psalm of David. A Song.",
    69: "To the choirmaster: according to Lilies. Of David.",
    70: "To the choirmaster. Of David, for the memorial offering.",
    71: None,  # No superscript
    72: "Of Solomon.",
    73: "A Psalm of Asaph.",
    74: "A Maskil of Asaph.",
    75: "To the choirmaster: according to Do Not Destroy. A Psalm of Asaph. A Song.",
    76: "To the choirmaster: with stringed instruments. A Psalm of Asaph. A Song.",
    77: "To the choirmaster: according to Jeduthun. Of Asaph. A Psalm.",
    78: "A Maskil of Asaph.",
    79: "A Psalm of Asaph.",
    80: "To the choirmaster: according to Lilies. A Testimony of Asaph. A Psalm.",
    81: "To the choirmaster: according to The Gittith. Of Asaph.",
    82: "A Psalm of Asaph.",
    83: "A Song. A Psalm of Asaph.",
    84: "To the choirmaster: according to The Gittith. Of the Sons of Korah. A Psalm.",
    85: "To the choirmaster. Of the Sons of Korah. A Psalm.",
    86: "A Prayer of David.",
    87: "Of the Sons of Korah. A Psalm. A Song.",
    88: "A Song. A Psalm of the Sons of Korah. To the choirmaster: according to Mahalath Leannoth. A Maskil of Heman the Ezrahite.",
    89: "A Maskil of Ethan the Ezrahite.",
    90: "A Prayer of Moses, the man of God.",
    91: None,  # No superscript
    92: "A Psalm. A Song for the Sabbath.",
    93: None,  # No superscript
    94: None,  # No superscript
    95: None,  # No superscript
    96: None,  # No superscript
    97: None,  # No superscript
    98: "A Psalm.",
    99: None,  # No superscript
    100: "A Psalm for giving thanks.",
    101: "Of David. A Psalm.",
    102: "A Prayer of one afflicted, when he is faint and pours out his complaint before the LORD.",
    103: "Of David.",
    104: None,  # No superscript
    105: None,  # No superscript
    106: None,  # No superscript
    107: None,  # No superscript
    108: "A Song. A Psalm of David.",
    109: "To the choirmaster. Of David. A Psalm.",
    110: "Of David. A Psalm.",
    111: None,  # No superscript
    112: None,  # No superscript
    113: None,  # No superscript
    114: None,  # No superscript
    115: None,  # No superscript
    116: None,  # No superscript
    117: None,  # No superscript
    118: None,  # No superscript
    119: None,  # No superscript
    120: "A Song of Ascents.",
    121: "A Song of Ascents.",
    122: "A Song of Ascents. Of David.",
    123: "A Song of Ascents.",
    124: "A Song of Ascents. Of David.",
    125: "A Song of Ascents.",
    126: "A Song of Ascents.",
    127: "A Song of Ascents. Of Solomon.",
    128: "A Song of Ascents.",
    129: "A Song of Ascents.",
    130: "A Song of Ascents.",
    131: "A Song of Ascents. Of David.",
    132: "A Song of Ascents.",
    133: "A Song of Ascents. Of David.",
    134: "A Song of Ascents.",
    135: None,  # No superscript
    136: None,  # No superscript
    137: None,  # No superscript
    138: "Of David.",
    139: "To the choirmaster. Of David. A Psalm.",
    140: "To the choirmaster. A Psalm of David.",
    141: "A Psalm of David.",
    142: "A Maskil of David, when he was in the cave. A Prayer.",
    143: "A Psalm of David.",
    144: "Of David.",
    145: "A Psalm of Praise. Of David.",
    146: None,  # No superscript
    147: None,  # No superscript
    148: None,  # No superscript
    149: None,  # No superscript
    150: None,  # No superscript
}

def get_psalm_superscript(psalm_number: int) -> str:
    """Get the superscript/inscription for a given psalm number"""
    if not (1 <= psalm_number <= 150):
        return None
    return PSALM_SUPERSCRIPTS.get(psalm_number)

def has_superscript(psalm_number: int) -> bool:
    """Check if a psalm has a superscript"""
    return get_psalm_superscript(psalm_number) is not None

def get_superscripts_by_author(author: str) -> list:
    """Get all psalm numbers attributed to a specific author"""
    author_lower = author.lower()
    results = []
    
    for psalm_num, superscript in PSALM_SUPERSCRIPTS.items():
        if superscript and author_lower in superscript.lower():
            results.append(psalm_num)
    
    return results

def get_musical_term_psalms(term: str) -> list:
    """Get all psalms that contain a specific musical term"""
    term_lower = term.lower()
    results = []
    
    for psalm_num, superscript in PSALM_SUPERSCRIPTS.items():
        if superscript and term_lower in superscript.lower():
            results.append(psalm_num)
    
    return results

# Statistics
DAVID_PSALMS = get_superscripts_by_author("David")  # 73 psalms
ASAPH_PSALMS = get_superscripts_by_author("Asaph")  # 12 psalms
SONS_OF_KORAH_PSALMS = get_superscripts_by_author("Sons of Korah")  # 11 psalms
SONGS_OF_ASCENTS = get_musical_term_psalms("Song of Ascents")  # 15 psalms (120-134)