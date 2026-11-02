# Méthodologie de veille Wazuh — BTS SIO SISR

**Sujet :** suivi de la plateforme SIEM/XDR Wazuh, versions, correctifs de sécurité, agents et nouvelles fonctionnalités.

## Sources
- [Blog officiel et flux RSS Wazuh](https://wazuh.com/feed/)
- [Releases Wazuh GitHub](https://github.com/wazuh/wazuh/releases)
- [Security Advisories Wazuh](https://github.com/wazuh/wazuh/security/advisories)
- [Flux du CERT-FR](https://www.cert.cyber.gouv.fr/flux-rss)

## Collecte et recherche
Le script `scripts/maj_veille.py` collecte les flux RSS/Atom et les avis via l'API GitHub si accessible. L'action GitHub `.github/workflows/veille-rss.yml` tente une collecte toutes les six heures, puis actualise `data/veille-wazuh.json`. Les anciennes données restent disponibles si une source échoue.

Le champ de recherche du portfolio cherche **dans cet index local de publications**, pas sur tout Internet. Les résultats s'ouvrent en fenêtres pop-up avec lien vers la publication officielle.

## Livrables scolaires
- Fiche de veille : `veille-wazuh.html`, imprimable
- Architecture de référence Wazuh, incluse dans la fiche
- Tableau de suivi : dans la section Veille du portfolio, avec sources et dates de collecte
- Synthèse initiale datée : dans la fiche
- Relevés hebdomadaires personnels : **à compléter** avec date, source, point retenu, impact et décision

**Attention :** les e-mails d'alerte ne sont pas configurés ; une collecte RSS n'est pas une preuve de lecture personnelle. Aucun déploiement Wazuh n'est revendiqué. La politique de support ou un éventuel statut LTS doit être vérifié directement auprès de l'éditeur avant une décision de migration.
