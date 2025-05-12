import json
import os
import random
from datetime import datetime

# File paths
QUIZ_FILE = 'quiz.json'
RESULTS_FILE = 'risultati.txt'

# Load quiz data
def load_quiz():
    if not os.path.exists(QUIZ_FILE):
        return []
    with open(QUIZ_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Save quiz data
def save_quiz(quiz):
    with open(QUIZ_FILE, 'w', encoding='utf-8') as f:
        json.dump(quiz, f, indent=4, ensure_ascii=False)

# Add a new question with auto-incrementing ID
def add_question():
    quiz = load_quiz()
    new_id = max((q.get("id", 0) for q in quiz), default=0) + 1
    domanda = input("Inserisci la domanda: ")
    categoria = input("Inserisci la categoria: ")
    risposte = []
    while True:
        r = input("Inserisci una possibile risposta (invio per terminare): ")
        if r == "":
            break
        risposte.append(r)
    while True:
        try:
            corretta = int(input(f"Indice della risposta corretta (0 - {len(risposte)-1}): "))
            if 0 <= corretta < len(risposte):
                break
        except:
            pass
        print("Indice non valido.")
    quiz.append({
        "id": new_id,
        "domanda": domanda,
        "risposte": risposte,
        "corretta": corretta,
        "categoria": categoria
    })
    save_quiz(quiz)
    print("✅ Domanda aggiunta con ID", new_id)

# Extract last incorrect answers
def get_last_wrong_ids():
    if not os.path.exists(RESULTS_FILE):
        return []
    with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines:
        return []
    last_line = lines[-1]
    try:
        data = json.loads(last_line)
        return data.get("sbagliate", [])
    except json.JSONDecodeError:
        return []

# Save results to file
def save_results(punteggio, totali, errori):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = {
        "timestamp": timestamp,
        "punteggio": f"{punteggio}/{totali}",
        "sbagliate": errori
    }
    with open(RESULTS_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")

# Create recovery quiz
def recovery_quiz():
    quiz = load_quiz()
    wrong_ids = get_last_wrong_ids()
    if not wrong_ids:
        print("✅ Nessun argomento da recuperare ma continua ad esercitarti!")
        return
    recovery = [q for q in quiz if q["id"] in wrong_ids]
    if not recovery:
        print("⚠️ Nessuna domanda trovata per il recupero.")
        return
    run_quiz(recovery)

# Run a quiz session
def run_quiz(subset=None):
    quiz = subset if subset else load_quiz()
    if not quiz:
        print("⚠️ Nessuna domanda disponibile.")
        return

    n = len(quiz)
    if not subset:
        while True:
            try:
                richiesta = int(input(f"Quante domande vuoi (1 - {min(33, n)})? "))
                if 1 <= richiesta <= min(33, n):
                    quiz = random.sample(quiz, richiesta)
                    break
            except:
                pass
            print("Valore non valido.")

    punteggio = 0
    errori = []

    for q in quiz:
        print(f"\n[{q['categoria']}] {q['domanda']}")
        for idx, r in enumerate(q['risposte']):
            print(f"{idx + 1}. {r}")
        try:
            scelta = int(input("Risposta: ")) - 1
            if scelta == q["corretta"]:
                print("✔️ Corretto!")
                punteggio += 1
            else:
                print(f"❌ Errato. Risposta giusta: {q['risposte'][q['corretta']]}")
                errori.append(q["id"])
        except:
            print("❌ Risposta non valida.")
            errori.append(q["id"])

    print(f"\n🎯 Risultato: {punteggio}/{len(quiz)}")
    save_results(punteggio, len(quiz), errori)
    
# Aggiungiamo la funzione "quiz per argomento" allo script esistente

def quiz_per_argomento():
    quiz = load_quiz()
    if not quiz:
        print("⚠️ Nessuna domanda disponibile.")
        return

    categorie = sorted(set(q["categoria"] for q in quiz))
    print("\nCategorie disponibili:")
    for i, cat in enumerate(categorie, start=1):
        print(f"{i}. {cat}")
    try:
        scelta = int(input("Seleziona il numero della categoria: ")) - 1
        if 0 <= scelta < len(categorie):
            categoria_scelta = categorie[scelta]
            domande_categoria = [q for q in quiz if q["categoria"] == categoria_scelta]
            run_quiz(domande_categoria)
        else:
            print("❌ Scelta non valida.")
    except ValueError:
        print("❌ Inserisci un numero valido.")

# Inseriamo questa nuova funzione nel menu

def menu_con_categoria():
    while True:
        print("\n=== QUIZ MENU ===")
        print("1. Esegui quiz")
        print("2. Aggiungi domanda")
        print("3. Quiz di recupero")
        print("4. Quiz per argomento")
        print("5. Esci")
        scelta = input("Scelta: ")
        if scelta == "1":
            run_quiz()
        elif scelta == "2":
            add_question()
        elif scelta == "3":
            recovery_quiz()
        elif scelta == "4":
            quiz_per_argomento()
        elif scelta == "5":
            break
        else:
            print("❌ Opzione non valida.")
            
# Main menu


















menu()