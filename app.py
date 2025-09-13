from flask import Flask, render_template, request, jsonify
from google import genai
import json
import os
#from google_trans_new import google_translator

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Initialize Gemini API client
client = genai.Client(api_key="AIzaSyC8Jpsr36NM-YEQjLR9sIg3-EYaCskLQJs")

# Initialize translator
#translator = google_translator()

from googletrans import Translator

# Initialize translator
translator = Translator()

# Museum data configuration
MUSEUM_DATA ={
    "name": "Indian Museum, Archaeological Section",
    "location": "Calcutta, India",
    "hours": {
        "Tuesday-Friday": "10:00 AM - 6:00 PM",
        "Saturday-Sunday": "10:00 AM - 8:00 PM",
        "Monday": "Closed"
    },
    "ticket_prices": {
        "Adults": "₹500",
        "Children (5-12 years)": "₹200",
        "Students": "₹250",
        "Seniors (65+)": "₹250",
        "Free admission": "Children under 5"
    },
    "facilities": {
        "restrooms": {
            "main_floor": "Near the main entrance",
            "first_floor": "Next to the sculpture gallery",
            "second_floor": "Beside the cafe"
        },
        "cafe": {
            "location": "Second floor, west wing",
            "hours": "11:00 AM - 5:00 PM"
        },
        "gift_shop": {
            "location": "Ground floor, near exit",
            "hours": "10:00 AM - 6:00 PM"
        },
        "library": {
            "location": "First floor, east wing",
            "hours": "11:00 AM - 4:00 PM",
            "reference": "732.44 Maj"
        }
    },
    "galleries": {
        "entrance_hall": {
            "floor": "Ground floor",
            "description": "Contains Maurya and Sunga sculptures including Asokan pillars and Yaksha statues",
            "highlights": ["Cast of Sarnath Lion Capital (N.S. 3596)", "Rampurwa Lion Capital (6298-6299)", "Rampurwa Bull Capital (6297)", "Patna Yaksha Statues (P.1, P.2)", "Besnagar Yakshi Statue (1790-1797)", "Besnagar Kalpadruma (1795)"],
            "artistic_analysis": {
                "asokan_art_characteristics": ["Strength and massiveness", "High polish", "Realistic modeling", "Anatomical treatment"],
                "influences": ["Persian (bell-shaped capitals, animal figures back to back, polish)", "Hellenistic (realistic modeling of animals)", "Indigenous (free-standing conception, cable moulding)"],
                "materials": ["Chunar sandstone"],
                "interpretation": "According to R. Chanda, Imperial art of Asoka is synthesis of Indian, Persian and Hellenistic arts"
            }
        },
        "bharhut_gallery": {
            "floor": "First floor",
            "description": "Collection of red sandstone sculpture from Bharhut Stupa, a village in Nagod State, Central India",
            "highlights": ["Bharhut Gateway", "Yaksha and Yakshi figures", "Jataka tale reliefs", "Buddha life scenes", "Inscribed railings"],
            "architecture": {
                "stupa_design": "Similar plan and design to Great Stupa of Sanchi",
                "railing": {
                    "height": "About 9 feet",
                    "composition": "Pillars (stambha) rectangular in section, joined by lenticular cross-bars (suchi), with coping-stones (ushnisha)",
                    "purpose": "Enclosed the stupa with circumambulatory passage (pradakshina-patha)"
                },
                "gateway": {
                    "height": "22.5 feet",
                    "composition": "Two pillars with shafts moulded into four octagonal parts, lotus-shaped bell-capitals crowned by four animals (lions and bulls), supporting superstructure of three curviform architraves",
                    "surviving": "Only Eastern Gateway has survived",
                    "design_influence": "Strongly suggests copying from wooden prototypes"
                }
            },
            "life_size_figures": [
                {
                    "type": "Yakshas",
                    "examples": [
                        {"id": "199", "name": "Gangita", "posture": "Standing on elephant, hands folded"},
                        {"id": "141", "name": "Suchiloma", "posture": "Standing on railing, hands folded"},
                        {"id": "197", "name": "Virudhaka", "posture": "Standing on rocks, hands folded (guardian of Southern Quarter)"},
                        {"id": "105", "name": "Kubera", "posture": "Standing on squatting human figure, hands folded"}
                    ]
                },
                {
                    "type": "Yakshis",
                    "examples": [
                        {"id": "62", "name": "Chulakoka", "posture": "Holding bough of tree, standing on elephant"},
                        {"id": "141", "name": "Sirima", "posture": "Standing on railing"},
                        {"id": "106", "name": "Chandra", "posture": "Holding bough of tree, standing on horse-headed makara"}
                    ]
                }
            ],
            "artistic_analysis": {
                "production_context": "Different parts erected from subscriptions by various donors, executed by artisans of different grades",
                "characteristics": ["Frontality", "Dependence on 'memory picture'", "Condensed narration", "Lack of perspective", "Equal height figures regardless of distance", "Limited expression of human feelings"],
                "comparison_with_mauryan_art": "Lacks vigor and animation of Mauryan examples, crude animal figures",
                "positive_qualities": ["Charming simplicity", "Decorative beauty", "Sincere attempt to portray nature"],
                "composition_techniques": ["Continuous narration", "Figures in single plane (columnar array or horizontal row)", "Repetition of main figures at intervals", "Larger size for important figures"]
            }
        },
        "miscellaneous_sculptures": {
            "floor": "Second floor",
            "description": "Sculptures from various sites including Sanchi, Buddha-Gaya, Patna, Rajgir, Udayagiri Caves, and Sarnath",
            "subsections": {
                "sanchi": {
                    "description": "Casts of reliefs from Sanchi stupas in Bhopal State, Central India",
                    "dating": {
                        "Stupa II": "Latter part of 2nd century BCE (slightly earlier than Bharhut)",
                        "Stupa I Gateways": "1st century BCE (Andhra kings period)"
                    },
                    "highlights": ["S.1: Dedication of a stupa", "S.13: Offering of honey to Buddha", "S.12: Sanchi Bracket Figure"]
                },
                "buddha_gaya": {
                    "description": "Reconstructed railing from Buddha-Gaya in Gaya District, Bihar",
                    "dating": "Not earlier than 1st century BCE, some parts as late as 300-600 AD",
                    "highlights": ["Medallion with three elephants bringing garlands", "Yakshi clinging to tree", "Corner pillar with eight panels"]
                },
                "patna_rajgir": {
                    "description": "Sculptures from Rajgir (ancient Rajagriha) and Kumrahar (ancient Pataliputra)",
                    "dating": "2nd century BCE",
                    "highlights": ["N.S.3: Serpent-hood from Rajgir", "5582: Griffin from Kumrahar", "5006-5007: Wooden Beams from Pataliputra"]
                },
                "udayagiri": {
                    "description": "Rock-cut caves near Bhuvanesvar in Puri District, residence of Jaina monks",
                    "dating": "1st century BCE",
                    "highlights": ["Rani Nur Cave friezes", "Sarpa Cave serpent hood", "Ganesa Cave battle scene"]
                },
                "sarnath": {
                    "description": "Fragments of sculpture and architectural pieces from Sarnath",
                    "highlights": ["9433-9499: Fragments of abacus with Mauryan polish", "9495: Fragment of female figure in grey speckled sandstone"]
                }
            }
        }
    },
    "tours": {
        "guided_tours": {
            "schedule": "11:00 AM and 2:00 PM daily",
            "duration": "90 minutes",
            "meeting_point": "Information desk",
            "focus": "Highlights of Mauryan and Sunga sculpture, Bharhut Stupa remains"
        },
        "self_guided_tours": {
            "themes": ["Asokan Art", "Bharhut Narrative Reliefs", "Early Buddhist Symbolism", "Yaksha and Yakshi Cult Figures"]
        }
    },
    "publications": {
        "guidebook": {
            "title": "A Guide to the Sculptures in the Indian Museum",
            "subtitle": "Part I: Early Indian Schools",
            "author": "N. G. Majumdar, M.A., F.R.A.S.B.",
            "author_title": "Superintendent, Indian Museum, Archaeological Section",
            "publication_year": 1937,
            "publisher": "Manager of Publications, Delhi",
            "library_reference": "732.44 Maj",
            "catalog_number": "14275",
            "total_pages": 148,
            "availability": "Available at museum gift shop"
        }
    },
    "research_resources": {
        "library": {
            "location": "First floor, east wing",
            "hours": "11:00 AM - 4:00 PM",
            "collections": ["Archaeological reports", "Art historical texts", "Epigraphic studies", "Photographic archives"]
        },
        "access_policy": "Research access by appointment only, contact curator for details"
    }
}

# All 22 official languages of India with their codes and display names
LANGUAGES = {
    'en': 'English',
    'hi': 'हिन्दी (Hindi)',
    'bn': 'বাংলা (Bengali)',
    'ta': 'தமிழ் (Tamil)',
    'te': 'తెలుగు (Telugu)',
    'mr': 'मराठी (Marathi)',
    'gu': 'ગુજરાતી (Gujarati)',
    'kn': 'ಕನ್ನಡ (Kannada)',
    'ml': 'മലയാളം (Malayalam)',
    'pa': 'ਪੰਜਾਬੀ (Punjabi)',
    'or': 'ଓଡ଼ିଆ (Odia)',
    'as': 'অসমীয়া (Assamese)',
    'ur': 'اردو (Urdu)',
    'ne': 'नेपाली (Nepali)',
    'sd': 'सिन्धी (Sindhi)',
    'sa': 'संस्कृतम् (Sanskrit)',
    'ks': 'कश्मीरी (Kashmiri)',
    'kok': 'कोंकणी (Konkani)',
    'doi': 'डोगरी (Dogri)',
    'mni': 'মৈতৈলোন্ (Manipuri)',
    'sat': 'संथाली (Santali)',
    'brx': 'बोडो (Bodo)',
    'mai': 'मैथिली (Maithili)'
}

