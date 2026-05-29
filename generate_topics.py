import os
import requests
from dotenv import load_dotenv

load_dotenv()

POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")

TOPIC_STYLES = [
    "aventure magique dans un monde imaginaire",
    "histoire d'amitié entre un enfant et une créature fantastique",
    "voyage extraordinaire à travers des paysages merveilleux",
    "mystère enchanté dans une forêt ou un jardin secret",
    "conte de fée moderne avec une leçon de vie",
    "histoire drôle et touchante d'un personnage attachant",
    "rêve éveillé où tout devient possible",
    "légende douce sur les étoiles, la lune ou le soleil",
    "histoire réconfortante sur le courage et la gentillesse",
    "découverte d'un monde caché sous la mer ou dans les nuages"
]

THEMES = [
    "un petit dragon qui a peur du feu mais rêve de voler",
    "une fée des étoiles qui tombe sur Terre par accident",
    "un nuage tout doux qui veut devenir un arc-en-ciel",
    "une graine magique qui pousse jusqu'au ciel",
    "un ours qui décide d'apprendre à danser le ballet",
    "une luciole qui cherche la plus belle lumière du monde",
    "un chaton perdu qui découvre une cité dans les nuages",
    "une pierre précieuse qui renferme les souvenirs du monde",
    "un petit bateau en papier qui traverse l'océan",
    "une fusée construite avec des jouets qui va sur la Lune",
    "un livre enchanté dont les histoires prennent vie",
    "une goutte d'eau qui voyage de la source à la mer",
    "un escargot qui rêve de gagner la course du jardin",
    "une plume magique qui peut exaucer un souhait par jour",
    "un bonhomme de neige qui veut voir le printemps",
    "une étoile filante qui cherche un ami sur Terre",
    "un jardin suspendu où les fleurs brillent la nuit",
    "une clé en or qui ouvre la porte des rêves",
    "une petite sorcière qui prépare la potion de l'amitié",
    "un cheval à bascule qui voyage dans le temps",
    "une boîte à musique qui joue la chanson du monde",
    "un reflet dans l'eau qui devient un ami",
    "une cité sous-marine où les poissons parlent",
    "un cerf-volant qui s'envole vers l'inconnu",
    "une montagne qui garde le secret des nuages",
    "un feu follet qui guide les enfants perdus",
    "une larme de joie qui fait pousser des fleurs",
    "un violon qui joue la musique des animaux",
    "une ombre amicale qui veut jouer dans la lumière",
    "une rose qui s'épanouit sous la lumière de la lune"
]

