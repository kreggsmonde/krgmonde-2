import os
import requests
from dotenv import load_dotenv

load_dotenv()

POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")

def generate_french_psychology_topics(num_topics=100):
    """Generate psychology and self-improvement topics in French using AI."""

    url = "https://gen.pollinations.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
        "Content-Type": "application/json"
    }

    system = (
        "Tu es un expert en psychologie et developpement personnel. "
        "Genere des courts titres sur la psychologie, les emotions, les relations humaines, "
        "la productivite, le bien-etre mental, la confiance en soi, et la croissance personnelle. "
        "NE GENERE PAS d'histoires pour enfants. NE GENERE PAS d'animaux. "
        "Chaque titre doit etre un sujet concret et utile pour les adultes. "
        "Genere UNIQUEMENT les titres, chacun sur une nouvelle ligne, sans numerotation."
    )

    prompt = (
        f"Genere {num_topics} titres uniques sur la psychologie et le developpement personnel en francais. "
        "Sujets demandes: "
        "- Gestion des emotions (colere, stress, anxiete, tristesse, peur) "
        "- Confiance en soi (estime de soi, courage, prise de decision) "
        "- Relations humaines (communication, empathie, conflits, couples, famille) "
        "- Habitudes et productivite (routine, discipline, procrastination, organisation) "
        "- Bien-etre mental (meditation, pleine conscience, gratitude, sante mentale) "
        "- Motivation et objectifs (perseverance, reussite, echec, ambitions) "
        "- Psychologie cognitive (biais, prise de decision, pensee positive) "
        "- Developpement personnel (lucidite, introspection, evolution personnelle) "
        "Chaque titre sur une nouvelle ligne, sans numeros."
    )

    payload = {
        "model": "openai",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "temperature": 1.2
    }

    print(f"[topics] Generating {num_topics} psychology topics in French...")

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        text = data['choices'][0]['message']['content'].strip()

        topics = [line.strip() for line in text.split('\n') if line.strip()]

        cleaned_topics = []
        for topic in topics:
            topic = topic.lstrip('0123456789.-) ')
            if len(topic) > 10 and not topic.startswith('['):
                cleaned_topics.append(topic)

        if len(cleaned_topics) < num_topics:
            print(f"[topics] {len(cleaned_topics)} topics generated, trying to generate more...")
            additional_needed = num_topics - len(cleaned_topics)
            if additional_needed > 0:
                additional_topics = generate_french_psychology_topics(additional_needed)
                cleaned_topics.extend(additional_topics)

        return cleaned_topics[:num_topics]

    except Exception as e:
        print(f"[topics] Error generating topics: {e}")
        return get_fallback_topics()[:num_topics]

