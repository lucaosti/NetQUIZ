import json
import random
from datetime import datetime

QUIZ_FILE = 'quiz.json'
RISULTATI_FILE = 'risultati.txt'

def carica_quiz():
    try:
        with open(QUIZ_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def salva_quiz(quiz):
    with open(QUIZ_FILE, 'w') as f:
        json.dump(quiz, f, indent=4)

def aggiungi_domanda():
    quiz = carica_quiz()
    domanda = input("Inserisci la domanda: ")
    categoria = input("Inserisci la categoria della domanda: ")
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
        "domanda": domanda,
        "risposte": risposte,
        "corretta": corretta,
        "categoria": categoria
    })
    salva_quiz(quiz)
    print("✅ Domanda aggiunta con successo.")

def esegui_quiz():
    quiz = carica_quiz()
    if not quiz:
        print("⚠️ Nessuna domanda disponibile.")
        return

    max_domande = min(len(quiz), 33)
    while True:
        try:
            n = int(input(f"Quante domande vuoi (1 - {max_domande})? "))
            if 1 <= n <= max_domande:
                break
        except:
            pass
        print("Numero non valido.")

    domande = random.sample(quiz, n)
    punteggio = 0

    for i, q in enumerate(domande, 1):
        print(f"\nDomanda {i}/{n} [{q['categoria']}]: {q['domanda']}")
        for idx, risposta in enumerate(q['risposte']):
            print(f"{idx + 1}. {risposta}")
        try:
            scelta = int(input("Risposta (numero): ")) - 1
            if scelta == q["corretta"]:
                print("✔️ Corretto!")
                punteggio += 1
            else:
                print(f"❌ Errato. Risposta giusta: {q['risposte'][q['corretta']]}")
        except:
            print("❌ Risposta non valida.")

    print(f"\n🎯 Risultato: {punteggio}/{n}")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(RISULTATI_FILE, 'a') as f:
        f.write(f"{timestamp} - Punteggio: {punteggio}/{n}\n")

def menu():
    while True:
        print("\n=== QUIZ LTE ===")
        print("1. Esegui quiz")
        print("2. Aggiungi nuova domanda")
        print("3. Esci")
        scelta = input("Scelta: ")
        if scelta == "1":
            esegui_quiz()
        elif scelta == "2":
            aggiungi_domanda()
        elif scelta == "3":
            break
        else:
            print("Opzione non valida.")

if __name__ == "__main__":
    menu()
