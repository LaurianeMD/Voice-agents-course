# Agents vocaux de 0 à Z

Formation sur quatre journées et 13 modules. Fil rouge : **Awa**, assistante commerciale vocale de Baobab Software, entreprise fictive.

**[Trouver rapidement un exercice ou un notebook →](notebooks/README.md)** — accès par module, section et numéro d’exercice, avec des repères précis dans chaque notebook.

## Parcours

| Journée | Modules et supports | Notebook participant |
| --- | --- | --- |
| 1 — Fondations | [1 à 4](supports/jour-01/) : panorama, son numérique, transport temps réel, Awa no-code | [Fondations](notebooks/participants/jour1_fondations.ipynb) |
| 2 — Les briques d’Awa | [5 à 7](supports/jour-02/) : reconnaissance vocale, LLM et outils, synthèse vocale | [Les briques](notebooks/participants/jour2_briques.ipynb) |
| 3 — La conversation | [8 à 10](supports/jour-03/) : orchestration, tours de parole, attente et transfert | [Conversation](notebooks/participants/jour3_conversation.ipynb) |
| 4 — Évaluation et production | [11 à 13](supports/jour-04/) : speech-to-speech, évaluation, production et sécurité | [S2S, évaluation, production](notebooks/participants/jour4_s2s_evaluation_production.ipynb) |

Le [catalogue des supports](supports/README.md) donne accès aux 13 présentations PowerPoint et au kit de l’atelier no-code.

## Démarrer les notebooks

Depuis la racine du dépôt, avec Python 3.10 ou supérieur (minimum syntaxique du code fourni) :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m jupyterlab
```

Ouvrir le notebook voulu dans `notebooks/participants/` et exécuter les cellules dans l’ordre, en commençant par la configuration. Les exercices comprennent des cellules à compléter. Les versions corrigées sont conservées localement par le formateur et exclues de ce dépôt distant.

Les simulations sont prévues pour fonctionner hors ligne après installation des dépendances. Les sections optionnelles OpenAI demandent le paquet `openai` et la variable d’environnement `OPENAI_API_KEY`. Le notebook du jour 2 retrouve automatiquement `code/baobab_api.py` depuis le dépôt complet. Pour un enregistrement personnel, placer `ma_voix.wav` à côté du notebook, comme indiqué dans l’exercice.

Pour les ateliers de l’agent vocal, consulter le [guide du code Awa](code/README.md).

Pour relancer la vérification du format des notebooks, l’exécution des corrigés hors ligne et le test du CRM, suivre les [instructions de validation](scripts/README.md).

La [validation locale](docs/validation.md) des quatre corrigés et du CRM a réussi sous Windows avec Python 3.14.2, en mode hors ligne.

## Organisation

```text
supports/                 Présentations par journée et module, fiche atelier et kit
notebooks/participants/   Exercices des quatre journées
code/                     Agent Awa, CRM et agenda simulés, normalisation TTS
scripts/                  Outils de validation du cours
docs/                     Notes et corrections pédagogiques fournies
```

## Sources et versions

Les supports proviennent des ZIP `Formation_Agents_Vocaux_Modules1-5.zip` et `Agents_vocaux_0_a_Z.zip`. Le parcours utilise la version complète du notebook du jour 2, couvrant les modules 5 à 7.

Les dossiers `formateur/`, `notebooks/formateur/` et `archives/`, ainsi que `scripts/build_jour2.py`, restent uniquement en local : ils contiennent les corrigés ou permettent de les reconstituer. Ils sont exclus par `.gitignore`.

Les supports bureautiques et le code source sont conservés tels que fournis. Seuls les deux notebooks complets du jour 2 ont été adaptés pour retrouver le dossier `code/`. Les [corrections signalées sur les modules 4 et 5](docs/corrections_modules_4_5.md) sont des notes historiques livrées dans le ZIP : elles restent à vérifier sur les présentations disponibles.