# UI translations for all 22 languages
UI_TRANSLATIONS = {
    'en': {
        'welcome': 'Welcome to Museum Guide',
        'ask_question': 'Ask a Question',
        'question_placeholder': 'Type your question here...',
        'ask_button': 'Ask',
        'plan_trip': 'Plan a Personalized Trip',
        'interests': 'Your Interests (e.g., history, art, science)',
        'time_available': 'Time Available (e.g., 1 hour, half-day)',
        'with_kids': 'With Kids? (yes/no)',
        'generate_plan': 'Generate Plan',
        'museum_info': 'Museum Information',
        'change_language': 'Change Language',
        'answer': 'Answer',
        'your_plan': 'Your Personalized Plan',
        'hours': 'Hours',
        'tickets': 'Tickets',
        'facilities': 'Facilities',
        'galleries': 'Galleries',
        'tours': 'Tours',
        'quick_questions': 'Quick Questions',
        'ask_about': 'Ask about:',
        'question1': 'Where are the restrooms?',
        'question2': 'What are the ticket prices?',
        'question3': 'Where is the cafe?',
        'question4': 'What are the opening hours?',
        'question5': 'Are guided tours available?'
    },
    'hi': {
        'welcome': 'संग्रहालय गाइड में आपका स्वागत है',
        'ask_question': 'प्रश्न पूछें',
        'question_placeholder': 'अपना प्रश्न यहाँ टाइप करें...',
        'ask_button': 'पूछें',
        'plan_trip': 'व्यक्तिगत यात्रा की योजना बनाएं',
        'interests': 'आपकी रुचियाँ (जैसे, इतिहास, कला, विज्ञान)',
        'time_available': 'उपलब्ध समय (जैसे, 1 घंटा, आधा दिन)',
        'with_kids': 'क्या बच्चों के साथ आ रहे हैं? (हाँ/नहीं)',
        'generate_plan': 'योजना बनाएं',
        'museum_info': 'संग्रहालय जानकारी',
        'change_language': 'भाषा बदलें',
        'answer': 'उत्तर',
        'your_plan': 'आपकी व्यक्तिगत योजना',
        'hours': 'समय',
        'tickets': 'टिकट',
        'facilities': 'सुविधाएं',
        'galleries': 'गैलरी',
        'tours': 'यात्राएं',
        'quick_questions': 'त्वरित प्रश्न',
        'ask_about': 'इसके बारे में पूछें:',
        'question1': 'शौचालय कहाँ हैं?',
        'question2': 'टिकट की कीमतें क्या हैं?',
        'question3': 'कैफे कहाँ है?',
        'question4': 'खुलने का समय क्या है?',
        'question5': 'क्या निर्देशित यात्राएं उपलब्ध हैं?'
    },
    'bn': {
        'welcome': 'জাদুঘর গাইডে স্বাগতম',
        'ask_question': 'একটি প্রশ্ন জিজ্ঞাসা করুন',
        'question_placeholder': 'আপনার প্রশ্ন এখানে টাইপ করুন...',
        'ask_button': 'জিজ্ঞাসা করুন',
        'plan_trip': 'ব্যক্তিগতকৃত ট্রিপ প্ল্যান করুন',
        'interests': 'আপনার আগ্রহ (যেমন, ইতিহাস, শিল্প, বিজ্ঞান)',
        'time_available': 'সময় উপলব্ধ (যেমন, 1 ঘন্টা, অর্ধ-দিন)',
        'with_kids': 'বাচ্চাদের সাথে আসছেন? (হ্যাঁ/না)',
        'generate_plan': 'পরিকল্পনা তৈরি করুন',
        'museum_info': 'জাদুঘর তথ্য',
        'change_language': 'ভাষা পরিবর্তন করুন',
        'answer': 'উত্তর',
        'your_plan': 'আপনার ব্যক্তিগতকৃত পরিকল্পনা',
        'hours': 'ঘন্টা',
        'tickets': 'টিকেট',
        'facilities': 'সুবিধা',
        'galleries': 'গ্যালারি',
        'tours': 'ট্যুর',
        'quick_questions': 'দ্রুত প্রশ্ন',
        'ask_about': 'এটি সম্পর্কে জিজ্ঞাসা করুন:',
        'question1': 'টয়লেট কোথায়?',
        'question2': 'টিকেটের দাম কত?',
        'question3': 'ক্যাফে কোথায়?',
        'question4': 'খোলার সময় কি?',
        'question5': 'নির্দেশিত সফর উপলব্ধ?'
    },
    'ta': {
        'welcome': 'அருங்காட்சியக வழிகாட்டிக்கு வரவேற்கிறோம்',
        'ask_question': 'ஒரு கேள்வி கேட்க',
        'question_placeholder': 'உங்கள் கேள்வியை இங்கே தட்டச்சு செய்யவும்...',
        'ask_button': 'கேளுங்கள்',
        'plan_trip': 'தனிப்பயனாக்கப்பட்ட பயணத்தைத் திட்டமிடுங்கள்',
        'interests': 'உங்கள் ஆர்வங்கள் (எ.கா., வரலாறு, கலை, அறிவியல்)',
        'time_available': 'கிடைக்கும் நேரம் (எ.கா., 1 மணி நேரம், அரை நாள்)',
        'with_kids': 'குழந்தைகளுடன் வருகிறீர்களா? (ஆம்/இல்லை)',
        'generate_plan': 'திட்டத்தை உருவாக்கு',
        'museum_info': 'அருங்காட்சியக தகவல்',
        'change_language': 'மொழியை மாற்று',
        'answer': 'பதில்',
        'your_plan': 'உங்கள் தனிப்பயனாக்கப்பட்ட திட்டம்',
        'hours': 'நேரங்கள்',
        'tickets': 'டிக்கெட்டுகள்',
        'facilities': 'வசதிகள்',
        'galleries': 'காட்சியகங்கள்',
        'tours': 'சுற்றுப்பயணங்கள்',
        'quick_questions': 'விரைவான கேள்விகள்',
        'ask_about': 'இதைப் பற்றி கேளுங்கள்:',
        'question1': 'கழிப்பறைகள் எங்கே உள்ளன?',
        'question2': 'டிக்கெட் விலைகள் என்ன?',
        'question3': 'கஃபே எங்கே உள்ளது?',
        'question4': 'திறப்பு நேரம் என்ன?',
        'question5': 'வழிகாட்டப்பட்ட சுற்றுப்பயணங்கள் உள்ளனவா?'
    },
    'te': {
        'welcome': 'మ్యూజియం గైడ్ కు స్వాగతం',
        'ask_question': 'ఒక ప్రశ్న అడగండి',
        'question_placeholder': 'మీ ప్రశ్నను ఇక్కడ టైప్ చేయండి...',
        'ask_button': 'అడగండి',
        'plan_trip': 'వ్యక్తిగతీకరించిన ట్రిప్ ప్లాన్ చేయండి',
        'interests': 'మీ ఆసక్తులు (ఉదా., చరిత్ర, కళ, సైన్స్)',
        'time_available': 'అందుబాటులో ఉన్న సమయం (ఉదా., 1 గంట, అర్ధ-రోజు)',
        'with_kids': 'పిల్లలతో వస్తున్నారా? (అవును/కాదు)',
        'generate_plan': 'ప్లాన్ జనరేట్ చేయండి',
        'museum_info': 'మ్యూజియం సమాచారం',
        'change_language': 'భాష మార్చు',
        'answer': 'సమాధానం',
        'your_plan': 'మీ వ్యక్తిగతీకరించిన ప్రణాళిక',
        'hours': 'గంటలు',
        'tickets': 'టిక్కెట్లు',
        'facilities': 'సదుపాయాలు',
        'galleries': 'గ్యాలరీలు',
        'tours': 'పర్యటనలు',
        'quick_questions': 'త్వరిత ప్రశ్నలు',
        'ask_about': 'దీని గురించి అడగండి:',
        'question1': 'శౌచాలయాలు ఎక్కడ ఉన్నాయి?',
        'question2': 'టిక్కెట్ ధరలు ఎంత?',
        'question3': 'కాఫే ఎక్కడ ఉంది?',
        'question4': 'తెరవే సమయాలు ఏమిటి?',
        'question5': 'మార్గదర్శక పర్యటనలు ఉన్నాయా?'
    },
    'mr': {
        'welcome': 'म्युझियम मार्गदर्शकात आपले स्वागत आहे',
        'ask_question': 'एक प्रश्न विचारा',
        'question_placeholder': 'आपला प्रश्न येथे टाइप करा...',
        'ask_button': 'विचारा',
        'plan_trip': 'वैयक्तिकृत सहलची योजना करा',
        'interests': 'तुमच्या आवडी (उदा., इतिहास, कला, विज्ञान)',
        'time_available': 'उपलब्ध वेळ (उदा., 1 तास, अर्धा दिवस)',
        'with_kids': 'मुलांसोबत येत आहात? (होय/नाही)',
        'generate_plan': 'योजना तयार करा',
        'museum_info': 'म्युझियम माहिती',
        'change_language': 'भाषा बदला',
        'answer': 'उत्तर',
        'your_plan': 'तुमची वैयक्तिकृत योजना',
        'hours': 'वेळ',
        'tickets': 'तिकिटे',
        'facilities': 'सुविधा',
        'galleries': 'गॅलरी',
        'tours': 'सहली',
        'quick_questions': 'द्रुत प्रश्न',
        'ask_about': 'याबद्दल विचारा:',
        'question1': 'शौचालये कुठे आहेत?',
        'question2': 'तिकिट किंमती काय आहेत?',
        'question3': 'कॅफे कुठे आहे?',
        'question4': 'उघडण्याचे वेळेचे काय आहे?',
        'question5': 'मार्गदर्शित सहली उपलब्ध आहेत का?'
    },
    'gu': {
        'welcome': 'મ્યુઝિયમ ગાઇડમાં આપનું સ્વાગત છે',
        'ask_question': 'એક પ્રશ્ન પૂછો',
        'question_placeholder': 'તમારો પ્રશ્ન અહીં ટાઇપ કરો...',
        'ask_button': 'પૂછો',
        'plan_trip': 'વ્યક્તિગત ટ્રિપની યોજના બનાવો',
        'interests': 'તમારી રુચિઓ (દા.ત., ઇતિહાસ, કલા, વિજ્ઞાન)',
        'time_available': 'ઉપલબ્ધ સમય (દા.ત., 1 કલાક, અડધો દિવસ)',
        'with_kids': 'બાળકો સાથે આવો છો? (હા/ના)',
        'generate_plan': 'યોજના જનરેટ કરો',
        'museum_info': 'મ્યુઝિયમ માહિતી',
        'change_language': 'ભાષા બદલો',
        'answer': 'જવાબ',
        'your_plan': 'તમારી વ્યક્તિગત યોજના',
        'hours': 'સમય',
        'tickets': 'ટિકિટ',
        'facilities': 'સુવિધાઓ',
        'galleries': 'ગેલેરીઓ',
        'tours': 'ટૂર',
        'quick_questions': 'ઝડપી પ્રશ્નો',
        'ask_about': 'આ વિશે પૂછો:',
        'question1': 'ટોયલેટ ક્યાં છે?',
        'question2': 'ટિકિટના ભાવ શું છે?',
        'question3': 'કેફે ક્યાં છે?',
        'question4': 'ખુલવાનો સમય શું છે?',
        'question5': 'માર્ગદર્શિત ટૂર ઉપલબ્ધ છે?'
    },
    'kn': {
        'welcome': 'ಮ್ಯೂಸಿಯಂ ಗೈಡ್ ಗೆ ಸುಸ್ವಾಗತ',
        'ask_question': 'ಒಂದು ಪ್ರಶ್ನೆ ಕೇಳಿ',
        'question_placeholder': 'ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಇಲ್ಲಿ ಟೈಪ್ ಮಾಡಿ...',
        'ask_button': 'ಕೇಳಿ',
        'plan_trip': 'ವೈಯಕ್ತಿಕರಿಸಿದ ಪ್ರವಾಸದ ಯೋಜನೆ ಮಾಡಿ',
        'interests': 'ನಿಮ್ಮ ಆಸಕ್ತಿಗಳು (ಉದಾ., ಇತಿಹಾಸ, ಕಲೆ, ವಿಜ್ಞಾನ)',
        'time_available': 'ಲಭ್ಯವಿರುವ ಸಮಯ (ಉದಾ., 1 ಗಂಟೆ, ಅರ್ಧ ದಿನ)',
        'with_kids': 'ಮಕ್ಕಳೊಂದಿಗೆ ಬರುವಿರಾ? (ಹೌದು/ಇಲ್ಲ)',
        'generate_plan': 'ಯೋಜನೆಯನ್ನು ರಚಿಸಿ',
        'museum_info': 'ಮ್ಯೂಸಿಯಂ ಮಾಹಿತಿ',
        'change_language': 'ಭಾಷೆ ಬದಲಾಯಿಸಿ',
        'answer': 'ಉತ್ತರ',
        'your_plan': 'ನಿಮ್ಮ ವೈಯಕ್ತಿಕರಿಸಿದ ಯೋಜನೆ',
        'hours': 'ಸಮಯ',
        'tickets': 'ಟಿಕೆಟ್ ಗಳು',
        'facilities': 'ಸೌಲಭ್ಯಗಳು',
        'galleries': 'ಗ್ಯಾಲರಿಗಳು',
        'tours': 'ಪ್ರವಾಸಗಳು',
        'quick_questions': 'ತ್ವರಿತ ಪ್ರಶ್ನೆಗಳು',
        'ask_about': 'ಇದರ ಬಗ್ಗೆ ಕೇಳಿ:',
        'question1': 'ಶೌಚಾಲಯಗಳು ಎಲ್ಲಿವೆ?',
        'question2': 'ಟಿಕೆಟ್ ದರಗಳು ಏನು?',
        'question3': 'ಕೆಫೆ ಎಲ್ಲಿದೆ?',
        'question4': 'ತೆರೆಯುವ ಸಮಯ ಏನು?',
        'question5': 'ಮಾರ್ಗದರ್ಶಿತ ಪ್ರವಾಸಗಳು ಲಭ್ಯವಿದೆಯೇ?'
    },
    'ml': {
        'welcome': 'മ്യൂസിയം ഗൈഡിലേക്ക് സ്വാഗതം',
        'ask_question': 'ഒരു ചോദ്യം ചോദിക്കുക',
        'question_placeholder': 'നിങ്ങളുടെ ചോദ്യം ഇവിടെ ടൈപ്പ് ചെയ്യുക...',
        'ask_button': 'ചോദിക്കുക',
        'plan_trip': 'വ്യക്തിഗതമായ ട്രിപ്പ് പ്ലാൻ ചെയ്യുക',
        'interests': 'നിങ്ങളുടെ താൽപ്പര്യങ്ങൾ (ഉദാ., ചരിത്രം, കല, ശാസ്ത്രം)',
        'time_available': 'ലഭ്യമായ സമയം (ഉദാ., 1 മണിക്കൂർ, അര ദിവസം)',
        'with_kids': 'കുട്ടികളോടൊപ്പം വരുന്നുണ്ടോ? (അതെ/ഇല്ല)',
        'generate_plan': 'പ്ലാൻ സൃഷ്ടിക്കുക',
        'museum_info': 'മ്യൂസിയം വിവരം',
        'change_language': 'ഭാഷ മാറ്റുക',
        'answer': 'ഉത്തരം',
        'your_plan': 'നിങ്ങളുടെ വ്യക്തിഗത പ്ലാൻ',
        'hours': 'സമയം',
        'tickets': 'ടിക്കറ്റുകൾ',
        'facilities': 'സൗകര്യങ്ങൾ',
        'galleries': 'ഗാലറികൾ',
        'tours': 'ടൂറുകൾ',
        'quick_questions': 'ദ്രുത ചോദ്യങ്ങൾ',
        'ask_about': 'ഇതിനെക്കുറിച്ച് ചോദിക്കുക:',
        'question1': 'ടോയ്ലറ്റുകൾ എവിടെയാണ്?',
        'question2': 'ടിക്കറ്റ് വിലകൾ എന്താണ്?',
        'question3': 'കഫേ എവിടെയാണ്?',
        'question4': 'തുറക്കുന്ന സമയം എന്താണ്?',
        'question5': 'വിദഗ്ദ്ധ ടൂറുകൾ ലഭ്യമാണോ?'
    },
    'pa': {
        'welcome': 'ਮਿਊਜ਼ੀਅਮ ਗਾਈਡ ਵਿੱਚ ਜੀ ਆਇਆਂ ਨੂੰ',
        'ask_question': 'ਇੱਕ ਸਵਾਲ ਪੁੱਛੋ',
        'question_placeholder': 'ਆਪਣਾ ਸਵਾਲ ਇੱਥੇ ਟਾਈਪ ਕਰੋ...',
        'ask_button': 'ਪੁੱਛੋ',
        'plan_trip': 'ਵਿਅਕਤੀਗਤ ਯਾਤਰਾ ਦੀ ਯੋਜਨਾ ਬਣਾਓ',
        'interests': 'ਤੁਹਾਡੀ ਦਿਲਚਸਪੀ (ਜਿਵੇਂ, ਇਤਿਹਾਸ, ਕਲਾ, ਵਿਗਿਆਨ)',
        'time_available': 'ਉਪਲਬਧ ਸਮਾਂ (ਜਿਵੇਂ, 1 ਘੰਟਾ, ਅੱਧਾ ਦਿਨ)',
        'with_kids': 'ਬੱਚਿਆਂ ਨਾਲ ਆ ਰਹੇ ਹੋ? (ਹਾਂ/ਨਹੀਂ)',
        'generate_plan': 'ਯੋਜਨਾ ਬਣਾਓ',
        'museum_info': 'ਮਿਊਜ਼ੀਅਮ ਜਾਣਕਾਰੀ',
        'change_language': 'ਭਾਸ਼ਾ ਬਦਲੋ',
        'answer': 'ਜਵਾਬ',
        'your_plan': 'ਤੁਹਾਡੀ ਵਿਅਕਤੀਗਤ ਯੋਜਨਾ',
        'hours': 'ਸਮਾਂ',
        'tickets': 'ਟਿਕਟਾਂ',
        'facilities': 'ਸੁਵਿਧਾਵਾਂ',
        'galleries': 'ਗੈਲਰੀਆਂ',
        'tours': 'ਟੂਰ',
        'quick_questions': 'ਤੇਜ਼ ਸਵਾਲ',
        'ask_about': 'ਇਸ ਬਾਰੇ ਪੁੱਛੋ:',
        'question1': 'ਟਾਇਲਟ ਕਿੱਥੇ ਹਨ?',
        'question2': 'ਟਿਕਟ ਦੀਆਂ ਕੀਮਤਾਂ ਕੀ ਹਨ?',
        'question3': 'ਕੈਫੇ ਕਿੱਥੇ ਹੈ?',
        'question4': 'ਖੁੱਲ੍ਹਣ ਦੇ ਸਮੇਂ ਕੀ ਹਨ?',
        'question5': 'ਕੀ ਮਾਰਗਦਰਸ਼ਿਤ ਟੂਰ ਉਪਲਬਧ ਹਨ?'
    },
    'or': {
        'welcome': 'ମ୍ୟୁଜିଅମ ଗାଇଡକୁ ସ୍ୱାଗତ',
        'ask_question': 'ଏକ ପ୍ରଶ୍ନ ପଚାର',
        'question_placeholder': 'ଆପଣଙ୍କର ପ୍ରଶ୍ନ ଏଠାରେ ଟାଇପ୍ କରନ୍ତୁ...',
        'ask_button': 'ପଚାରନ୍ତୁ',
        'plan_trip': 'ବ୍ୟକ୍ତିଗତ ଯାତ୍ରା ଯୋଜନା କରନ୍ତୁ',
        'interests': 'ଆପଣଙ୍କର ଆଗ୍ରହ (ଯେପରିକି, ଇତିହାସ, କଳା, ବିଜ୍ଞାନ)',
        'time_available': 'ଉପଲବ୍ଧ ସମୟ (ଯେପରିକି, 1 ଘଣ୍ଟା, ଅଧା ଦିନ)',
        'with_kids': 'ପିଲାମାନଙ୍କ ସହିତ ଆସୁଛନ୍ତି କି? (ହଁ/ନା)',
        'generate_plan': 'ଯୋଜନା ତିଆରି କରନ୍ତୁ',
        'museum_info': 'ମ୍ୟୁଜିଅମ ସୂଚନା',
        'change_language': 'ଭାଷା ବଦଳାନ୍ତୁ',
        'answer': 'ଉତ୍ତର',
        'your_plan': 'ଆପଣଙ୍କର ବ୍ୟକ୍ତିଗତ ଯୋଜନା',
        'hours': 'ସମୟ',
        'tickets': 'ଟିକେଟ୍',
        'facilities': 'ସୁବିଧା',
        'galleries': 'ଗ୍ୟାଲେରୀ',
        'tours': 'ଭ୍ରମଣ',
        'quick_questions': 'ଦ୍ରୁତ ପ୍ରଶ୍ନ',
        'ask_about': 'ଏହା ବିଷୟରେ ପଚାରନ୍ତୁ:',
        'question1': 'ଶୌଚାଳୟ କୁଆଡେ?',
        'question2': 'ଟିକେଟ୍ ମୂଲ୍ୟ କେତେ?',
        'question3': 'କାଫେ କୁଆଡେ?',
        'question4': 'ଖୋଲିବାର ସମୟ କଣ?',
        'question5': 'ମାର୍ଗଦର୍ଶିତ ଭ୍ରମଣ ଉପଲବ୍ଧ କି?'
    },
    'as': {
        'welcome': 'সংগ্ৰহালয় গাইডলৈ স্বাগতম',
        'ask_question': 'এটা প্ৰশ্ন সোধক',
        'question_placeholder': 'আপোনাৰ প্ৰশ্ন ইয়াত টাইপ কৰক...',
        'ask_button': 'সোধক',
        'plan_trip': 'ব্যক্তিগত ভ্ৰমণৰ পৰিকল্পনা কৰক',
        'interests': 'আপোনাৰ আগ্রহ (যেনে, ইতিহাস, কলা, বিজ্ঞান)',
        'time_available': 'উপলব্ধ সময় (যেনে, 1 ঘণ্টা, আধা দিন)',
        'with_kids': 'লৰা-ছোৱালীৰ সৈতে আহিছে নেকি? (হয়/নহয়)',
        'generate_plan': 'পৰিকল্পনা সৃষ্টি কৰক',
        'museum_info': 'সংগ্ৰহালয়ৰ তথ্য',
        'change_language': 'ভাষা সলনি কৰক',
        'answer': 'উত্তৰ',
        'your_plan': 'আপোনাৰ ব্যক্তিগত পৰিকল্পনা',
        'hours': 'সময়',
        'tickets': 'টিকট',
        'facilities': 'সুবিধা',
        'galleries': 'গেলেৰী',
        'tours': 'ভ্ৰমণ',
        'quick_questions': 'দ্রুত প্ৰশ্ন',
        'ask_about': 'এই বিষয়ে সোধক:',
        'question1': 'পায়খানা কʼত আছে?',
        'question2': 'টিকটৰ দাম কিমান?',
        'question3': 'কেফে কʼত আছে?',
        'question4': 'খোলাৰ সময় কি?',
        'question5': 'পৰিদৰ্শন উপলব্ধ নেকি?'
    },
    'ur': {
        'welcome': 'میوزیم گائیڈ میں خوش آمدید',
        'ask_question': 'ایک سوال پوچھیں',
        'question_placeholder': 'اپنا سوال یہاں ٹائپ کریں...',
        'ask_button': 'پوچھیں',
        'plan_trip': 'ذاتی نوعیت کا سفر کی منصوبہ بندی کریں',
        'interests': 'آپ کی دلچسپیاں (مثلاً، تاریخ، فن، سائنس)',
        'time_available': 'دستیاب وقت (مثلاً، 1 گھنٹہ، آدھا دن)',
        'with_kids': 'بچوں کے ساتھ آ رہے ہیں؟ (ہاں/نہیں)',
        'generate_plan': 'منصوبہ بنائیں',
        'museum_info': 'میوزیم کی معلومات',
        'change_language': 'زبان تبدیل کریں',
        'answer': 'جواب',
        'your_plan': 'آپ کا ذاتی منصوبہ',
        'hours': 'اوقات',
        'tickets': 'ٹکٹ',
        'facilities': 'سہولیات',
        'galleries': 'گیلریاں',
        'tours': 'ٹورز',
        'quick_questions': 'فوری سوالات',
        'ask_about': 'اس کے بارے میں پوچھیں:',
        'question1': 'بیت الخلا کہاں ہیں؟',
        'question2': 'ٹکٹ کی قیمتیں کیا ہیں؟',
        'question3': 'کیفے کہاں ہے؟',
        'question4': 'کھلنے کے اوقات کیا ہیں؟',
        'question5': 'کیا ہدایت کردہ دورے دستیاب ہیں؟'
    },
    'ne': {
        'welcome': 'संग्रहालय गाइडमा स्वागत छ',
        'ask_question': 'एक प्रश्न सोध्नुहोस्',
        'question_placeholder': 'आफ्नो प्रश्न यहाँ टाइप गर्नुहोस्...',
        'ask_button': 'सोध्नुहोस्',
        'plan_trip': 'व्यक्तिगत यात्राको योजना बनाउनुहोस्',
        'interests': 'तपाईंको रुचिहरू (जस्तै, इतिहास, कला, विज्ञान)',
        'time_available': 'उपलब्ध समय (जस्तै, 1 घण्टा, आधा दिन)',
        'with_kids': 'बच्चाहरूसँग आउँदै हुनुहुन्छ? (हो/होइन)',
        'generate_plan': 'योजना सिर्जना गर्नुहोस्',
        'museum_info': 'संग्रहालय जानकारी',
        'change_language': 'भाषा परिवर्तन गर्नुहोस्',
        'answer': 'उत्तर',
        'your_plan': 'तपाईंको व्यक्तिगत योजना',
        'hours': 'समय',
        'tickets': 'टिकट',
        'facilities': 'सुविधाहरू',
        'galleries': 'ग्यालरीहरू',
        'tours': 'यात्राहरू',
        'quick_questions': 'द्रुत प्रश्नहरू',
        'ask_about': 'यसको बारेमा सोध्नुहोस्:',
        'question1': 'शौचालय कहाँ छन्?',
        'question2': 'टिकटको मूल्य के हो?',
        'question3': 'कफे कहाँ छ?',
        'question4': 'खुल्ने समय के हो?',
        'question5': 'निर्देशित भ्रमणहरू उपलब्ध छन्?'
    },
    'sd': {
        'welcome': 'عجائب گھر گائيڊ ۾ خوشآمديد',
        'ask_question': 'هڪ سوال پڇو',
        'question_placeholder': 'پنهنجو سوال هتي ٽائيپ ڪريو...',
        'ask_button': 'پڇو',
        'plan_trip': 'ذاتي سفر جي منصوبابندي ڪريو',
        'interests': 'توهان جي دلچسپيون (جهڙوڪ، تاريخ، فن، سائنس)',
        'time_available': 'دستياب وقت (جهڙوڪ، 1 ڪلاڪ، اڌ ڏينهن)',
        'with_kids': 'ٻارن سان ايندا آهيو؟ (ها / نه)',
        'generate_plan': 'منصوبو ٺاهيو',
        'museum_info': 'عجائب گھر جي معلومات',
        'change_language': 'ٻولي تبديل ڪريو',
        'answer': 'جواب',
        'your_plan': 'توهان جو ذاتي منصوبو',
        'hours': 'وقت',
        'tickets': 'ٽڪيٽ',
        'facilities': 'سھولتون',
        'galleries': 'گئلرين',
        'tours': 'دورا',
        'quick_questions': 'فوري سوال',
        'ask_about': 'هن بابت پڇو:',
        'question1': 'ٽوائليٽ ڪٿي آهن؟',
        'question2': 'ٽڪيٽ جي قيمتون ڪهڙيون آهن؟',
        'question3': 'ڪيفي ڪٿي آهي؟',
        'question4': 'کولڻ جو وقت ڪهڙو آهي؟',
        'question5': 'رهنمائي ڪيل دورا دستياب آهن؟'
    },
    'sa': {
        'welcome': 'संग्रहालयमार्गदर्शके स्वागतम्',
        'ask_question': 'प्रश्नं पृच्छतु',
        'question_placeholder': 'भवतः प्रश्नम् अत्र टाइप् कुरुत...',
        'ask_button': 'पृच्छतु',
        'plan_trip': 'व्यक्तिगतयात्रायोजनां कुरुत',
        'interests': 'भवतः रुचयः (यथा, इतिहासः, कला, विज्ञानम्)',
        'time_available': 'उपलब्धः समयः (यथा, 1 घण्टा, अर्धदिनम्)',
        'with_kids': 'बालकैः सह आगच्छति वा? (आम्/न)',
        'generate_plan': 'योजनां निर्माणं कुरुत',
        'museum_info': 'संग्रहालयसूचना',
        'change_language': 'भाषां परिवर्तयतु',
        'answer': 'उत्तरम्',
        'your_plan': 'भवतः व्यक्तिगतयोजना',
        'hours': 'समयाः',
        'tickets': 'टिकटानि',
        'facilities': 'सुविधाः',
        'galleries': 'प्रदर्शन्यः',
        'tours': 'पर्यटनानि',
        'quick_questions': 'द्रुतप्रश्नाः',
        'ask_about': 'अस्य विषये पृच्छतु:',
        'question1': 'शौचालयाः कुत्र सन्ति?',
        'question2': 'टिकटमूल्यानि कानि?',
        'question3': 'काफेः कुत्र अस्ति?',
        'question4': 'उद्घाटनसमयः कः?',
        'question5': 'मार्गदर्शितपर्यटनानि उपलब्धानि सन्ति वा?'
    },
    'ks': {
        'welcome': 'میوزیم گائیڈ وچ خوش آمدید',
        'ask_question': 'ہک سوال پُچھو',
        'question_placeholder': 'اپݨا سوال اتھ ٹائپ کرو...',
        'ask_button': 'پُچھو',
        'plan_trip': 'ذاتی سفر دی منصوبہ بندی کرو',
        'interests': 'تہاݙیاں دلچسپیاں (جیویں، تاریخ، فن، سائنس)',
        'time_available': 'دستیاب وقت (جیویں، 1 گھنٹہ، آدھا ݙینہ)',
        'with_kids': 'ٻالاں نال آندے پئے ہو؟ (ہاں/کو)',
        'generate_plan': 'منصوبہ بݨاؤ',
        'museum_info': 'میوزیم دی معلومات',
        'change_language': 'زبان بدلو',
        'answer': 'جواب',
        'your_plan': 'تہاݙا ذاتی منصوبہ',
        'hours': 'وقت',
        'tickets': 'ٹکٹ',
        'facilities': 'سہولتاں',
        'galleries': 'گیلریاں',
        'tours': 'دورے',
        'quick_questions': 'فوری سوال',
        'ask_about': 'ایں بارے پُچھو:',
        'question1': 'ٹوائلیٹ کتھاں ہن؟',
        'question2': 'ٹکٹ دیاں قیمتاں کیہڑیاں ہن؟',
        'question3': 'کیفے کتھاں ہے؟',
        'question4': 'کھلݨ دا وقت کیہڑا ہے؟',
        'question5': 'کیا رہنمائی شدہ دورے دستیاب ہن؟'
    },
    'kok': {
        'welcome': 'संग्रहालय मार्गदर्शकाक स्वागत',
        'ask_question': 'एक प्रस्न विचार',
        'question_placeholder': 'तुजो प्रस्न हांगा टायप कर...',
        'ask_button': 'विचार',
        'plan_trip': 'वैयक्तिक भोंवणीची योजना कर',
        'interests': 'तुजे आवडी (देखील, इतिहास, कला, विज्ञान)',
        'time_available': 'उपलब्ध वेळ (देखील, 1 तास, अर्दे दीस)',
        'with_kids': 'भुरग्यांसयत येता? (हय/ना)',
        'generate_plan': 'योजना तयार कर',
        'museum_info': 'संग्रहालय म्हायती',
        'change_language': 'भास बदल',
        'answer': 'उत्तर',
        'your_plan': 'तुजी वैयक्तिक योजना',
        'hours': 'वेळ',
        'tickets': 'तिकीट',
        'facilities': 'सुविधा',
        'galleries': 'गॅलरी',
        'tours': 'टूर',
        'quick_questions': 'त्वरित प्रस्न',
        'ask_about': 'हाचे विशीं विचार:',
        'question1': 'शौचालय खंय आसात?',
        'question2': 'तिकीट किंमत कितें?',
        'question3': 'कॅफे खंय आसा?',
        'question4': 'उक्त्या वेळ कितें?',
        'question5': 'मार्गदर्शीत टूर उपलब्ध आसात?'
    },
    'doi': {
        'welcome': 'म्यूजियम गाइड में स्वागत है',
        'ask_question': 'एक सवाल पूछो',
        'question_placeholder': 'अपना सवाल यहाँ टाइप करो...',
        'ask_button': 'पूछो',
        'plan_trip': 'निजी यात्रा की योजना बनाओ',
        'interests': 'तुम्हारी रुचियाँ (जैसे, इतिहास, कला, विज्ञान)',
        'time_available': 'उपलब्ध समय (जैसे, 1 घंटा, आधा दिन)',
        'with_kids': 'बच्चों के साथ आ रहे हो? (हाँ/ना)',
        'generate_plan': 'योजना बनाओ',
        'museum_info': 'म्यूजियम जानकारी',
        'change_language': 'भाषा बदलो',
        'answer': 'जवाब',
        'your_plan': 'तुम्हारी निजी योजना',
        'hours': 'समय',
        'tickets': 'टिकट',
        'facilities': 'सुविधाएँ',
        'galleries': 'गैलरी',
        'tours': 'यात्राएँ',
        'quick_questions': 'जल्दी सवाल',
        'ask_about': 'इस बारे में पूछो:',
        'question1': 'टॉयलेट कहाँ हैं?',
        'question2': 'टिकट की कीमतें क्या हैं?',
        'question3': 'कैफे कहाँ है?',
        'question4': 'खुलने का समय क्या है?',
        'question5': 'क्या गाइडेड टूर उपलब्ध हैं?'
    },
    'mni': {
        'welcome': 'মুজিয়াম গাইডগা লৌসিল্লিবা',
        'ask_question': 'মপানী অহুম লৌরিবা',
        'question_placeholder': 'নমংপা অহুমদা ইয়াইত টাইপ লৌরিবা...',
        'ask_button': 'লৌরিবা',
        'plan_trip': 'নিজিনা সক্নীগী য়ুম্জাও লৌরিবা',
        'interests': 'নমংপা মমাং (যথা, পুখং, শৈরেং, বিজ্ঞান)',
        'time_available': 'লম্দবা ওই (যথা, 1 ঘণ্টা, নুমিৎ নুমিৎ)',
        'with_kids': 'চাপ চাবা লৌদুনা? (হোই/নত্তে)',
        'generate_plan': 'য়ুম্জাও সাজাও',
        'museum_info': 'মুজিয়াম খ্বাই',
        'change_language': 'লোল্ ত্না লৌবা',
        'answer': 'খ্বাই',
        'your_plan': 'নমংপা নিজিনা য়ুম্জাও',
        'hours': 'ওই',
        'tickets': 'টিকেট',
        'facilities': 'সুবিদা',
        'galleries': 'গ্যালারী',
        'tours': 'সক্নী',
        'quick_questions': 'চৎনবা অহুম',
        'ask_about': 'মদুগী মমাং লৌরিবা:',
        'question1': 'শৌচালয় কদা ওইরিবা?',
        'question2': 'টিকেটগী মৌনৎফম করি?',
        'question3': 'ক্যাফে কদা ওইরিবা?',
        'question4': 'খল্লবগী ওই করি?',
        'question5': 'দেসল্লিবা সক্নী লম্দবা ওইরিবা?'
    },
    'sat': {
        'welcome': 'ᱢᱤᱭᱩᱡᱤᱭᱟᱢ ᱜᱟᱭᱰ ᱨᱮ ᱥᱟᱣᱟᱜᱟᱞ',
        'ask_question': 'ᱢᱤᱫᱴᱟᱝ ᱥᱚᱢᱥᱚ ᱢᱮᱱᱟᱣ',
        'question_placeholder': 'ᱟᱢᱟᱜ ᱥᱚᱢᱥᱚ ᱱᱚᱸᱰᱮ ᱚᱞᱚᱜ ᱢᱮ...',
        'ask_button': 'ᱢᱮᱱᱟᱣ',
        'plan_trip': 'ᱱᱤᱡᱚᱨ ᱥᱯᱷᱟᱨ ᱮᱢᱟᱱ ᱛᱮᱭᱟᱨ ᱢᱮ',
        'interests': 'ᱟᱢᱟᱜ ᱨᱩᱪᱤ (ᱡᱮᱞᱮᱠᱟ, ᱱᱟᱜᱟᱢ, ᱠᱟᱞᱟ, ᱵᱤᱜᱽᱭᱟᱱ)',
        'time_available': 'ᱩᱯᱞᱚᱵᱽ ᱚᱠᱛᱚ (ᱡᱮᱞᱮᱠᱟ, 1 ᱴᱟᱲᱟᱝ, ᱟᱰᱮᱼᱵᱷᱟᱜᱮ ᱢᱟᱦᱟ)',
        'with_kids': 'ᱜᱤᱫᱽᱨᱟᱹ ᱥᱟᱶ ᱦᱮᱡ ᱟᱠᱟᱱᱟ ᱥᱮ? (ᱦᱚᱭ/ᱵᱟᱝ)',
        'generate_plan': 'ᱮᱢᱟᱱ ᱛᱮᱭᱟᱨ ᱢᱮ',
        'museum_info': 'ᱢᱤᱭᱩᱡᱤᱭᱟᱢ ᱵᱤᱵᱽᱨᱟᱱ',
        'change_language': 'ᱯᱟᱹᱨᱥᱤ ᱵᱚᱫᱚᱞ ᱢᱮ',
        'answer': 'ᱡᱚᱵᱟᱵᱽ',
        'your_plan': 'ᱟᱢᱟᱜ ᱱᱤᱡᱚᱨ ᱮᱢᱟᱱ',
        'hours': 'ᱴᱟᱲᱟᱝ',
        'tickets': 'ᱴᱤᱠᱮᱴ',
        'facilities': 'ᱥᱩᱵᱤᱫᱷᱟ',
        'galleries': 'ᱜᱮᱞᱟᱨᱤ',
        'tours': 'ᱥᱯᱷᱟᱨ',
        'quick_questions': 'ᱞᱚᱜᱚᱱ ᱥᱚᱢᱥᱚ',
        'ask_about': 'ᱱᱚᱣᱟ ᱵᱟᱵᱚᱫᱽ ᱢᱮᱱᱟᱣ:',
        'question1': 'ᱴᱚᱭᱞᱮᱴ ᱠᱚ ᱚᱠᱟ ᱨᱮ ᱢᱮᱱᱟᱜᱼᱟ?',
        'question2': 'ᱴᱤᱠᱮᱴ ᱨᱮᱭᱟᱜ ᱫᱟᱢ ᱠᱚ ᱪᱮᱫ ᱞᱮᱠᱟ?',
        'question3': 'ᱠᱮᱯᱷᱮ ᱚᱠᱟ ᱨᱮ ᱢᱮᱱᱟᱜᱼᱟ?',
        'question4': 'ᱡᱷᱤᱞᱚᱜ ᱚᱠᱛᱚ ᱪᱮᱫ ᱞᱮᱠᱟ?',
        'question5': 'ᱜᱟᱭᱰᱮᱰ ᱴᱩᱨ ᱠᱚ ᱩᱯᱞᱚᱵᱽ ᱢᱮᱱᱟᱜᱼᱟ ᱥᱮ?'
    },
    'brx': {
        'welcome': 'म्युजियम गाइडाव थांनाय',
        'ask_question': 'मोनसे सोंनाय सों',
        'question_placeholder': 'नोंसोर सोंनाया इयें टाइप खालाम...',
        'ask_button': 'सों',
        'plan_trip': 'गुसु आवगायनाय आबहावा साजाय',
        'interests': 'नोंसोरनि गोसो (जेरै, मुंखां, सोदोब, बिगियान)',
        'time_available': 'मोननाय सम (जेरै, 1 घन्टा, गुदि सान)',
        'with_kids': 'गोजौफोर लोगोआव फैदोंमा? (हां/ना)',
        'generate_plan': 'आबहावा साजाय',
        'museum_info': 'म्युजियम खौरां',
        'change_language': 'राव सोलाय',
        'answer': 'फिन',
        'your_plan': 'नोंसोरनि गुसु आबहावा',
        'hours': 'सम',
        'tickets': 'टिकेट',
        'facilities': 'सुबिदा',
        'galleries': 'ग्यालारि',
        'tours': 'आवगायनाय',
        'quick_questions': 'गोख्रै सोंनाय',
        'ask_about': 'बेयाव सों:',
        'question1': 'टयालेटफोरा बबे?',
        'question2': 'टिकेटनि बेंसिनफोरा मा?',
        'question3': 'क्याफेआ बबे?',
        'question4': 'खेलनाय समा मा?',
        'question5': 'गाइडेड टुरफोरा मोननायगोनना?'
    },
    'mai': {
        'welcome': 'संग्रहालय गाइडमे स्वागत छी',
        'ask_question': 'एकटा प्रश्न पूछू',
        'question_placeholder': 'अपन प्रश्न एतय टाइप करू...',
        'ask_button': 'पूछू',
        'plan_trip': 'व्यक्तिगत यात्रा योजना बनाउ',
        'interests': 'अहाँक रुचि (जहिना, इतिहास, कला, विज्ञान)',
        'time_available': 'उपलब्ध समय (जहिना, 1 घंटा, आधा दिन)',
        'with_kids': 'बच्चासँग आबि रहल छी? (हाँ/नहि)',
        'generate_plan': 'योजना बनाउ',
        'museum_info': 'संग्रहालय जानकारी',
        'change_language': 'भाषा बदलू',
        'answer': 'उत्तर',
        'your_plan': 'अहाँक व्यक्तिगत योजना',
        'hours': 'समय',
        'tickets': 'टिकट',
        'facilities': 'सुविधा',
        'galleries': 'ग्यालरी',
        'tours': 'यात्रा',
        'quick_questions': 'त्वरित प्रश्न',
        'ask_about': 'एकरा के बारेमे पूछू:',
        'question1': 'शौचालय कतय अछि?',
        'question2': 'टिकटक दाम की अछि?',
        'question3': 'कैफे कतय अछि?',
        'question4': 'खुललाक समय की अछि?',
        'question5': 'की गाइडेड टूर उपलब्ध अछि?'
    }
}

