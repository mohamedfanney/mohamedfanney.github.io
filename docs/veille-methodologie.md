# Veille technologique BTS SIO – SISR

## Sujet
Suivi des fuites de données, des cyberattaques et des vulnérabilités affectant les systèmes et les réseaux.

## Sources
- ZATAZ : https://www.zataz.com/feed/
- DataBreaches.net : https://databreaches.net/feed/
- BleepingComputer : https://www.bleepingcomputer.com/feed/

## Collecte
Le programme `scripts/maj_veille.py` lit les flux RSS (ou Atom), conserve les titres, de courts extraits, la date, le lien de l'article et la source, puis classe les articles par mots-clés.

Le workflow `.github/workflows/veille-rss.yml` tente une actualisation quatre fois par jour et lors d'un déclenchement manuel. Si toutes les sources échouent, les dernières données restent inchangées. Si le cache GitHub n'est pas disponible, le portfolio essaie l'ancienne passerelle RSS.

## Démarche pour l'épreuve
Pour présenter une veille exploitable à l'oral, sélectionner quelques articles, justifier leur intérêt, comparer les informations, expliquer leurs conséquences et décrire les précautions adaptées à un environnement systèmes et réseaux. Ne pas présenter le simple flux automatique comme une analyse personnelle.

## Vérification
1. Ouvrir le portfolio et la section « Veille technologique ».
2. Vérifier les filtres et les liens vers les sources.
3. Consulter GitHub > Actions > « Actualiser les flux RSS du portfolio » pour vérifier l'historique.
4. Ouvrir `data/veille-rss.json` pour la date et les sources réellement récupérées.
