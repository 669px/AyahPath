# models/mappings.py

# Comprehensive scenario mappings with full metadata
SCENARIO_MAPPINGS = {
    "lying": {
        "title": "Lying",
        "icon": "lying",
        "description": "The weight of dishonesty on the soul and its worldly consequences",
        "ayahs": [
            {"surah": 9, "ayah": 119, "context": "Be with the truthful"},
            {"surah": 2, "ayah": 10, "context": "Lying brings disease to the heart"},
            {"surah": 16, "ayah": 105, "context": "Those who fabricate lies"},
        ],
        "category": "character"
    },
    "patience": {
        "title": "Patience",
        "icon": "patience",
        "description": "Finding strength in steadfastness through trials and tribulations",
        "ayahs": [
            {"surah": 2, "ayah": 153, "context": "Allah is with the patient"},
            {"surah": 39, "ayah": 10, "context": "The patient will be given reward without measure"},
            {"surah": 94, "ayah": 5, "context": "With hardship comes ease"},
        ],
        "category": "virtue"
    },
    "anger": {
        "title": "Anger",
        "icon": "anger",
        "description": "Controlling rage and choosing mercy over wrath",
        "ayahs": [
            {"surah": 3, "ayah": 134, "context": "Those who restrain anger and pardon people"},
            {"surah": 42, "ayah": 37, "context": "Those who avoid sins and forgive when angry"},
            {"surah": 41, "ayah": 34, "context": "Repel evil with that which is better"},
        ],
        "category": "emotion"
    },
    "charity": {
        "title": "Charity",
        "icon": "charity",
        "description": "The purifying power of giving and its eternal rewards",
        "ayahs": [
            {"surah": 2, "ayah": 261, "context": "Those who spend in the way of Allah"},
            {"surah": 2, "ayah": 274, "context": "Those who spend by night and day"},
            {"surah": 57, "ayah": 18, "context": "Charity will be multiplied"},
        ],
        "category": "action"
    },
    "forgiveness": {
        "title": "Forgiveness",
        "icon": "forgiveness",
        "description": "Releasing the burden of grudges and embracing divine mercy",
        "ayahs": [
            {"surah": 24, "ayah": 22, "context": "Let them pardon and forgive"},
            {"surah": 42, "ayah": 40, "context": "Whoever pardons and makes reconciliation"},
            {"surah": 3, "ayah": 159, "context": "Pardon them and ask forgiveness for them"},
        ],
        "category": "virtue"
    },
    "gratitude": {
        "title": "Gratitude",
        "icon": "gratitude",
        "description": "Recognizing blessings and the promise of increase through thankfulness",
        "ayahs": [
            {"surah": 14, "ayah": 7, "context": "If you are grateful, I will increase you"},
            {"surah": 31, "ayah": 12, "context": "Be grateful to Allah"},
            {"surah": 2, "ayah": 152, "context": "Remember Me, I will remember you"},
        ],
        "category": "virtue"
    },
    "trust_in_allah": {
        "title": "Trust in Allah",
        "icon": "trust",
        "description": "Surrendering outcomes to the Divine and finding peace in tawakkul",
        "ayahs": [
            {"surah": 65, "ayah": 3, "context": "Whoever puts their trust in Allah, He is sufficient"},
            {"surah": 3, "ayah": 159, "context": "When you have decided, put your trust in Allah"},
            {"surah": 8, "ayah": 2, "context": "Upon Allah let the believers put their trust"},
        ],
        "category": "faith"
    },
    "jealousy": {
        "title": "Jealousy",
        "icon": "jealousy",
        "description": "Overcoming envy and being content with Allah's decree",
        "ayahs": [
            {"surah": 113, "ayah": 5, "context": "From the evil of the envier when they envy"},
            {"surah": 4, "ayah": 32, "context": "Do not wish for what Allah has favored others with"},
            {"surah": 20, "ayah": 131, "context": "Do not extend your eyes toward worldly enjoyment"},
        ],
        "category": "emotion"
    },
    "stress": {
        "title": "Stress & Anxiety",
        "icon": "stress",
        "description": "Finding tranquility in remembrance and divine reassurance",
        "ayahs": [
            {"surah": 13, "ayah": 28, "context": "In the remembrance of Allah do hearts find rest"},
            {"surah": 94, "ayah": 6, "context": "Indeed, with hardship comes ease"},
            {"surah": 2, "ayah": 286, "context": "Allah does not burden a soul beyond capacity"},
        ],
        "category": "emotion"
    },
    "arrogance": {
        "title": "Arrogance",
        "icon": "arrogance",
        "description": "The danger of pride and the virtue of humility before Allah",
        "ayahs": [
            {"surah": 31, "ayah": 18, "context": "Do not turn your cheek in scorn toward people"},
            {"surah": 17, "ayah": 37, "context": "Do not walk on earth with insolence"},
            {"surah": 4, "ayah": 36, "context": "Allah does not love the arrogant"},
        ],
        "category": "character"
    },
}

