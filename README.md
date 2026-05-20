# AyahPath

**Qur'anic Life Guidance at Your Fingertips**

AyahPath is a modern web application that helps you navigate life's challenges with wisdom from the Qur'an. Whether you're facing stress, difficult decisions, or seeking spiritual growth, AyahPath connects you with relevant verses, prophetic wisdom, and practical spiritual guidance.

**Visit us:** [ayahpath.online](https://ayahpath.online)

---

## About the Project

AyahPath was built for the [Quran Hackathon](https://launch.provisioncapital.com/quran-hackathon), a prestigious competition to innovate Islamic technology solutions. The project combines Flask backend APIs with a modern vanilla JavaScript frontend to create a seamless, accessible experience for seeking Qur'anic guidance in everyday life.

### Hackathon Achievement

Built during the Quran Hackathon competition, AyahPath demonstrates:
- Respectful integration of Islamic texts with modern technology
- Accessible design for diverse audiences and abilities
- Smart categorization of Qur'anic wisdom for real-world scenarios
- Seamless offline-first architecture with local persistence
- Performance optimization for all devices and connection speeds

---

## Key Features

**Qur'anic Guidance**
- Daily and personalized ayah (verse) selections with Arabic text and multiple translations
- Audio recitations for every verse
- Life-scenario mapping (stress, anger, jealousy, gratitude, forgiveness, patience, charity, honesty, humility, trust)

**Prophetic Wisdom**
- Authentic Hadiths (sayings and actions of Prophet Muhammad ﷺ) integrated with every guidance
- Curated selections from Sahih Bukhari, Sahih Muslim, and other trusted collections
- Smart context-matching between verses and Hadiths

**Personal Tracking**
- Daily reflection journal with AI-powered category mapping
- Prayer completion tracker with streaks and weekly summaries
- Personal goals with progress tracking
- Activity history and insights

**Accessibility & Personalization**
- Multiple Qur'an translations (Urdu, English, French, Indonesian, Bengali, Turkish, Hindi)
- Customizable themes (Midnight, Light, Arabic Majlis, Quranic Emerald, Ramadan Lantern)
- Colorblind accessibility modes (Protanopia, Deuteranopia, Tritanopia)
- Adjustable text sizing for comfortable reading
- High-contrast mode for better readability

**Offline-First Architecture**
- Works completely offline after first load
- Local SQLite database for personal data
- Bundled Qur'an data (no external API required)
- Optional live API integration when available

---

## Tech Stack

**Backend**
- Python 3 with Flask framework
- Flask-CORS for secure cross-origin requests
- SQLite for reliable local persistence
- RESTful API design

**Frontend**
- Vanilla JavaScript (no frameworks)
- Responsive CSS with modern design patterns
- HTML5 semantic markup
- Progressive Web App capabilities

**External Integrations**
- Quran Foundation APIs (optional, graceful fallback)
- Hadith API for authentic Islamic texts
- OpenRouter AI (optional, with local fallback)

---

## How It Works

1. **Explore Scenarios** - Browse life situations and challenges
2. **Read Guidance** - Get relevant Qur'anic verses with tafsir (explanation)
3. **Discover Hadiths** - Learn from prophetic wisdom connected to your situation
4. **Personal Reflection** - Journal your thoughts and get AI-powered spiritual guidance
5. **Track Progress** - Build habits with daily check-ins and streak tracking
6. **Set Goals** - Define spiritual and personal growth objectives

---

## API Endpoints

### Scenarios & Guidance
```
GET  /api/scenarios              - List all life scenarios
GET  /api/scenarios/<id>         - Get detailed scenario with verses and hadiths
POST /api/reflections            - Submit a personal reflection
GET  /api/reflections/<user_id>  - Get saved reflections
```

### Daily Content
```
GET /api/daily-ayah              - Get ayah of the day
GET /api/personalized-ayah       - Get personalized verse recommendation
```

### Tracking
```
GET  /api/streak/<user_id>       - View current streak
POST /api/streak/<user_id>/checkin - Daily check-in
GET  /api/goals/<user_id>        - View goals
POST /api/goals                  - Create new goal
GET  /api/activity/<user_id>     - View activity log
```

### Qur'an & Prayer
```
GET /api/quran/chapters          - List all chapters
GET /api/quran/verse/<s>/<a>     - Get specific verse
GET /api/quran/tafsir/<s>/<a>    - Get verse interpretation
GET /api/prayers/<date>          - Get prayer log for date
POST /api/prayers/<date>/<id>    - Mark prayer as completed
GET /api/prayers/stats           - Prayer statistics
```

---

## Data Privacy

Your data stays with you:
- All reflections stored locally in your browser
- Prayer tracking saved in local database
- No analytics or user tracking
- Optional account features coming soon
- Secure HTTPS transmission
- No data sold or shared

---

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)
- Progressive Web App: Install as app on home screen

---

## Offline Capabilities

AyahPath works seamlessly offline:
- View all saved reflections and prayers
- Access bundled Qur'an data
- Update personal goals and streaks
- Automatic sync when connection returns
- No features disabled offline (except live API calls)

---

## Accessibility

Designed with inclusivity in mind:
- WCAG 2.1 AA compliance target
- Keyboard navigation support
- Screen reader friendly
- Colorblind modes
- Adjustable text sizing
- High contrast options
- Semantic HTML structure

---

## Language Support

Currently available in:
- English (Hilali & other translations)
- Urdu
- French
- Indonesian
- Bengali
- Turkish
- Hindi

More languages coming soon.

---

## Contributing

We welcome contributions! Areas where we'd love help:

- Adding new Qur'anic scenario categories
- Improving AI guidance algorithms
- Translating to additional languages
- Enhancing accessibility features
- Bug fixes and performance improvements
- UI/UX refinements

See the repository for technical details: [github.com/669px/AyahPath](https://github.com/669px/AyahPath)

---

## Security & Safety

- All data transmitted over HTTPS
- Strong input validation and sanitization
- Rate limiting on API endpoints
- CORS protection
- No external scripts loaded
- Open source for community audit

---

## Qur'an & Hadith Sources

**Qur'an Translations:**
- Multiple trusted English translations
- Original Arabic text
- Regional translations (Urdu, Bengali, etc.)
- Audio recitations from renowned Qaris

**Hadiths:**
- Sahih Bukhari
- Sahih Muslim
- Jami' al-Tirmidhi
- Sunan Abu Dawood
- Only authenticated (Sahih/Hasan) Hadiths included

---

## License

This project is open source. See LICENSE file in the repository for details.

---

## Support & Feedback

Have questions or suggestions? We'd love to hear from you:

- Visit [ayahpath.online](https://ayahpath.online)
- Check the FAQ section in the app
- Report issues on GitHub
- Share your story of how AyahPath helped you

---

## Acknowledgments

- Built for the [Quran Hackathon](https://launch.provisioncapital.com/quran-hackathon)
- Qur'an data from Quran.com and Quran Foundation
- Hadith data from Hadith API
- Inspired by the need for accessible Islamic guidance in digital age
- Thanks to all contributors and community members

---

**AyahPath — Guided by the Words of Allah ﷻ**

*"Indeed, in the Qur'an there is guidance and good news for the believers." (Qur'an 2:97)*
