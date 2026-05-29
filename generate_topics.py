import os
import requests
from dotenv import load_dotenv

load_dotenv()

POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")

def generate_french_kids_topics(num_topics=100):
    """Générer des sujets d'histoires pour enfants en français."""
    
    url = "https://gen.pollinations.ai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
        "Content-Type": "application/json"
    }

    system = (
        "Vous êtes un auteur créatif de livres pour enfants. "
        "Générez de courts titres pour des histoires pour enfants en français (âges 3-8) sur les animaux. "
        "Chaque histoire doit avoir un héros animal et une leçon morale simple. "
        "Utilisez un langage simple et adapté aux enfants. "
        "Générez UNIQUEMENT les titres, chacun sur une nouvelle ligne, sans numérotation."
    )
    
    prompt = (
        f"Générez {num_topics} titres uniques pour des histoires pour enfants en français sur les animaux. "
        "Exemples de thèmes: "
        "- Animaux de la forêt (ours, renards, lapins, cerfs, écureuils) "
        "- Animaux de la ferme (vaches, poules, cochons, chevaux, moutons) "
        "- Animaux marins (dauphins, tortues, poissons, baleines) "
        "- Animaux de la jungle (singes, éléphants, perroquets, tigres) "
        "- Leçons morales (amitié, honnêteté, gentillesse, courage, générosité) "
        "Chaque titre sur une nouvelle ligne, sans numéros."
    )
    
    payload = {
        "model": "openai",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "temperature": 1.2
    }
    
    print(f"[sujets] Génération de {num_topics} sujets d'histoires pour enfants en français...")
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        text = data['choices'][0]['message']['content'].strip()
        
        # Diviser en lignes et nettoyer
        topics = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Supprimer la numérotation si présente
        cleaned_topics = []
        for topic in topics:
            # Supprimer les modèles de numérotation courants
            topic = topic.lstrip('0123456789.-) ')
            if len(topic) > 10 and not topic.startswith('['):
                cleaned_topics.append(topic)
        
        # S'assurer d'avoir suffisamment de sujets
        if len(cleaned_topics) < num_topics:
            print(f"[sujets] {len(cleaned_topics)} sujets générés, tentative de génération de plus...")
            # Générer plus si nécessaire
            additional_needed = num_topics - len(cleaned_topics)
            if additional_needed > 0:
                additional_topics = generate_french_kids_topics(additional_needed)
                cleaned_topics.extend(additional_topics)
        
        return cleaned_topics[:num_topics]
        
    except Exception as e:
        print(f"[sujets] Erreur lors de la génération des sujets: {e}")
        # Sujets de secours
        return get_fallback_topics()[:num_topics]

