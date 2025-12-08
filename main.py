import sys
import asyncio
import os
import json
from typing import List, Optional, Dict, Any, Tuple
from fastapi import FastAPI, UploadFile, File, Request, WebSocket, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import fitz  # PyMuPDF
import spacy
import random
from datetime import datetime
from questions import ADAPTIVE_QUESTIONS, LEVEL_THRESHOLDS, LEVEL_REWARDS, XP_BY_DIFFICULTY, XP_CORRECT_ANSWER, STREAK_BONUS
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from study_sites import STUDY_SITES

# Event loop Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# FastAPI
app = FastAPI(title="Chatbot Stage IA + NLP (Système de Niveaux)")

# Static & Templates
BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Fichier de stockage des niveaux utilisateurs
USER_PROGRESS_FILE = os.path.join(DATA_DIR, "user_progress.json")

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

# ========================================
# SYSTÈME DE NIVEAUX ET PROGRESSION
# ========================================

def load_user_progress(user_id: str = "default") -> Dict[str, Any]:
    """Charge la progression de l'utilisateur"""
    try:
        if os.path.exists(USER_PROGRESS_FILE):
            with open(USER_PROGRESS_FILE, 'r') as f:
                data = json.load(f)
                return data.get(user_id, {
                    "user_id": user_id,
                    "skills": {},
                    "total_xp": 0,
                    "global_level": "Débutant",
                    "level_up_history": [],
                    "created_at": datetime.now().isoformat()
                })
    except:
        pass
    
    return {
        "user_id": user_id,
        "skills": {},
        "total_xp": 0,
        "global_level": "Débutant",
        "level_up_history": [],
        "created_at": datetime.now().isoformat()
    }

