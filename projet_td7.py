import pandas as pd
from Corpus import Corpus
from Document import Document

# Charger le DataFrame à partir du fichier CSV
loaded_corpus_df = pd.read_csv('corpus_data.csv', sep='\t')

# Convertir le DataFrame en Corpus
loaded_corpus = Corpus("Mon corpus chargé")

for index, row in loaded_corpus_df.iterrows():
    doc = Document(
        titre=row['Titre'],
        auteur=row['Auteur'],
        date=row['Date'],
        url=row['URL'],
        texte=row['Texte']
    )
    loaded_corpus.add(doc)  

# Afficher le Corpus chargé
print(loaded_corpus)
print('####################################')
print('####################################')
#loaded_corpus.show(tri="123")
print('####################################')
print('####################################')
loaded_corpus.search("about")
print('####################################')
print('####################################')
loaded_corpus.concorde("about")
print('####################################')
print('####################################')
loaded_corpus.stats(top_n_words=15)
print('####################################')
print('####################################')
loaded_corpus.afficher_vocabulaire()
print('####################################')
print('####################################')
loaded_corpus.afficher_tableau_frequences()
print('####################################')
print('####################################')
loaded_corpus.afficher_vocab()
print('####################################')
print('####################################')
loaded_corpus.afficher_matrice_TF()
print('####################################')
print('####################################')
loaded_corpus.afficher_matrice_TF_IDF()