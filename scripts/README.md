# Scripts du cours

## Validation des notebooks

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-validation.txt
.\.venv\Scripts\python.exe scripts/valider_notebooks.py
```

Le script vérifie le format des huit notebooks, exécute les quatre corrigés puis l’auto-test du CRM local. Il désactive `OPENAI_API_KEY` pour ignorer les appels aux fournisseurs. Les exercices participants comportant des trous à compléter ne sont pas exécutés automatiquement.

Les copies exécutées et le rapport JSON sont écrits dans `.validation/`, ignoré par Git. Les notebooks du cours restent inchangés. Jupyter et les exercices WebSocket nécessitent les connexions locales à `127.0.0.1`.

Les corrigés doivent être présents localement dans `notebooks/formateur/` pour lancer cette commande. Ils ne sont pas publiés dans le dépôt distant. Le générateur historique `build_jour2.py`, qui contient des solutions, reste lui aussi en local.
