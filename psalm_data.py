from models import Psalm

# Sample Psalm data - In production, this would be populated from a complete database
PSALM_DATA = [
    {
        'number': 1,
        'title': 'The Way of the Righteous and the Wicked',
        'text_niv': '''Blessed is the one
    who does not walk in step with the wicked
or stand in the way that sinners take
    or sit in the company of mockers,
but whose delight is in the law of the Lord,
    and who meditates on his law day and night.
That person is like a tree planted by streams of water,
    which yields its fruit in season
and whose leaf does not wither—
    whatever they do prospers.

Not so the wicked!
    They are like chaff
    that the wind blows away.
Therefore the wicked will not stand in the judgment,
    nor sinners in the assembly of the righteous.

For the Lord watches over the way of the righteous,
    but the way of the wicked leads to destruction.''',
        'youtube_url': 'https://www.youtube.com/embed/j9phNEaPrv8',
        'prompt_1': 'What does it mean to "delight in the law of the Lord" in your daily life?',
        'prompt_2': 'How can you be more like a tree planted by streams of water?',
        'prompt_3': 'What are some ways you can meditate on God\'s word day and night?',
        'prompt_4': 'Ask God to show you areas where you might be walking with the wicked instead of the righteous.'
    },
    {
        'number': 23,
        'title': 'The Lord is My Shepherd',
        'text_niv': '''The Lord is my shepherd, I lack nothing.
    He makes me lie down in green pastures,
he leads me beside quiet waters,
    he refreshes my soul.
He guides me along the right paths
    for his name's sake.
Even though I walk
    through the darkest valley,
I will fear no evil,
    for you are with me;
your rod and your staff,
    they comfort me.

You prepare a table before me
    in the presence of my enemies.
You anoint my head with oil;
    my cup overflows.
Surely your goodness and love will follow me
    all the days of my life,
and I will dwell in the house of the Lord
    forever.''',
        'youtube_url': 'https://www.youtube.com/embed/e5dVeR4fv54',
        'prompt_1': 'In what ways has God been your shepherd recently?',
        'prompt_2': 'What "darkest valleys" are you walking through right now, and how can you trust God\'s presence?',
        'prompt_3': 'How has God\'s goodness and love followed you in your life?',
        'prompt_4': 'Pray and thank God for being your shepherd and ask Him to guide you today.'
    },
    {
        'number': 91,
        'title': 'Safe in the Shadow of the Almighty',
        'text_niv': '''Whoever dwells in the shelter of the Most High
    will rest in the shadow of the Almighty.
I will say of the Lord, "He is my refuge and my fortress,
    my God, in whom I trust."

Surely he will save you
    from the fowler's snare
    and from the deadly pestilence.
He will cover you with his feathers,
    and under his wings you will find refuge;
    his faithfulness will be your shield and rampart.
You will not fear the terror of night,
    nor the arrow that flies by day,
nor the pestilence that stalks in the darkness,
    nor the plague that destroys at midday.
A thousand may fall at your side,
    ten thousand at your right hand,
    but it will not come near you.
You will only observe with your eyes
    and see the punishment of the wicked.

If you say, "The Lord is my refuge,"
    and you make the Most High your dwelling,
no harm will overtake you,
    no disaster will come near your tent.
For he will command his angels concerning you
    to guard you in all your ways;
they will lift you up in their hands,
    so that you will not strike your foot against a stone.
You will tread on the lion and the cobra;
    you will trample the great lion and the serpent.

"Because he loves me," says the Lord, "I will rescue him;
    I will protect him, for he acknowledges my name.
He will call on me, and I will answer him;
    I will be with him in trouble,
    I will deliver him and honor him.
With long life I will satisfy him
    and show him my salvation."''',
        'youtube_url': 'https://www.youtube.com/embed/jhLuAgs1_7Y',
        'prompt_1': 'What does it mean to dwell in the shelter of the Most High in practical terms?',
        'prompt_2': 'What fears or anxieties can you surrender to God\'s protection today?',
        'prompt_3': 'How have you experienced God as your refuge and fortress?',
        'prompt_4': 'Pray and declare God\'s protection over your life and loved ones.'
    }
]

def initialize_psalms():
    """Initialize Supabase with sample Psalm data"""
    for psalm_data in PSALM_DATA:
        # Check if psalm already exists
        existing_psalm = Psalm.get_by_number(psalm_data['number'])
        if not existing_psalm:
            psalm = Psalm(
                psalm_number=psalm_data['number'],
                title=psalm_data['title'],
                text_niv=psalm_data['text_niv'],
                text_esv=psalm_data['text_niv'],  # Using NIV for all translations in this demo
                text_nlt=psalm_data['text_niv'],
                text_nkjv=psalm_data['text_niv'],
                text_nrsv=psalm_data['text_niv'],
                music_url=psalm_data['youtube_url'],
                prompt_1=psalm_data['prompt_1'],
                prompt_2=psalm_data['prompt_2'],
                prompt_3=psalm_data['prompt_3'],
                prompt_4=psalm_data['prompt_4']
            )
            result = psalm.save()
            if result:
                print(f"Successfully initialized Psalm {psalm_data['number']}")
            else:
                print(f"Failed to initialize Psalm {psalm_data['number']}")
    
    print("Psalm initialization complete")
