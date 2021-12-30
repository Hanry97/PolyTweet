import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()
#password = flask21
cur.execute("INSERT INTO users (nom,username,password) VALUES (?, ?, ?)",
            ('Hanry','Hanry22','sha256$iyO9Ketm5aTA2L0O$ba42f591ed2bd51ac68cca39c47ab409f88fc1d6df2b7fe7c4fd1ca94744f404')
            )
"""

cur.execute("INSERT INTO candidats (nom, parti_poli, datenaisse, urlphoto, twitter) VALUES (?, ?, ?, ?, ?)",
            ('Emmanuel Macron', 'République en Marche', '1977-12-21','https://lesjours.fr/ressources/square/people/emmanuel-macron-coronavirus.jpeg','@EmmanuelMacron')
            )

cur.execute("INSERT INTO candidats (nom, parti_poli, datenaisse, urlphoto, twitter) VALUES (?, ?, ?, ?, ?)",
            ('Éric Zemmour', 'Indépendant', '1958-08-31','https://resize-pdm.francedimanche.ladmedia.fr/rcrop/635,500/img/2021-05/bestimage-00345615-000029.jpeg?version=v1','@ZemmourEric')
            )

cur.execute("INSERT INTO candidats (nom,parti_poli,datenaisse,urlphoto, twitter) VALUES (?, ?, ?, ?, ?)",
            ('Marine Le Pen','Rassemblement national','1968-08-05','https://www.francetvinfo.fr/docs/desk3/candidat-tracker/2021_10_11_marine_le_pen.png','@MLP_officiel')
            )

cur.execute("INSERT INTO candidats (nom,parti_poli,datenaisse,urlphoto, twitter) VALUES (?, ?, ?, ?, ?)",
            ('Anne Hidalgo','Parti socialiste','1959-06-19','https://cdn-s-www.leprogres.fr/images/B053E572-6FFD-452A-91B9-5FB2C204A920/NW_raw/anne-hidalgo-veut-porter-un-programme-axe-sur-la-transition-ecologique-et-l-education-photo-afp-bertrand-guay-1631380975.jpg','@Hildalgo_2022_')
            )

"""
connection.commit()
connection.close()