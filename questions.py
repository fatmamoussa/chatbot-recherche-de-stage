# questions.py

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

    "java": {
        "easy": [
            {"q": "Java est ?", "a": ["Compilé + Interprété", "Uniquement compilé", "Script"], "correct": 0},
        ],
        "medium": [
            {"q": "Mot clé pour une interface ?", "a": ["class", "interface", "struct"], "correct": 1},
        ],
        "hard": [
            {"q": "Type par défaut pour décimaux en Java ?", "a": ["float", "double", "BigDecimal"], "correct": 1},
        ]
    },


    "javascript": {
        "easy": [
            {"q": "JS est ?", "a": ["Compilé", "Interprété", "Assembleur"], "correct": 1}
        ],
        "medium": [
            {"q": "DOM signifie ?", "a": ["Document Object Model", "Data Object Machine", "Display Object Map"], "correct": 0}
        ],
        "hard": [
            {"q": "Résultat de '3' + 2 ?", "a": ["5", "'32'", "Erreur"], "correct": 1}
        ]
    },

    "sql": {
        "easy": [
            {"q": "SQL signifie ?", "a": ["Structured Query Language", "Simple Query Logic", "Search Query List"], "correct": 0}
        ],
        "medium": [
            {"q": "Mot clé pour filtrer ?", "a": ["FILTER", "WHERE", "ORDER"], "correct": 1}
        ],
        "hard": [
            {"q": "Quel JOIN retourne tout, même sans correspondance ?", "a": ["INNER", "LEFT", "FULL"], "correct": 2}
        ]
    }
    ,
    
    
    
    
    "c": {
        "easy": [
            {"q": "Extension fichier C ?", "a": [".java", ".c", ".py"], "correct": 1}
        ],
        "medium": [
            {"q": "Mot clé pour constante ?", "a": ["const", "final", "static"], "correct": 0}
        ],
        "hard": [
            {"q": "Taille d’un int (en général) ?", "a": ["2 bytes", "4 bytes", "8 bytes"], "correct": 1}
        ]
    },

    "cpp": {
        "easy": [
            {"q": "C++ supporte ?", "a": ["POO", "Pas de POO", "Uniquement Script"], "correct": 0}
        ],
        "medium": [
            {"q": "Mot clé héritage ?", "a": ["->", "extends", ":"], "correct": 2}
        ],
        "hard": [
            {"q": "Quel type est le plus grand ?", "a": ["int", "long long", "short"], "correct": 1}
        ]
    },

    "csharp": {
        "easy": [
            {"q": "C# est développé par ?", "a": ["Google", "Microsoft", "IBM"], "correct": 1}
        ],
        "medium": [
            {"q": ".NET est ?", "a": ["Framework", "OS", "Navigateurs"], "correct": 0}
        ],
        "hard": [
            {"q": "Mot clé héritage ?", "a": ["extends", "inherits", ":"], "correct": 2}
        ]
    },

    "javascript": {
        "easy": [
            {"q": "JS est ?", "a": ["Compilé", "Interprété", "Assembleur"], "correct": 1}
        ],
        "medium": [
            {"q": "DOM signifie ?", "a": ["Document Object Model", "Data Object Machine", "Display Object Map"], "correct": 0}
        ],
        "hard": [
            {"q": "Résultat de '3' + 2 ?", "a": ["5", "'32'", "Erreur"], "correct": 1}
        ]
    },

    "typescript": {
        "easy": [
            {"q": "TS est un sur-ensemble de ?", "a": ["Python", "JavaScript", "C"], "correct": 1}
        ],
        "medium": [
            {"q": "TS ajoute ?", "a": ["Types", "POO", "Threads"], "correct": 0}
        ],
        "hard": [
            {"q": "Extension TS ?", "a": [".tss", ".ts", ".tsx"], "correct": 1}
        ]
    },

    "php": {
        "easy": [
            {"q": "PHP est utilisé pour ?", "a": ["Backend", "Frontend", "Design"], "correct": 0}
        ],
        "medium": [
            {"q": "Extension de fichier PHP ?", "a": [".ph", ".php", ".pp"], "correct": 1}
        ],
        "hard": [
            {"q": "Framework populaire ?", "a": ["Laravel", "Django", "Spring"], "correct": 0}
        ]
    },


    "html": {
        "easy": [
            {"q": "HTML signifie ?", "a": ["HyperText Markup Language", "Home Tool Markup List", "HyperText Markdown"], "correct": 0}
        ],
        "medium": [
            {"q": "Balise titre ?", "a": ["<p>", "<h1>", "<title>"], "correct": 1}
        ],
        "hard": [
            {"q": "Balise pour tableau ?", "a": ["<table>", "<grid>", "<tab>"], "correct": 0}
        ]
    },

    "css": {
        "easy": [
            {"q": "CSS signifie ?", "a": ["Cascading Style Sheets", "Creative Style Syntax", "Color Sheet System"], "correct": 0}
        ],
        "medium": [
            {"q": "Propriété couleur ?", "a": ["style", "color", "background-text"], "correct": 1}
        ],
        "hard": [
            {"q": "Layout moderne CSS ?", "a": ["Flexbox", "Silverlight", "Flash"], "correct": 0}
        ]
    },

    "react": {
        "easy": [
            {"q": "React est ?", "a": ["Framework", "Bibliothèque", "Langage"], "correct": 1}
        ],
        "medium": [
            {"q": "Hooks introduit en ?", "a": ["2019", "2005", "2010"], "correct": 0}
        ],
        "hard": [
            {"q": "useEffect se déclenche ?", "a": ["Chaque render", "Jamais", "Uniquement au clic"], "correct": 0}
        ]
    },

    "angular": {
        "easy": [
            {"q": "Angular utilise ?", "a": ["Java", "TypeScript", "PHP"], "correct": 1}
        ],
        "medium": [
            {"q": "Directive Angular ?", "a": ["*ngIf", "$watch", "v-if"], "correct": 0}
        ],
        "hard": [
            {"q": "Cycle de vie avancé ?", "a": ["ngOnInit", "initState", "onCreate"], "correct": 0}
        ]
    },

    "nodejs": {
        "easy": [
            {"q": "Node repose sur ?", "a": ["Java", "C++", "JavaScript"], "correct": 2}
        ],
        "medium": [
            {"q": "Gestion packages ?", "a": ["pip", "npm", "composer"], "correct": 1}
        ],
        "hard": [
            {"q": "Type event-loop ?", "a": ["Multi-thread", "Single-thread", "No threads"], "correct": 1}
        ]
    },


    "sql": {
        "easy": [
            {"q": "SQL signifie ?", "a": ["Structured Query Language", "Simple Query Logic", "Search Query List"], "correct": 0}
        ],
        "medium": [
            {"q": "Clause pour filtrer ?", "a": ["FILTER", "WHERE", "SELECT"], "correct": 1}
        ],
        "hard": [
            {"q": "JOIN qui retourne tout ?", "a": ["INNER", "LEFT", "FULL"], "correct": 2}
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

    "postgresql": {
        "easy": [
            {"q": "PostgreSQL est ?", "a": ["Relationnel", "Graph DB", "Key-Value"], "correct": 0}
        ],
        "medium": [
            {"q": "Port PostgreSQL ?", "a": ["5432", "3306", "8080"], "correct": 0}
        ],
        "hard": [
            {"q": "Support JSON ?", "a": ["Non", "Oui", "Seulement XML"], "correct": 1}
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


    "machine_learning": {
        "easy": [
            {"q": "ML signifie ?", "a": ["Machine Learning", "Macro Language", "Model Loader"], "correct": 0}
        ],
        "medium": [
            {"q": "Apprentissage supervisé ?", "a": ["Sans labels", "Avec labels", "Impossible"], "correct": 1}
        ],
        "hard": [
            {"q": "Algorithme non supervisé ?", "a": ["KMeans", "SVM", "RandomForest"], "correct": 0}
        ]
    },

    "deep_learning": {
        "easy": [
            {"q": "DL utilise ?", "a": ["CNN/RNN", "SQL", "HTML"], "correct": 0}
        ],
        "medium": [
            {"q": "Framework DL ?", "a": ["TensorFlow", "Laravel", "Bootstrap"], "correct": 0}
        ],
        "hard": [
            {"q": "GPU utile pour ?", "a": ["CNN", "HTML", "SQL"], "correct": 0}
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

    "git": {
        "easy": [
            {"q": "Git est ?", "a": ["VCS", "Cloud", "Database"], "correct": 0}
        ],
        "medium": [
            {"q": "Envoyer commit ?", "a": ["git send", "git push", "git upload"], "correct": 1}
        ],
        "hard": [
            {"q": "Fusion de branches ?", "a": ["git join", "git merge", "git attach"], "correct": 1}
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

# Skills reconnus dans CV
SKILLS = list(ADAPTIVE_QUESTIONS.keys())
