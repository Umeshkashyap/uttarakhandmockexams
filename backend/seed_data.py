# ================= SUBJECTS =================
SUBJECTS = [
    {
        "name": "Mathematics",
        "name_hindi": "गणित",
        "icon": "📐",
        "color_class": "bg-blue-500",
        "exam_types": ["SSC", "UKPSC"],
        "sort_order": 1
    },
    {
        "name": "Science",
        "name_hindi": "विज्ञान",
        "icon": "🔬",
        "color_class": "bg-green-500",
        "exam_types": ["SSC", "Railway"],
        "sort_order": 2
    }
]

# ================= QUESTIONS =================
QUESTIONS = {
    "Mathematics": [
        {
            "qe": "2 + 2 = ?",
            "qh": "2 + 2 = ?",
            "opts": ["1", "2", "3", "4"],
            "ans": 4,
            "exp": "2+2=4",
            "diff": "easy"
        }
    ],
    "Science": [
        {
            "qe": "Water formula?",
            "qh": "पानी का सूत्र क्या है?",
            "opts": ["CO2", "H2O", "O2", "NaCl"],
            "ans": 2,
            "exp": "Water = H2O",
            "diff": "easy"
        }
    ]
}
