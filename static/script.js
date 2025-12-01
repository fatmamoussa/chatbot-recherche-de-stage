
document.addEventListener("DOMContentLoaded", () => {
    const cvForm = document.getElementById("cvForm");
    const fileInput = document.getElementById("cvFile");
    const quizContainer = document.getElementById("quizContainer");
    const results = document.getElementById("results");

    let quizData = [];
    let currentSkillIndex = 0;
    let currentQuestionIndex = 0;
    let scoreTracker = {};  // stocke les indices choisis par l'utilisateur

    // Soumission CV
    cvForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!fileInput.files.length) {
            alert("Veuillez sélectionner un fichier PDF !");
            return;
        }

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);
        results.textContent = "Analyse du CV...";
        quizContainer.innerHTML = "";

        try {
            const response = await fetch("/upload-cv/", { method: "POST", body: formData });
            const data = await response.json();

            if (Array.isArray(data.quiz) && data.quiz.length > 0) {
                quizData = data.quiz;
                currentSkillIndex = 0;
                currentQuestionIndex = 0;
                scoreTracker = {};
                showQuestion();
            } else {
                results.textContent = "Aucune compétence détectée pour le quiz.";
            }
        } catch (err) {
            results.textContent = "Erreur fetch : " + err;
            console.error(err);
        }
    });

    // Affiche une question
    function showQuestion() {
        quizContainer.innerHTML = "";
        results.textContent = "";

        if (currentSkillIndex >= quizData.length) {
            submitQuiz();
            return;
        }

        const skillQuiz = quizData[currentSkillIndex];
        const question = skillQuiz.questions[currentQuestionIndex];

        const div = document.createElement("div");
        div.innerHTML = `<h3>Compétence: ${skillQuiz.skill}</h3>
                         <p>${currentQuestionIndex + 1}. ${question.q}</p>`;

        question.a.forEach((ans, idx) => {
            const label = document.createElement("label");
            label.innerHTML = `<input type="radio" name="answer" value="${idx}"> ${ans}<br>`;
            div.appendChild(label);
        });

        const nextBtn = document.createElement("button");
        nextBtn.textContent = "Valider";
        nextBtn.type = "button";

        nextBtn.addEventListener("click", () => {
            const selected = document.querySelector('input[name="answer"]:checked');
            if (!selected) {
                alert("Veuillez sélectionner une réponse !");
                return;
            }
            const userAnswer = parseInt(selected.value);
            if (!scoreTracker[skillQuiz.skill]) scoreTracker[skillQuiz.skill] = [];
            scoreTracker[skillQuiz.skill].push(userAnswer);

            currentQuestionIndex++;
            if (currentQuestionIndex >= skillQuiz.questions.length) {
                currentSkillIndex++;
                currentQuestionIndex = 0;
            }
            showQuestion();
        });

        div.appendChild(nextBtn);
        quizContainer.appendChild(div);
    }

    // Soumission finale du quiz
    async function submitQuiz() {
        quizContainer.innerHTML = "";
        results.textContent = "Calcul des scores et récupération des offres...";

        // Préparer payload pour backend
        const payload = {
            answers: scoreTracker,
            quiz_data: quizData.reduce((acc, q) => {
                acc[q.skill] = { questions: q.questions, used_questions: [] };
                return acc;
            }, {})
        };

        try {
            const response = await fetch("/submit-quiz/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await response.json();

            results.innerHTML = "<h3>Résultats du Quiz:</h3>";
            data.quiz_results.forEach(qr => {
                const div = document.createElement("div");
                div.innerHTML = `<strong>${qr.skill}</strong>: ${qr.score}% - ${qr.passed ? "✅ Passé" : "❌ À réviser"}`;
                if (!qr.passed && qr.study_sites.length > 0) {
                    div.innerHTML += "<br>Sites de révision: " +
                        qr.study_sites.map(s => `<a href="${s}" target="_blank">${s}</a>`).join(", ");
                }
                results.appendChild(div);
            });

            // Affichage offres si score >=50%
            if (data.offers && data.offers.length > 0) {
                const offersDiv = document.createElement("div");
                offersDiv.innerHTML = "<h3>Offres recommandées:</h3>";
                data.offers.forEach((offer, idx) => {
                    const p = document.createElement("p");
                    p.innerHTML = `<strong>${idx+1}. ${offer.title}</strong> - ${offer.company}<br>`;
                    if (offer.link) p.innerHTML += `Lien: <a href="${offer.link}" target="_blank">${offer.link}</a>`;
                    offersDiv.appendChild(p);
                });
                results.appendChild(offersDiv);
            }

        } catch (err) {
            results.textContent = "Erreur fetch : " + err;
            console.error(err);
        }
    }
});

