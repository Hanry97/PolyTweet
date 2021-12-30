-- SQLite
--INSERT INTO candidats (nom,parti_poli,datenaisse,urlphoto) VALUES ('Marine Le Pen','Rassemblement national','1968-08-05','https://www.francetvinfo.fr/docs/desk3/candidat-tracker/2021_10_11_marine_le_pen.png');
SELECT candidat_id, nom, count(created_at) as created_at from tweets t INNER JOIN candidats c ON c.id=t.candidat_id  group by t.candidat_id;
INSERT INTO candidats (nom,parti_poli,datenaisse,urlphoto) VALUES ('Anne Hidalgo','Parti socialiste','1959-06-19','https://cdn-s-www.leprogres.fr/images/B053E572-6FFD-452A-91B9-5FB2C204A920/NW_raw/anne-hidalgo-veut-porter-un-programme-axe-sur-la-transition-ecologique-et-l-education-photo-afp-bertrand-guay-1631380975.jpg');

DELETE FROM tweets; DELETE FROM feelings;
DELETE FROM candidats;
SELECT COUNT(*) as positif FROM tweets WHERE candidat_id=1 AND score >0;

ALTER TABLE tweets
  ADD score_vader REAL DEFAULT -100;

ALTER TABLE tweets ADD lat REAL DEFAULT 0.0;

UPDATE tweets SET score_vader = 0.1 WHERE tweet_id = 1468218628701138944; 