def generate_french_kids_topics(num_topics=100):
    """Générer des sujets d'histoires magnifiques et variés."""

    url = "https://gen.pollinations.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
        "Content-Type": "application/json"
    }

    examples = [
        "L'aventure du petit robot qui voulait apprendre à danser",
        "La baleine qui chantait les secrets de l'océan",
        "Le voyage extraordinaire d'une feuille d'automne",
        "Le mystère de la cité des chats disparus",
        "La fée qui avait perdu ses ailes de cristal",
        "Le dragon qui préférait lire des livres que de cracher du feu",
        "Le jardin secret où les fleurs racontent des histoires",
        "La légende de la montagne de glace éternelle"
    ]

    system = (
        "Vous êtes un auteur de contes pour enfants avec une imagination débordante. "
        "Générez des titres d'histoires MAGIQUES et POÉTIQUES pour enfants (3-8 ans). "
        "Chaque titre doit évoquer un univers merveilleux, de l'aventure, de la douceur. "
        "Variez les structures: 'Le/La/L'... qui...', 'Comment...', 'L'aventure de...', "
        "'Le voyage de...', 'Le secret de...', 'La légende de...', 'Le mystère de...' "
        "Pas de numéros. Chaque titre sur une nouvelle ligne. "
        "Évitez les formules génériques comme 'Le chat apprend à...' — soyez poétique et original."
    )

    prompt = (
        f"Générez {num_topics} titres uniques et magnifiques pour des histoires pour enfants en français."
        f"\n\nExemples du style attendu:"
        f"\n" + "\n".join(f"- {ex}" for ex in examples) +
        "\n\nThèmes à explorer (variez):"
        "\n- Magie et créatures fantastiques (dragons, fées, licornes, lutins, sorcières)"
        "\n- Aventures dans la nature (forêts enchantées, océans, montagnes, jardin secret)"
        "\n- Objets magiques qui prennent vie (jouets, livres, instruments de musique)"
        "\n- Voyages imaginaires (dans les étoiles, sous la mer, au centre de la Terre)"
        "\n- Amitié et émotions (courage, gentillesse, partage, dépassement de soi)"
        "\n- Petits miracles quotidiens (saisons, météo, plantes, animaux)"
        "\n\nIMPORTANT: Chaque titre doit être unique, poétique, et donner envie d'écouter l'histoire."
        "\nTitres uniquement, un par ligne, sans numérotation."
    )

    payload = {
        "model": "openai",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "temperature": 1.3
    }

    print(f"[sujets] Génération de {num_topics} sujets magnifiques et variés...")

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        text = data['choices'][0]['message']['content'].strip()

        topics = [line.strip() for line in text.split('\n') if line.strip()]

        cleaned_topics = []
        for topic in topics:
            topic = topic.lstrip('0123456789.-) ')
            if len(topic) > 15 and not topic.startswith('['):
                cleaned_topics.append(topic)

        if len(cleaned_topics) < num_topics:
            print(f"[sujets] {len(cleaned_topics)} sujets générés, complément avec des sujets locaux...")
            fallback_needed = num_topics - len(cleaned_topics)
            cleaned_topics.extend(get_fallback_topics()[:fallback_needed])

        return cleaned_topics[:num_topics]

    except Exception as e:
        print(f"[sujets] Erreur API: {e}. Utilisation des sujets locaux.")
        return get_fallback_topics()[:num_topics]

