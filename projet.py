#####################################
# Partie 1 : chargement des données #
#####################################

################ 1.1 ################
#REDDIT

import praw
# Identification
reddit = praw.Reddit(client_id='KTdgvYo7sGyiNb02hQZWJQ', client_secret='wTyymqM0ysjUrLrK7nkLMZHwq1ERlg', user_agent='ferdaousse')
# Requête
posts = reddit.subreddit('corona').hot(limit=100)
# Récupération du texte
docs = []
docs_bruts = []
textes_Reddit=[]
for i, post in enumerate(posts):
	if post.selftext != "":  # ne pas retenir les posts avec selftext vide
		docs.append(post.selftext.replace("\n", " "))
		docs_bruts.append(("Reddit", post))

textes_Reddit = docs
print("Taille du corpus REDDIT : ", len(textes_Reddit))

################ 1.2 ################
#ARXIV

import urllib, urllib.request
import xmltodict

# Paramètres
query_terms = ["corona"]
max_results = 100
textes_Arvix=[]
# Requête
url = f'http://export.arxiv.org/api/query?search_query=all:{"+".join(query_terms)}&start=0&max_results={max_results}'
entries = urllib.request.urlopen(url)

# Format dict (OrderedDict)
data = xmltodict.parse(entries.read().decode('utf-8'))

# Ajout résumés à la liste
for i, entry in enumerate(data["feed"]["entry"]):
	if entry["summary"] != "": # ne pas retenir les entries avec summary vide
		textes_Arvix.append(entry["summary"].replace("\n", ""))
		docs_bruts.append(("ArXiv", entry))


print("Taille du corpus ARXIV : ", len(textes_Arvix))
docs = textes_Arvix + docs	
print("Taille du corpus global : ", len(docs))

#####################################
# Partie 1 : la classe Document     #
#####################################

################ TD4 : 1.3 & 2.3 ####

