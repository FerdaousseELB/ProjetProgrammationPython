#exo 1.1
import praw
# Identification
reddit = praw.Reddit(client_id='KTdgvYo7sGyiNb02hQZWJQ', client_secret='wTyymqM0ysjUrLrK7nkLMZHwq1ERlg', user_agent='ferdaousse')
# Requête
posts = reddit.subreddit('corona').hot(limit=100)
# Récupération du texte
docs = []
docs_bruts = []
for i, post in enumerate(posts):
	if post.selftext != "":  # ne pas retenir les posts avec selftext vide
		docs.append(post.selftext.replace("\n", " "))
		docs_bruts.append(("Reddit", post))
# affichage de la taille des posts retenus
print(len(docs))
print(len(docs_bruts))

#exo 1.2
import urllib, urllib.request
import xmltodict

# Paramètres
query_terms = ["corona"]
max_results = 100

# Requête
url = f'http://export.arxiv.org/api/query?search_query=all:{"+".join(query_terms)}&start=0&max_results={max_results}'
entries = urllib.request.urlopen(url)

# Format dict (OrderedDict)
data = xmltodict.parse(entries.read().decode('utf-8'))

# Ajout résumés à la liste
for i, entry in enumerate(data["feed"]["entry"]):
	if entry["summary"] != "": # ne pas retenir les entries avec summary vide
		docs.append(entry["summary"].replace("\n", ""))
		docs_bruts.append(("ArXiv", entry))

# affichage de la taille finale : post + enttries
print(len(docs))
print(len(docs_bruts))