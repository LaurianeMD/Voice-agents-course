"""awa_agent.py : Awa en Python avec LiveKit Agents (ateliers des modules 6 à 9).

Awa qualifie un prospect avec trois outils branchés sur le CRM et l'agenda simulés :
create_lead, check_availability, book_meeting. Module 7 : Awa annonce le rendez-vous à voix haute,
le texte étant normalisé (dates, montants, e-mails, numéros, noms propres) avant le TTS.
Module 8 : chaque tour est mesuré (e2e_latency, TTFT du LLM, TTFB du TTS), journalisé dans awa_metriques.jsonl
et résumé en médiane et p95 à la fin de l'appel.
Module 9 : la patience d'Awa se règle avec AWA_PATIENCE (vive, equilibree, patiente) ; AWA_TURN_DETECTOR=1 active
le détecteur de fin de tour audio de LiveKit (inference.TurnDetector).

Module 13 : annonce de l'IA dès la première phrase, journaux sans données personnelles (masquer_pii), appel sortant
(AWA_AGENT_NAME, AWA_SIP_TRUNK_ID, métadonnées {"phone_number": "+221..."}) avec contrôle des horaires et du numéro.

Préparation :
    1. Dans un premier terminal :   python baobab_api.py --port 8077
    2. Variables d'environnement LiveKit (LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET),
       nécessaires pour LiveKit Inference (STT et LLM).
    3. Dans un second terminal, en texte :
           python awa_agent.py console --text
       Pour entendre Awa (module 7), choisissez votre voix (voir l'atelier) et exportez son identifiant :
           export AWA_TTS_MODELE="cartesia/sonic-3"
           export AWA_TTS_VOIX="<identifiant de la voix choisie>"
       puis lancez :  python awa_agent.py console

Modes de lancement (console, dev, start, connect) : voir la page « Startup modes » de la
documentation LiveKit Agents. L'API évolue vite : vérifiez la version installée de livekit-agents
(testé avec la 1.8.10).
"""

import asyncio
import datetime as dt
import json
import logging
import os
import statistics
import re
import uuid
from collections.abc import AsyncIterable
from typing import Literal
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from livekit.agents import Agent, AgentServer, AgentSession, JobContext, RunContext, cli, function_tool, inference
from livekit.agents import llm
from livekit.agents.llm import ChatMessage, ToolError

from tts_normalisation import normaliser   # module 7 : texte écrit -> texte à dire

BAOBAB_URL = "http://127.0.0.1:8077"
JOURS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

PROMPT_SYSTEME = """Tu es Awa, l'assistante commerciale vocale de Baobab Software, éditeur d'un logiciel de gestion pour PME basé à Dakar.
Dès ta première phrase, présente-toi comme une assistante virtuelle (une intelligence artificielle) de Baobab Software. Si on te demande si tu es une personne ou une machine, dis la vérité.
Tu parles au téléphone : réponds en une ou deux phrases courtes, sans liste, sans gras, sans émoji.
Pose une seule question à la fois.
Tu qualifies le prospect (besoin, taille de l'entreprise, budget mensuel, délai), puis tu proposes un rendez-vous de 30 minutes.
N'invente jamais un créneau ni un prix : utilise tes outils.
Avant de réserver, répète le jour et l'heure au prospect et attends son accord.
Après la réservation, annonce le rendez-vous en une phrase (jour et heure) et dis qu'un message de confirmation sera envoyé.
Offres : Essentiel 25 000 F CFA par mois (jusqu'à 3 utilisateurs), Pro 49 000 F CFA par mois (jusqu'à 15 utilisateurs), Entreprise sur devis.
Seule réduction : deux mois offerts en paiement annuel.
Avant d'appeler un outil, dis une très courte phrase (par exemple « Je regarde l'agenda. »).
Objection de prix : reconnais-la, redonne le tarif exact, rappelle la seule réduction possible, puis propose un rendez-vous. N'invente jamais une autre remise.
Si le prospect préfère un e-mail, propose aussi un rendez-vous de 30 minutes, et relis l'adresse lettre par lettre.
Si le prospect demande un humain, est en colère, ou si tu échoues deux fois de suite, annonce le transfert et appelle transfer_to_human.
Si le prospect est hors cible (par exemple un étudiant), reste aimable, explique brièvement et conclus sans créer de fiche."""