# Daily ayahs for consistent daily reminders
DAILY_AYAHS = [
    {"surah": 2, "ayah": 152}, {"surah": 2, "ayah": 186}, {"surah": 3, "ayah": 139},
    {"surah": 13, "ayah": 28}, {"surah": 94, "ayah": 5}, {"surah": 93, "ayah": 5},
    {"surah": 2, "ayah": 286}, {"surah": 65, "ayah": 3}, {"surah": 14, "ayah": 7},
    {"surah": 39, "ayah": 53}, {"surah": 29, "ayah": 69}, {"surah": 73, "ayah": 8},
    {"surah": 33, "ayah": 56}, {"surah": 49, "ayah": 13}, {"surah": 55, "ayah": 60},
    {"surah": 16, "ayah": 97}, {"surah": 3, "ayah": 173}, {"surah": 9, "ayah": 51},
    {"surah": 67, "ayah": 2}, {"surah": 5, "ayah": 8}, {"surah": 40, "ayah": 60},
    {"surah": 57, "ayah": 4}, {"surah": 10, "ayah": 62}, {"surah": 4, "ayah": 135},
    {"surah": 23, "ayah": 1}, {"surah": 25, "ayah": 63}, {"surah": 51, "ayah": 56},
    {"surah": 96, "ayah": 1}, {"surah": 112, "ayah": 1}, {"surah": 1, "ayah": 1},
    {"surah": 36, "ayah": 58},
]

# Counter for every ayah across the Quran
AYAH_COUNTS = [
    7, 286, 200, 176, 120, 165, 206, 75, 129, 109,
    123, 111, 43, 52, 99, 128, 111, 110, 98, 135,
    112, 78, 118, 64, 77, 227, 93, 88, 69, 60,
    34, 30, 73, 54, 45, 83, 182, 88, 75, 85,
    54, 53, 89, 59, 37, 35, 38, 29, 18, 45,
    60, 49, 62, 55, 78, 96, 29, 22, 24, 13,
    14, 11, 11, 18, 12, 12, 30, 52, 52, 44,
    28, 28, 20, 56, 40, 31, 50, 40, 46, 42,
    29, 19, 36, 25, 22, 17, 19, 26, 30, 20,
    15, 21, 11, 8, 8, 19, 5, 8, 8, 11,
    11, 8, 3, 9, 5, 4, 7, 3, 6, 3,
    5, 4, 5, 6
]

# Curated YouTube videos by scenario
YOUTUBE_VIDEOS = {
    "lying": [
        {"id": "nKBo_nHe4Lk", "title": "The Weight of Lying — Nouman Ali Khan", "channel": "Bayyinah Official"},
        {"id": "sSMFuEsATbk", "title": "Why We Must Stop Lying — Islamic Reminder", "channel": "MercifulServant"},
    ],
    "patience": [
        {"id": "k09NfXCS-8M", "title": "Beautiful Patience (Sabr) — Nouman Ali Khan", "channel": "Bayyinah Official"},
        {"id": "BJ0XnFfGz68", "title": "The Reward of Patience — Islamic Reminder", "channel": "MercifulServant"},
    ],
    "anger": [
        {"id": "Ow3Bv7JKXWU", "title": "Controlling Your Anger — Nouman Ali Khan", "channel": "Bayyinah Official"},
        {"id": "3KjPQSnd6Vc", "title": "Prophetic Advice on Controlling Anger", "channel": "One Islam Productions"},
    ],
    "charity": [
        {"id": "y8K0lBEgOJo", "title": "The Power of Giving — Nouman Ali Khan", "channel": "Bayyinah Official"},
        {"id": "K5kAsxxrGeM", "title": "The Virtue of Giving Charity", "channel": "MercifulServant"},
    ],
    "forgiveness": [
        {"id": "vu1hcPWbp6Q", "title": "The Beauty of Forgiveness — Nouman Ali Khan", "channel": "Bayyinah Official"},
        {"id": "6TksMPnXYqU", "title": "Forgive Others for Allah's Sake", "channel": "One Islam Productions"},
    ],
    "gratitude": [
        {"id": "V8ETq07M3Dw", "title": "Being Grateful to Allah — Nouman Ali Khan", "channel": "Bayyinah Official"},
        {"id": "M3LMNKCgszA", "title": "Gratitude and Happiness in Islam", "channel": "Towards Eternity"},
    ],
    "trust_in_allah": [
        {"id": "9h2GkS1dN_4", "title": "Trust Allah's Plan — Nouman Ali Khan", "channel": "Bayyinah Official"},
        {"id": "NkNEH8s0tsE", "title": "Tawakkul: Concept of Trust in Allah", "channel": "MercifulServant"},
    ],
    "jealousy": [
        {"id": "PoEFqXNkiDg", "title": "Jealousy and Envy — Nouman Ali Khan", "channel": "Bayyinah Official"},
        {"id": "P35J9EPCk7A", "title": "Overcoming Jealousy in Islam", "channel": "One Islam Productions"},
    ],
    "stress": [
        {"id": "vI3BnWuqVGo", "title": "Anxiety and Worry — Nouman Ali Khan", "channel": "Bayyinah Official"},
        {"id": "oxN2UoOn9WM", "title": "Stress Relief Through Remembrance", "channel": "MercifulServant"},
    ],
    "arrogance": [
        {"id": "Y8b5hCxiN2c", "title": "The Danger of Arrogance — Nouman Ali Khan", "channel": "Bayyinah Official"},
        {"id": "2K9LnqfRjSU", "title": "Humility vs Pride in Islam", "channel": "Towards Eternity"},
    ],
    "_default": [
        {"id": "k09NfXCS-8M", "title": "Finding Peace Through the Qur'an", "channel": "Bayyinah Official"},
        {"id": "BJ0XnFfGz68", "title": "The Beauty of Islam", "channel": "MercifulServant"},
    ]
}

def get_all_categories():
    return list(SCENARIO_MAPPINGS.keys())

def get_scenario(scenario_id):
    return SCENARIO_MAPPINGS.get(scenario_id)

def get_daily_ayahs():
    return DAILY_AYAHS

def get_youtube_videos(scenario_id):
    return YOUTUBE_VIDEOS.get(scenario_id, YOUTUBE_VIDEOS.get("_default", []))