from Document import Document
from Author import Author
import datetime
# Dictionnaire pour stocker les documents avec leurs identifiants
id2doc = {}  
# Initialiser un compteur d'identifiants
id_counter = 1  
# Dictionnaire pour stocker les auteurs avec leurs noms
id2aut = {}  
# Parcourir les documents bruts et créer des instances de la classe Document
for nature, doc in docs_bruts:
    if nature == "ArXiv":
        # Gestion des auteurs
        authors_data = doc.get("author", [])
        if isinstance(authors_data, list):
            # Si c'est une liste d'auteurs
            for author_data in authors_data:
                author_name = author_data.get("name", "")
                # Vérifier si l'auteur est déjà connu
                if author_name not in id2aut:
                    # Si l'auteur n'est pas connu, créer une instance de la classe Author
                    author_instance = Author(author_name)
                    id2aut[author_name] = author_instance
                # Ajouter la production à l'auteur
                id2aut[author_name].add(id_counter)
        elif isinstance(authors_data, dict):
            # Si c'est un seul auteur
            author_name = authors_data.get("name", "")
            # Vérifier si l'auteur est déjà connu
            if author_name not in id2aut:
                # Si l'auteur n'est pas connu, créer une instance de la classe Author
                author_instance = Author(author_name)
                id2aut[author_name] = author_instance
            # Ajouter la production à l'auteur
            id2aut[author_name].add(id_counter) 
        # Gestion des documents
		# On enlève les retours à la ligne
        titre = doc["title"].replace('\n', '')  
        try:
            # On fait une liste d'auteurs, séparés par une virgule
            authors = ", ".join([a["name"] for a in doc["author"]])  
        except:
            # Si l'auteur est seul, pas besoin de liste
            authors = doc["author"]["name"] 
        # On enlève les retours à la ligne 
        summary = doc["summary"].replace("\n", "")  
        # Formatage de la date en année/mois/jour avec librairie datetime
        date = datetime.datetime.strptime(doc["published"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y/%m/%d")
        # Création du Document
        doc_classe = Document(titre, authors, date, doc["id"], summary)
        # Ajout du Document à la collection avec un identifiant unique
        id2doc[id_counter] = doc_classe
        id_counter += 1

    elif nature == "Reddit":
        # Gestion des auteurs
        author_name = str(doc.author)
        # Vérifier si l'auteur est déjà connu
        if author_name not in id2aut:
            # Si l'auteur n'est pas connu, créer une instance de la classe Author
            author_instance = Author(author_name)
            id2aut[author_name] = author_instance
        # Ajouter la production à l'auteur
        id2aut[author_name].add(id_counter)
        # Gestion des documents
		# On enlève les retours à la ligne
        titre = doc.title.replace("\n", '')
        auteur = str(doc.author)
        date = datetime.datetime.fromtimestamp(doc.created).strftime("%Y/%m/%d")
        url = str(doc.url)
        texte = doc.selftext.replace("\n", "")
        # Création du Document
        doc_classe = Document(titre, auteur, date, url, texte)
        # Ajout du Document à la collection avec un identifiant unique
        id2doc[id_counter] = doc_classe
        id_counter += 1

print("Taille de la collection id2aut : ", len(id2aut))
print("Taille de la collection id2doc : ", len(id2doc))

################ 2.4 ####

liste_auteurs = list(id2aut.keys())
auteur_demande = liste_auteurs[0]

auteur_analyse = id2aut[auteur_demande]

# Nombre de documents produits par l'auteur
nombre_documents = auteur_analyse.ndoc
print(f"Nombre de documents produits par {auteur_demande} : {nombre_documents}")

# Taille moyenne des documents produits par l'auteur
if auteur_analyse.ndoc > 0:
    taille_moyenne = sum(len(id2doc[production].texte) for production in auteur_analyse.production) / auteur_analyse.ndoc
    print(f"Taille moyenne des documents produits par {auteur_demande} : {taille_moyenne:.2f} caractères")
else:
    print(f"{auteur_demande} n'a produit aucun document.")

### Liste des auteurs avec plus d'un document
auteurs_plusieurs_documents = [auteur for auteur in id2aut.values() if auteur.ndoc > 1]
# Affichage de la liste des auteurs avec plus d'un document
print("Auteurs avec plus d'un document :")
for auteur in auteurs_plusieurs_documents:
    print(f"{auteur.name} : {auteur.ndoc} documents")

#####################################
# Partie 2 : sauvegarde des données #
#####################################

################ 2.1 ################
#tableau de type DataFrame avec 3 colonnes

import pandas as pd
taille_reddit = len(textes_Reddit) + 1
df_reddit = pd.DataFrame({'Identifiant': range(1, taille_reddit), 'Texte': textes_Reddit, 'Origine': 'Reddit'})
df_arxiv = pd.DataFrame({'Identifiant': range(taille_reddit, taille_reddit + len(textes_Arvix)), 'Texte': textes_Arvix, 'Origine': 'Arxiv'})

df = pd.concat([df_reddit,df_arxiv], ignore_index=True)
#print(df)

################ 2.2 ################
#Sauvegarde du tableau sur le disque dans un fichier de type .csv
df.to_csv(r'tableau_textes.csv', sep='\t', index=False)

################ 2.3 ################
#charger directement ce tableau en m´emoire
df_loaded = pd.read_csv('tableau_textes.csv', sep='\t')

#################################################
# Partie 3 : premières manipulation des données #
#################################################

################ 3.1 ################
#Affichez la taille du corpus
taille_corpus = df_loaded.shape[0]
print("Taille du corpus : ", taille_corpus)

################ 3.2 ################
import numpy as np

# Fonction pour compter le nombre de mots dans une phrase
def count_words(text):
    return len(text.split())

# Fonction pour compter le nombre de phrases dans un texte
def count_sentences(text):
    return len(text.split('.'))

# Appliquer les fonctions à chaque ligne et afficher les résultats
for index, row in df_loaded.iterrows():
    mots = count_words(row['Texte'])
    phrases = count_sentences(row['Texte'])
    print(f"Pour la ligne {index + 1} : Nombre de mots = {mots}, Nombre de phrases = {phrases}")

################ 3.3 ################
#Supprimer les documents qui contiennent moins de 20 caractères
df_filtered = df_loaded[df_loaded['Texte'].str.len() >= 20]

# Enregistrer le nouveau DataFrame dans un fichier CSV
df_filtered.to_csv(r'tableau_textes_filtre.csv', sep='\t', index=False)

################ 3.4 ################
#Créez une unique chaine de caractère contenant tous les documents
corpus_string = ' '.join(df_filtered['Texte'])