#####################################
# Partie 1 : chargement des données #
#####################################

################ 1.1 ################
#REDDIT

import praw
# Identification
reddit = praw.Reddit(client_id='KTdgvYo7sGyiNb02hQZWJQ', client_secret='wTyymqM0ysjUrLrK7nkLMZHwq1ERlg', user_agent='ferdaousse')
# Requête
posts = reddit.subreddit('python').hot(limit=100)
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
query_terms = ["python"]
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