def get_fallback_topics():
    """Sujets de secours pour histoires d'enfants en français si l'API échoue."""
    return [
        "Le Petit Ours Cherche du Miel dans la Forêt",
        "Le Renard Amical Aide le Lapin Perdu",
        "Le Dauphin Sauve la Petite Tortue",
        "L'Écureuil Courageux Partage des Noix",
        "Le Hibou Sage Enseigne aux Animaux de la Forêt",
        "Les Canetons Joyeux Apprennent à Nager",
        "Le Chaton Trouve une Nouvelle Maison",
        "Le Chiot Apprend à Partager",
        "La Petite Souris Aide le Grand Lion",
        "Le Lapin et la Tortue Apprennent l'Amitié",
        "L'Éléphant Oublie et Apprend à S'Excuser",
        "Le Perroquet Apprend à Dire la Vérité",
        "Le Petit Pingouin Apprend le Courage",
        "Le Grillon Chante pour ses Amis",
        "La Coccinelle Aide dans le Jardin",
        "Le Papillon Apprend la Patience",
        "Le Hérisson Partage des Pommes",
        "La Vache Donne du Lait pour Tout le Monde",
        "Le Poussin Apprend à Être Courageux",
        "Le Mouton Partage sa Laine",
        "Le Cheval Aide à la Ferme",
        "Le Porcelet Apprend la Propreté",
        "Le Lapin Plante des Carottes",
        "La Chèvre Grimpe la Montagne",
        "Le Canard Apprend à Voler",
        "L'Oie Guide ses Amis à la Maison",
        "Le Dindon Apprend l'Humilité",
        "L'Âne Aide à Porter",
        "Le Rat Apprend la Gentillesse",
        "Le Hamster Rassemble des Provisions pour l'Hiver",
        "Le Castor Construit une Maison pour la Famille",
        "La Loutre Joue dans l'Eau",
        "L'Élan Protège la Forêt",
        "Le Loup Apprend l'Amitié",
        "Le Lynx Aide les Petits Animaux",
        "Le Sanglier Cherche de la Nourriture dans la Forêt",
        "Le Cerf Apprend la Vitesse",
        "Le Lièvre Apprend le Courage",
        "Le Renard Apprend l'Honnêteté",
        "L'Ours se Réveille de l'Hibernation",
        "Le Panda Mange du Bambou et Partage",
        "Le Koala Dort dans l'Arbre",
        "Le Kangourou Porte son Bébé dans sa Poche",
        "La Girafe Atteint les Feuilles Hautes",
        "Le Zèbre Apprend à Propos de ses Rayures",
        "Le Lion Apprend à Être Doux",
        "Le Tigre Apprend à Partager",
        "Le Singe Joue avec ses Amis",
        "Le Gorille Protège la Famille",
        "Le Chimpanzé Apprend Quelque Chose de Nouveau",
        "L'Orang-outan Aide dans la Jungle",
        "L'Hippopotame Nage dans la Rivière",
        "Le Rhinocéros Défend son Territoire",
        "Le Crocodile Apprend à Être Doux",
        "Le Serpent Apprend l'Amitié",
        "La Tortue Gagne Lentement la Course",
        "Le Lézard se Prélasse au Soleil",
        "Le Caméléon Change de Couleurs",
        "L'Iguane Apprend à Grimper",
        "La Salamandre Apprend à Nager",
        "La Grenouille Saute dans l'Étang",
        "Le Crapaud Apprend à Chanter",
        "Le Triton Trouve une Nouvelle Maison",
        "Le Dauphin Apprend les Sauts",
        "La Baleine Chante des Chansons",
        "Le Requin Apprend à Être Amical",
        "La Pieuvre Aide ses Amis",
        "Le Calmar Apprend à se Cacher",
        "La Méduse Nage dans l'Océan",
        "L'Étoile de Mer Aide sur le Fond Marin",
        "Le Crabe Apprend à Marcher Droit",
        "Le Homard Partage la Nourriture",
        "La Crevette Apprend à Nager",
        "L'Hippocampe Danse dans l'Eau",
        "Le Petit Poisson Apprend à l'École",
        "Le Saumon Retourne à la Maison",
        "La Truite Saute dans le Ruisseau",
        "Le Brochet Apprend la Patience",
        "L'Aigle Vole Haut dans le Ciel",
        "Le Faucon Apprend à Chasser",
        "Le Faucon Protège le Nid",
        "Le Hibou Enseigne la Sagesse",
        "Le Grand-duc Aide la Nuit",
        "Le Corbeau Apprend à Partager",
        "La Pie Collectionne des Objets Brillants",
        "Le Choucas Apprend en Groupe",
        "La Colombe Porte des Messages",
        "Le Moineau Chante le Matin",
        "La Mésange Partage la Nourriture",
        "Le Rouge-gorge Apprend à Chanter",
        "Le Rossignol Chante le Plus Joliment",
        "L'Hirondelle Construit un Nid",
        "La Cigogne Apporte la Bonne Chance",
        "Le Héron Attrape des Poissons",
        "Le Cygne Nage sur le Lac",
        "Le Pélican Partage les Poissons",
        "Le Flamant Rose se Tient sur une Patte",
        "Le Perroquet Apprend à Parler",
        "Le Toucan a un Bec Coloré",
        "Le Colibri Boit du Nectar",
        "Le Pic Frappe sur l'Arbre",
        "Le Coucou Chante dans la Forêt"
    ]

def save_topics_to_file(topics, filename="topics.txt"):
    """Sauvegarder les sujets dans un fichier."""
    with open(filename, "w", encoding="utf-8") as f:
        for topic in topics:
            f.write(f"{topic}\n")
    print(f"[sujets] {len(topics)} sujets sauvegardés dans {filename}")

def main():
    """Générer et sauvegarder des sujets d'histoires pour enfants en français."""
    print("=" * 60)
    print("=== Générateur d'Histoires pour Enfants en Français ===")
    print("=" * 60)
    
    # Vérifier si topics.txt existe et a du contenu
    try:
        with open("topics.txt", "r", encoding="utf-8") as f:
            existing_topics = [line.strip() for line in f if line.strip()]
        
        if len(existing_topics) >= 50:
            print(f"[sujets] {len(existing_topics)} sujets trouvés. Aucun nouveau sujet nécessaire.")
            return
        else:
            print(f"[sujets] Seulement {len(existing_topics)} sujets trouvés. Génération de nouveaux...")
    except FileNotFoundError:
        print("[sujets] Le fichier topics.txt n'existe pas. Génération de nouveaux sujets...")
        existing_topics = []
    
    # Générer de nouveaux sujets
    num_to_generate = 100
    new_topics = generate_french_kids_topics(num_to_generate)
    
    # Combiner avec les existants (s'il y en a) et supprimer les doublons
    all_topics = existing_topics + new_topics
    unique_topics = []
    seen = set()
    for topic in all_topics:
        if topic.lower() not in seen:
            unique_topics.append(topic)
            seen.add(topic.lower())
    
    # Sauvegarder dans le fichier
    save_topics_to_file(unique_topics)
    
    print("=" * 60)
    print(f"✅ {len(unique_topics)} sujets uniques générés!")
    print("=" * 60)

if __name__ == "__main__":
    main()
