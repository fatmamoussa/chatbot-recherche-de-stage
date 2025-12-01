import sys
import asyncio
import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import fitz  # PyMuPDF
import spacy
import random
from questions import ADAPTIVE_QUESTIONS
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Event loop Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# FastAPI
app = FastAPI(title="Chatbot Stage IA + NLP (Quiz Adaptatif)")

# Static & Templates
BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# spaCy modèle français
try:
    nlp = spacy.load("fr_core_news_md")
except OSError:
    import subprocess
    subprocess.run([sys.executable, "-m", "spacy", "download", "fr_core_news_md"], check=True)
    nlp = spacy.load("fr_core_news_md")

# Lecture PDF
def _read_pdf_sync(path: str) -> str:
    text = ""
    with fitz.open(path) as doc:
        for page in doc:
            text += page.get_text()
    return text

async def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    tmp_name = "cv-temp.pdf"
    with open(tmp_name, "wb") as f:
        f.write(pdf_bytes)
    try:
        text = await asyncio.to_thread(_read_pdf_sync, tmp_name)
    finally:
        try:
            os.remove(tmp_name)
        except OSError:
            pass
    return text

SKILLS = list(ADAPTIVE_QUESTIONS.keys())

def extract_skills_sync(text: str) -> List[str]:
    text_lower = text.lower()
    return [kw for kw in SKILLS if kw in text_lower]

async def extract_skills(text: str) -> List[str]:
    return await asyncio.to_thread(extract_skills_sync, text)


LEVELS = ["easy", "medium", "hard"]

def generate_question(skill: str, level: str, used_questions: List[str]) -> Optional[Dict[str, Any]]:
    questions_list = [q for q in ADAPTIVE_QUESTIONS.get(skill, {}).get(level, []) if q["q"] not in used_questions]
    if not questions_list:
        return None
    q = random.choice(questions_list).copy()
    q["level"] = level
    return q

async def create_adaptive_quiz(skills: List[str], num_questions: int = 3):
    quiz_data = []
    for skill in skills:
        used = []
        skill_quiz = []
        level_idx = 0
        for _ in range(num_questions):
            level = LEVELS[level_idx]
            q = generate_question(skill, level, used)
            if not q:
                for lvl in LEVELS:
                    q = generate_question(skill, lvl, used)
                    if q:
                        break
            if not q:
                break
            skill_quiz.append(q)
            used.append(q["q"])
        if skill_quiz:
            quiz_data.append({"skill": skill, "questions": skill_quiz, "used_questions": used})
    return quiz_data

def update_level(level: str, correct: bool) -> str:
    idx = LEVELS.index(level)
    if correct and idx < len(LEVELS) - 1:
        return LEVELS[idx + 1]
    elif not correct and idx > 0:
        return LEVELS[idx - 1]
    return level

# ============================
# Scraping Indeed (selenium)
# ============================
def scrape_indeed_selenium(keyword, max_pages=2, max_offers=2):
    offers = []
    seen_links = set()
    options = uc.ChromeOptions()
    # options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options)
    try:
        for page in range(max_pages):
            start = page * 10
            url = f"https://www.indeed.com/jobs?q={keyword}&start={start}"
            driver.get(url)
            try:
                driver.find_element(By.CSS_SELECTOR, "button#onetrust-accept-btn-handler").click()
            except:
                pass
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.job_seen_beacon, div.cardOutline"))
            )
            jobs = driver.find_elements(By.CSS_SELECTOR, "div.job_seen_beacon, div.cardOutline")
            for job in jobs:
                try:
                    title = job.find_element(By.CSS_SELECTOR, "h2.jobTitle").text
                except:
                    title = job.text.split("\n")[0]
                company = "Entreprise inconnue"
                try:
                    company_elem = job.find_element(By.CSS_SELECTOR, 'a[href*="/cmp/"]')
                    if company_elem.text.strip():
                        company = company_elem.text.strip()
                except:
                    try:
                        company_elem = job.find_element(By.XPATH, './/span[contains(@class, "company")]')
                        if company_elem.text.strip():
                            company = company_elem.text.strip()
                    except:
                        try:
                            company = job.text.split("\n")[1]
                        except:
                            pass
                try:
                    link = job.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                except:
                    link = url
                if link in seen_links:
                    continue
                seen_links.add(link)
                offers.append({
                    "title": title,
                    "company": company,
                    "link": link,
                    "matched_skill": keyword
                })
                if len(offers) >= max_offers:
                    break
            if len(offers) >= max_offers:
                break
    finally:
        try:
            driver.quit()
        except:
            pass
    if not offers:
        offers.append({"error": f"Aucune offre récente trouvée pour {keyword}.", "matched_skill": keyword})
    return offers

async def real_job_offers(skills: List[str]):
    results = []
    for skill in skills:
        try:
            offers = await asyncio.to_thread(scrape_indeed_selenium, skill)
            results.extend(offers)
        except Exception as e:
            results.append({"error": str(e)})
    return results

# ============================
# Routes FastAPI
# ============================
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception:
        return HTMLResponse("<h1>Bienvenue - Chatbot Stage IA + NLP</h1><p>Upload votre CV via /upload-cv/</p>")

@app.post("/upload-cv/")
async def upload_cv(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = await extract_text_from_pdf_bytes(content)
        skills = await extract_skills(text)
        dynamic_quiz = await create_adaptive_quiz(skills, num_questions=3)
        return {"quiz": dynamic_quiz, "extracted_skills": skills}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    
    
@app.post("/submit-quiz/")
async def submit_quiz(data: Dict[str, Any]):
    try:
        answers = data.get("answers", {})
        previous_quiz = data.get("quiz_data", {})  # contient questions et used_questions
        results = []
        validated_skills = []

        for skill, user_ans_list in answers.items():
            skill_quiz = previous_quiz.get(skill, {})
            questions = skill_quiz.get("questions", [])
            used_questions = skill_quiz.get("used_questions", [])
            correct_count = 0
            current_level = "easy"

            # Vérifier les réponses et générer la prochaine question adaptative immédiatement
            next_quiz = []

            for i, ans in enumerate(user_ans_list):
                if i >= len(questions):
                    continue
                correct_index = questions[i]["correct"]
                is_correct = ans == correct_index
                if is_correct:
                    correct_count += 1

                # Marquer la question comme utilisée
                used_questions.append(questions[i]["q"])

                # Mettre à jour le niveau pour la prochaine question
                current_level = update_level(current_level, is_correct)

                # Générer la prochaine question adaptative si on n’a pas atteint le nombre maximum
                if len(next_quiz) < 3:
                    q = generate_question(skill, current_level, used_questions)
                    if q:
                        next_quiz.append(q)
                        used_questions.append(q["q"])

            # Calcul du score correct
            total_questions = len(user_ans_list)
            score = int((correct_count / total_questions) * 100) if total_questions > 0 else 0

            # Sites d’apprentissage si score < 50
            study_sites = []
            if score < 50:
                if skill == "python":
                    study_sites = ["https://www.learnpython.org/", "https://realpython.com/"]
                elif skill == "java":
                    study_sites = ["https://www.w3schools.com/java/", "https://www.geeksforgeeks.org/java/"]

            # Ajouter les résultats du skill
            results.append({
                "skill": skill,
                "score": score,
                "passed": score >= 50,
                "study_sites": study_sites,
                "next_adaptive_questions": next_quiz
            })

            if score >= 50:
                validated_skills.append(skill)

        # Offres pour les compétences validées
        offers = await real_job_offers(validated_skills) if validated_skills else []

        return {"quiz_results": results, "offers": offers}

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
