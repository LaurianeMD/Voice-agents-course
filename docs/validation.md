# Validation locale du cours

Validation réalisée le 2 novembre 2026 sous Windows avec Python 3.14.2, dans l’environnement `.venv` du dépôt.

| Vérification | Résultat |
| --- | --- |
| Format des 8 notebooks, via `nbformat.validate` | Valide |
| Exécution du corrigé du jour 1 | Aucune erreur de cellule |
| Exécution du corrigé du jour 2 | Aucune erreur de cellule |
| Exécution du corrigé du jour 3 | Aucune erreur de cellule |
| Exécution du corrigé du jour 4 | Aucune erreur de cellule |
| Auto-test du CRM, y compris HTTP local | Réussi |
| Cohérence des dépendances, via `pip check` | Aucun conflit |

Les corrigés ont été exécutés intégralement, avec `OPENAI_API_KEY` retirée de l’environnement de validation. Les sections optionnelles utilisant les fournisseurs ont donc été ignorées par leurs conditions prévues. Les services OpenAI, LiveKit et téléphoniques ne sont pas couverts par cette validation. Les notebooks participants ont été validés structurellement ; leurs exercices à compléter ne sont pas exécutés automatiquement.

Versions utilisées : NumPy 2.5.4, SciPy 1.18.1, Matplotlib 3.11.2, websockets 17.4, nbclient 0.11.0 et nbformat 5.11.1.

Les copies exécutées et le rapport détaillé sont disponibles localement dans `.validation/`, ignoré par Git. Les notebooks sources sont inchangés par la validation. Pour reproduire la vérification, suivre le [guide des scripts](../scripts/README.md).
