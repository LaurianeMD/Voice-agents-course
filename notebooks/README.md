# Retrouver un notebook ou un exercice

Commencer par la ligne du module dans le tableau. Le détail plus bas donne le titre exact de chaque section et les numéros des exercices associés.

Dans JupyterLab, ouvrir la **table des matières** du notebook pour rejoindre une section. Pour un exercice précis, utiliser la recherche du notebook avec son libellé, par exemple `Exercice 7.1`. **Le numéro d’un exercice peut différer du numéro de sa section** : l’exercice 7.1 se trouve dans la section 7.2.

Avant de travailler sur une section, exécuter la configuration puis les cellules précédentes dont elle dépend.

## Accès par module

| Jour | Module | Travail à ouvrir | Exercices / sections |
| --- | --- | --- | --- |
| 1 | 01 — Panorama et architecture d'un agent vocal | [Notebook jour 1](participants/jour1_fondations.ipynb) | [Repères du module 1](#module-01) |
| 1 | 02 — Le son numérique | [Notebook jour 1](participants/jour1_fondations.ipynb) | [Repères du module 2](#module-02) |
| 1 | 03 — Le transport temps réel | [Notebook jour 1](participants/jour1_fondations.ipynb) | [Repères du module 3](#module-03) |
| 1 | 04 — Awa no-code | [Fiche atelier](../supports/jour-01/module-04-awa-no-code/Fiche_atelier_Module4.docx) · [Kit](../supports/jour-01/module-04-awa-no-code/kit/) | Atelier sans notebook |
| 2 | 05 — La reconnaissance vocale (STT) : l'oreille d'Awa | [Notebook jour 2](participants/jour2_briques.ipynb) | [Repères du module 5](#module-05) |
| 2 | 06 — Le LLM dans une boucle vocale : le cerveau d'Awa | [Notebook jour 2](participants/jour2_briques.ipynb) | [Repères du module 6](#module-06) |
| 2 | 07 — La synthèse vocale (TTS) : la voix d'Awa | [Notebook jour 2](participants/jour2_briques.ipynb) | [Repères du module 7](#module-07) |
| 3 | 08 — L'orchestration et le pipeline : faire travailler les briques ensemble | [Notebook jour 3](participants/jour3_conversation.ipynb) | [Repères du module 8](#module-08) |
| 3 | 09 — Tours de parole et interruptions : la patience d'Awa | [Notebook jour 3](participants/jour3_conversation.ipynb) | [Repères du module 9](#module-09) |
| 3 | 10 — Attente, objections, transfert et accents : une Awa fluide | [Notebook jour 3](participants/jour3_conversation.ipynb) | [Repères du module 10](#module-10) |
| 4 | 11 — L'architecture speech-to-speech : Awa sans texte au milieu | [Notebook jour 4](participants/jour4_s2s_evaluation_production.ipynb) | [Repères du module 11](#module-11) |
| 4 | 12 — Évaluer un agent vocal : mesurer avant de choisir | [Notebook jour 4](participants/jour4_s2s_evaluation_production.ipynb) | [Repères du module 12](#module-12) |
| 4 | 13 — Production, sécurité et conformité : mettre Awa en service | [Notebook jour 4](participants/jour4_s2s_evaluation_production.ipynb) | [Repères du module 13](#module-13) |

## Repères dans les notebooks

Les repères reprennent les titres réellement présents dans les notebooks. Les quiz se trouvent à la fin de chaque module. Les ateliers et les sections optionnelles sont indiqués dans leur titre.

<a id="module-01"></a>

### Module 01 — Panorama et architecture d'un agent vocal

[Ouvrir le notebook](participants/jour1_fondations.ipynb)

| Section à retrouver dans la table des matières | Exercices identifiés |
| --- | --- |
| 1.0 Rappel : l'anatomie d'un agent vocal | Activité, démonstration ou préparation de la section |
| 1.1 Un agent simulé | 1.1 (guidé) |
| 1.2 Séquentiel contre streaming | 1.2 (guidé), 1.2 bis (avancé) |
| 1.3 Le budget de latence | 1.3 (guidé) |
| 1.4 Simuler un appel d'outil | 1.4 (guidé) |
| 1.5 [Avancé, optionnel] Mesurer un vrai LLM | Activité, démonstration ou préparation de la section |

<a id="module-02"></a>

### Module 02 — Le son numérique

[Ouvrir le notebook](participants/jour1_fondations.ipynb)

| Section à retrouver dans la table des matières | Exercices identifiés |
| --- | --- |
| 2.1 Échantillonner et replier | 2.1 (guidé) |
| 2.2 La voix au téléphone | 2.2 (guidé) |
| 2.3 PCM, débit et µ-law | 2.3 (guidé), 2.3 bis (avancé) |
| 2.4 Trames et énergie | 2.4 (guidé), 2.4 bis (avancé) |
| 2.5 Bruit et écho | 2.5 (guidé) |
| 2.6 Atelier : votre propre voix | Activité, démonstration ou préparation de la section |

<a id="module-03"></a>

### Module 03 — Le transport temps réel

[Ouvrir le notebook](participants/jour1_fondations.ipynb)

| Section à retrouver dans la table des matières | Exercices identifiés |
| --- | --- |
| 3.1 Requête contre streaming, sur un vrai réseau local | 3.1 (guidé) |
| 3.2 TCP contre UDP | 3.2 (guidé) |
| 3.3 Le tampon de gigue | 3.3 (guidé) |
| 3.4 Les pertes à l'oreille | 3.4 (guidé), 3.4 bis (avancé) |
| 3.5 Le budget réseau depuis Dakar | 3.5 (guidé) |

<a id="module-05"></a>

### Module 05 — La reconnaissance vocale (STT) : l'oreille d'Awa

[Ouvrir le notebook](participants/jour2_briques.ipynb)

| Section à retrouver dans la table des matières | Exercices identifiés |
| --- | --- |
| 5.1 Ce que voit un modèle STT : le spectrogramme log-mel | 5.1 (guidé) |
| 5.2 Coder le WER à partir de zéro | Activité, démonstration ou préparation de la section |
| 5.3 Normaliser avant de mesurer | 5.3 (guidé) |
| 5.4 Ce que le WER ne voit pas : les entités | 5.4 (guidé) |
| 5.5 Résultats partiels et endpointing | 5.5 (guidé) |
| 5.6 Le vocabulaire métier : keyterms et post-correction | 5.6 (guidé) |
| 5.7 (Optionnel) Un vrai STT sur votre voix | Activité, démonstration ou préparation de la section |

<a id="module-06"></a>

### Module 06 — Le LLM dans une boucle vocale : le cerveau d'Awa

[Ouvrir le notebook](participants/jour2_briques.ipynb)

| Section à retrouver dans la table des matières | Exercices identifiés |
| --- | --- |
| 6.1 Écrire pour l'oral | 6.1 (guidé) |
| 6.2 Le contexte : tout est renvoyé à chaque tour | 6.2 (guidé) |
| 6.3 TTFT et streaming : la latence que le prospect entend | 6.3 (guidé) |
| 6.4 Le cycle d'un appel d'outil | 6.4 (guidé) |
| 6.5 Valider les arguments côté serveur | 6.5 (guidé) |
| 6.6 Idempotence : un appel répété ne doit pas agir deux fois | 6.6 (avancé) |
| 6.7 (Optionnel) Un vrai LLM : mesurer le TTFT et observer la décision | Activité, démonstration ou préparation de la section |

<a id="module-07"></a>

### Module 07 — La synthèse vocale (TTS) : la voix d'Awa

[Ouvrir le notebook](participants/jour2_briques.ipynb)

| Section à retrouver dans la table des matières | Exercices identifiés |
| --- | --- |
| 7.1 Du texte au son : trois étapes | Activité, démonstration ou préparation de la section |
| 7.2 Dire les nombres en français | 7.1 (guidé) |
| 7.3 Normaliser les dates, montants, e-mails et numéros | 7.2 (avancé) |
| 7.4 Streaming et TTFB : la latence de la voix | Activité, démonstration ou préparation de la section |
| 7.5 Prononciation des noms propres | Activité, démonstration ou préparation de la section |
| 7.6 Choisir la voix d'Awa sur des critères mesurés | 7.3 (guidé) |
| 7.7 (Optionnel) Un vrai TTS : mesurer le TTFB | Activité, démonstration ou préparation de la section |

<a id="module-08"></a>

### Module 08 — L'orchestration et le pipeline : faire travailler les briques ensemble

[Ouvrir le notebook](participants/jour3_conversation.ipynb)

| Section à retrouver dans la table des matières | Exercices identifiés |
| --- | --- |
| 8.1 Le parcours d'un tour de parole | Activité, démonstration ou préparation de la section |
| 8.2 `asyncio` en cinq minutes | 8.1 (guidé) |
| 8.3 Un mini pipeline avec des files | 8.2 (guidé) |
| 8.4 Ce qui tourne en parallèle, ce qui reste en séquence | Activité, démonstration ou préparation de la section |
| 8.5 Le budget de latence, brique par brique | 8.3 (guidé) |
| 8.6 [Avancé] Annuler une réponse en cours | 8.4 (avancé) |
| 8.7 Instrumenter Awa : lire les mesures de chaque tour | 8.5 (guidé) |

<a id="module-09"></a>

### Module 09 — Tours de parole et interruptions : la patience d'Awa

[Ouvrir le notebook](participants/jour3_conversation.ipynb)

| Section à retrouver dans la table des matières | Exercices identifiés |
| --- | --- |
| 9.1 Le rythme d'une conversation humaine | Activité, démonstration ou préparation de la section |
| 9.2 Le VAD : voir la parole image par image | 9.1 (guidé) |
| 9.3 Faire varier le seuil et le silence | Activité, démonstration ou préparation de la section |
| 9.4 Phrases incomplètes : la fin de tour sémantique | 9.2 (guidé) |
| 9.5 [Avancé] Combiner le VAD et la règle sémantique | 9.3 (avancé) |
| 9.6 Quand le prospect parle pendant qu'Awa parle | 9.4 (guidé) |
| 9.7 Mettre à jour le contexte après une interruption | 9.5 (guidé) |
| 9.8 Atelier : régler la patience d'Awa | Activité, démonstration ou préparation de la section |

<a id="module-10"></a>

### Module 10 — Attente, objections, transfert et accents : une Awa fluide

[Ouvrir le notebook](participants/jour3_conversation.ipynb)

| Section à retrouver dans la table des matières | Exercices identifiés |
| --- | --- |
| 10.1 Le silence pendant un outil lent | 10.1 (guidé) |
| 10.2 Un outil lent en asyncio : filler, relance, timeout | Activité, démonstration ou préparation de la section |
| 10.3 Choisir le filler selon le contexte, sans répétition | 10.2 (avancé) |
| 10.4 Les objections commerciales | 10.3 (guidé), 10.4 (guidé) |
| 10.5 Le transfert vers un humain | 10.5 (guidé) |
| 10.6 Accents et choix du STT | 10.6 (guidé) |
| 10.7 Atelier : une Awa fluide | Activité, démonstration ou préparation de la section |

<a id="module-11"></a>

### Module 11 — L'architecture speech-to-speech : Awa sans texte au milieu

[Ouvrir le notebook](participants/jour4_s2s_evaluation_production.ipynb)

| Section à retrouver dans la table des matières | Exercices identifiés |
| --- | --- |
| 11.1 Cascade ou speech-to-speech ? | 11.1 (guidé) |
| 11.2 L'audio dans une session Realtime | 11.2 (guidé) |
| 11.3 Lire les événements d'une session Realtime | 11.3 (guidé) |
| 11.4 `server_vad` contre `semantic_vad` | 11.4 (guidé) |
| 11.5 Les outils en speech-to-speech | 11.5 (guidé), 11.6 (avancé) |
| 11.6 Contrôle contre naturel | 11.7 (guidé) |
| 11.7 Ouvrir une vraie session Realtime (optionnel) | Activité, démonstration ou préparation de la section |
| 11.8 Atelier : Awa en speech-to-speech contre Awa en cascade | Activité, démonstration ou préparation de la section |

<a id="module-12"></a>

### Module 12 — Évaluer un agent vocal : mesurer avant de choisir

[Ouvrir le notebook](participants/jour4_s2s_evaluation_production.ipynb)

| Section à retrouver dans la table des matières | Exercices identifiés |
| --- | --- |
| 12.1 La méthode : cinq étapes | Activité, démonstration ou préparation de la section |
| 12.2 Le jeu de 20 scénarios | Activité, démonstration ou préparation de la section |
| 12.3 Simuler des appels et enregistrer des traces | Activité, démonstration ou préparation de la section |
| 12.4 Le taux de rendez-vous | 12.1 (guidé) |
| 12.5 L'exactitude des données CRM | 12.2 (guidé) |
| 12.6 La latence : médiane et p95 | 12.3 (guidé) |
| 12.7 Le WER sur les noms et les numéros | 12.4 (guidé) |
| 12.8 Le coût par appel | 12.5 (guidé) |
| 12.9 Le tableau de bord | Activité, démonstration ou préparation de la section |
| 12.10 Combien de confiance accorder à ces chiffres ? | Activité, démonstration ou préparation de la section |
| 12.11 [Avancé] Un LLM juge | 12.6 (avancé) |
| 12.12 Choisir à partir des chiffres | 12.7 (guidé) |
| 12.13 Atelier : choisir entre cascade et speech-to-speech | Activité, démonstration ou préparation de la section |

<a id="module-13"></a>

### Module 13 — Production, sécurité et conformité : mettre Awa en service

[Ouvrir le notebook](participants/jour4_s2s_evaluation_production.ipynb)

| Section à retrouver dans la table des matières | Exercices identifiés |
| --- | --- |
| 13.1 Où faire tourner Awa ? | Activité, démonstration ou préparation de la section |
| 13.2 La téléphonie SIP et l'appel sortant | 13.1 (guidé) |
| 13.3 Le coût mensuel | 13.2 (guidé) |
| 13.4 Sécurité : les clés et les données vocales | 13.3 (guidé) |
| 13.5 Annonce de l'IA, consentement et horaires | 13.4 (guidé) |
| 13.6 [Avancé] Masquer les données personnelles dans les journaux | 13.5 (avancé) |
| 13.7 Atelier : déployer Awa sur un numéro de test et passer un appel sortant | Activité, démonstration ou préparation de la section |

## Autres accès utiles

- [Supports et présentations des 13 modules](../supports/README.md)
- [Code partagé Awa et CRM](../code/README.md)
- [Accueil du cours](../README.md)
