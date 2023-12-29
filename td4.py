from Document import Document
from Author import Author
from Corpus import Corpus
import praw
import urllib.request
import xmltodict
import datetime
import pandas as pd

# Partie 1 : chargement des données

# REDDIT
reddit = praw.Reddit(client_id='KTdgvYo7sGyiNb02hQZWJQ', client_secret='wTyymqM0ysjUrLrK7nkLMZHwq1ERlg', user_agent='ferdaousse')
posts = reddit.subreddit('corona').hot(limit=100)
docs = []
docs_bruts = []
textes_Reddit = []

for i, post in enumerate(posts):
    if post.selftext != "":
        textes_Reddit.append(post.selftext.replace("\n", " "))
        docs_bruts.append(("Reddit", post))

print("Taille du corpus REDDIT : ", len(textes_Reddit))

# ARXIV
query_terms = ["corona"]
max_results = 100
textes_Arvix = []

url = f'http://export.arxiv.org/api/query?search_query=all:{"+".join(query_terms)}&start=0&max_results={max_results}'
entries = urllib.request.urlopen(url)

data = xmltodict.parse(entries.read().decode('utf-8'))

for i, entry in enumerate(data["feed"]["entry"]):
    if entry["summary"] != "":
        textes_Arvix.append(entry["summary"].replace("\n", ""))
        docs_bruts.append(("ArXiv", entry))

print("Taille du corpus ARXIV : ", len(textes_Arvix))
docs = textes_Reddit + textes_Arvix 
print("Taille du corpus global : ", len(docs))

collection = []

for nature, doc in docs_bruts:
    if nature == "ArXiv": 
        titre = doc["title"].replace('\n', '')  # On enlève les retours à la ligne
        try:
            authors = ", ".join([a["name"] for a in doc["author"]])  # On fait une liste d'auteurs, séparés par une virgule
        except:
            authors = doc["author"]["name"]  # Si l'auteur est seul, pas besoin de liste
        summary = doc["summary"].replace("\n", "")  # On enlève les retours à la ligne
        date = datetime.datetime.strptime(doc["published"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y/%m/%d")  # Formatage de la date en année/mois/jour avec librairie datetime

        doc_classe = Document(titre, authors, date, doc["id"], summary)  # Création du Document
        collection.append(doc_classe)  # Ajout du Document à la liste.

    elif nature == "Reddit":
        titre = doc.title.replace("\n", '')
        auteur = str(doc.author)
        date = datetime.datetime.fromtimestamp(doc.created).strftime("%Y/%m/%d")
        url = str(doc.url)
        texte = doc.selftext.replace("\n", "")

        doc_classe = Document(titre, auteur, date, url, texte)

        collection.append(doc_classe)
id2doc = {}
for i, doc in enumerate(collection):
    id2doc[i] = doc.titre
print(len(id2doc))
authors = {}
aut2id = {}
num_auteurs_vus = 0
for doc in collection:
    if doc.auteur not in aut2id:
        num_auteurs_vus += 1
        authors[num_auteurs_vus] = Author(doc.auteur)
        aut2id[doc.auteur] = num_auteurs_vus

    authors[aut2id[doc.auteur]].add(doc.texte)
from Corpus import Corpus
corpus = Corpus("Mon corpus")
for doc in collection:
    corpus.add(doc)
corpus.show(tri="abc")
