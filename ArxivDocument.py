from Document import Document

class ArxivDocument(Document):
    def __init__(self, titre="", auteurs=None, date="", url="", resume=""):
        # Appeler le constructeur de la classe mère avec super()
        super().__init__(titre, "", date, url, resume)  # L'auteur est une liste, pas une chaîne vide
        # Ajouter la variable spécifique à ArxivDocument
        self.auteurs = auteurs if auteurs else []  # Liste des co-auteurs

    # Accesseurs/mutateurs pour la variable spécifique
    def get_auteurs(self):
        return self.auteurs

    def set_auteurs(self, auteurs):
        self.auteurs = auteurs

    # Méthode spécifique pour l'affichage de l'objet
    def __str__(self):
        # Utiliser super().__str__() pour obtenir la représentation de la classe mère
        return f"{super().__str__()}, Auteurs : {', '.join(self.auteurs)}"