def save_user_progress(user_id: str, progress: Dict[str, Any]):
    """Sauvegarde la progression de l'utilisateur"""
    try:
        data = {}
        if os.path.exists(USER_PROGRESS_FILE):
            with open(USER_PROGRESS_FILE, 'r') as f:
                data = json.load(f)
        
        data[user_id] = progress
        
        with open(USER_PROGRESS_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except:
        pass

def calculate_xp_earned(skill: str, answers: List[int], questions: List[Dict]) -> Dict[str, Any]:
    """Calcule l'XP gagné pour une session de quiz"""
    total_xp = 0
    correct_count = 0
    streak = 0
    max_streak = 0
    xp_details = []
    
    for i, (answer, question) in enumerate(zip(answers, questions)):
        difficulty = question.get("level", "easy")
        base_xp = XP_BY_DIFFICULTY.get(difficulty, 10)
        
        # XP de base pour la question
        question_xp = base_xp
        
        # Vérifier si la réponse est correcte
        is_correct = answer == question["correct"]
        
        if is_correct:
            correct_count += 1
            streak += 1
            max_streak = max(max_streak, streak)
            
            # Bonus pour bonne réponse
            bonus_xp = XP_CORRECT_ANSWER.get(difficulty, 5)
            question_xp += bonus_xp
            
            # Bonus pour streak
            if streak in STREAK_BONUS:
                streak_bonus = STREAK_BONUS[streak]
                question_xp += streak_bonus
        else:
            streak = 0
        
        total_xp += question_xp
        
        xp_details.append({
            "question_index": i,
            "difficulty": difficulty,
            "is_correct": is_correct,
            "base_xp": base_xp,
            "bonus_xp": question_xp - base_xp,
            "total_xp": question_xp,
            "streak": streak
        })
    
    # Bonus de session pour bon score
    if correct_count >= len(questions) * 0.8:  # 80% ou plus de bonnes réponses
        session_bonus = 50
        total_xp += session_bonus
        xp_details.append({
            "type": "session_bonus",
            "reason": "Score élevé (>80%)",
            "bonus_xp": session_bonus
        })
    
    return {
        "total_xp_earned": total_xp,
        "correct_count": correct_count,
        "total_questions": len(questions),
        "accuracy": correct_count / len(questions) if questions else 0,
        "max_streak": max_streak,
        "xp_details": xp_details
    }

def update_skill_level(skill: str, xp_earned: int, current_progress: Dict[str, Any]) -> Dict[str, Any]:
    """Met à jour le niveau d'une compétence"""
    skill_data = current_progress.get("skills", {}).get(skill, {
        "skill": skill,
        "xp": 0,
        "level": "Débutant",
        "questions_answered": 0,
        "correct_answers": 0,
        "accuracy": 0,
        "last_practiced": None
    })
    
    # Mettre à jour l'XP
    old_xp = skill_data["xp"]
    new_xp = old_xp + xp_earned
    
    # Trouver l'ancien niveau
    old_level = skill_data["level"]
    new_level = old_level
    
    # Déterminer le nouveau niveau
    for level_name, threshold in sorted(LEVEL_THRESHOLDS.items(), key=lambda x: x[1]):
        if new_xp >= threshold:
            new_level = level_name
    
    # Vérifier le level up
    level_up = old_level != new_level
    level_up_info = None
    
    if level_up:
        level_up_info = {
            "skill": skill,
            "old_level": old_level,
            "new_level": new_level,
            "old_xp": old_xp,
            "new_xp": new_xp,
            "xp_earned": xp_earned,
            "timestamp": datetime.now().isoformat(),
            "reward": LEVEL_REWARDS.get(new_level, {})
        }
        
        # Ajouter à l'historique
        current_progress["level_up_history"].append(level_up_info)
    
    # Mettre à jour les données de la compétence
    skill_data.update({
        "xp": new_xp,
        "level": new_level,
        "questions_answered": skill_data.get("questions_answered", 0) + 1,
        "correct_answers": skill_data.get("correct_answers", 0) + (xp_earned // 10),  # Estimation
        "last_practiced": datetime.now().isoformat(),
        "accuracy": skill_data.get("accuracy", 0)  # À calculer proprement
    })
    
    # Mettre à jour dans la progression
    if "skills" not in current_progress:
        current_progress["skills"] = {}
    current_progress["skills"][skill] = skill_data
    
    # Mettre à jour l'XP global
    current_progress["total_xp"] = current_progress.get("total_xp", 0) + xp_earned
    
    # Mettre à jour le niveau global
    global_xp = current_progress["total_xp"]
    global_level = "Débutant"
    for level_name, threshold in sorted(LEVEL_THRESHOLDS.items(), key=lambda x: x[1]):
        if global_xp >= threshold:
            global_level = level_name
    current_progress["global_level"] = global_level
    
    return {
        "skill_progress": skill_data,
        "level_up": level_up_info,
        "global_progress": {
            "total_xp": current_progress["total_xp"],
            "global_level": global_level
        }
    }

def get_level_progress(xp: int, current_level: str) -> Dict[str, Any]:
    """Calcule la progression vers le prochain niveau"""
    levels = list(LEVEL_THRESHOLDS.keys())
    
    if current_level not in levels:
        return {"progress_percent": 0, "xp_to_next": 0}
    
    current_index = levels.index(current_level)
    
    # Si c'est le niveau maximum
    if current_index == len(levels) - 1:
        return {
            "current_level": current_level,
            "next_level": None,
            "xp_current": xp,
            "xp_needed": 0,
            "progress_percent": 100,
            "is_max_level": True
        }
    
    # Niveau suivant
    next_level = levels[current_index + 1]
    current_threshold = LEVEL_THRESHOLDS[current_level]
    next_threshold = LEVEL_THRESHOLDS[next_level]
    
    xp_in_level = xp - current_threshold
    xp_needed = next_threshold - current_threshold
    
    progress_percent = (xp_in_level / xp_needed) * 100 if xp_needed > 0 else 0
    
    return {
        "current_level": current_level,
        "next_level": next_level,
        "xp_current": xp_in_level,
        "xp_needed": xp_needed,
        "progress_percent": min(100, progress_percent),
        "is_max_level": False
    }

def get_level_badge(level: str) -> Dict[str, Any]:
    """Retourne les informations du badge de niveau"""
    return LEVEL_REWARDS.get(level, LEVEL_REWARDS["Débutant"])

# ========================================
# GÉNÉRATION DU QUIZ
# ========================================

LEVELS = ["easy", "medium", "hard"]

def generate_question(skill: str, level: str, used_questions: List[str]) -> Optional[Dict[str, Any]]:
    questions_list = [q for q in ADAPTIVE_QUESTIONS.get(skill, {}).get(level, []) if q["q"] not in used_questions]
    if not questions_list:
        return None
    q = random.choice(questions_list).copy()
    q["level"] = level
    q["time_limit"] = 50
    return q

async def create_adaptive_quiz(skills: List[str], num_questions: int = 3):
    """Crée un quiz adaptatif basé sur les compétences"""
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
            quiz_data.append({
                "skill": skill, 
                "questions": skill_quiz, 
                "used_questions": used,
                "skill_info": get_level_badge("Débutant")  # Niveau initial
            })
    
    return quiz_data

def update_level(level: str, correct: bool) -> str:
    """Met à jour le niveau de difficulté basé sur la réponse"""
    idx = LEVELS.index(level)
    if correct and idx < len(LEVELS) - 1:
        return LEVELS[idx + 1]
    elif not correct and idx > 0:
        return LEVELS[idx - 1]
    return level

# ========================================
# SCRAPING INDEED
# ========================================
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

async def real_job_offers_by_skill(skills: List[str], offers_per_skill: int = 2):
    """Récupère des offres d'emploi pour chaque compétence validée"""
    all_offers = []
    
    # Pour chaque compétence, chercher des offres
    for skill in skills:
        try:
            # Scraper pour cette compétence
            skill_offers = await asyncio.to_thread(
                scrape_indeed_selenium, 
                skill, 
                max_pages=1, 
                max_offers=offers_per_skill
            )
            
            # Ajouter le nom de la compétence à chaque offre
            for offer in skill_offers:
                offer["skill"] = skill
                all_offers.append(offer)
                
        except Exception as e:
            print(f"Erreur pour {skill}: {str(e)}")
            # Ajouter un message d'erreur pour cette compétence
            all_offers.append({
                "error": f"Erreur de scraping pour {skill}",
                "skill": skill,
                "matched_skill": skill
            })
    
    return all_offers

# ========================================
# ROUTES FASTAPI
# ========================================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload-cv/")
async def upload_cv(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = await extract_text_from_pdf_bytes(content)
        skills = await extract_skills(text)
        
        if not skills:
            return JSONResponse({
                "error": "Aucune compétence détectée dans votre CV",
                "message": "Essayez avec un CV contenant des technologies comme Python, JavaScript, React, etc."
            })
        
        # Charger la progression utilisateur
        user_progress = load_user_progress()
        
        # Ajouter les infos de niveau aux compétences
        enhanced_skills = []
        for skill in skills:
            skill_progress = user_progress.get("skills", {}).get(skill, {
                "level": "Débutant",
                "xp": 0
            })
            enhanced_skills.append({
                "skill": skill,
                "current_level": skill_progress["level"],
                "xp": skill_progress["xp"],
                "badge": get_level_badge(skill_progress["level"])
            })
        
        # Créer le quiz
        dynamic_quiz = await create_adaptive_quiz(skills, num_questions=3)
        
        return {
            "quiz": dynamic_quiz,
            "skills": enhanced_skills,
            "user_progress": {
                "global_level": user_progress.get("global_level", "Débutant"),
                "total_xp": user_progress.get("total_xp", 0)
            },
            "message": f"✅ {len(skills)} compétence(s) détectée(s)"
        }
        
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
@app.post("/submit-quiz/")
async def submit_quiz(data: Dict[str, Any]):
    try:
        answers = data.get("answers", {})
        previous_quiz = data.get("quiz_data", {})
        user_id = data.get("user_id", "default")
        
        # Charger la progression actuelle
        user_progress = load_user_progress(user_id)
        
        results = []
        validated_skills = []
        level_up_notifications = []
        
        for skill, user_ans_list in answers.items():
            skill_quiz = previous_quiz.get(skill, {})
            questions = skill_quiz.get("questions", [])
            
            if not questions:
                continue
            
            # Calculer le score
            correct_count = sum(1 for i, ans in enumerate(user_ans_list) 
                              if i < len(questions) and ans == questions[i]["correct"])
            total_questions = len(user_ans_list)
            score = int((correct_count / total_questions) * 100) if total_questions > 0 else 0
            
            # Calculer l'XP gagné
            xp_result = calculate_xp_earned(skill, user_ans_list, questions)
            
            # Mettre à jour le niveau
            update_result = update_skill_level(skill, xp_result["total_xp_earned"], user_progress)
            
            # Vérifier le level up
            if update_result["level_up"]:
                level_up_notifications.append(update_result["level_up"])
            
            # Progression vers le prochain niveau
            skill_progress = update_result["skill_progress"]
            level_progress = get_level_progress(
                skill_progress["xp"], 
                skill_progress["level"]
            )
            
            # Sites d'apprentissage si score < 50
            study_sites = []
            if score < 50:
                study_sites = STUDY_SITES.get(skill, [])
            
            # Ajouter aux résultats
            results.append({
                "skill": skill,
                "score": score,
                "passed": score >= 50,
                "study_sites": study_sites,
                "xp_earned": xp_result["total_xp_earned"],
                "current_level": skill_progress["level"],
                "level_progress": level_progress,
                "badge": get_level_badge(skill_progress["level"]),
                "accuracy": xp_result["accuracy"],
                "streak": xp_result["max_streak"],
                "details": xp_result
            })
            
            if score >= 50:
                validated_skills.append(skill)
        
        # Sauvegarder la progression
        save_user_progress(user_id, user_progress)
        
        # Offres d'emploi pour TOUTES les compétences validées (2 offres par compétence)
        offers = []
        if validated_skills:
            offers = await real_job_offers_by_skill(validated_skills, offers_per_skill=2)
        
        # Grouper les offres par compétence pour l'affichage
        offers_by_skill = {}
        for skill in validated_skills:
            skill_offers = [o for o in offers if o.get("skill") == skill]
            offers_by_skill[skill] = skill_offers
        
        # Statistiques globales
        global_stats = {
            "total_xp": user_progress.get("total_xp", 0),
            "global_level": user_progress.get("global_level", "Débutant"),
            "skills_learned": len(user_progress.get("skills", {})),
            "total_questions_answered": sum(
                s.get("questions_answered", 0) 
                for s in user_progress.get("skills", {}).values()
            )
        }
        
        return {
            "quiz_results": results,
            "offers": offers,  # Toutes les offres
            "offers_by_skill": offers_by_skill,  # Offres groupées par compétence
            "validated_skills": validated_skills,
            "level_up_notifications": level_up_notifications,
            "global_stats": global_stats,
            "user_progress": user_progress
        }
        
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/user-progress/{user_id}")
async def get_user_progress(user_id: str):
    """Récupère la progression d'un utilisateur"""
    progress = load_user_progress(user_id)
    
    # Calculer les statistiques détaillées
    skills_progress = []
    for skill, data in progress.get("skills", {}).items():
        level_progress = get_level_progress(data["xp"], data["level"])
        skills_progress.append({
            "skill": skill,
            **data,
            "level_progress": level_progress,
            "badge": get_level_badge(data["level"])
        })
    
    # Trier par XP
    skills_progress.sort(key=lambda x: x["xp"], reverse=True)
    
    return {
        "user_id": user_id,
        "global_stats": {
            "total_xp": progress.get("total_xp", 0),
            "global_level": progress.get("global_level", "Débutant"),
            "skills_count": len(skills_progress),
            "level_up_count": len(progress.get("level_up_history", []))
        },
        "skills": skills_progress,
        "level_up_history": progress.get("level_up_history", [])[-10:],  # 10 derniers level ups
        "created_at": progress.get("created_at")
    }

@app.post("/reset-progress/{user_id}")
async def reset_progress(user_id: str):
    """Réinitialise la progression d'un utilisateur"""
    progress = {
        "user_id": user_id,
        "skills": {},
        "total_xp": 0,
        "global_level": "Débutant",
        "level_up_history": [],
        "created_at": datetime.now().isoformat()
    }
    
    save_user_progress(user_id, progress)
    
    return {
        "message": "Progression réinitialisée avec succès",
        "new_progress": progress
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)