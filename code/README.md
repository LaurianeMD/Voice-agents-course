# Code des ateliers Awa

| Fichier | Rôle |
| --- | --- |
| [baobab_api.py](baobab_api.py) | CRM et agenda simulés, importables ou exposés en HTTP local ; bibliothèque standard uniquement |
| [tts_normalisation.py](tts_normalisation.py) | Normalisation du texte français avant synthèse vocale ; bibliothèque standard uniquement |
| [awa_agent.py](awa_agent.py) | Agent LiveKit : outils, synthèse, latences, tours de parole, transfert, cascade/realtime |

Depuis la racine du dépôt, vérifier le CRM sans service externe :

```powershell
python code/baobab_api.py --selftest
```

Le code fourni mentionne LiveKit Agents `1.8.10` comme version testée par son auteur. L’intégration aux fournisseurs n’est pas validée par la seule organisation du dépôt.

```powershell
python -m pip install "livekit-agents==1.8.10"
python code/baobab_api.py --port 8077
```

Dans un second terminal, avec le même environnement Python, renseigner `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` dans l’environnement, puis lancer :

```powershell
python code/awa_agent.py console --text
```

Pour le mode vocal, renseigner `AWA_TTS_MODELE` et `AWA_TTS_VOIX` selon l’atelier, puis lancer `python code/awa_agent.py console`. Les autres paramètres sont documentés dans le code et les notebooks. Le mode realtime utilise aussi `livekit-plugins-openai`, à installer pour cet atelier. Les expériences OpenAI des notebooks utilisent le paquet `openai` et `OPENAI_API_KEY`.

Les clés restent dans les variables d’environnement. Les journaux `awa_metriques.jsonl` sont produits dans le répertoire courant et ignorés par Git.