# Standard questions for quick access in all languages
STANDARD_QUESTIONS = {
    'en': [
        "Where are the restrooms?",
        "What are the ticket prices?",
        "Where is the cafe?",
        "What are the opening hours?",
        "Are guided tours available?",
        "Where is the ancient civilizations gallery?",
        "Do you have wheelchair accessibility?",
        "Where is the gift shop?",
        "Is photography allowed?",
        "Where can I find information about current exhibitions?"
    ],
    'hi': [
        "शौचालय कहाँ हैं?",
        "टिकट की कीमतें क्या हैं?",
        "कैफे कहाँ है?",
        "खुलने का समय क्या है?",
        "क्या निर्देशित यात्राएं उपलब्ध हैं?",
        "प्राचीन सभ्यताओं की गैलरी कहाँ है?",
        "क्या आपके पास व्हीलचेयर की सुविधा है?",
        "उपहार की दुकान कहाँ है?",
        "क्या फोटोग्राफी की अनुमति है?",
        "वर्तमान प्रदर्शनियों के बारे में जानकारी मैं कहाँ प्राप्त कर सकता हूँ?"
    ],
    'bn': [
        "টয়লেট কোথায়?",
        "টিকেটের দাম কত?",
        "ক্যাফে কোথায়?",
        "খোলার সময় কি?",
        "নির্দেশিত সফর উপলব্ধ?",
        "প্রাচীন সভ্যতার গ্যালারি কোথায়?",
        "আপনার হুইলচেয়ার অ্যাক্সেসযোগ্যতা আছে?",
        "উপহারের দোকান কোথায়?",
        "ফটোগ্রাফি অনুমোদিত?",
        "বর্তমান প্রদর্শনী সম্পর্কে তথ্য আমি কোথায় পেতে পারি?"
    ],
    'ta': [
        "கழிப்பறைகள் எங்கே உள்ளன?",
        "டிக்கெட் விலைகள் என்ன?",
        "கஃபே எங்கே உள்ளது?",
        "திறப்பு நேரம் என்ன?",
        "வழிகாட்டப்பட்ட சுற்றுப்பயணங்கள் உள்ளனவா?",
        "பண்டைய நாகரிகங்களின் காட்சியகம் எங்கே?",
        "நீங்கள் சக்கர நாற்காலி அணுகல் வசதி உள்ளதா?",
        "பரிசு கடை எங்கே?",
        "புகைப்படம் எடுக்க அனுமதி உள்ளதா?",
        "தற்போதைய கண்காட்சிகள் பற்றிய தகவல்களை நான் எங்கு பெற முடியும்?"
    ],
    'te': [
        "శౌచాలయాలు ఎక్కడ ఉన్నాయి?",
        "టిక్కెట్ ధరలు ఎంత?",
        "కాఫే ఎక్కడ ఉంది?",
        "తెరవే సమయాలు ఏమిటి?",
        "మార్గదర్శక పర్యటనలు ఉన్నాయా?",
        "ప్రాచిన నాగరికతల గ్యాలరీ ఎక్కడ ఉంది?",
        "మీకు వీల్చెయిర్ ప్రవేశం ఉందా?",
        "బహుమతి దుకాణం ఎక్కడ ఉంది?",
        "ఫోటోగ్రఫీ అనుమతించబడుతుందా?",
        "ప్రస్తుత ప్రదర్శనల గురించి సమాచారం నేను ఎక్కడ పొందగలను?"
    ],
    'mr': [
        "शौचालये कुठे आहेत?",
        "तिकिट किंमती काय आहेत?",
        "कॅफे कुठे आहे?",
        "उघडण्याचे वेळेचे काय आहे?",
        "मार्गदर्शित सहली उपलब्ध आहेत का?",
        "प्राचीन संस्कृती गॅलरी कुठे आहे?",
        "तुमच्याकडे व्हीलचेअर प्रवेश्यता आहे का?",
        "भेटवस्तू दुकान कुठे आहे?",
        "फोटोग्राफी परवानगी आहे का?",
        "वर्तमान प्रदर्शनांबद्दल माहिती मी कुठे मिळवू शकतो?"
    ],
    'gu': [
        "ટોયલેટ ક્યાં છે?",
        "ટિકિટના ભાવ શું છે?",
        "કેફે ક્યાં છે?",
        "ખુલવાનો સમય શું છે?",
        "માર્ગદર્શિત ટૂર ઉપલબ્ધ છે?",
        "પ્રાચીન સંસ્કૃતિ ગેલેરી ક્યાં છે?",
        "શું તમારી પાસે વ્હીલચેર એક્સેસિબિલિટી છે?",
        "ભેટ દુકાન ક્યાં છે?",
        "શું ફોટોગ્રાફી મંજૂર છે?",
        "વર્તમાન પ્રદર્શનો વિશે માહિતી હું ક્યાં મેળવી શકું?"
    ],
    'kn': [
        "ಶೌಚಾಲಯಗಳು ಎಲ್ಲಿವೆ?",
        "ಟಿಕೆಟ್ ದರಗಳು ಏನು?",
        "ಕೆಫೆ ಎಲ್ಲಿದೆ?",
        "ತೆರೆಯುವ ಸಮಯ ಏನು?",
        "ಮಾರ್ಗದರ್ಶಿತ ಪ್ರವಾಸಗಳು ಲಭ್ಯವಿದೆಯೇ?",
        "ಪ್ರಾಚೀನ ನಾಗರಿಕತೆಗಳ ಗ್ಯಾಲರಿ ಎಲ್ಲಿದೆ?",
        "ನಿಮಗೆ ವೀಲ್ಚೇರ್ ಪ್ರವೇಶವಿದೆಯೇ?",
        "ಉಪಹಾರದ ಅಂಗಡಿ ಎಲ್ಲಿದೆ?",
        "ಛಾಯಾಗ್ರಹಣಕ್ಕೆ ಅನುಮತಿ ಇದೆಯೇ?",
        "ಪ್ರಸ್ತುತ ಪ್ರದರ್ಶನಗಳ ಬಗ್ಗೆ ಮಾಹಿತಿ ನಾನು ಎಲ್ಲಿ ಪಡೆಯಬಹುದು?"
    ],
    'ml': [
        "ടോയ്ലറ്റുകൾ എവിടെയാണ്?",
        "ടിക്കറ്റ് വിലകൾ എന്താണ്?",
        "കഫേ എവിടെയാണ്?",
        "തുറക്കുന്ന സമയം എന്താണ്?",
        "വിദഗ്ദ്ധ ടൂറുകൾ ലഭ്യമാണോ?",
        "പുരാതന നാഗരികതകളുടെ ഗാലറി എവിടെയാണ്?",
        "നിങ്ങൾക്ക് വീൽചെയർ ആക്‌സസ്സിബിലിറ്റി ഉണ്ടോ?",
        "സമ്മാന കട എവിടെയാണ്?",
        "ഫോട്ടോഗ്രഫി അനുവദനീയമാണോ?",
        "നിലവിലെ പ്രദർശനങ്ങളെക്കുറിച്ചുള്ള വിവരങ്ങൾ എവിടെ നിന്ന് ലഭിക്കും?"
    ],
    'pa': [
        "ਟਾਇਲਟ ਕਿੱਥੇ ਹਨ?",
        "ਟਿਕਟ ਦੀਆਂ ਕੀਮਤਾਂ ਕੀ ਹਨ?",
        "ਕੈਫੇ ਕਿੱਥੇ ਹੈ?",
        "ਖੁੱਲ੍ਹਣ ਦੇ ਸਮੇਂ ਕੀ ਹਨ?",
        "ਕੀ ਮਾਰਗਦਰਸ਼ਿਤ ਟੂਰ ਉਪਲਬਧ ਹਨ?",
        "ਪ੍ਰਾਚੀਨ ਸਭਿਅਤਾਵਾਂ ਦੀ ਗੈਲਰੀ ਕਿੱਥੇ ਹੈ?",
        "ਕੀ ਤੁਹਾਡੇ ਕੋਲ ਵ੍ਹੀਲਚੇਅਰ ਪਹੁੰਚ ਹੈ?",
        "ਤੋਹਫ਼ੇ ਦੀ ਦੁਕਾਨ ਕਿੱਥੇ ਹੈ?",
        "ਕੀ ਫੋਟੋਗ੍ਰਾਫੀ ਦੀ ਇਜਾਜ਼ਤ ਹੈ?",
        "ਮੌਜੂਦਾ ਪ੍ਰਦਰਸ਼ਨੀਆਂ ਬਾਰੇ ਜਾਣਕਾਰੀ ਮੈਂ ਕਿੱਥੇ ਪ੍ਰਾਪਤ ਕਰ ਸਕਦਾ ਹਾਂ?"
    ],
    'or': [
        "ଶୌଚାଳୟ କୁଆଡେ?",
        "ଟିକେଟ୍ ମୂଲ୍ୟ କେତେ?",
        "କାଫେ କୁଆଡେ?",
        "ଖୋଲିବାର ସମୟ କଣ?",
        "ମାର୍ଗଦର୍ଶିତ ଭ୍ରମଣ ଉପଲବ୍ଧ କି?",
        "ପ୍ରାଚୀନ ସଭ୍ୟତାର ଗ୍ୟାଲେରୀ କୁଆଡେ?",
        "ଆପଣଙ୍କର ହ୍ୱିଲଚେୟାର ପ୍ରବେଶ୍ୟତା ଅଛି କି?",
        "ଉପହାର ଦୋକାନ କୁଆଡେ?",
        "ଫୋଟୋଗ୍ରାଫି ଅନୁମୋଦିତ କି?",
        "ବର୍ତ୍ତମାନର ପ୍ରଦର୍ଶନୀଗୁଡିକ ବିଷୟରେ ମୁଁ କୁଆଡେ ସୂଚନା ପାଇପାରିବି?"
    ],
    'as': [
        "পায়খানা কʼত আছে?",
        "টিকটৰ দাম কিমান?",
        "কেফে কʼত আছে?",
        "খোলাৰ সময় কি?",
        "পৰিদৰ্শন উপলব্ধ নেকি?",
        "প্ৰাচীন সভ্যতাৰ গেলেৰী কʼত আছে?",
        "আপোনাৰ হুইলচেয়াৰ প্ৰৱেশযোগ্যতা আছে নেকি?",
        "উপহাৰৰ দোকান কʼত আছে?",
        "ফটোগ্ৰাফী অনুমোদিত নেকি?",
        "বৰ্তমানৰ প্ৰদৰ্শনীসমূহৰ বিষয়ে তথ্য মই কʼত পাব পাৰো?"
    ],
    'ur': [
        "بیت الخلا کہاں ہیں؟",
        "ٹکٹ کی قیمتیں کیا ہیں؟",
        "کیفے کہاں ہے؟",
        "کھلنے کے اوقات کیا ہیں؟",
        "کیا ہدایت کردہ دورے دستیاب ہیں؟",
        "قدیم تہذیبوں کی گیلری کہاں ہے؟",
        "کیا آپ کے پاس وہیل چیئر رسائی ہے؟",
        "تحفے کی دکان کہاں ہے؟",
        "کیا فوٹوگرافی کی اجازت ہے؟",
        "موجودہ نمائشوں کے بارے میں معلومات میں کہاں سے حاصل کر سکتا ہوں؟"
    ],
    'ne': [
        "शौचालय कहाँ छन्?",
        "टिकटको मूल्य के हो?",
        "कफे कहाँ छ?",
        "खुल्ने समय के हो?",
        "निर्देशित भ्रमणहरू उपलब्ध छन्?",
        "प्राचीन सभ्यताहरूको ग्यालरी कहाँ छ?",
        "तपाईंसँग व्हीलचेयर पहुँच छ?",
        "उपहार पसल कहाँ छ?",
        "के फोटोग्राफी अनुमति छ?",
        "वर्तमान प्रदर्शनीहरूको बारेमा जानकारी म कहाँ पाउन सक्छु?"
    ],
    'sd': [
        "ٽوائليٽ ڪٿي آهن؟",
        "ٽڪيٽ جي قيمتون ڪهڙيون آهن؟",
        "ڪيفي ڪٿي آهي؟",
        "کولڻ جو وقت ڪهڙو آهي?",
        "رهنمائي ڪيل دورا دستياب آهن؟",
        "قديم تمدن جي گئلري ڪٿي آهي?",
        "ڇا توهان وٽ وھيل چيئر رسائي آهي؟",
        "تحفو جي دڪان ڪٿي آهي?",
        "ڇا فوٽوگرافي جي اجازت آهي؟",
        "موجودہ نمائشن بابت معلومات مون کي ڪٿي ملندي؟"
    ],
    'sa': [
        "शौचालयाः कुत्र सन्ति?",
        "टिकटमूल्यानि कानि?",
        "काफेः कुत्र अस्ति?",
        "उद्घाटनसमयः कः?",
        "मार्गदर्शितपर्यटनानि उपलब्धानि सन्ति वा?",
        "प्राचीनसभ्यतानां प्रदर्शनी कुत्र अस्ति?",
        "भवतः पार्श्वे कक्ष्ययानप्रवेशः अस्ति वा?",
        "उपहारदुकानं कुत्र अस्ति?",
        "किं छायाचित्रणं अनुमतम् अस्ति?",
        "वर्तमानप्रदर्शनीनां विषये जानकारीं कुत्र प्राप्नोमि?"
    ],
    'ks': [
        "ٹوائلیٹ کتھاں ہن؟",
        "ٹکٹ دیاں قیمتاں کیہڑیاں ہن؟",
        "کیفے کتھاں ہے؟",
        "کھلݨ دا وقت کیہڑا ہے؟",
        "کیا رہنمائی شدہ دورے دستیاب ہن؟",
        "قدیم تہذیباں دی گیلری کتھاں ہے؟",
        "کیا تہاݙے کول وھیل چیئر رسائی ہے؟",
        "تحفے دی دکان کتھاں ہے؟",
        "کیا فوٹوگرافی دی اجازت ہے؟",
        "موجودہ نمائشاں بارے معلومات میں کتھوں گھن سڳداں؟"
    ],
    'kok': [
        "शौचालय खंय आसात?",
        "तिकीट किंमत कितें?",
        "कॅफे खंय आसा?",
        "उक्त्या वेळ कितें?",
        "मार्गदर्शीत टूर उपलब्ध आसात?",
        "पुर्विल्ल्या संस्कृतायेची गॅलरी खंय आसा?",
        "तुजेकडेन व्हीलचेअर ऍक्सेस आसा?",
        "भेटवस्तूची दुकान खंय आसा?",
        "की फोटोग्राफीक अनुमती आसा?",
        "वर्तमान प्रदर्शनांविशीं म्हाका खंय म्हायती मेळटली?"
    ],
    'doi': [
        "टॉयलेट कहाँ हैं?",
        "टिकट की कीमतें क्या हैं?",
        "कैफे कहाँ है?",
        "खुलने का समय क्या है?",
        "क्या गाइडेड टूर उपलब्ध हैं?",
        "प्राचीन सभ्यताओं की गैलरी कहाँ है?",
        "क्या आपके पास व्हीलचेयर एक्सेस है?",
        "तोहफे की दुकान कहाँ है?",
        "क्या फोटोग्राफी की अनुमति है?",
        "मौजूदा प्रदर्शनियों के बारे में जानकारी मैं कहाँ से प्राप्त कर सकता हूँ?"
    ],
    'mni': [
        "শৌচালয় কদা ওইরিবা?",
        "টিকেটগী মৌনৎফম করি?",
        "ক্যাফে কদা ওইরিবা?",
        "খল্লবগী ওই করি?",
        "দেসল্লিবা সক্নী লম্দবা ওইরিবা?",
        "পুখংনা লাইরেম্বী গ্যালারী কদা ওইরিবা?",
        "নমংপা ওইনা হুইলচেয়ার এক্সেস ওইরিবা?",
        "চৎনী লম্জেং কদা ওইরিবা?",
        "কী ফটোগ্রাফী অনুমোদিত ওইরিবা?",
        "মমাং থবকশিংগী খ্বাই মমাং মাকোই কদা মনদুনা ওইরিবা?"
    ],
    'sat': [
        "ᱴᱚᱭᱞᱮᱴ ᱠᱚ ᱚᱠᱟ ᱨᱮ ᱢᱮᱱᱟᱜᱼᱟ?",
        "ᱴᱤᱠᱮᱴ ᱨᱮᱭᱟᱜ ᱫᱟᱢ ᱠᱚ ᱪᱮᱫ ᱞᱮᱠᱟ?",
        "ᱠᱮᱯᱷᱮ ᱚᱠᱟ ᱨᱮ ᱢᱮᱱᱟᱜᱼᱟ?",
        "ᱡᱷᱤᱞᱚᱜ ᱚᱠᱛᱚ ᱪᱮᱫ ᱞᱮᱠᱟ?",
        "ᱜᱟᱭᱰᱮᱰ ᱴᱩᱨ ᱠᱚ ᱩᱯᱞᱚᱵᱽ ᱢᱮᱱᱟᱜᱼᱟ ᱥᱮ?",
        "ᱯᱩᱨᱟᱺᱱ ᱥᱚᱵᱷᱮᱛᱟ ᱜᱮᱞᱟᱨᱤ ᱚᱠᱟ ᱨᱮ ᱢᱮᱱᱟᱜᱼᱟ?",
        "ᱟᱢ ᱴᱷᱮᱱ ᱦᱩᱭᱤᱞᱪᱮᱭᱟᱨ ᱮᱠᱥᱮᱥ ᱢᱮᱱᱟᱜᱼᱟ ᱥᱮ?",
        "ᱛᱷᱩᱠᱩ ᱫᱩᱠᱟᱱ ᱚᱠᱟ ᱨᱮ ᱢᱮᱱᱟᱜᱼᱟ?",
        "ᱪᱤᱛᱟᱹᱨ ᱦᱤᱡᱩᱜ ᱨᱮᱭᱟᱜ ᱨᱩᱣᱟᱹᱲ ᱢᱮᱱᱟᱜᱼᱟ ᱥᱮ?",
        "ᱱᱤᱛᱟᱜ ᱩᱫᱩᱜ ᱥᱚᱫᱚᱨ ᱵᱟᱵᱚᱫᱽ ᱠᱟᱛᱷᱟ ᱤᱧ ᱚᱠᱷᱚᱱ ᱧᱟᱢ ᱫᱟᱲᱮᱭᱟᱜᱼᱟ?"
    ],
    'brx': [
        "टयालेटफोरा बबे?",
        "टिकेटनि बेंसिनफोरा मा?",
        "क्याफेआ बबे?",
        "खेलनाय समा मा?",
        "गाइडेड टुरफोरा मोननायगोनना?",
        "पुर्खानि सभ्यतानि ग्यालारिया बबे?",
        "नोंसोरनि ओनसोलाव व्हीलचेयर एसेस आगोनना?",
        "मुवा फुंनाय दुकाना बबे?",
        "फटग्राफी खालामनाया मोननायगोनना?",
        "एदेर फोरमाण्डियारि सोमोन्दै खौरां मां आंगो मोननो हागोन?"
    ],
    'mai': [
        "शौचालय कतय अछि?",
        "टिकटक दाम की अछि?",
        "कैफे कतय अछि?",
        "खुललाक समय की अछि?",
        "की गाइडेड टूर उपलब्ध अछि?",
        "प्राचीन सभ्यताक ग्यालरी कतय अछि?",
        "अहाँक पास व्हीलचेयर एक्सेस अछि?",
        "उपहारक दोकान कतय अछि?",
        "की फोटोग्राफीक अनुमति अछि?",
        "वर्तमान प्रदर्शनीक बारेमे जानकारी हम कतय सँ प्राप्त करी सकैत छी?"
    ]
}

