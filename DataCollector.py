import praw
import urllib.request
import xmltodict

class DataCollector:
    def __init__(self, subreddit='corona', limit=100, query_terms=["corona"], max_results=100):
        self.docs = []
        self.docs_bruts = []
        self.reddit_subreddit = subreddit
        self.reddit_limit = limit
        self.arxiv_query_terms = query_terms
        self.arxiv_max_results = max_results

    def collect_reddit_data(self):
        reddit = praw.Reddit(client_id='KTdgvYo7sGyiNb02hQZWJQ', client_secret='wTyymqM0ysjUrLrK7nkLMZHwq1ERlg', user_agent='ferdaousse')
        hot_posts = reddit.subreddit(self.reddit_subreddit).hot(limit=self.reddit_limit)

        for i, post in enumerate(hot_posts):
            if post.selftext != "":
                self.docs.append(post.selftext.replace("\n", " "))
                self.docs_bruts.append(("Reddit", post))

    def collect_arxiv_data(self):
        url = f'http://export.arxiv.org/api/query?search_query=all:{"+".join(self.arxiv_query_terms)}&start=0&max_results={self.arxiv_max_results}'
        data = urllib.request.urlopen(url)
        data = xmltodict.parse(data.read().decode('utf-8'))

        for i, entry in enumerate(data["feed"]["entry"]):
            self.docs.append(entry["summary"].replace("\n", ""))
            self.docs_bruts.append(("ArXiv", entry))