def get_fallback_topics():
    """Fallback psychology/self-improvement topics in French."""
    return [
        "La puissance de la gratitude au quotidien",
        "Comment gerer le stress efficacement",
        "Les habitudes qui transforment votre vie",
        "Apprendre a dire non avec bienveillance",
        "La confiance en soi commence par la pensee",
        "Pourquoi l'echec est votre meilleur enseignant",
        "Les secrets d'une matinee productive",
        "Comment surmonter la procrastination",
        "L'art de la communication non violente",
        "La meditation pour debutants",
        "Comment developper l'empathie",
        "Les bienfaits de la pleine conscience",
        "Pourquoi la routine est liberatrice",
        "Comment gerer la colere constructivement",
        "L'importance du self-care",
        "Comment motiver soi-meme",
        "Les 5 langages de l'amour",
        "Pourquoi la comparaison est destructrice",
        "Comment creer de bonnes habitudes",
        "La puissance du positivisme",
        "Gestion du temps et productivite",
        "Comment vaincre la peur de l'echec",
        "L'art de la patience",
        "Les bienfaits de l'ecriture expressive",
        "Comment developper la resilience",
        "La confiance dans les relations",
        "Pourquoi la vulnerable est une force",
        "Comment gerer l'anxiete sociale",
        "Les bases de l'intelligence emotionnelle",
        "Comment cultiver la joie",
        "La philosophie du bonheur",
        "Les secrets des gens heureux",
        "Comment sortir de sa zone de confort",
        "L'importance de l'entourage",
        "Comment developper la creativite",
        "La psychologie du succes",
        "Les erreurs a eviter en communication",
        "Comment guerir ses blessures du passe",
        "La puissance de l'autocompassion",
        "Les regles d'or de l'estime de soi",
        "Comment trouver sa vocation",
        "La sagesse dans les petits gestes",
        "Les bases d'une vie equilibree",
        "Comment gerer le deuil et les pertes",
        "L'art de l'ecoute active",
        "Pourquoi la solitude peut etre benefique",
        "Comment developper la discipline",
        "Les mythes sur le bonheur",
        "La psychologie des habitudes",
        "Comment vaincre les croyances limitantes",
        "L'importance du rire",
        "Les techniques de relaxation",
        "Comment gerer les conflits",
        "La philosophie stoicienne pour la vie moderne",
        "Les cles de la motivation durable",
        "Comment developper l'intuition",
        "La psychologie du changement",
        "Les erreurs courantes en gestion du stress",
        "Comment creer un environnement positif",
        "L'art de la gratitude pratique",
        "Les bases de la communication assertive",
        "Comment vaincre la peur du jugement",
        "La psychologie de la reussite",
        "Les secrets de la productivite",
        "Comment gerer les emotions fortes",
        "L'importance des limites personnelles",
        "La philosophie du bonheur simple",
        "Les bases de la psychologie positive",
        "Comment developper la confiance",
        "La puissance des affirmations positives",
        "Les regles de la vie equilibree",
        "Comment surmonter les difficultes",
        "L'art de la simplicite volontaire",
        "La psychologie des relations",
        "Les cles de la communication efficace",
        "Comment gerer le changement",
        "La sagesse des stoiciens",
        "Les bases de la pleine conscience",
        "Comment developper la perseverance",
        "La psychologie du bonheur durable",
        "Les secrets de l'estime de soi",
        "Comment vaincre les habitudes negatives",
        "L'importance de l'autocompassion",
        "La philosophie de la resilience",
        "Les regles de la gestion du temps",
        "Comment gerer la frustration",
        "La puissance de la meditation",
        "Les bases de l'intelligence sociale",
        "Comment developper la sagesse",
        "La psychologie de la motivation",
        "Les secrets de la vie equilibree",
        "Comment gerer l'incertitude",
        "L'art de la serenite",
        "La philosophie du bien-etre",
        "Les bases de la communication non violente",
        "Comment developper la creativite",
        "La psychologie de la confiance",
        "Les regles de l'estime de soi",
        "Comment vaincre la procrastination",
        "L'importance de la croissance personnelle",
        "La philosophie du developpement personnel",
        "Les bases de la gestion des emotions",
        "Comment gerer le stress au quotidien",
        "La puissance de la positivite",
        "Les secrets de la vie heureuse",
        "Comment developper la patience",
        "L'art de la communication bienveillante",
        "La psychologie du succes personnel",
        "Les regles de la productivite",
        "Comment gerer les conflits interpersonnels",
        "La philosophie de la reussite",
        "Les bases de la resilience emotionnelle"
    ]

def save_topics_to_file(topics, filename="topics.txt"):
    """Save topics to file."""
    with open(filename, "w", encoding="utf-8") as f:
        for topic in topics:
            f.write(f"{topic}\n")
    print(f"[topics] {len(topics)} topics saved to {filename}")

def main():
    """Generate and save psychology topics in French."""
    print("=" * 60)
    print("=== French Psychology & Self-Improvement Topic Generator ===")
    print("=" * 60)

    try:
        with open("topics.txt", "r", encoding="utf-8") as f:
            existing_topics = [line.strip() for line in f if line.strip()]

        if len(existing_topics) >= 50:
            print(f"[topics] {len(existing_topics)} topics found. No new topics needed.")
            return
        else:
            print(f"[topics] Only {len(existing_topics)} topics found. Generating new ones...")
    except FileNotFoundError:
        print("[topics] topics.txt not found. Generating new topics...")
        existing_topics = []

    num_to_generate = 100
    new_topics = generate_french_psychology_topics(num_to_generate)

    all_topics = existing_topics + new_topics
    unique_topics = []
    seen = set()
    for topic in all_topics:
        if topic.lower() not in seen:
            unique_topics.append(topic)
            seen.add(topic.lower())

    save_topics_to_file(unique_topics)

    print("=" * 60)
    print(f"{len(unique_topics)} unique topics generated!")
    print("=" * 60)

if __name__ == "__main__":
    main()