def get_fallback_topics():
    """200 sujets magnifiques et variés (fallback quand l'API est indisponible)."""
    topics = [
        "Le petit dragon qui avait peur des flammes mais rêvait de voler",
        "La fée des étoiles qui tombée du ciel un soir d'été",
        "Le voyage d'une goutte d'eau de la source jusqu'à l'océan",
        "Le mystère du jardin qui fleurissait seulement la nuit",
        "Comment un nuage tout doux est devenu un magnifique arc-en-ciel",
        "La boîte à musique qui jouait la chanson des souvenirs",
        "L'aventure d'un petit bateau en papier qui traversa l'océan",
        "Le secret de la vieille horloge qui arrêtait le temps",
        "La légende de la montagne de cristal qui brillait sous la lune",
        "Le chaton qui découvrit une cité cachée dans les nuages",
        "L'incroyable voyage d'une plume portée par le vent",
        "Comment un flocon de neige unique apprit à être spécial",
        "Le mystère de la forêt où les arbres chuchotaient des secrets",
        "La petite étoile qui voulait rejoindre les feux follets",
        "L'aventure d'un livre enchanté dont les histoires prenaient vie",
        "La graine magique qui poussa jusqu'à toucher le ciel",
        "Le reflet dans l'eau qui devint le meilleur ami d'une petite fille",
        "Comment un morceau de lune tomba dans un étang magique",
        "La licorne qui cherchait la source de toutes les couleurs",
        "Le voyage extraordinaire d'une feuille d'automne autour du monde",
        "La petite sorcière qui préparait la potion de l'amitié éternelle",
        "L'ours qui décida d'apprendre à danser comme un papillon",
        "Le secret du violon qui faisait danser les animaux de la forêt",
        "La fusée construite avec des jouets qui partit explorer Mars",
        "Comment un sourire perdu fut retrouvé au fond d'un puits à souhaits",
        "La luciole qui cherchait la lumière la plus belle du monde",
        "Le cerf-volant qui s'envola si haut qu'il toucha les étoiles",
        "La rose qui s'épanouissait sous la lumière argentée de la lune",
        "L'aventure d'un bonhomme de neige qui voulait voir le printemps",
        "Le mystère de la clé en or qui ouvrait la porte des rêves",
        "Une sirène qui échangea sa voix contre des ailes pour voler",
        "Le petit robot qui apprit à ressentir la chaleur du soleil",
        "Comment la Lune et le Soleil devinrent les gardiens du ciel",
        "La grotte secrète où les cristaux chantaient des berceuses",
        "L'enfant qui parlait aux animaux et comprenait leur langage",
        "Le nuage paresseux qui ne voulait jamais pleuvoir",
        "Comment un simple caillou devint le plus précieux des trésors",
        "La fée du printemps qui réveillait les fleurs endormies",
        "L'arbre centenaire qui gardait la mémoire du monde",
        "Le voyage d'un rayon de soleil à travers les saisons",
        "La petite ourse qui apprit à briller dans le ciel nocturne",
        "Le secret du sable qui conservait l'empreinte des pas",
        "Comment un flocon de neige retrouva ses six frères perdus",
        "La loutre qui construisit le plus beau barrage de la rivière",
        "Le vent qui apprenait aux feuilles à danser",
        "L'aventure d'un message dans une bouteille parti de l'autre côté du monde",
        "Le papillon qui traversa l'océan sur le dos d'une baleine",
        "Comment une petite graine de pissenlit apprit à voyager",
        "L'étoile filante qui cherchait un ami sur Terre pour jouer",
        "Le mystère de l'île flottante cachée derrière la brume",
        "Le petit fantôme qui avait peur du noir mais aimait les câlins",
        "Comment un arc-en-ciel apprit qu'il était beau même sans ses couleurs",
        "La montre à remonter le temps qui appartenait à grand-père",
        "Le voyage d'une larme de joie qui fit pousser des fleurs partout",
        "La chatte qui tissait des couvertures avec des fils de lune",
        "Comment un escargot lent mais déterminé gagna la grande course",
        "La fête foraine des animaux où tout le monde était le bienvenu",
        "Le mystère du miroir qui montrait non pas le visage mais le cœur",
        "Le petit pingouin qui voulait apprendre à voler comme un albatros",
        "Comment une coccinelle à sept points trouva son huitième point",
        "La légende du phare qui guidait les rêves vers le sommeil",
        "Une chouette qui collectionnait les histoires du monde entier",
        "Le chemin de briques jaunes qui menait au pays des câlins",
        "Comment un sourire dessiné sur un post-it voyagea de main en main",
        "La baleine qui chantait des berceuses aux enfants de l'océan",
        "Le petit cheval à bascule qui galopa dans les rêves d'un enfant",
        "La lanterne magique qui éclairait les chemins dans l'obscurité",
        "Comment un ourson en peluche apprit à guérir les cœurs tristes",
        "Le secret de la fontaine aux souhaits qui ne fonctionnait qu'à l'aube",
        "L'aventure d'un fil de laine rose qui tricota une couverture d'amitié",
        "Le dinosaure qui préférait manger des fleurs plutôt que de la viande",
        "Comment les couleurs de l'automne apprirent à tomber gracieusement",
        "Le mystère de la cabane dans l'arbre qui changeait de pays chaque nuit",
        "La petite tasse de thé qui réchauffait les cœurs froids",
        "Le voyage d'une bougie qui éclaira le chemin de la maison",
        "Comment un oursin tout piquant trouva des amis tout doux",
        "Le piano abandonné qui rejoua pour la première fois depuis cent ans",
        "L'ombre qui voulait devenir une amie plutôt que de faire peur",
        "Comment un trou dans un arbre devint la porte d'un monde enchanté",
        "La petite voix intérieure qui apprit à un enfant à s'aimer",
        "Le voyage d'une écharpe rouge à travers les saisons et les pays",
        "Le dragon de Komodo qui rêvait d'être doux comme un chaton",
        "Comment une tache d'encre sur une feuille devint un chef-d'œuvre",
        "La gardienne des rêves qui triait les cauchemars et les beaux songes",
        "Le petit train qui n'osait pas sortir de son tunnel",
        "Comment un miroir cassé apprit que ses morceaux étaient encore beaux",
        "L'aventure d'un grain de riz qui voulait nourrir le monde",
        "La fée des dents qui avait perdu sa poussière magique",
        "Le secret de la corne du narval qui exauçait les vœux",
        "Comment un vieux chêne et un jeune gland partagèrent leur sagesse",
        "Le voleur de couleurs qui rendit le monde gris et triste",
        "La petite flamme qui n'osait pas briller de peur de s'éteindre",
        "Comment une empreinte de patte dans la neige devint une carte au trésor",
        "Le mystère du lac gelé où dansaient les lumières du Nord",
        "Un petit pois qui refusait de devenir purée voulait voyager",
        "La légende du colibri qui apporta le feu aux hommes",
        "Comment un bâton de pluie apprit à faire de la musique",
        "L'enfant qui plantait des étoiles dans son jardin chaque nuit",
        "La recette secrète des biscuits qui donnent des ailes",
        "Le voyage d'une plume d'ange tombée du paradis",
        "Comment un ventre qui gargouille devint une symphonie rigolote",
        "La petite bibliothèque ambulante qui parcourait les villages",
        "Le rossignol qui apprit aux oiseaux à chanter en chœur",
        "Comment un rond-point devint la place la plus joyeuse du monde",
        "L'aventure d'un fil électrique qui voulait devenir une guirlande",
        "Le secret du grenier où les jouets oubliés reprenaient vie",
        "Comment une petite fille apprivoisa son ombre et devint courageuse",
        "Le glacier magique qui fabriquait des glaces aux souvenirs",
        "Une constellation qui s'ennuyait décida de descendre sur Terre",
        "Le voyage d'une bulle de savon qui voulait toucher le soleil",
        "Comment un coquillage préserva le bruit de l'océan pendant mille ans",
        "L'horloge coucou qui voulait chanter autre chose que l'heure",
        "Le monstre sous le lit qui avait en fait très peur des enfants",
        "Comment une paire de lunettes magiques révéla la beauté cachée du monde",
        "La petite abeille qui sauva la dernière fleur du monde",
        "Le secret du brouillard matinal qui cache un monde parallèle",
        "Comment un téléphone sans fil transmit le mot le plus important",
        "L'aventure d'un marronnier qui lançait ses marrons comme des messages",
        "Le poussin qui refusait de sortir de sa coquille par peur du monde",
        "Comment une tache de rousseur devint une carte des trésors du visage",
        "La légende des lucioles qui gardent les secrets de la forêt",
        "Le petit sapin qui rêvait de devenir un arbre de Noël",
        "Comment un pour toujours devint le mot le plus doux du monde",
        "Le voyage d'une madeleine qui transportait les souvenirs d'enfance",
        "L'oiseau qui construisit son nid avec des fils de rêves",
        "Comment un ver luisant apprit que sa lumière intérieure était unique",
        "Le secret de la rosée du matin qui rafraîchit les cœurs fatigués",
        "La soupe magique de grand-mère qui guérissait tous les chagrins",
        "Comment une simple pomme de pin devint le plus beau des arbres",
        "Le chemin de cailloux blancs qui menait toujours à la maison",
        "L'aventure d'un mot doux qui voyagea de bouche à oreille",
        "Le koala qui voulait explorer le monde sans quitter son arbre",
        "Comment un orage apprit à gronder doucement pour ne pas effrayer",
        "La petite sirène qui préférait marcher sur Terre plutôt que nager",
        "Le secret de la première neige qui rend tout silencieux et beau",
        "Comment un ballon rouge perdu retrouva son chemin vers le ciel",
        "Le voyage d'un parfum de fleur à travers les saisons",
        "Un champignon lumineux qui éclairait les chemins de la forêt",
        "La légende du pont arc-en-ciel qui reliait deux mondes",
        "Comment une vague apprit à ne pas submerger mais à caresser",
        "Le petit chaperon rouge qui n'avait pas peur du loup mais du noir",
        "Le mystère des œufs de Pâques qui n'étaient jamais trouvés",
        "Un nuage en forme de cœur qui flottait au-dessus de la ville",
        "Comment une montre arrêtée indiqua le meilleur moment pour aimer",
        "Le voyage d'un pétale de rose dans le vent du printemps",
        "Le grillon qui jouait du violon pour endormir la lune",
        "Comment un tas de feuilles mortes devint un château de souvenirs",
        "La petite goutte de pluie qui avait peur de tomber",
        "Le secret de la dernière feuille d'automne qui refusait de tomber",
        "L'aventure d'un morceau de craie qui dessinait des portes magiques",
        "Comment un bâton devint la plus belle baguette magique du monde",
        "Le voyage d'une étoile de mer qui voulait voir les étoiles du ciel",
        "Un petit pois dans une cosse qui rêvait de devenir une princesse",
        "La légende du vent qui transportait les messages d'amour",
        "Comment un nœud dans un foulard aida à ne pas oublier l'essentiel",
        "Le hérisson qui cherchait quelqu'un pour lui faire un câlin",
        "Le secret du grenier à foin où les rêves fermentaient doucement",
        "L'aventure d'un timbre-poste qui voyagea autour du monde",
        "Comment un soupir de soulagement devint une brise légère",
        "La petite boîte à secrets qui contenait les plus beaux souvenirs",
        "Le voyage d'une graine de pissenlit portée par le vent d'été",
        "Comment la pluie apprit à tomber en musique",
        "Le mystère de la porte qui n'apparaissait que les soirs de pleine lune",
        "Un caillou tout rond qui roula si loin qu'il vit l'océan",
        "Comment une respiration profonde apaisa toute la colère du monde",
        "Le voyage d'un bisou envoyé par la poste à travers les continents",
        "La petite flaque d'eau qui voulait devenir un océan",
        "Le secret du sable chaud qui gardait les empreintes de pas",
        "L'aventure d'une paille qui voulait aspirer les étoiles",
        "Comment une boîte vide apprit qu'elle pouvait être remplie d'amour",
        "Le chat qui croyait être un poisson et qui apprit à nager",
        "La légende de l'oiseau qui rapporta le feu du soleil",
        "Comment une miette de pain devint le festin des fourmis",
        "Le voyage d'un sourire qui traversa sept continents",
        "Un bracelet d'amitié qui parcourut le monde avant de revenir",
        "Comment le silence devint la plus belle musique pour les oreilles attentives",
        "Le petit rat de bibliothèque qui vivait entre les pages des livres",
        "Le secret de la couverture trouée qui protégeait des cauchemars",
        "L'aventure d'une tranche de pain de mie qui voulait devenir toast doré",
        "Comment une échelle de corde aida à atteindre les rêves les plus hauts",
        "La tirelire qui collectionnait non pas l'argent mais les sourires",
        "Le voyage d'un mot magique qui ouvrait toutes les portes",
        "Un nid d'oiseau tissé avec des fils de tendresse et des brins de patience",
        "Comment une flaque après la pluie reflétait tout l'univers",
        "Le lutin qui réparait les jouets cassés pendant la nuit",
        "Le secret du pot de confiture qui gardait le goût de l'été",
        "L'aventure d'un crayon de couleur qui voulait dessiner l'infini",
        "Comment une casserole de soupe réchauffa tout un village",
        "Le voyage d'un pépin de pomme qui devint le plus bel arbre du verger",
        "Un bisou du soir qui voyagea jusqu'au pays des rêves",
        "La légende des patins à glace qui dansaient seuls sous la lune",
        "Comment une couverture de sécurité aida à traverser les tempêtes",
        "Le petit mouton qui comptait les enfants pour s'endormir",
        "Le secret du nichoir où les oiseaux déposaient leurs chansons",
        "L'aventure d'une boule de neige qui contenait tout l'hiver",
        "Comment une écharpe tricotée avec amour réchauffa le cœur du monde",
        "La flûte enchantée qui faisait danser même les pierres",
        "Le voyage d'une écorce de bateau qui navigua sur sept mers",
        "Un pétale de fleur qui servit de lit à une coccinelle fatiguée",
        "Comment un champ de lavande apaisa toutes les inquiétudes",
        "Le petit théâtre de marionnettes où les ombres racontaient des histoires",
        "Le secret du cache-cache éternel entre le Soleil et la Lune",
        "L'aventure d'une moustache de chat qui devint un pinceau magique",
        "Comment un tapis volant usé retrouva sa capacité à planer",
        "La recette du calme pour les jours de tempête intérieure",
        "Le voyage d'un rire d'enfant qui parcourut toute la galaxie",
        "Un pois chiche qui refusait d'être mangé voulait devenir comédien",
        "Comment la dernière feuille d'automne apprit à danser avec le vent",
        "Le petit astronaute qui explora la galaxie dans son carton",
        "Le secret des marrons chauds qui réchauffent les cœurs en hiver",
        "L'aventure d'un gland qui devint le roi de la forêt centenaire",
        "Comment une étoile de mer apprit à nager jusqu'au ciel",
        "Un caméléon qui changeait de couleur selon ses émotions",
        "La légende du colibri qui but la dernière goutte de pluie",
        "Comment une goutte de rosée devint un diamant au lever du soleil",
        "Le chapelier fou qui fabriquait des chapeaux de rêves sur mesure",
        "Le voyage d'un fil de téléphone qui connecta les cœurs éloignés",
        "Un hérisson tout doux qui cherchait un câlin sans piquer",
        "Comment une flaque d'eau de pluie devint un miroir magique",
        "Le secret du pain chaud qui embaume la maison du bonheur",
        "L'aventure d'une bille perdue qui roula jusqu'au bout du monde",
        "Comment un flocon de neige unique apprit que sa différence était sa force",
        "Le petit gardien de phare qui allumait les étoiles chaque soir",
        "La valise qui contenait tous les souvenirs du monde",
        "Un pois dans une cosse qui refusait de grandir trop vite",
        "Comment le parfum d'une fleur traversa les océans pour retrouver son jardin",
    ]
    return topics

def save_topics_to_file(topics, filename="topics.txt"):
    """Sauvegarder les sujets dans un fichier."""
    with open(filename, "w", encoding="utf-8") as f:
        for topic in topics:
            f.write(f"{topic}\n")
    print(f"[sujets] {len(topics)} sujets sauvegardés dans {filename}")

def main():
    """Générer et sauvegarder des sujets magnifiques pour histoires d'enfants."""
    print("=" * 60)
    print("=== Générateur de Sujets Magiques pour Enfants ===")
    print("=" * 60)

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

    num_to_generate = 100
    new_topics = generate_french_kids_topics(num_to_generate)

    all_topics = existing_topics + new_topics
    unique_topics = []
    seen = set()
    for topic in all_topics:
        if topic.lower() not in seen:
            unique_topics.append(topic)
            seen.add(topic.lower())

    save_topics_to_file(unique_topics)

    print("=" * 60)
    print(f"✅ {len(unique_topics)} sujets uniques et magnifiques générés!")
    print("=" * 60)

if __name__ == "__main__":
    main()
