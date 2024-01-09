from Author import Author
from Document import Document
from RedditDocument import RedditDocument
from ArxivDocument import ArxivDocument
import re
import pandas as pd

def singleton(class_):
    instances = {}

    def wrapper(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return wrapper

@singleton
class Corpus:
    def __init__(self, nom):
        self.nom = nom
        self.authors = {}
        self.aut2id = {}
        self.id2doc = {}
        self.ndoc = 0
        self.naut = 0
        self.all_text = ""  # Variable pour stocker l'ensemble du texte concaténé


    def add(self, doc):
        if isinstance(doc, ArxivDocument):
            for auteur in doc.auteurs:
                if auteur not in self.aut2id:
                    self.naut += 1
                    self.authors[self.naut] = Author(auteur)
                    self.aut2id[auteur] = self.naut
                self.authors[self.aut2id[auteur]].add(doc.titre)
            doc.auteur = doc.auteurs
        elif isinstance(doc, (Document, RedditDocument)):
            if doc.auteur not in self.aut2id:
                self.naut += 1
                self.authors[self.naut] = Author(doc.auteur)
                self.aut2id[doc.auteur] = self.naut
            self.authors[self.aut2id[doc.auteur]].add(doc.titre)
        
        self.ndoc += 1
        self.id2doc[self.ndoc] = doc

    def show(self, n_docs=-1, tri="abc"):
        docs = list(self.id2doc.values())
        if tri == "abc":  # Tri alphabétique
            docs = list(sorted(docs, key=lambda x: x.titre.lower()))[:n_docs]
        elif tri == "123":  # Tri temporel
            docs = list(sorted(docs, key=lambda x: x.date))[:n_docs]

        print("\n".join(list(map(repr, docs))))

    def __repr__(self):
        docs = list(self.id2doc.values())
        docs = list(sorted(docs, key=lambda x: x.titre.lower()))

        return "\n".join(list(map(str, docs)))
    
    def build_all_text(self):
        #Construire la chaîne unique à partir de l'intégralité des chaînes dans les documents.
        all_docs = list(self.id2doc.values())
        self.all_text = "\n".join([doc.texte for doc in all_docs])

    def search(self, keyword):
        #Rechercher le mot-clé dans l'ensemble du texte.
        if not self.all_text:
            # Construire la chaîne unique si elle n'a pas encore été construite
            self.build_all_text()

        # Utiliser re.findall pour trouver toutes les occurrences du mot-clé dans l'ensemble du texte
        matches = re.findall(fr'\b{re.escape(keyword)}\b', self.all_text, flags=re.IGNORECASE)

        if not matches:
            print(f"Aucune correspondance trouvée pour le mot-clé '{keyword}'.")
        else:
            print(f"Occurrences trouvées pour le mot-clé '{keyword}':")
            for match in matches:
                print(match)
    
    def concorde(self, expression, context_size=20):
        #Construire un concordancier pour une expression donnée avec un contexte fixe.
        if not self.all_text:
            # Construire la chaîne unique si elle n'a pas encore été construite
            self.build_all_text()

        # Utiliser re.finditer pour trouver toutes les occurrences de l'expression dans l'ensemble du texte
        matches = list(re.finditer(fr'\b{re.escape(expression)}\b', self.all_text, flags=re.IGNORECASE))

        if not matches:
            print(f"Aucune occurrence trouvée pour l'expression '{expression}'.")
            return

        # Construire le tableau pour stocker les résultats
        concordance_data = {
            'Contexte Gauche': [],
            'Motif Trouvé': [],
            'Contexte Droit': []
        }

        for match in matches:
            # Extraire le contexte gauche et droit autour de l'expression
            start_idx = max(0, match.start() - context_size)
            end_idx = min(len(self.all_text), match.end() + context_size)
            left_context = '...' + self.all_text[start_idx:match.start()].strip()
            right_context = self.all_text[match.end():end_idx].strip() + '...'

            # Ajouter les résultats au tableau
            concordance_data['Contexte Gauche'].append(left_context)
            concordance_data['Motif Trouvé'].append(match.group())
            concordance_data['Contexte Droit'].append(right_context)

        # Créer un DataFrame pandas à partir des données
        concordance_df = pd.DataFrame(concordance_data)

        # Afficher le tableau de concordance
        print(concordance_df)