# ---- module 13 : production, sécurité, conformité -------------------------------------
PHRASE_OUVERTURE = ("Bonjour, ici Awa, l'assistante virtuelle de Baobab Software. Je suis une intelligence artificielle. "
                    "Avez-vous deux minutes pour parler de la gestion de votre entreprise ?")
HORAIRES_APPEL = {"jours": (0, 1, 2, 3, 4), "debut": 9, "fin": 17}   # lundi à vendredi, 9 h à 17 h (repère indicatif, à valider par le juridique)

_RE_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_RE_TEL = re.compile(r"(?<!\d)(?:\+221[\s.-]?)?(?:7[05678])(?:[\s.-]?\d{2,3}){3}(?!\d)")


def masquer_pii(texte: str) -> str:
    """Remplace e-mails et numéros de téléphone sénégalais par des marqueurs, pour les journaux."""
    texte = _RE_EMAIL.sub("[EMAIL]", texte)
    return _RE_TEL.sub("[TEL]", texte)


class FiltrePII(logging.Filter):
    """À brancher sur un logger ou un handler : le message est masqué avant d'être écrit."""
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = masquer_pii(record.getMessage())
        record.args = ()
        return True


def numero_valide(numero: str) -> bool:
    """Numéro mobile sénégalais au format international : +221 puis 9 chiffres commençant par 70, 75, 76, 77 ou 78."""
    return re.fullmatch(r"\+221(?:70|75|76|77|78)\d{7}", re.sub(r"[\s.-]", "", numero)) is not None


def appel_autorise(maintenant: dt.datetime, numero: str, liste_refus: set | None = None, horaires: dict | None = None) -> tuple:
    """Contrôle avant un appel sortant : numéro valide, liste de refus, jour et heure (heure de Dakar). Renvoie (ok, raison)."""
    h = horaires or HORAIRES_APPEL
    if not numero_valide(numero):
        return False, "numéro invalide"
    if numero.replace(" ", "") in (liste_refus or set()):
        return False, "numéro sur la liste de refus"
    if maintenant.weekday() not in h["jours"]:
        return False, "jour non autorisé"
    if not h["debut"] <= maintenant.hour < h["fin"]:
        return False, "hors des horaires"
    return True, "ok"


def classer_echec_sip(code: int) -> str:
    """Classe un code SIP d'échec d'appel sortant (correspondance de la documentation LiveKit)."""
    if code in (486, 603):
        return "refuse"
    if code in (408, 480):
        return "indisponible"
    if 500 <= code <= 599:
        return "panne_operateur"
    return "autre"


