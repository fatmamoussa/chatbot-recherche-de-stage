

ADAPTIVE_QUESTIONS = {
    "python": {
        "easy": [
            {"q": "Python est un langage ?", "a": ["Compilé", "Interprété", "Aucun"], "correct": 1},
           
        ],
        "medium": [
            {"q": "Que renvoie range(3) ?", "a": ["0,1,2", "1,2,3", "Erreur"], "correct": 0},
         
        ],
        "hard": [
            {"q": "Résultat de list(map(lambda x: x*x, [1,2,3])) ?", "a": ["[1,4,9]", "[2,4,6]", "Erreur"], "correct": 0},
          
        ]
    },

   
    "mysql": {
        "easy": [
            {"q": "MySQL est ?", "a": ["NoSQL", "Relationnel", "Graph DB"], "correct": 1}
        ],
        "medium": [
            {"q": "Port MySQL ?", "a": ["3306", "5432", "1521"], "correct": 0}
        ],
        "hard": [
            {"q": "Très gros dataset → utiliser ?", "a": ["InnoDB", "CSV", "Memory"], "correct": 0}
        ]
    },

  
    "mongodb": {
        "easy": [
            {"q": "MongoDB est ?", "a": ["Relationnel", "NoSQL Document", "Graph"], "correct": 1}
        ],
        "medium": [
            {"q": "Format MongoDB ?", "a": ["CSV", "JSON", "XML"], "correct": 1}
        ],
        "hard": [
            {"q": "Indexation MongoDB ?", "a": ["Non", "Oui", "Uniquement unique"], "correct": 1}
        ]
    },


   

    "nlp": {
        "easy": [
            {"q": "NLP signifie ?", "a": ["Natural Language Processing", "Native Logic Program", "Network Language Protocol"], "correct": 0}
        ],
        "medium": [
            {"q": "Tokenisation sert à ?", "a": ["Créer tableaux", "Couper texte", "Compresser"], "correct": 1}
        ],
        "hard": [
            {"q": "Transformers utilisent ?", "a": ["Attention", "SQL", "FTP"], "correct": 0}
        ]
    },

    "data_analysis": {
        "easy": [
            {"q": "Analyse de données vise ?", "a": ["Décision", "Dessiner", "Compiler"], "correct": 0}
        ],
        "medium": [
            {"q": "CSV signifie ?", "a": ["Comma Separated Values", "Central System View", "Compute Selected Variable"], "correct": 0}
        ],
        "hard": [
            {"q": "EDA signifie ?", "a": ["Exploratory Data Analysis", "Enhanced Data Analytics", "Element Data Algorithm"], "correct": 0}
        ]
    },

    "pandas": {
        "easy": [
            {"q": "Pandas manipule ?", "a": ["Dataframes", "Images", "Audio"], "correct": 0}
        ],
        "medium": [
            {"q": "Lire un CSV ?", "a": ["pd.load()", "pd.readcsv()", "pd.read_csv()"], "correct": 2}
        ],
        "hard": [
            {"q": "Concaténer DataFrames ?", "a": ["pd.concat()", "pd.bind()", "pd.add()"], "correct": 0}
        ]
    },

    "numpy": {
        "easy": [
            {"q": "NumPy manipule ?", "a": ["Matrices", "Pages web", "Audio"], "correct": 0}
        ],
        "medium": [
            {"q": "Créer un array ?", "a": ["np.array()", "np.new()", "np.create()"], "correct": 0}
        ],
        "hard": [
            {"q": "Produit matriciel ?", "a": ["A*B", "np.dot(A,B)", "A+B"], "correct": 1}
        ]
    },

    "linux": {
        "easy": [
            {"q": "Linux est ?", "a": ["OS", "Langage", "IDE"], "correct": 0}
        ],
        "medium": [
            {"q": "Commandes fichiers ?", "a": ["ls", "run", "open"], "correct": 0}
        ],
        "hard": [
            {"q": "Droits 755 signifie ?", "a": ["RWX R-X R-X", "RWX RWX RWX", "R-- R-- R--"], "correct": 0}
        ]
    },

   

    "docker": {
        "easy": [
            {"q": "Docker utilise ?", "a": ["Containers", "Machines virtuelles", "Navigateur"], "correct": 0}
        ],
        "medium": [
            {"q": "Fichier Dockerfile démarre avec ?", "a": ["ENTRY", "IMAGE", "FROM"], "correct": 2}
        ],
        "hard": [
            {"q": "Commande pour lancer un conteneur ?", "a": ["docker start", "docker run", "docker launch"], "correct": 1}
        ]
    },

    "kubernetes": {
        "easy": [
            {"q": "Kubernetes gère ?", "a": ["Containers", "PDF", "Code C++"], "correct": 0}
        ],
        "medium": [
            {"q": "Un Pod est ?", "a": ["Container group", "API", "Network"], "correct": 0}
        ],
        "hard": [
            {"q": "Fichier de config ?", "a": ["JSON", "YAML", "TXT"], "correct": 1}
        ]
    }
}

# Configuration des niveaux
LEVEL_THRESHOLDS = {
    "Débutant": 0,
    "Intermédiaire": 100,
    "Avancé": 300,
    "Expert": 600,
    "Maître": 1000
}

LEVEL_NAMES = list(LEVEL_THRESHOLDS.keys())

# Récompenses par niveau
LEVEL_REWARDS = {
    "Débutant": {
        "icon": "🌱",
        "color": "gray",
        "badge": "badge-gray-100",
        "message": "Bienvenue débutant ! Commencez votre voyage d'apprentissage."
    },
    "Intermédiaire": {
        "icon": "🚀",
        "color": "blue",
        "badge": "badge-blue-100",
        "message": "Félicitations ! Vous progressez bien. Continuez ainsi !"
    },
    "Avancé": {
        "icon": "⚡",
        "color": "purple",
        "badge": "badge-purple-100",
        "message": "Impressionnant ! Vos compétences sont maintenant avancées."
    },
    "Expert": {
        "icon": "🏆",
        "color": "yellow",
        "badge": "badge-yellow-100",
        "message": "Expert reconnu ! Vous maîtrisez cette technologie."
    },
    "Maître": {
        "icon": "👑",
        "color": "red",
        "badge": "badge-red-100",
        "message": "Niveau Maître atteint ! Vous êtes parmi les meilleurs."
    }
}

# XP par difficulté
XP_BY_DIFFICULTY = {
    "easy": 10,
    "medium": 20,
    "hard": 30
}

# XP bonus pour bonnes réponses
XP_CORRECT_ANSWER = {
    "easy": 5,
    "medium": 10,
    "hard": 15
}

# XP bonus pour streak
STREAK_BONUS = {
    3: 10,  # 3 réponses correctes d'affilée
    5: 25,  # 5 réponses correctes d'affilée
    10: 50  # 10 réponses correctes d'affilée
}

# Skills reconnus dans CV
SKILLS = list(ADAPTIVE_QUESTIONS.keys())