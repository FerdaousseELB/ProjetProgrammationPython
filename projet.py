import praw
# Identification
reddit = praw.Reddit(client_id='KTdgvYo7sGyiNb02hQZWJQ', client_secret='wTyymqM0ysjUrLrK7nkLMZHwq1ERlg', user_agent='ferdaousse')
# Requête
hot_posts = reddit.subreddit('corona').hot(limit=100)
# Récupération du texte
docs = []
docs_bruts = []
for i, post in enumerate(hot_posts):
	if post.selftext != "":  # Osef des posts sans texte
		docs.append(post.selftext.replace("\n", " "))
		docs_bruts.append(("Reddit", post))
# affichage de la taille des posts retenus
print(len(docs))
print(len(docs_bruts))