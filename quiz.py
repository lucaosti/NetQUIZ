import json
import os
import random
from datetime import datetime


# File paths
QUIZ_FILE = 'quiz.json'
RESULTS_FILE = 'results.txt'
ARGOMENTI_FILE = 'topics.json'

# Load topics from file
def load_argomenti():
    if not os.path.exists(ARGOMENTI_FILE):
        return []
    with open(ARGOMENTI_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)
    

def ripassa_teoria():
    argomenti = load_argomenti()
    if not argomenti:
        print("⚠️ Nessun argomento disponibile.")
        return

    categorie = sorted(set(a['categoria'] for a in argomenti))
    print("\nCategorie disponibili:")
    for i, c in enumerate(categorie, start=1):
        print(f"{i}. {c}")
    try:
        scelta = int(input("Scegli la categoria: ")) - 1
        if scelta < 0 or scelta >= len(categorie):
            print("❌ Scelta non valida.")
            return
        cat_sel = categorie[scelta]
    except ValueError:
        print("❌ Inserisci un numero valido.")
        return

    arg_cat = [a for a in argomenti if a['categoria'] == cat_sel]
    if not arg_cat:
        print("⚠️ Nessun argomento per questa categoria.")
        return

    idx = 0
    while True:
        a = arg_cat[idx]
        print(f"\n[{idx+1}/{len(arg_cat)}] {a['titolo']}\n{a['contenuto']}")
        cmd = input("\nComandi: [N]ext, [P]revious, [E]xit: ").strip().lower()
        if cmd == 'n':
            idx = (idx + 1) % len(arg_cat)
        elif cmd == 'p':
            idx = (idx - 1) % len(arg_cat)
        elif cmd == 'e':
            break
        else:
            print("Comando non riconosciuto.")
            return


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
        print("Invalid index.")
    quiz.append({
        "id": new_id,
        "domanda": domanda,
        "risposte": risposte,
        "corretta": corretta,
        "categoria": categoria
    })
    save_quiz(quiz)
    print("✅ Question added with ID", new_id)


# Extract last incorrect and skipped question IDs
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
        wrong = data.get("sbagliate", [])
        skipped = data.get("skippate", [])
        return list(set(wrong + skipped))  # merge and remove duplicates
    except json.JSONDecodeError:
        return []


# Save results to file
def save_results(score, total, wrong, skipped):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = {
        "timestamp": timestamp,
        "punteggio": f"{score:.2f}/{total}",
        "sbagliate": wrong,
        "skippate": skipped
    }
    with open(RESULTS_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")


# Create recovery quiz
def recovery_quiz():
    quiz = load_quiz()
    wrong_ids = get_last_wrong_ids()
    if not wrong_ids:
        print("✅ No topics to recover, keep practicing!")
        return
    recovery = [q for q in quiz if q["id"] in wrong_ids]
    if not recovery:
        print("⚠️ No questions found for recovery.")
        return
    run_quiz(recovery)


# Run a quiz session
def run_quiz(subset=None):
    quiz = subset if subset else load_quiz()
    if not quiz:
        print("⚠️ No questions available.")
        return

    n = len(quiz)
    if not subset:
        while True:
            try:
                requested = int(input(f"How many questions do you want (1 - {min(33, n)})? "))
                if 1 <= requested <= min(33, n):
                    quiz = random.sample(quiz, requested)
                    break
            except:
                pass
            print("Invalid value.")

    score = 0
    wrong = []
    skipped = []

    for q in quiz:
        print(f"\n[{q['categoria']}] {q['domanda']}")
        for idx, r in enumerate(q['risposte']):
            print(f"{idx + 1}. {r}")
        print("Press ENTER to skip the question (0 points).")
        try:
            choice = input("Answer: ").strip()
            if choice == "":
                print("⭕ Question skipped, 0 points.")
                skipped.append(q["id"])
            else:
                choice = int(choice) - 1
                if choice == q["corretta"]:
                    print("✔️ Correct!")
                    score += 1
                else:
                    print(f"❌ Wrong. Correct answer: {q['risposte'][q['corretta']]}")
                    score -= 0.33
                    wrong.append(q["id"])
        except:
            print("❌ Invalid answer.")
            score -= 0.33
            wrong.append(q["id"])

    print(f"\n🎯 Result: {score:.2f}/{len(quiz)}")
    save_results(score, len(quiz), wrong, skipped)


# Function to display quiz by category
def quiz_per_argomento():
    quiz = load_quiz()
    if not quiz:
        print("⚠️ No questions available.")
        return

    categories = sorted(set(q["categoria"] for q in quiz))
    print("\nAvailable categories:")
    for i, cat in enumerate(categories, start=1):
        print(f"{i}. {cat}")
    try:
        choice = int(input("Select the category number: ")) - 1
        if 0 <= choice < len(categories):
            selected_category = categories[choice]
            category_questions = [q for q in quiz if q["categoria"] == selected_category]
            n_questions = len(category_questions)
            if n_questions == 0:
                print("⚠️ No questions found for this category.")
                return
            while True:
                try:
                    requested = int(input(f"How many questions do you want (1 - {n_questions})? "))
                    if 1 <= requested <= n_questions:
                        selected_questions = random.sample(category_questions, requested)
                        break
                    else:
                        print("❌ Number out of range.")
                except ValueError:
                    print("❌ Enter a valid number.")
            run_quiz(selected_questions)
        else:
            print("❌ Invalid choice.")
    except ValueError:
        print("❌ Enter a valid number.")


# Main menu
def menu():
    while True:
        print("\n=== QUIZ MENU ===")
        print("1. Run quiz")
        print("2. Add question")
        print("3. Recovery quiz")
        print("4. Quiz by category")
        print("5. Study theory")
        print("6. Exit")
        choice = input("Choice: ")
        if choice == "1":
            run_quiz()
        elif choice == "2":
            add_question()
        elif choice == "3":
            recovery_quiz()
        elif choice == "4":
            quiz_per_argomento()
        elif choice == "5":
            ripassa_teoria()
        elif choice == "6":
            break
        else:
            print("❌ Invalid option.")
            
            
# Ensure the quiz file exists
def ensure_quiz_file():
    if not os.path.exists(QUIZ_FILE):
        with open(QUIZ_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=4, ensure_ascii=False)
    ensure_quiz_file()
    # Ensure the results file exists
def ensure_results_file():
    if not os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
            pass
    ensure_results_file()
# Ensure the arguments file exists
def ensure_argomenti_file():
    if not os.path.exists(ARGOMENTI_FILE):
        with open(ARGOMENTI_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=4, ensure_ascii=False)
    ensure_argomenti_file()
    # Ensure the arguments file exists
def ensure_argomenti_file():
    if not os.path.exists(ARGOMENTI_FILE):
        with open(ARGOMENTI_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=4, ensure_ascii=False)
    ensure_argomenti_file()


# Run the menu
if __name__ == "__main__":
    if not os.path.exists(QUIZ_FILE):
        save_quiz([])
    if not os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
            pass
    menu()