import json
import os
import time
import random
from collections import Counter, defaultdict
from datetime import datetime


# File paths
QUIZ_FILE = 'quiz.json'
RESULTS_FILE = 'results.txt'
ARGOMENTI_FILE = 'topics.json'
PROGRESS_FILE = 'progress.json'
STATS_FILE = "stats.json"


# Load topics from file
def load_topics():
    if not os.path.exists(ARGOMENTI_FILE):
        return []
    with open(ARGOMENTI_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def study_theory():
    argomenti = load_topics()
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


def save_progress(start_time, quiz, score, wrong, skipped):
    duration = int(time.time() - start_time)
    total = len(quiz)
    correct = total - len(wrong) - len(skipped)
    accuracy = (correct / total) * 100 if total else 0
    categories = sorted(set(q["categoria"] for q in quiz))

    progress_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_questions": total,
        "score": round(score, 2),
        "correct": correct,
        "wrong": len(wrong),
        "skipped": len(skipped),
        "accuracy_percent": round(accuracy, 2),
        "duration_sec": duration,
        "categories": categories
    }

    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(progress_entry)

    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def show_study_stats():
    if not os.path.exists(STATS_FILE) or os.path.getsize(STATS_FILE) == 0:
        print("⚠️ Nessun progresso registrato.")
        return

    with open(STATS_FILE, "r", encoding="utf-8") as f:
        try:
            stats = json.load(f)
        except json.JSONDecodeError:
            print("⚠️ Errore nella lettura del file di statistiche.")
            return

    print("\n📈 Statistiche di studio:")
    print(f"Totale quiz completati: {stats.get('quiz_totali', 0)}")
    print(f"Domande corrette:       {stats.get('domande_corrette', 0)}")
    print(f"Domande sbagliate:      {stats.get('domande_sbagliate', 0)}")
    print(f"Domande saltate:        {stats.get('domande_skippate', 0)}")

    per_categoria = stats.get("per_categoria", {})
    if per_categoria:
        print("\n📊 Statistiche per categoria:")
        for cat, s in per_categoria.items():
            print(f"- {cat}: {s['corrette']} corrette, {s['sbagliate']} sbagliate")


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
            corretta = int(
                input(f"Indice della risposta corretta (0 - {len(risposte)-1}): "))
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


def update_study_stats(quiz, wrong, skipped):
    total = len(quiz)
    correct = total - len(wrong) - len(skipped)

    # Carica stats cumulative
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            try:
                stats = json.load(f)
            except json.JSONDecodeError:
                stats = {}
    else:
        stats = {}

    # Inizializza se mancano
    stats.setdefault("quiz_totali", 0)
    stats.setdefault("domande_corrette", 0)
    stats.setdefault("domande_sbagliate", 0)
    stats.setdefault("domande_skippate", 0)
    stats.setdefault("per_categoria", {})

    # Aggiorna totali
    stats["quiz_totali"] += 1
    stats["domande_corrette"] += correct
    stats["domande_sbagliate"] += len(wrong)
    stats["domande_skippate"] += len(skipped)

    # Aggiorna per categoria
    for q in quiz:
        cat = q["categoria"]
        if cat not in stats["per_categoria"]:
            stats["per_categoria"][cat] = {"corrette": 0, "sbagliate": 0}
        if q["id"] in wrong:
            stats["per_categoria"][cat]["sbagliate"] += 1
        elif q["id"] not in skipped:
            stats["per_categoria"][cat]["corrette"] += 1

    # Salva
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)


