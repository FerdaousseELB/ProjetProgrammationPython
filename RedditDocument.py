from Document import Document

class RedditDocument(Document):
    def __init__(self, titre="", auteur="", date="", url="", texte="", nombre_commentaires=0):
        # Appeler le constructeur de la classe mère avec super()
        super().__init__(titre, auteur, date, url, texte)
        # Ajouter la variable spécifique à RedditDocument
        self.nombre_commentaires = nombre_commentaires

    # Accesseurs/mutateurs pour la variable spécifique
    def get_nombre_commentaires(self):
        return self.nombre_commentaires

    def set_nombre_commentaires(self, nombre_commentaires):
        self.nombre_commentaires = nombre_commentaires

    # Méthode spécifique pour l'affichage de l'objet
    def __str__(self):
        # Utiliser super().__str__() pour obtenir la représentation de la classe mère
        return f"{super().__str__()}, Commentaires : {self.nombre_commentaires}"