def ask_gemini(prompt: str, model="gemini-2.0-flash"):
    """Send prompt to Gemini and get response."""
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

def translate_text(text, dest_language='en'):
    """Translate text to the specified language using googletrans-py."""
    try:
        if dest_language == 'en':
            return text
            
        translated = translator.translate(text, dest=dest_language)
        return translated.text
        
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def get_museum_answer(question, language='en'):
    """Get specific answer about the museum in the specified language."""
    museum_context = json.dumps(MUSEUM_DATA, indent=2)
    
    if language != 'en':
        # Translate the question to English for processing
        question_en = translate_text(question, 'en')
    else:
        question_en = question
    
    prompt = f"""
    You are a knowledgeable museum guide at {MUSEUM_DATA['name']}. 
    Answer the following question based ONLY on the museum information provided.
    
    MUSEUM INFORMATION:
    {museum_context}
    
    QUESTION: {question_en}
    
    Instructions:
    1. Be direct, concise and factual
    2. Provide specific location details if applicable
    3. If information is not available, say "I don't have that information"
    4. Keep response under 3 sentences
    """
    
    answer = ask_gemini(prompt)
    
    if language != 'en':
        # Translate the answer back to the requested language
        answer = translate_text(answer, language)
    
    return answer

def plan_personalized_trip(interests, time_available, with_kids, language='en'):
    """Generate a personalized museum trip plan."""
    museum_context = json.dumps(MUSEUM_DATA, indent=2)
    
    if language != 'en':
        # Translate inputs to English for processing
        interests_en = translate_text(interests, 'en')
        time_available_en = translate_text(time_available, 'en')
        with_kids_en = translate_text(with_kids, 'en')
    else:
        interests_en = interests
        time_available_en = time_available
        with_kids_en = with_kids
    
    prompt = f"""
    You are a friendly museum tour planner at {MUSEUM_DATA['name']}. 
    Create a personalized tour plan based on the visitor's preferences.
    
    VISITOR PREFERENCES:
    - Interests: {interests_en}
    - Time available: {time_available_en}
    - With kids: {with_kids_en}
    
    MUSEUM INFORMATION:
    {museum_context}
    
    Instructions:
    1. Create a concise, engaging tour plan
    2. Suggest specific galleries/exhibits based on their interests
    3. Include practical tips (where to start, where to eat, etc.)
    4. Consider time constraints and whether they have children
    5. Keep it friendly and welcoming
    6. Limit to 5-7 sentences
    """
    
    plan = ask_gemini(prompt)
    
    if language != 'en':
        # Translate the plan back to the requested language
        plan = translate_text(plan, language)
    
    return plan