# ---- validation côté serveur (module 6, section 6.5) ----------------------------------
def valider_date(valeur: str, aujourdhui: dt.date | None = None) -> dt.date:
    """Lève ToolError si la date n'est pas AAAA-MM-JJ, n'existe pas, est passée ou trop lointaine."""
    aujourdhui = aujourdhui or dt.date.today()
    if not isinstance(valeur, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", valeur):
        raise ToolError("date : format AAAA-MM-JJ obligatoire (par exemple 2026-11-10).")
    try:
        jour = dt.date.fromisoformat(valeur)
    except ValueError:
        raise ToolError("date : ce jour n'existe pas.")
    if jour < aujourdhui or jour > aujourdhui + dt.timedelta(days=60):
        raise ToolError("date : entre aujourd'hui et 60 jours.")
    return jour


# ---- normalisation avant TTS (module 7) ---------------------------------------------------
async def normaliser_flux(flux: AsyncIterable[str]) -> AsyncIterable[str]:
    """Regroupe le texte du LLM par phrase puis le normalise, car un chunk peut couper un nombre
    en deux (« 25 » puis « 000 F CFA »). Coût : la première phrase attend sa ponctuation finale."""
    tampon = ""
    async for morceau in flux:
        tampon += morceau
        # fin de phrase : . ! ? suivi d'un espace (évite de couper « 14. » dans une date ou « sow@baobab.sn »)
        while (m := re.search(r"[.!?]\s", tampon)):
            phrase, tampon = tampon[:m.end()], tampon[m.end():]
            yield normaliser(phrase)
    if tampon.strip():
        yield normaliser(tampon)


# ---- patience d'Awa (module 9) ----------------------------------------------------------
PROFILS_PATIENCE = {                     # secondes ; repères de départ, à régler sur de vrais appels (module 12)
    "vive": {"min_delay": 0.3, "max_delay": 1.5},
    "equilibree": {"min_delay": 0.5, "max_delay": 3.0},
    "patiente": {"min_delay": 0.9, "max_delay": 4.0},
}


def reglages_tours(profil: str = "equilibree", detecteur_audio: bool = False) -> dict:
    """Réglages de tours de parole pour AgentSession(turn_handling=...). Noms vérifiés dans livekit-agents 1.8.10 :
    endpointing (min_delay, max_delay), interruption (min_duration, min_words, mode, false_interruption_timeout...)."""
    if profil not in PROFILS_PATIENCE:
        raise ValueError(f"profil inconnu : {profil!r} (choisir parmi {sorted(PROFILS_PATIENCE)})")
    reglages: dict = {
        "endpointing": dict(PROFILS_PATIENCE[profil]),
        "interruption": {"min_duration": 0.5, "min_words": 1, "false_interruption_timeout": 2.0,
                         "resume_false_interruption": True},
    }
    if detecteur_audio:
        reglages["turn_detection"] = inference.TurnDetector()    # audio, recommandé par la documentation LiveKit
    return reglages


# ---- instrumentation (module 8) ---------------------------------------------------------
CHAMPS_MESURES = ("e2e_latency", "llm_node_ttft", "tts_node_ttfb", "end_of_turn_delay", "transcription_delay")


def enregistrer_tour(journal: list, role: str, metrics: dict | None) -> dict | None:
    """Garde les latences d'un message (en secondes) ; renvoie la ligne ajoutée, ou None si rien à mesurer.
    Les champs LLM et TTS sont vides avec un modèle speech-to-speech (documentation LiveKit)."""
    mesures = {k: metrics[k] for k in CHAMPS_MESURES if metrics and metrics.get(k) is not None}
    if not mesures:
        return None
    ligne = {"role": role, **mesures}
    journal.append(ligne)
    return ligne


def resumer(journal: list) -> dict:
    """Médiane et p95 en millisecondes, par champ. Le p95 demande au moins 20 tours pour être solide : repère indicatif."""
    resume = {}
    for champ in CHAMPS_MESURES:
        v = sorted(1000 * ligne[champ] for ligne in journal if champ in ligne)
        if v:
            p95 = v[min(len(v) - 1, max(0, round(0.95 * (len(v) - 1))))]
            resume[champ] = {"n": len(v), "mediane_ms": round(statistics.median(v)), "p95_ms": round(p95)}
    return resume


# ---- attente, relance, timeout et transfert (module 10) -------------------------------
SEUILS_ATTENTE = {"filler": 1.2, "relance": 4.0, "timeout": 8.0}      # secondes, repères indicatifs à régler sur vos appels
PHRASES_ATTENTE = {
    "agenda": ["Je regarde l'agenda.", "Je vérifie les disponibilités.", "Un instant, je consulte le planning."],
    "crm": ["Je note tout cela.", "Je prépare votre fiche, un instant.", "J'enregistre vos informations."],
    "generique": ["Un instant, s'il vous plaît.", "Je m'en occupe tout de suite."],
    "relance": ["Je suis toujours dessus, merci de patienter.", "Le système est un peu lent, je n'ai pas oublié votre demande."],
}
SECOURS_TIMEOUT = "Je n'arrive pas à joindre l'agenda pour le moment. Je peux vous rappeler, ou vous passer un conseiller."


def choisir_filler(outil: str, deja_dits: list, etape: int) -> str:
    """Étape 0 : phrase liée à l'outil. Étapes suivantes : relance. Jamais l'une des trois dernières phrases dites."""
    categorie = "relance" if etape >= 1 else (outil if outil in PHRASES_ATTENTE else "generique")
    candidates = PHRASES_ATTENTE[categorie]
    recentes = deja_dits[-3:]
    libres = [p for p in candidates if p not in recentes]
    phrase = (libres or [c for c in candidates if c != (deja_dits[-1] if deja_dits else None)] or candidates)[0]
    deja_dits.append(phrase)
    return phrase


async def avec_attente(context: RunContext, outil: str, travail, seuils: dict | None = None):
    """Exécute `travail()` (une coroutine) avec filler, relance et timeout. Les phrases passent par session.say :
    elles ne repassent pas par le LLM."""
    s = seuils or SEUILS_ATTENTE
    if isinstance(getattr(context.session, "llm", None), llm.RealtimeModel):
        # speech-to-speech : pas de TTS à part, le préambule est dit par le modèle (instructions) ; le timeout reste le nôtre
        try:
            return await asyncio.wait_for(travail(), timeout=s["timeout"])
        except asyncio.TimeoutError:
            raise ToolError(SECOURS_TIMEOUT)
    dits: list = []
    async with context.with_filler(lambda etape: choisir_filler(outil, dits, etape),
                                   delay=s["filler"], interval=s["relance"] - s["filler"], max_steps=2):
        try:
            return await asyncio.wait_for(travail(), timeout=s["timeout"])
        except asyncio.TimeoutError:
            raise ToolError(SECOURS_TIMEOUT)


# ---- architecture speech-to-speech (module 11) ---------------------------------------
def reglages_realtime(mode_vad: str = "semantic"):
    """Retourne le modèle Realtime d'OpenAI pour AgentSession. mode_vad : "semantic" (eagerness) ou "server" (silence).
    Noms vérifiés dans livekit-plugins-openai 1.8.10 et dans les types du SDK openai ; à revérifier le jour J."""
    from livekit.plugins import openai as lk_openai                       # pip install livekit-plugins-openai
    from openai.types.realtime.realtime_audio_input_turn_detection import SemanticVad, ServerVad
    if mode_vad == "server":
        detection = ServerVad(type="server_vad", threshold=0.5, prefix_padding_ms=300, silence_duration_ms=500,
                              create_response=True, interrupt_response=True)
    else:
        detection = SemanticVad(type="semantic_vad", eagerness="medium", create_response=True, interrupt_response=True)
    return lk_openai.realtime.RealtimeModel(model=os.environ.get("AWA_REALTIME_MODELE", "gpt-realtime"),
                                            voice=os.environ.get("AWA_REALTIME_VOIX", "marin"), turn_detection=detection)


# ---- client HTTP minimal vers baobab_api.py -------------------------------------------
def _appel_http(methode: str, chemin: str, corps: dict | None = None) -> dict:
    donnees = json.dumps(corps).encode("utf-8") if corps is not None else None
    requete = Request(BAOBAB_URL + chemin, data=donnees, method=methode,
                      headers={"Content-Type": "application/json"})
    try:
        with urlopen(requete, timeout=5) as reponse:
            return json.loads(reponse.read().decode("utf-8"))
    except HTTPError as e:                     # erreur métier de l'API : on la renvoie au modèle
        try:
            message = json.loads(e.read().decode("utf-8")).get("message", "Requête refusée.")
        except ValueError:
            message = "Requête refusée."
        raise ToolError(message)
    except (URLError, TimeoutError):
        raise ToolError("Le CRM ou l'agenda ne répond pas pour le moment.")


async def appel_baobab(methode: str, chemin: str, corps: dict | None = None) -> dict:
    return await asyncio.to_thread(_appel_http, methode, chemin, corps)


# ---- l'agent ---------------------------------------------------------------------------
class Awa(Agent):
    def __init__(self, ctx: JobContext | None = None) -> None:
        self.ctx = ctx
        aujourdhui = dt.date.today()
        super().__init__(instructions=PROMPT_SYSTEME +
                         f" Nous sommes {JOURS_FR[aujourdhui.weekday()]} {aujourdhui.isoformat()}.")
        # Une clé par appel téléphonique : deux appels différents ne partagent jamais de clé.
        self.cle_appel = uuid.uuid4().hex[:8]

    async def tts_node(self, text: AsyncIterable[str], model_settings):
        """Le texte du LLM passe par la normalisation, puis par le TTS par défaut."""
        return Agent.default.tts_node(self, normaliser_flux(text), model_settings)

    @function_tool()
    async def check_availability(self, context: RunContext, date: str) -> dict:
        """Donne les créneaux de rendez-vous libres pour un jour donné. À appeler dès que le prospect
        parle d'un jour ou d'une disponibilité, avant de proposer une heure.

        Args:
            date: Le jour demandé au format AAAA-MM-JJ, par exemple 2026-11-10. Convertir « mardi » ou « demain » en date réelle.
        """
        valider_date(date)
        return await avec_attente(context, "agenda", lambda: appel_baobab("GET", f"/availability?date={date}"))

    @function_tool()
    async def create_lead(self, context: RunContext, nom: str, taille_entreprise: int, budget_mensuel: int,
                          delai: Literal["immediat", "1_mois", "3_mois", "plus_tard"]) -> dict:
        """Crée la fiche du prospect dans le CRM. À appeler quand on connaît le nom, la taille de
        l'entreprise, le budget mensuel et le délai.

        Args:
            nom: Nom complet du prospect.
            taille_entreprise: Nombre de salariés.
            budget_mensuel: Budget mensuel en F CFA.
            delai: Quand le prospect veut démarrer.
        """
        cle = f"{self.cle_appel}|lead|{nom.strip().lower()}|{taille_entreprise}|{budget_mensuel}|{delai}"
        return await avec_attente(context, "crm", lambda: appel_baobab("POST", "/leads", {
            "nom": nom, "taille_entreprise": taille_entreprise, "budget_mensuel": budget_mensuel,
            "delai": delai, "rdv_reserve": False, "idempotency_key": cle}))

    @function_tool()
    async def book_meeting(self, context: RunContext, lead_id: str, date: str, heure: str) -> dict:
        """Réserve un rendez-vous de 30 minutes. À appeler seulement après que le prospect a confirmé
        le jour et l'heure, et que sa fiche existe.

        Args:
            lead_id: Identifiant renvoyé par create_lead, par exemple L-0001.
            date: Jour du rendez-vous au format AAAA-MM-JJ.
            heure: Heure de début au format HH:MM, par exemple 14:30.
        """
        valider_date(date)
        cle = f"{self.cle_appel}|rdv|{lead_id}|{date}|{heure}"     # contenu métier, pas l'identifiant d'appel du modèle
        return await avec_attente(context, "agenda", lambda: appel_baobab("POST", "/meetings", {
            "lead_id": lead_id, "date": date, "heure": heure, "idempotency_key": cle}))

    @function_tool()
    async def transfer_to_human(self, context: RunContext,
                                raison: Literal["demande_humain", "colere", "echecs_repetes", "hors_perimetre"],
                                resume: str) -> str:
        """Transfère l'appel vers un conseiller humain. À appeler après avoir annoncé le transfert au prospect.

        Args:
            raison: Pourquoi on transfère.
            resume: Résumé en une ou deux phrases pour le conseiller : qui est le prospect, ce qu'il veut, ce qui a été dit.
        """
        print("transfert demandé :", raison, "|", resume)
        numero = os.environ.get("AWA_TRANSFER_TO")           # par exemple +221xxxxxxxxx ; sans lui, le transfert est simulé
        if not numero or self.ctx is None:
            return "Transfert simulé : aucun numéro configuré. Dis au prospect qu'un conseiller le rappellera."
        from livekit import api, rtc                         # transfert SIP : nécessite un appel entrant SIP
        sip = [p for p in self.ctx.room.remote_participants.values()
               if p.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP]
        if not sip:
            return "Appel non téléphonique : dis au prospect qu'un conseiller le rappellera."
        async with api.LiveKitAPI() as lk:                   # lit LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
            await lk.sip.transfer_sip_participant(api.TransferSIPParticipantRequest(
                participant_identity=sip[0].identity, room_name=self.ctx.room.name, transfer_to=f"tel:{numero}"))
        return "Transfert en cours."


server = AgentServer()
logger = logging.getLogger("awa")
logger.addFilter(FiltrePII())


@server.rtc_session(agent_name=os.environ.get("AWA_AGENT_NAME", ""))   # un nom est requis pour la répartition explicite (appels sortants)
async def awa(ctx: JobContext) -> None:
    voix = os.environ.get("AWA_TTS_VOIX")          # identifiant de la voix choisie à l'atelier du module 7
    modele_tts = os.environ.get("AWA_TTS_MODELE", "cartesia/sonic-3")   # à vérifier dans la documentation LiveKit
    profil = os.environ.get("AWA_PATIENCE", "equilibree")
    vad = None
    try:
        from livekit.plugins import silero          # pip install livekit-plugins-silero
        vad = silero.VAD.load()
    except ImportError:
        print("Plugin Silero absent : AgentSession utilisera sa détection par défaut.")
    archi = os.environ.get("AWA_ARCHI", "cascade")                  # "cascade" (jours 2 et 3) ou "realtime" (module 11)
    if archi == "realtime":
        # un seul modèle audio de bout en bout : pas de STT ni de TTS à part, donc pas de normalisation ni de filler par session.say
        session = AgentSession(llm=reglages_realtime(os.environ.get("AWA_VAD_REALTIME", "semantic")))
    else:
        session = AgentSession(
            vad=vad,
            turn_handling=reglages_tours(profil, detecteur_audio=os.environ.get("AWA_TURN_DETECTOR") == "1"),
            stt=inference.STT(model="deepgram/nova-3", language="fr"),
            llm=inference.LLM(model="openai/gpt-4.1-mini"),
            tts=inference.TTS(model=modele_tts, voice=voix, language="fr") if voix else None,
        )
    journal: list = []

    @session.on("conversation_item_added")
    def _mesurer(ev) -> None:
        if isinstance(ev.item, ChatMessage):
            ligne = enregistrer_tour(journal, ev.item.role, ev.item.metrics)
            if ligne:
                print("mesure :", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in ligne.items()})
                with open("awa_metriques.jsonl", "a", encoding="utf-8") as f:
                    f.write(json.dumps(ligne, ensure_ascii=False) + "\n")

    async def _bilan() -> None:
        print("bilan de l'appel :", resumer(journal))

    ctx.add_shutdown_callback(_bilan)

    # Appel sortant : les métadonnées de la répartition contiennent le numéro à appeler.
    numero = json.loads(ctx.job.metadata or "{}").get("phone_number")
    if numero:
        from livekit import api
        ok, raison = appel_autorise(dt.datetime.now(dt.timezone.utc), numero)    # Dakar est à UTC+0 toute l'année
        if not ok:
            logger.warning("appel refusé (%s) : %s", raison, numero)
            ctx.shutdown()
            return
        try:
            await ctx.api.sip.create_sip_participant(api.CreateSIPParticipantRequest(
                room_name=ctx.room.name, sip_trunk_id=os.environ["AWA_SIP_TRUNK_ID"], sip_call_to=numero,
                participant_identity=numero, wait_until_answered=True))
        except api.SipCallError as e:
            logger.warning("appel échoué (%s) : %s %s", classer_echec_sip(e.sip_status_code), e.sip_status_code, numero)
            ctx.shutdown()
            return
        await ctx.wait_for_participant(identity=numero)
    await session.start(agent=Awa(ctx), room=ctx.room)
    if numero:
        # Appel sortant : on laisse le prospect parler en premier (il peut s'agir d'une messagerie), puis Awa s'annonce comme IA.
        await asyncio.sleep(1.5)
    if archi == "realtime" or not voix:
        # pas de TTS à part (speech-to-speech ou console texte) : on demande au modèle de dire la phrase d'ouverture
        await session.generate_reply(instructions="Dis exactement cette phrase d'ouverture : " + PHRASE_OUVERTURE)
    else:
        await session.say(PHRASE_OUVERTURE, allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(server)
