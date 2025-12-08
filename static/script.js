// script.js
document.addEventListener("DOMContentLoaded", () => {
    // Éléments DOM
    const cvForm = document.getElementById("cvForm");
    const fileInput = document.getElementById("cvFile");
    const quizContainer = document.getElementById("quizContainer");
    const results = document.getElementById("results");
    const loading = document.getElementById("loading");
    const fileNameDiv = document.getElementById("fileName");
    const levelSystem = document.getElementById("levelSystem");
    const currentLevel = document.getElementById("currentLevel");
    const currentXP = document.getElementById("currentXP");
    const levelProgressBar = document.getElementById("levelProgressBar");
    const progressPercent = document.getElementById("progressPercent");
    const nextLevelLabel = document.getElementById("nextLevelLabel");
    const currentXPInLevel = document.getElementById("currentXPInLevel");
    const xpNeeded = document.getElementById("xpNeeded");

    // Variables globales
    let quizData = [];
    let currentSkillIndex = 0;
    let currentQuestionIndex = 0;
    let scoreTracker = {};
    let timerInterval = null;
    let timeLeft = 50;
    let websocket = null;
    let userProgress = {
        global_level: "Débutant",
        total_xp: 0
    };

    // ============================================
    // FONCTIONS D'INITIALISATION
    // ============================================

    // Initialiser WebSocket
    function initWebSocket() {
        websocket = new WebSocket(`ws://${window.location.host}/ws/quiz`);
        
        websocket.onopen = () => {
            console.log("WebSocket connecté");
        };
        
        websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === "timeout") {
                handleTimeout(data.auto_answer);
            }
        };
        
        websocket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };
    }

    // Mettre à jour l'affichage du nom de fichier
    fileInput.addEventListener('change', function(e) {
        if (this.files.length > 0) {
            fileNameDiv.classList.remove('hidden');
            fileNameDiv.querySelector('span').textContent = this.files[0].name;
        } else {
            fileNameDiv.classList.add('hidden');
        }
    });

    // Charger la progression utilisateur
    async function loadUserProgress() {
        try {
            const response = await fetch('/user-progress/default');
            if (response.ok) {
                const data = await response.json();
                userProgress = data.global_stats;
                updateLevelDisplay();
                levelSystem.classList.remove('hidden');
            }
        } catch (error) {
            console.log("Nouvel utilisateur, progression par défaut");
        }
    }

    // Mettre à jour l'affichage des niveaux
    function updateLevelDisplay() {
        currentLevel.textContent = userProgress.global_level || "Débutant";
        currentXP.textContent = `${userProgress.total_xp || 0} XP`;
        
        // Calculer la progression (simplifié pour l'exemple)
        const levels = ["Débutant", "Intermédiaire", "Avancé", "Expert", "Maître"];
        const thresholds = [0, 100, 300, 600, 1000];
        const currentLevelIndex = levels.indexOf(userProgress.global_level);
        
        if (currentLevelIndex < levels.length - 1) {
            const nextLevel = levels[currentLevelIndex + 1];
            const currentThreshold = thresholds[currentLevelIndex];
            const nextThreshold = thresholds[currentLevelIndex + 1];
            const xpInLevel = userProgress.total_xp - currentThreshold;
            const xpNeededTotal = nextThreshold - currentThreshold;
            const progress = Math.min(100, (xpInLevel / xpNeededTotal) * 100);
            
            nextLevelLabel.textContent = `Prochain niveau: ${nextLevel}`;
            progressPercent.textContent = `${Math.round(progress)}%`;
            levelProgressBar.style.width = `${progress}%`;
            currentXPInLevel.textContent = `${xpInLevel} XP`;
            xpNeeded.textContent = `${xpNeededTotal} XP requis`;
        } else {
            nextLevelLabel.textContent = "Niveau maximum atteint !";
            progressPercent.textContent = "100%";
            levelProgressBar.style.width = "100%";
            currentXPInLevel.textContent = `${userProgress.total_xp} XP`;
            xpNeeded.textContent = "XP maximum";
        }
    }

    // ============================================
    // FONCTIONS DU QUIZ
    // ============================================

    // Démarrer le timer
    function startTimer() {
        clearInterval(timerInterval);
        timeLeft = 50;
        
        const timerDisplay = document.getElementById("timerDisplay");
        const progressBar = document.getElementById("progressBar");
        
        if (timerDisplay) timerDisplay.textContent = `${timeLeft}s`;
        if (progressBar) {
            progressBar.style.width = '100%';
            progressBar.style.transition = 'none';
            setTimeout(() => {
                progressBar.style.transition = 'width 50s linear';
                progressBar.style.width = '0%';
            }, 100);
        }
        
        timerInterval = setInterval(() => {
            timeLeft--;
            if (timerDisplay) timerDisplay.textContent = `${timeLeft}s`;
            
            if (timeLeft <= 10) {
                timerDisplay.classList.add("text-red-500", "animate-pulse");
            }
            
            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                handleTimeout(-1);
                
                if (websocket && websocket.readyState === WebSocket.OPEN) {
                    websocket.send(JSON.stringify({
                        action: "timeout",
                        skill: quizData[currentSkillIndex]?.skill,
                        question_index: currentQuestionIndex
                    }));
                }
            }
        }, 1000);
    }

    // Gérer le timeout
    function handleTimeout(autoAnswer) {
        if (!quizData[currentSkillIndex]) return;
        
        const skill = quizData[currentSkillIndex].skill;
        if (!scoreTracker[skill]) scoreTracker[skill] = [];
        scoreTracker[skill].push(autoAnswer);
        
        showNotification("⏰ Temps écoulé! Passage à la question suivante.", "warning");
        moveToNextQuestion();
    }

    // Passer à la question suivante
    function moveToNextQuestion() {
        clearInterval(timerInterval);
        
        currentQuestionIndex++;
        if (currentQuestionIndex >= quizData[currentSkillIndex].questions.length) {
            currentSkillIndex++;
            currentQuestionIndex = 0;
        }
        
        if (currentSkillIndex < quizData.length) {
            setTimeout(() => showQuestion(), 500);
        } else {
            submitQuiz();
        }
    }

    // Afficher une question
    function showQuestion() {
        if (currentSkillIndex >= quizData.length) {
            submitQuiz();
            return;
        }

        const skillQuiz = quizData[currentSkillIndex];
        const question = skillQuiz.questions[currentQuestionIndex];
        const totalQuestions = skillQuiz.questions.length;
        const progressPercentage = ((currentQuestionIndex + 1) / totalQuestions) * 100;

        quizContainer.innerHTML = `
            <div class="bg-white rounded-xl shadow-lg p-6 animate-slide-in">
                <!-- En-tête avec progression -->
                <div class="mb-6">
                    <div class="flex justify-between items-center mb-2">
                        <div>
                            <span class="text-sm font-medium text-gray-500">Compétence</span>
                            <h3 class="text-xl font-bold text-gray-800">${skillQuiz.skill.charAt(0).toUpperCase() + skillQuiz.skill.slice(1)}</h3>
                        </div>
                        <div class="text-right">
                            <span class="text-sm font-medium text-gray-500">Question</span>
                            <div class="text-lg font-bold text-blue-600">${currentQuestionIndex + 1}/${totalQuestions}</div>
                        </div>
                    </div>
                    
                    <!-- Barre de progression générale -->
                    <div class="w-full bg-gray-200 rounded-full h-2 mb-4">
                        <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                             style="width: ${progressPercentage}%"></div>
                    </div>
                    
                    <!-- Timer -->
                    <div class="flex items-center justify-between mb-6 p-3 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border border-yellow-200">
                        <div class="flex items-center">
                            <div class="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center mr-3">
                                <span class="text-yellow-600">⏱️</span>
                            </div>
                            <div>
                                <div class="text-sm font-medium text-yellow-800">Temps restant</div>
                                <div id="timerDisplay" class="text-2xl font-bold text-yellow-700">50s</div>
                            </div>
                        </div>
                        <div class="w-48">
                            <div class="text-sm text-yellow-700 mb-1 text-right">Progression du timer</div>
                            <div class="bg-yellow-200 rounded-full h-2 overflow-hidden">
                                <div id="progressBar" class="h-full bg-yellow-600 progress-bar-timer"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Question -->
                <div class="mb-8">
                    <div class="text-lg font-semibold text-gray-700 mb-2">Question ${currentQuestionIndex + 1}:</div>
                    <div class="text-2xl font-bold text-gray-900 mb-6">${question.q}</div>
                    
                    <!-- Options de réponse -->
                    <div id="answerOptions" class="space-y-3">
                        ${question.a.map((answer, index) => `
                            <label class="flex items-center p-4 border border-gray-300 rounded-lg cursor-pointer hover:bg-blue-50 hover:border-blue-300 transition-all duration-200 answer-option" data-index="${index}">
                                <input type="radio" name="answer" value="${index}" class="hidden">
                                <div class="w-6 h-6 border-2 border-gray-400 rounded-full mr-3 flex items-center justify-center">
                                    <div class="w-3 h-3 rounded-full bg-blue-600 hidden"></div>
                                </div>
                                <span class="text-lg">${answer}</span>
                            </label>
                        `).join('')}
                    </div>
                </div>

                <!-- Boutons de navigation -->
                <div class="flex justify-between pt-4 border-t border-gray-200">
                    <button id="prevBtn" class="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors duration-200 ${currentQuestionIndex === 0 && currentSkillIndex === 0 ? 'opacity-50 cursor-not-allowed' : ''}">
                        ← Précédent
                    </button>
                    <button id="nextBtn" class="px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 font-medium">
                        Valider et continuer →
                    </button>
                </div>
            </div>
        `;

        // Démarrer le timer
        startTimer();

        // Gérer la sélection des réponses
        const answerOptions = document.querySelectorAll('.answer-option');
        answerOptions.forEach(option => {
            option.addEventListener('click', (e) => {
                answerOptions.forEach(opt => {
                    opt.classList.remove('border-blue-500', 'bg-blue-50');
                    opt.querySelector('.w-3.h-3').classList.add('hidden');
                });
                
                option.classList.add('border-blue-500', 'bg-blue-50');
                option.querySelector('.w-3.h-3').classList.remove('hidden');
                document.getElementById('nextBtn').disabled = false;
            });
        });

        // Bouton précédent
        document.getElementById('prevBtn').addEventListener('click', () => {
            if (currentQuestionIndex === 0 && currentSkillIndex > 0) {
                currentSkillIndex--;
                currentQuestionIndex = quizData[currentSkillIndex].questions.length - 1;
            } else if (currentQuestionIndex > 0) {
                currentQuestionIndex--;
            }
            showQuestion();
        });

        // Bouton suivant/valider
        document.getElementById('nextBtn').addEventListener('click', () => {
            const selectedOption = document.querySelector('.answer-option.border-blue-500');
            if (!selectedOption) {
                showNotification("Veuillez sélectionner une réponse !", "warning");
                return;
            }
            
            const userAnswer = parseInt(selectedOption.dataset.index);
            const skill = skillQuiz.skill;
            
            if (!scoreTracker[skill]) scoreTracker[skill] = [];
            scoreTracker[skill].push(userAnswer);
            
            if (websocket && websocket.readyState === WebSocket.OPEN) {
                websocket.send(JSON.stringify({
                    action: "answer_submitted"
                }));
            }
            
            moveToNextQuestion();
        });
    }

    // ============================================
    // FONCTIONS DE SOUMISSION ET RÉSULTATS
    // ============================================

    // Soumission CV
    cvForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        if (!fileInput.files.length) {
            showNotification("Veuillez sélectionner un fichier PDF !", "error");
            return;
        }

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);
        
        loading.classList.remove("hidden");
        results.innerHTML = "";
        quizContainer.innerHTML = "";
        
        try {
            const response = await fetch("/upload-cv/", { 
                method: "POST", 
                body: formData 
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                showNotification(data.error, "error");
                return;
            }
            
            if (Array.isArray(data.quiz) && data.quiz.length > 0) {
                quizData = data.quiz;
                currentSkillIndex = 0;
                currentQuestionIndex = 0;
                scoreTracker = {};
                
                // Afficher les compétences détectées avec niveaux
                showSkillsDetected(data.skills, data.user_progress);
                
                // Initialiser WebSocket
                initWebSocket();
                
                // Commencer le quiz après un délai
                setTimeout(() => {
                    showQuestion();
                    loading.classList.add("hidden");
                }, 1500);
                
            } else {
                showNotification("Aucune compétence détectée dans votre CV.", "warning");
                loading.classList.add("hidden");
            }
        } catch (err) {
            console.error("Error:", err);
            showNotification("Erreur lors de l'analyse du CV: " + err.message, "error");
            loading.classList.add("hidden");
        }
    });

    // Afficher les compétences détectées
    function showSkillsDetected(skills, userProgress) {
        quizContainer.innerHTML = `
            <div class="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-200 animate-slide-in">
                <div class="flex items-center mb-4">
                    <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                        <span class="text-blue-600 text-xl">🎯</span>
                    </div>
                    <div>
                        <h2 class="text-2xl font-bold text-gray-800">Compétences détectées</h2>
                        <p class="text-gray-600">Niveau global: ${userProgress.global_level} (${userProgress.total_xp} XP)</p>
                    </div>
                </div>
                <p class="text-gray-600 mb-4">Votre CV a été analysé avec succès. Voici vos compétences:</p>
                <div class="flex flex-wrap gap-2 mb-6">
                    ${skills.map(skill => `
                        <div class="flex items-center px-3 py-1 ${skill.badge.color === 'blue' ? 'bg-blue-100 text-blue-800' : 
                                                                    skill.badge.color === 'purple' ? 'bg-purple-100 text-purple-800' :
                                                                    skill.badge.color === 'yellow' ? 'bg-yellow-100 text-yellow-800' :
                                                                    skill.badge.color === 'red' ? 'bg-red-100 text-red-800' :
                                                                    'bg-gray-100 text-gray-800'} rounded-full text-sm font-medium">
                            <span class="mr-1">${skill.badge.icon}</span>
                            ${skill.skill.charAt(0).toUpperCase() + skill.skill.slice(1)}
                            <span class="ml-2 text-xs px-1 bg-white rounded">${skill.current_level}</span>
                        </div>
                    `).join('')}
                </div>
                <div class="bg-blue-50 border border-blue-100 rounded-lg p-4">
                    <div class="flex items-center">
                        <span class="text-blue-600 mr-2">ℹ️</span>
                        <p class="text-sm text-blue-800">
                            Vous aurez 50 secondes par question. Le quiz s'adaptera à vos réponses.
                            Gagnez de l'XP et montez en niveau !
                        </p>
                    </div>
                </div>
            </div>
        `;
    }

    // Soumission finale du quiz
    async function submitQuiz() {
        clearInterval(timerInterval);
        quizContainer.innerHTML = "";
        loading.classList.remove("hidden");
        
        const payload = {
            answers: scoreTracker,
            quiz_data: quizData.reduce((acc, q) => {
                acc[q.skill] = { 
                    questions: q.questions, 
                    used_questions: [] 
                };
                return acc;
            }, {}),
            user_id: "default"
        };

        try {
            const response = await fetch("/submit-quiz/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Debug: afficher les données reçues
            console.log("Données reçues du backend:", data);
            console.log("Compétences validées:", data.validated_skills);
            console.log("Offres par compétence:", data.offers_by_skill);
            
            loading.classList.add("hidden");
            displayResults(data);
            
            // Mettre à jour l'affichage des niveaux
            if (data.user_progress) {
                userProgress = data.user_progress;
                updateLevelDisplay();
            }
            
        } catch (err) {
            console.error("Error:", err);
            showNotification("Erreur lors de la soumission du quiz: " + err.message, "error");
            loading.classList.add("hidden");
        }
    }

    // Afficher les résultats
    function displayResults(data) {
        // Section des offres d'emploi - CORRIGÉE
        let offersSection = '';
        if (data.validated_skills && data.validated_skills.length > 0) {
            // Calculer les compétences avec des offres réelles
            let skillsWithRealOffers = 0;
            
            // Construire le HTML des offres
            let offersHTML = '';
            
            // Pour chaque compétence validée
            data.validated_skills.forEach(skill => {
                // Récupérer les offres pour cette compétence
                const offersForSkill = data.offers_by_skill ? 
                    (data.offers_by_skill[skill] || []) : 
                    [];
                
                // Prendre au maximum 2 offres par compétence
                const displayOffers = offersForSkill.slice(0, 2);
                
                // Si pas d'offres, créer une offre par défaut
                let finalOffers = displayOffers;
                if (displayOffers.length === 0) {
                    finalOffers = [{
                        title: `Développeur ${skill}`,
                        company: 'Recherche en cours...',
                        link: `https://www.indeed.com/jobs?q=${skill}`,
                        matched_skill: skill,
                        is_default: true
                    }];
                } else {
                    skillsWithRealOffers++;
                }
                
                // Générer le HTML pour chaque offre de cette compétence
                finalOffers.forEach((offer, idx) => {
                    const isDefault = offer.is_default || false;
                    const badgeColor = isDefault ? 'yellow' : 'blue';
                    const badgeText = isDefault ? 'Recherche automatique' : 'Offre réelle';
                    const buttonClass = isDefault ? 
                        'bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600' : 
                        'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700';
                    const buttonText = isDefault ? 'Rechercher cette compétence →' : 'Voir cette offre →';
                    const icon = isDefault ? '🔍' : '💼';
                    
                    offersHTML += `
                        <div class="bg-white rounded-xl shadow-md border ${isDefault ? 'border-yellow-200' : 'border-blue-200'} hover:shadow-lg transition-shadow duration-300">
                            <div class="p-6">
                                <!-- Badge de compétence -->
                                <div class="flex items-center justify-between mb-4">
                                    <div class="flex items-center">
                                        <div class="w-10 h-10 ${isDefault ? 'bg-yellow-100' : 'bg-blue-100'} rounded-full flex items-center justify-center mr-3">
                                            <span class="${isDefault ? 'text-yellow-600' : 'text-blue-600'}">${icon}</span>
                                        </div>
                                        <div>
                                            <div class="font-bold text-gray-800">${skill.charAt(0).toUpperCase() + skill.slice(1)}</div>
                                            <div class="text-sm ${isDefault ? 'text-yellow-600' : 'text-blue-600'}">
                                                ${badgeText}
                                            </div>
                                        </div>
                                    </div>
                                    <span class="text-xs text-gray-500">${idx + 1}</span>
                                </div>
                                
                                <!-- Détails de l'offre -->
                                <h4 class="text-lg font-bold text-gray-900 mb-2">${offer.title}</h4>
                                <p class="text-gray-700 mb-4">${offer.company}</p>
                                
                                <!-- Bouton -->
                                <a href="${offer.link}" target="_blank"
                                   class="block w-full text-center py-3 ${buttonClass} text-white rounded-lg transition-all duration-200 font-medium">
                                    ${buttonText}
                                </a>
                            </div>
                        </div>
                    `;
                });
            });
            
            // Note sur les compétences sans offres réelles
            let noteHTML = '';
            if (skillsWithRealOffers < data.validated_skills.length) {
                noteHTML = `
                    <div class="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <div class="flex items-center">
                            <span class="text-yellow-600 mr-2">ℹ️</span>
                            <div>
                                <p class="text-yellow-800">
                                    <span class="font-bold">Note :</span> 
                                    ${data.validated_skills.length - skillsWithRealOffers} 
                                    compétence(s) sur ${data.validated_skills.length} n'ont pas d'offres récentes disponibles. 
                                    Cliquez sur "Rechercher cette compétence" pour trouver des offres manuellement.
                                </p>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            offersSection = `
                <div class="mb-8">
                    <div class="flex items-center justify-between mb-6">
                        <div>
                            <h3 class="text-2xl font-bold text-gray-800 flex items-center">
                                <span class="mr-2">💼</span> Offres d'emploi
                            </h3>
                            <p class="text-gray-600">Correspondant à vos compétences validées</p>
                        </div>
                        <div class="text-sm text-gray-500">
                            ${data.validated_skills.length} compétence(s)
                        </div>
                    </div>
                    
                    <!-- Affichage des offres -->
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        ${offersHTML}
                    </div>
                    
                    ${noteHTML}
                </div>
            `;
        }
        
        results.innerHTML = `
            <div class="animate-slide-in">
                ${data.level_up_notifications && data.level_up_notifications.length > 0 ? `
                    <!-- Notifications de Level Up -->
                    <div class="mb-8">
                        ${data.level_up_notifications.map(notification => `
                            <div class="bg-gradient-to-r from-yellow-50 via-orange-50 to-yellow-50 border-2 border-yellow-300 rounded-2xl p-6 mb-4 animate-pulse shadow-lg">
                                <div class="flex items-center">
                                    <div class="w-16 h-16 bg-gradient-to-r from-yellow-400 to-orange-400 rounded-full flex items-center justify-center mr-4">
                                        <span class="text-3xl text-white">${notification.reward?.icon || '🏆'}</span>
                                    </div>
                                    <div class="flex-grow">
                                        <h3 class="text-2xl font-bold text-gray-800 mb-1">🎉 LEVEL UP !</h3>
                                        <p class="text-gray-700 mb-2">
                                            <span class="font-bold">${notification.skill.toUpperCase()}</span> : 
                                            <span class="text-yellow-600 font-bold">${notification.old_level}</span> → 
                                            <span class="text-green-600 font-bold">${notification.new_level}</span>
                                        </p>
                                        <p class="text-gray-600">${notification.reward?.message || 'Félicitations pour votre progression !'}</p>
                                    </div>
                                    <div class="text-right">
                                        <div class="text-sm text-gray-500 mb-1">XP gagné</div>
                                        <div class="text-2xl font-bold text-green-600">+${notification.xp_earned} XP</div>
                                    </div>
                                </div>
                                <div class="mt-4 pt-4 border-t border-yellow-200">
                                    <div class="flex justify-between text-sm text-gray-600">
                                        <span>Ancien XP: ${notification.old_xp}</span>
                                        <span>Nouveau XP: ${notification.new_xp}</span>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                <!-- Statistiques globales -->
                <div class="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-200 mb-8">
                    <div class="flex items-center justify-between mb-4">
                        <div>
                            <h3 class="text-2xl font-bold text-gray-800">📊 Résultats du Quiz</h3>
                            <p class="text-gray-600">Synthèse de vos performances</p>
                        </div>
                        <div class="text-right">
                            <div class="text-3xl font-bold text-blue-600">${data.global_stats?.total_xp || 0} XP</div>
                            <div class="text-lg font-semibold text-gray-700">Niveau ${data.global_stats?.global_level || 'Débutant'}</div>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div class="bg-white p-4 rounded-lg text-center border border-gray-200">
                            <div class="text-2xl font-bold text-blue-600">${data.validated_skills?.length || 0}</div>
                            <div class="text-sm text-gray-600">Compétences validées</div>
                        </div>
                        <div class="bg-white p-4 rounded-lg text-center border border-gray-200">
                            <div class="text-2xl font-bold text-green-600">${data.quiz_results?.reduce((sum, r) => sum + (r.xp_earned || 0), 0) || 0}</div>
                            <div class="text-sm text-gray-600">XP gagnés</div>
                        </div>
                        <div class="bg-white p-4 rounded-lg text-center border border-gray-200">
                            <div class="text-2xl font-bold text-purple-600">${data.global_stats?.skills_learned || 0}</div>
                            <div class="text-sm text-gray-600">Compétences apprises</div>
                        </div>
                        <div class="bg-white p-4 rounded-lg text-center border border-gray-200">
                            <div class="text-2xl font-bold text-yellow-600">${data.quiz_results?.filter(r => r.passed).length || 0}</div>
                            <div class="text-sm text-gray-600">Quiz réussis</div>
                        </div>
                    </div>
                </div>
                
                <!-- Résultats détaillés par compétence -->
                ${data.quiz_results && data.quiz_results.length > 0 ? `
                <div class="mb-8">
                    <h3 class="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                        <span class="mr-2">📈</span> Détails par compétence
                    </h3>
                    
                    <div class="space-y-6">
                        ${data.quiz_results.map(result => {
                            const progress = result.level_progress || {};
                            const badge = result.badge || { icon: '📝', color: 'gray' };
                            
                            return `
                            <div class="bg-white rounded-xl shadow-md border border-gray-200 hover:shadow-lg transition-shadow duration-300">
                                <div class="p-6">
                                    <!-- En-tête avec niveau et badge -->
                                    <div class="flex justify-between items-start mb-4">
                                        <div>
                                            <div class="flex items-center">
                                                <span class="text-2xl mr-2">${badge.icon}</span>
                                                <h4 class="text-xl font-bold text-gray-800">
                                                    ${result.skill?.charAt(0).toUpperCase() + result.skill?.slice(1) || 'Compétence'}
                                                </h4>
                                            </div>
                                            <div class="flex items-center mt-2">
                                                <span class="px-3 py-1 ${badge.color === 'blue' ? 'bg-blue-100 text-blue-800' : 
                                                                    badge.color === 'purple' ? 'bg-purple-100 text-purple-800' :
                                                                    badge.color === 'yellow' ? 'bg-yellow-100 text-yellow-800' :
                                                                    badge.color === 'red' ? 'bg-red-100 text-red-800' :
                                                                    'bg-gray-100 text-gray-800'} rounded-full text-sm font-bold">
                                                    Niveau ${result.current_level || 'Débutant'}
                                                </span>
                                                <span class="ml-3 px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-bold">
                                                    +${result.xp_earned || 0} XP
                                                </span>
                                            </div>
                                        </div>
                                        <div class="text-right">
                                            <div class="text-3xl font-bold ${result.passed ? 'text-green-600' : 'text-red-600'}">
                                                ${result.score || 0}%
                                            </div>
                                            <div class="text-sm text-gray-600">Score</div>
                                        </div>
                                    </div>
                                    
                                    <!-- Barre de progression du niveau -->
                                    ${!progress.is_max_level ? `
                                    <div class="mb-4">
                                        <div class="flex justify-between text-sm text-gray-600 mb-1">
                                            <span>Progression vers ${progress.next_level || 'Intermédiaire'}</span>
                                            <span>${Math.round(progress.progress_percent || 0)}%</span>
                                        </div>
                                        <div class="w-full bg-gray-200 rounded-full h-3">
                                            <div class="h-3 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500" 
                                                 style="width: ${progress.progress_percent || 0}%"></div>
                                        </div>
                                        <div class="flex justify-between text-xs text-gray-500 mt-1">
                                            <span>${progress.xp_current || 0} XP</span>
                                            <span>${progress.xp_needed || 100} XP requis</span>
                                        </div>
                                    </div>
                                    ` : `
                                    <div class="mb-4 p-3 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border border-yellow-200">
                                        <div class="flex items-center">
                                            <span class="text-yellow-600 mr-2">🏆</span>
                                            <span class="text-yellow-800 font-bold">Niveau maximum atteint !</span>
                                        </div>
                                    </div>
                                    `}
                                    
                                    <!-- Statistiques détaillées -->
                                    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                                        <div class="text-center p-3 bg-blue-50 rounded-lg">
                                            <div class="text-lg font-bold text-blue-700">${result.details?.correct_count || 0}/${result.details?.total_questions || 0}</div>
                                            <div class="text-xs text-blue-600">Réponses correctes</div>
                                        </div>
                                        <div class="text-center p-3 bg-green-50 rounded-lg">
                                            <div class="text-lg font-bold text-green-700">${Math.round((result.details?.accuracy || 0) * 100)}%</div>
                                            <div class="text-xs text-green-600">Précision</div>
                                        </div>
                                        <div class="text-center p-3 bg-purple-50 rounded-lg">
                                            <div class="text-lg font-bold text-purple-700">${result.streak || 0}</div>
                                            <div class="text-xs text-purple-600">Streak max</div>
                                        </div>
                                        <div class="text-center p-3 bg-yellow-50 rounded-lg">
                                            <div class="text-lg font-bold text-yellow-700">${result.xp_earned || 0}</div>
                                            <div class="text-xs text-yellow-600">Total XP</div>
                                        </div>
                                    </div>
                                    
                                    <!-- Sites de révision si nécessaire -->
                                    ${!result.passed && result.study_sites && result.study_sites.length > 0 ? `
                                    <div class="mt-4 pt-4 border-t border-gray-200">
                                        <h5 class="text-sm font-semibold text-gray-700 mb-2">📚 Ressources de révision</h5>
                                        <div class="flex flex-wrap gap-2">
                                            ${result.study_sites.map(site => `
                                                <a href="${site}" target="_blank" 
                                                   class="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 transition-colors">
                                                    ${new URL(site).hostname}
                                                </a>
                                            `).join('')}
                                        </div>
                                    </div>
                                    ` : ''}
                                </div>
                            </div>
                            `;
                        }).join('')}
                    </div>
                </div>
                ` : ''}
                
                <!-- Offres d'emploi -->
                ${offersSection}
                
                <!-- Boutons d'action -->
                <div class="flex flex-col sm:flex-row gap-4 mt-8">
                    <button onclick="location.reload()" 
                            class="flex-1 px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 font-bold text-lg shadow-lg hover:shadow-xl">
                        <i class="fas fa-redo mr-2"></i>Nouveau Quiz
                    </button>
                    
                    <button onclick="showProgressDashboard()" 
                            class="flex-1 px-8 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:from-purple-700 hover:to-pink-700 transition-all duration-200 font-bold text-lg shadow-lg hover:shadow-xl">
                        <i class="fas fa-chart-line mr-2"></i>Voir ma progression
                    </button>
                </div>
            </div>
        `;
    }

    // ============================================
    // FONCTIONS UTILITAIRES
    // ============================================

    // Afficher une notification
    function showNotification(message, type = "info") {
        const notification = document.createElement("div");
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 animate-slide-in ${
            type === "error" ? "bg-red-100 text-red-800 border-red-200" :
            type === "success" ? "bg-green-100 text-green-800 border-green-200" :
            type === "warning" ? "bg-yellow-100 text-yellow-800 border-yellow-200" :
            "bg-blue-100 text-blue-800 border-blue-200"
        }`;
        notification.innerHTML = `
            <div class="flex items-center">
                <span class="mr-2">${type === "error" ? "❌" : type === "success" ? "✅" : type === "warning" ? "⚠️" : "ℹ️"}</span>
                <span>${message}</span>
            </div>
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add("opacity-0", "transition-opacity", "duration-300");
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Afficher le tableau de bord
    async function showProgressDashboard() {
        try {
            const response = await fetch(`/user-progress/default`);
            const progress = await response.json();
            
            results.innerHTML = `
                <div class="animate-slide-in">
                    <div class="bg-gradient-to-r from-blue-50 to-indigo-50 p-8 rounded-2xl border border-blue-200 mb-8">
                        <div class="flex items-center justify-between mb-6">
                            <div>
                                <h2 class="text-3xl font-bold text-gray-800">🏆 Tableau de Bord</h2>
                                <p class="text-gray-600">Votre progression détaillée</p>
                            </div>
                            <div class="text-right">
                                <div class="text-4xl font-bold text-blue-600">${progress.global_stats?.total_xp || 0} XP</div>
                                <div class="text-xl font-semibold text-gray-700">Niveau ${progress.global_stats?.global_level || 'Débutant'}</div>
                            </div>
                        </div>
                        
                        <!-- Progression globale -->
                        <div class="mb-8">
                            <h3 class="text-xl font-bold text-gray-800 mb-4">📊 Progression Globale</h3>
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div class="bg-white p-6 rounded-xl border border-gray-200">
                                    <div class="text-center">
                                        <div class="text-3xl font-bold text-blue-600">${progress.global_stats?.skills_count || 0}</div>
                                        <div class="text-gray-700">Compétences</div>
                                    </div>
                                </div>
                                <div class="bg-white p-6 rounded-xl border border-gray-200">
                                    <div class="text-center">
                                        <div class="text-3xl font-bold text-green-600">${progress.level_up_history?.length || 0}</div>
                                        <div class="text-gray-700">Level Ups</div>
                                    </div>
                                </div>
                                <div class="bg-white p-6 rounded-xl border border-gray-200">
                                    <div class="text-center">
                                        <div class="text-3xl font-bold text-purple-600">${progress.global_stats?.total_xp || 0}</div>
                                        <div class="text-gray-700">Total XP</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Compétences par niveau -->
                        ${progress.skills && progress.skills.length > 0 ? `
                        <div class="mb-8">
                            <h3 class="text-xl font-bold text-gray-800 mb-4">🎯 Vos Compétences</h3>
                            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                ${progress.skills.map(skill => {
                                    const badge = skill.badge || { icon: '📝', color: 'gray' };
                                    return `
                                    <div class="bg-white p-6 rounded-xl border border-gray-200 hover:shadow-lg transition-shadow">
                                        <div class="flex items-center mb-3">
                                            <span class="text-2xl mr-2">${badge.icon}</span>
                                            <h4 class="font-bold text-gray-800">${skill.skill?.charAt(0).toUpperCase() + skill.skill?.slice(1) || 'Compétence'}</h4>
                                        </div>
                                        <div class="mb-3">
                                            <span class="px-3 py-1 ${badge.color === 'blue' ? 'bg-blue-100 text-blue-800' : 
                                                                    badge.color === 'purple' ? 'bg-purple-100 text-purple-800' :
                                                                    badge.color === 'yellow' ? 'bg-yellow-100 text-yellow-800' :
                                                                    badge.color === 'red' ? 'bg-red-100 text-red-800' :
                                                                    'bg-gray-100 text-gray-800'} rounded-full text-sm font-bold">
                                                Niveau ${skill.level || 'Débutant'}
                                            </span>
                                        </div>
                                        <div class="text-2xl font-bold text-gray-800 mb-2">${skill.xp || 0} XP</div>
                                        <div class="text-sm text-gray-600">
                                            ${skill.questions_answered || 0} questions répondues
                                        </div>
                                    </div>
                                    `;
                                }).join('')}
                            </div>
                        </div>
                        ` : ''}
                        
                        <!-- Historique des Level Ups -->
                        ${progress.level_up_history && progress.level_up_history.length > 0 ? `
                        <div class="mb-8">
                            <h3 class="text-xl font-bold text-gray-800 mb-4">🚀 Historique des Level Ups</h3>
                            <div class="space-y-3">
                                ${progress.level_up_history.map((history, idx) => `
                                    <div class="bg-white p-4 rounded-lg border border-gray-200">
                                        <div class="flex items-center">
                                            <div class="w-10 h-10 bg-gradient-to-r from-yellow-400 to-orange-400 rounded-full flex items-center justify-center mr-3">
                                                <span class="text-white">${idx + 1}</span>
                                            </div>
                                            <div class="flex-grow">
                                                <div class="font-semibold text-gray-800">
                                                    ${history.skill?.toUpperCase() || 'COMPÉTENCE'} : ${history.old_level || 'Débutant'} → ${history.new_level || 'Intermédiaire'}
                                                </div>
                                                <div class="text-sm text-gray-600">
                                                    ${new Date(history.timestamp).toLocaleDateString('fr-FR')}
                                                </div>
                                            </div>
                                            <div class="text-right">
                                                <div class="text-lg font-bold text-green-600">+${history.xp_earned || 0} XP</div>
                                            </div>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                        ` : ''}
                    </div>
                    
                    <!-- Boutons -->
                    <div class="flex gap-4">
                        <button onclick="location.reload()" 
                                class="flex-1 px-8 py-3 bg-gradient-to-r from-gray-600 to-gray-800 text-white rounded-xl hover:from-gray-700 hover:to-gray-900 transition-all duration-200 font-bold">
                            Retour à l'accueil
                        </button>
                        <button onclick="resetProgress()" 
                                class="flex-1 px-8 py-3 bg-gradient-to-r from-red-600 to-pink-600 text-white rounded-xl hover:from-red-700 hover:to-pink-700 transition-all duration-200 font-bold">
                            Réinitialiser progression
                        </button>
                    </div>
                </div>
            `;
        } catch (error) {
            console.error("Error loading progress:", error);
            showNotification("Erreur lors du chargement du tableau de bord", "error");
        }
    }

    // Réinitialiser la progression
    async function resetProgress() {
        if (confirm("Êtes-vous sûr de vouloir réinitialiser toute votre progression ? Cette action est irréversible.")) {
            try {
                const response = await fetch('/reset-progress/default', { method: 'POST' });
                if (response.ok) {
                    showNotification("Progression réinitialisée avec succès !", "success");
                    setTimeout(() => location.reload(), 1500);
                }
            } catch (error) {
                showNotification("Erreur lors de la réinitialisation", "error");
            }
        }
    }

    // Fermer WebSocket lors du déchargement de la page
    window.addEventListener('beforeunload', () => {
        if (websocket) {
            websocket.close();
        }
    });

    // Mettre à jour l'heure
    function updateTime() {
        const now = new Date();
        const options = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        const dateStr = now.toLocaleDateString('fr-FR', options);
        
        const timeElement = document.getElementById('currentTime');
        if (timeElement) {
            timeElement.textContent = dateStr;
        }
    }

    // Initialiser l'application
    updateTime();
    setInterval(updateTime, 60000);
    loadUserProgress();
});