@app.route('/')
def index():
    """Render the main page."""
    lang = request.args.get('lang', 'en')
    return render_template('index.html', 
                         languages=LANGUAGES, 
                         translations=UI_TRANSLATIONS.get(lang, UI_TRANSLATIONS['en']), 
                         current_lang=lang,
                         standard_questions=STANDARD_QUESTIONS.get(lang, STANDARD_QUESTIONS['en']))

@app.route('/ask', methods=['POST'])
def ask_question():
    """Handle question asking."""
    data = request.json
    question = data.get('question', '')
    lang = data.get('lang', 'en')
    
    if not question:
        return jsonify({'error': 'No question provided'})
    
    answer = get_museum_answer(question, lang)
    return jsonify({'answer': answer})

@app.route('/plan', methods=['POST'])
def plan_trip():
    """Handle trip planning."""
    data = request.json
    interests = data.get('interests', '')
    time_available = data.get('time_available', '')
    with_kids = data.get('with_kids', '')
    lang = data.get('lang', 'en')
    
    if not all([interests, time_available, with_kids]):
        return jsonify({'error': 'Missing required fields'})
    
    plan = plan_personalized_trip(interests, time_available, with_kids, lang)
    return jsonify({'plan': plan})

@app.route('/info')
def museum_info():
    """Return museum information."""
    lang = request.args.get('lang', 'en')
    
    # Translate museum information
    info = {}
    for key, value in MUSEUM_DATA.items():
        if isinstance(value, str):
            info[key] = translate_text(value, lang) if lang != 'en' else value
        elif isinstance(value, dict):
            info[key] = {}
            for k, v in value.items():
                if isinstance(v, str):
                    info[key][k] = translate_text(v, lang) if lang != 'en' else v
                else:
                    info[key][k] = v
        else:
            info[key] = value
    
    return jsonify(info)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create the HTML template
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Museum Guide - Multilingual Assistant</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            background: linear-gradient(135deg, #4682B4 0%, #5F9EA0 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
        }
        h1 {
            margin: 0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle {
            font-style: italic;
            margin-top: 10px;
            opacity: 0.9;
        }
        .language-selector {
            text-align: right;
            margin-bottom: 20px;
        }
        select {
            padding: 10px;
            border-radius: 8px;
            border: 2px solid #ddd;
            font-size: 16px;
            background: white;
        }
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        .section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }
        .section h2 {
            color: #4682B4;
            border-bottom: 2px solid #4682B4;
            padding-bottom: 10px;
            margin-top: 0;
        }
        .quick-questions {
            grid-column: 1 / -1;
        }
        .question-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .question-btn {
            background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
            color: white;
            border: none;
            padding: 12px;
            border-radius: 8px;
            cursor: pointer;
            text-align: left;
            transition: all 0.3s ease;
            font-size: 14px;
        }
        .question-btn:hover {
            background: linear-gradient(135deg, #5a6268 0%, #343a40 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        input, textarea {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 2px solid #ddd;
            border-radius: 8px;
            box-sizing: border-box;
            font-size: 16px;
        }
        input:focus, textarea:focus {
            border-color: #4682B4;
            outline: none;
            box-shadow: 0 0 5px rgba(70, 130, 180, 0.5);
        }
        button {
            background: linear-gradient(135deg, #4682B4 0%, #36648B 100%);
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        button:hover {
            background: linear-gradient(135deg, #36648B 0%, #254e70 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .result {
            margin-top: 20px;
            padding: 20px;
            background: white;
            border-radius: 8px;
            border: 2px solid #e9ecef;
            min-height: 100px;
        }
        .result h3 {
            color: #4682B4;
            margin-top: 0;
        }
        .info-section {
            margin-bottom: 20px;
        }
        .info-section h3 {
            color: #4682B4;
            border-bottom: 2px solid #4682B4;
            padding-bottom: 5px;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #4682B4 0%, #5F9EA0 100%);
            border-radius: 10px;
            color: white;
        }
        .tab {
            overflow: hidden;
            border: 1px solid #ccc;
            background-color: #f1f1f1;
            border-radius: 10px 10px 0 0;
        }
        .tab button {
            background-color: inherit;
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 14px 16px;
            transition: 0.3s;
            font-size: 16px;
            width: 33.33%;
        }
        .tab button:hover {
            background-color: #ddd;
        }
        .tab button.active {
            background-color: #4682B4;
            color: white;
        }
        .tabcontent {
            display: none;
            padding: 20px;
            border: 1px solid #ccc;
            border-top: none;
            border-radius: 0 0 10px 10px;
            animation: fadeEffect 1s;
        }
        @keyframes fadeEffect {
            from {opacity: 0;}
            to {opacity: 1;}
        }
        .active-tab {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ {{ translations.welcome }}</h1>
            <div class="subtitle">Your personal museum assistant in multiple languages</div>
        </div>
        
        <div class="language-selector">
            <select id="languageSelect" onchange="changeLanguage()">
                {% for code, name in languages.items() %}
                    <option value="{{ code }}" {% if code == current_lang %}selected{% endif %}>{{ name }}</option>
                {% endfor %}
            </select>
        </div>
        
        <div class="main-content">
            <div class="section">
                <h2>❓ {{ translations.ask_question }}</h2>
                <input type="text" id="questionInput" placeholder="{{ translations.question_placeholder }}">
                <button onclick="askQuestion()">{{ translations.ask_button }}</button>
                <div class="result">
                    <h3>{{ translations.answer }}</h3>
                    <div id="answerResult"></div>
                </div>
            </div>
            
            <div class="section">
                <h2>🗺️ {{ translations.plan_trip }}</h2>
                <input type="text" id="interestsInput" placeholder="{{ translations.interests }}">
                <input type="text" id="timeInput" placeholder="{{ translations.time_available }}">
                <input type="text" id="kidsInput" placeholder="{{ translations.with_kids }}">
                <button onclick="planTrip()">{{ translations.generate_plan }}</button>
                <div class="result">
                    <h3>{{ translations.your_plan }}</h3>
                    <div id="planResult"></div>
                </div>
            </div>
            
            <div class="section quick-questions">
                <h2>⚡ {{ translations.quick_questions }}</h2>
                <p>{{ translations.ask_about }}</p>
                <div class="question-grid">
                    {% for question in standard_questions %}
                        <button class="question-btn" onclick="setQuestion('{{ question }}')">{{ question }}</button>
                    {% endfor %}
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>ℹ️ {{ translations.museum_info }}</h2>
            <div id="museumInfo"></div>
        </div>
        
        <div class="footer">
            <p>🏛️ MusoBot - Your Intelligent Museum Guide | Available in {{ languages|length }} languages</p>
        </div>
    </div>

    <script>
        let currentLang = '{{ current_lang }}';
        
        function changeLanguage() {
            const lang = document.getElementById('languageSelect').value;
            window.location.href = `/?lang=${lang}`;
        }
        
        function setQuestion(question) {
            document.getElementById('questionInput').value = question;
            askQuestion();
        }
        
        function askQuestion() {
            const question = document.getElementById('questionInput').value;
            if (!question) return;
            
            fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question,
                    lang: currentLang
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('answerResult').innerText = data.answer || data.error;
            })
            .catch(error => {
                document.getElementById('answerResult').innerText = 'Error: ' + error;
            });
        }
        
        function planTrip() {
            const interests = document.getElementById('interestsInput').value;
            const timeAvailable = document.getElementById('timeInput').value;
            const withKids = document.getElementById('kidsInput').value;
            
            if (!interests || !timeAvailable || !withKids) return;
            
            fetch('/plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    interests: interests,
                    time_available: timeAvailable,
                    with_kids: withKids,
                    lang: currentLang
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('planResult').innerText = data.plan || data.error;
            })
            .catch(error => {
                document.getElementById('planResult').innerText = 'Error: ' + error;
            });
        }
        
        function loadMuseumInfo() {
            fetch(`/info?lang=${currentLang}`)
            .then(response => response.json())
            .then(data => {
                let html = `
                    <div class="info-section">
                        <h2>${data.name}</h2>
                        <p><strong>Location:</strong> ${data.location}</p>
                    </div>
                    
                    <div class="info-section">
                        <h3>{{ translations.hours }}</h3>
                        <ul>
                `;
                
                for (const [day, hours] of Object.entries(data.hours)) {
                    html += `<li><strong>${day}:</strong> ${hours}</li>`;
                }
                
                html += `
                        </ul>
                    </div>
                    
                    <div class="info-section">
                        <h3>{{ translations.tickets }}</h3>
                        <ul>
                `;
                
                for (const [category, price] of Object.entries(data.ticket_prices)) {
                    html += `<li><strong>${category}:</strong> ${price}</li>`;
                }
                
                html += `
                        </ul>
                    </div>
                    
                    <div class="info-section">
                        <h3>{{ translations.facilities }}</h3>
                        <p><strong>Restrooms:</strong> Available on all floors</p>
                        <p><strong>Cafe:</strong> ${data.facilities.cafe.location} (${data.facilities.cafe.hours})</p>
                        <p><strong>Gift Shop:</strong> ${data.facilities.gift_shop.location} (${data.facilities.gift_shop.hours})</p>
                    </div>
                    
                    <div class="info-section">
                        <h3>{{ translations.tours }}</h3>
                        <p><strong>Schedule:</strong> ${data.tours.guided_tours.schedule}</p>
                        <p><strong>Duration:</strong> ${data.tours.guided_tours.duration}</p>
                        <p><strong>Meeting Point:</strong> ${data.tours.guided_tours.meeting_point}</p>
                    </div>
                `;
                
                document.getElementById('museumInfo').innerHTML = html;
            })
            .catch(error => {
                document.getElementById('museumInfo').innerText = 'Error loading museum information: ' + error;
            });
        }
        
        // Load museum info when page loads
        document.addEventListener('DOMContentLoaded', function() {
            loadMuseumInfo();
        });
    </script>
</body>
</html>''')
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
