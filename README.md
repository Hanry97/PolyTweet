# 1-Installer Flask 

https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3-fr

# 2-Créer et activer l'environnement de dev

virtualenv poly_tweet (création de l'environnement poly_tweet)
poly_tweet\Scripts\activate (activation)
pip install -r requirements.txt (installation des dépendances)

$env:FLASK_APP = "app"
flask run (lancement du serveur)

# 3-Si le fichier database.db n'existe pas, lancer le script de création de la database

python init_db.py 

# 4-Lancer le server

flask run

# 5-Longin as administrator

username = Hanry22
password = flask21