# Run a quiz session
def run_quiz(subset=None):
    start_time = time.time()
    quiz = subset if subset else load_quiz()
    if not quiz:
        print("⚠️ No questions available.")
        return [], [], []

    if not subset:
        total_questions = len(quiz)
        categories = list(set(q["categoria"] for q in quiz))

        while True:
            try:
                requested = int(
                    input(f"How many questions do you want (1 - {min(33, total_questions)})? "))
                if 1 <= requested <= min(33, total_questions):
                    break
            except:
                pass
            print("Invalid value.")

        min_categories = min(requested // 2, len(categories), 15)
        selected_questions = []
        selected_categories = random.sample(categories, min_categories)

        for cat in selected_categories:
            questions_in_cat = [q for q in quiz if q["categoria"] == cat]
            if questions_in_cat:
                selected_questions.append(random.choice(questions_in_cat))

        remaining_needed = requested - len(selected_questions)
        remaining_pool = [q for q in quiz if q not in selected_questions]

        if remaining_needed > 0:
            selected_questions += random.sample(
                remaining_pool, remaining_needed)

        random.shuffle(selected_questions)
        quiz = selected_questions

    # Stato quiz
    n = len(quiz)
    risposte = [None] * n
    idx = 0

    while True:
        q = quiz[idx]
        print(f"\n[{idx+1}/{n}] [{q['categoria']}] {q['domanda']}")
        for i, r in enumerate(q["risposte"]):
            print(f"{i+1}. {r}")
        if risposte[idx] is None:
            print("Press ENTER to skip.")
            inp = input(
                "Answer / [N]ext / [P]rev / [F]inish: ").strip().lower()
            if inp == "n":
                idx = (idx + 1) % n
                continue
            elif inp == "p":
                idx = (idx - 1) % n
                continue
            elif inp == "f":
                break
            elif inp == "":
                risposte[idx] = "skip"
            else:
                try:
                    ans = int(inp) - 1
                    if 0 <= ans < len(q["risposte"]):
                        risposte[idx] = ans
                    else:
                        print("❌ Invalid answer index.")
                except:
                    print("❌ Invalid input.")
        else:
            status = "skipped" if risposte[
                idx] == "skip" else f"answered: {q['risposte'][risposte[idx]]}"
            print(f"✅ Already {status}.")
            inp = input(
                "Command: [N]ext / [P]rev / [C]hange / [F]inish: ").strip().lower()
            if inp == "n":
                idx = (idx + 1) % n
            elif inp == "p":
                idx = (idx - 1) % n
            elif inp == "c":
                risposte[idx] = None
            elif inp == "f":
                break

    # Calcolo punteggio
    score = 0
    wrong = []
    skipped = []

    for i, r in enumerate(risposte):
        q = quiz[i]
        if r == "skip":
            skipped.append(q["id"])
        elif r == q["corretta"]:
            score += 1
        else:
            score -= 0.33
            wrong.append(q["id"])

    print(f"\n🎯 Final Score: {score:.2f}/{n}")
    save_results(score, n, wrong, skipped)
    save_progress(start_time, quiz, score, wrong, skipped)
    return quiz, wrong, skipped


def quiz_by_category():
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
            category_questions = [
                q for q in quiz if q["categoria"] == selected_category]
            n_questions = len(category_questions)
            if n_questions == 0:
                print("⚠️ No questions found for this category.")
                return
            while True:
                try:
                    requested = int(
                        input(f"How many questions do you want (1 - {n_questions})? "))
                    if 1 <= requested <= n_questions:
                        selected_questions = random.sample(
                            category_questions, requested)
                        break
                    else:
                        print("❌ Number out of range.")
                except ValueError:
                    print("❌ Enter a valid number.")
            quiz_data, wrong, skipped = run_quiz(selected_questions)
            update_study_stats(quiz_data, wrong, skipped)
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
        print("6. View study statistics")
        print("7. Exit")
        choice = input("Choice: ")
        if choice == "1":
            run_quiz()
        elif choice == "2":
            add_question()
        elif choice == "3":
            recovery_quiz()
        elif choice == "4":
            quiz_by_category()
        elif choice == "5":
            study_theory()
        elif choice == "6":
            show_study_stats()
        elif choice == "7":
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
