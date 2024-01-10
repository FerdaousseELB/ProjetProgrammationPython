from Author import Author
from Document import Document
from RedditDocument import RedditDocument
from ArxivDocument import ArxivDocument
import re
import pandas as pd
from collections import Counter
from collections import defaultdict
from scipy.sparse import csr_matrix
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

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
        print(f"Document ajouté au corpus : {doc}")
        print(f"Nombre total de documents dans le corpus : {self.ndoc}")

    def show(self, n_docs=-1, tri="abc"):
        docs = list(self.id2doc.values())
        if tri == "abc":  # Tri alphabétique
            docs = list(sorted(docs, key=lambda x: x.titre.lower()))
        elif tri == "123":  # Tri temporel
            docs = list(sorted(docs, key=lambda x: x.date))
        #print(docs)
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
    
    def nettoyer_texte(self, texte):
        #Appliquer différents traitements au texte.
        # Mise en minuscules
        texte = texte.lower()

        # Remplacement des passages à la ligne
        texte = texte.replace('\n', ' ')

        # Retrait de la ponctuation et des chiffres
        texte = re.findall(r'[a-zA-Z]+', texte)

        return texte
    
    def stats(self, top_n_words=10):
        #Afficher plusieurs statistiques textuelles sur le corpus.
        if not self.all_text:
            # Construire la chaîne unique si elle n'a pas encore été construite
            self.build_all_text()

        cleaned_text = self.nettoyer_texte(self.all_text)

        print(f"Nombre de mots dans le corpus : {len(cleaned_text)}")

        # Calculer le nombre de mots différents dans le corpus
        nombre_mots_differents = len(set(cleaned_text))

        print(f"Nombre de mots différents dans le corpus : {nombre_mots_differents}")

        # Afficher les n mots les plus fréquents
        mots_frequents = Counter(cleaned_text).most_common(top_n_words)
        print(f"\nLes {top_n_words} mots les plus fréquents dans le corpus :")
        for mot, frequence in mots_frequents:
            print(f"{mot}: {frequence}")

    def construire_vocabulaire(self):
        #Construire le vocabulaire à partir des documents du corpus.
        if not self.all_text:
            # Construire la chaîne unique si elle n'a pas encore été construite
            self.build_all_text()

        cleaned_text = self.nettoyer_texte(self.all_text)

        # Construire le vocabulaire en utilisant un ensemble (set) pour éliminer les doublons
        self.vocabulaire = set(cleaned_text)

    def afficher_vocabulaire(self):
        #Afficher le vocabulaire construit.
        if not hasattr(self, 'vocabulaire'):
            # Construire le vocabulaire si ce n'est pas encore fait
            self.construire_vocabulaire()

        print("Vocabulaire construit :")
        for mot in self.vocabulaire:
            print(mot)

    def construire_tableau_frequences(self):
        #Construire un tableau de fréquences pour chaque mot du vocabulaire.
        if not hasattr(self, 'vocabulaire'):
            # Construire le vocabulaire si ce n'est pas encore fait
            self.construire_vocabulaire()

        if not self.all_text:
            # Construire la chaîne unique si elle n'a pas encore été construite
            self.build_all_text()

        cleaned_text = self.nettoyer_texte(self.all_text)

        # Utiliser la fonction Counter pour compter les occurrences de chaque mot dans le vocabulaire
        freq = dict(Counter(cleaned_text))

        # Calculer le document frequency pour chaque mot
        doc_freq = defaultdict(int)
        for mot in self.vocabulaire:
            for doc in self.id2doc.values():
                if mot in doc.texte.lower():
                    doc_freq[mot] += 1

        # Ajouter une colonne 'Document Frequency' au tableau de fréquences
        self.tableau_frequences = pd.DataFrame(list(freq.items()), columns=['Mot', 'Fréquence'])
        self.tableau_frequences['Document Frequency'] = self.tableau_frequences['Mot'].apply(lambda mot: doc_freq[mot])

    def afficher_tableau_frequences(self):
        #Afficher le tableau de fréquences construit.
        if not hasattr(self, 'tableau_frequences'):
            # Construire le tableau de fréquences si ce n'est pas encore fait
            self.construire_tableau_frequences()

        print("Tableau de fréquences :")
        print(self.tableau_frequences)

    def construire_vocab(self):
        # Construire le vocabulaire à partir des documents du corpus.
        if not self.all_text:
            # Construire la chaîne unique si elle n'a pas encore été construite
            self.build_all_text()

        cleaned_text = self.nettoyer_texte(self.all_text)

        # Initialiser le dictionnaire pour stocker les informations sur les mots
        mots_info = {}

        # Initialiser un dictionnaire pour stocker le nombre total de documents contenant chaque mot
        doc_freq = defaultdict(int)

        # Parcourir les documents et remplir les informations sur les mots
        for mot in self.vocabulaire:
            # Initialiser le nombre total d'occurrences et de documents contenant le mot
            nb_occurrences = 0
            nb_documents_contenant = 0

            # Parcourir les documents et mettre à jour les compteurs
            for doc in self.id2doc.values():
                if mot in doc.texte.lower():
                    nb_occurrences += doc.texte.lower().count(mot)
                    nb_documents_contenant += 1

            # Créer le sous-dictionnaire pour le mot
            info_mot = {
                'Identifiant': len(mots_info) + 1,
                'Nombre total d\'occurrences': nb_occurrences,
                'Nombre total de documents contenant le mot': nb_documents_contenant
            }

            # Ajouter le sous-dictionnaire au dictionnaire mots_info
            mots_info[mot] = info_mot

            # Mettre à jour le dictionnaire doc_freq
            doc_freq[mot] = nb_documents_contenant

        # Triez les mots par ordre alphabétique
        vocab_list = sorted(self.vocabulaire)

        # Construire le dictionnaire vocab
        self.vocab = {mot: mots_info[mot] for mot in vocab_list}

    def afficher_vocab(self):
        #Afficher le dictionnaire vocab.
        if not hasattr(self, 'vocab'):
            # Construire le dictionnaire vocab si ce n'est pas encore fait
            self.construire_vocab()

        print("Dictionnaire vocab :")
        for mot, info in self.vocab.items():
            print(f"{mot}: {info}")

    def construire_matrice_TF(self):
        #Construire la matrice de Term Frequency (TF).
        if not hasattr(self, 'vocab'):
            # Construire le dictionnaire vocab si ce n'est pas encore fait
            self.construire_vocab()

        # Initialiser une liste pour stocker les indices des colonnes dans la matrice
        colonnes_indices = []

        # Initialiser des listes pour stocker les valeurs des données et les indices des lignes
        valeurs_data = []
        indices_lignes = []

        # Parcourir les documents et remplir les listes
        for idx, doc in self.id2doc.items():
            for mot, info in self.vocab.items():
                if mot in doc.texte.lower():
                    # Ajouter l'indice de colonne
                    colonnes_indices.append(info['Identifiant'] - 1)  # Soustraire 1 pour obtenir l'indice 0-based

                    # Ajouter la valeur du TF
                    valeurs_data.append(doc.texte.lower().count(mot))

                    # Ajouter l'indice de ligne
                    indices_lignes.append(idx - 1)  # Soustraire 1 pour obtenir l'indice 0-based

        # Construire la matrice de Term Frequency (TF) avec sparse.csr_matrix
        self.mat_TF = csr_matrix((valeurs_data, (indices_lignes, colonnes_indices)),
                                 shape=(len(self.id2doc), len(self.vocab)))

    def afficher_matrice_TF(self):
        #Afficher la matrice de Term Frequency (TF).
        if not hasattr(self, 'mat_TF'):
            # Construire la matrice de Term Frequency (TF) si ce n'est pas encore fait
            self.construire_matrice_TF()

        print("Matrice de Term Frequency (TF) :")
        print(self.mat_TF)
    
    def construire_matrice_TF_IDF(self):
        #Construire la matrice TF-IDF.
        if not hasattr(self, 'vocab'):
            # Construire le dictionnaire vocab si ce n'est pas encore fait
            self.construire_vocab()

        # Extraire les textes des documents
        textes = [doc.texte.lower() for doc in self.id2doc.values()]

        # Utiliser TfidfVectorizer pour calculer la matrice TF-IDF
        vectorizer = TfidfVectorizer(vocabulary=self.vocabulaire)
        self.mat_TF_IDF = vectorizer.fit_transform(textes)

    def afficher_matrice_TF_IDF(self):
        #Afficher la matrice TF-IDF.
        if not hasattr(self, 'mat_TF_IDF'):
            # Construire la matrice TF-IDF si ce n'est pas encore fait
            self.construire_matrice_TF_IDF()

        print("Matrice TF-IDF :")
        print(self.mat_TF_IDF)