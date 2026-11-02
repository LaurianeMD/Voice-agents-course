"""baobab_api.py : CRM et agenda simulés de Baobab Software (entreprise fictive).

Formation Agents vocaux de 0 à Z, AI&ML Factory (module 6).

Aucune dépendance : bibliothèque standard uniquement.

Deux façons de l'utiliser :

1. Dans le code (le notebook du jour 2 fait ainsi) :

       from baobab_api import BaobabAPI, ApiError
       api = BaobabAPI()
       api.check_availability("2026-11-10")

2. Comme petit serveur HTTP local (pour l'atelier LiveKit) :

       python baobab_api.py --port 8077

   Points d'accès (JSON) :
       GET  /availability?date=2026-11-10
       POST /leads       {nom, taille_entreprise, budget_mensuel, delai, rdv_reserve, idempotency_key?}
       POST /meetings    {lead_id, date, heure, idempotency_key?}
       GET  /meetings
       GET  /leads
       POST /reset

Règles de l'agenda : du lundi au vendredi, de 9 h à 17 h, créneaux de 30 minutes
(le dernier commence à 16 h 30). Quelques créneaux sont déjà occupés, de façon
déterministe, pour que chaque participant voie les mêmes disponibilités.

Option `latence_s` : délai artificiel avant chaque réponse, pour simuler un agenda
lent (module 10).

Auto-test : python baobab_api.py --selftest
"""

from __future__ import annotations

import argparse
import json
import threading
import time
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

DELAIS_VALIDES = ("immediat", "1_mois", "3_mois", "plus_tard")
HEURE_DEBUT, HEURE_FIN, PAS_MIN = 9, 17, 30


class ApiError(Exception):
    """Erreur renvoyée par l'API : `status` suit la logique HTTP, `code` est stable."""

    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status, self.code, self.message = status, code, message

    def to_dict(self) -> dict:
        return {"erreur": self.code, "message": self.message}


def creneaux_du_jour() -> list[str]:
    """Tous les créneaux théoriques d'une journée ouvrée : ['09:00', '09:30', ..., '16:30']."""
    out, t = [], datetime(2000, 1, 1, HEURE_DEBUT)
    while t.hour < HEURE_FIN:
        out.append(t.strftime("%H:%M"))
        t += timedelta(minutes=PAS_MIN)
    return out


def parse_date(texte) -> date:
    """Accepte uniquement le format ISO AAAA-MM-JJ."""
    if not isinstance(texte, str):
        raise ApiError(422, "date_invalide", "La date doit être une chaîne AAAA-MM-JJ.")
    try:
        return datetime.strptime(texte, "%Y-%m-%d").date()
    except ValueError:
        raise ApiError(422, "date_invalide", f"Date illisible : {texte!r}. Format attendu : AAAA-MM-JJ.")


def parse_heure(texte) -> str:
    """Accepte uniquement HH:MM sur un créneau valide (:00 ou :30, entre 09:00 et 16:30)."""
    if texte not in creneaux_du_jour():
        raise ApiError(422, "heure_invalide",
                       f"Heure invalide : {texte!r}. Créneaux : de 09:00 à 16:30, toutes les 30 minutes.")
    return texte


class BaobabAPI:
    """CRM + agenda en mémoire. Sûr pour plusieurs threads (verrou unique)."""

    def __init__(self, latence_s: float = 0.0):
        self.latence_s = latence_s
        self._verrou = threading.RLock()
        self.reset()

    # ---- état -----------------------------------------------------------------
    def reset(self) -> dict:
        with self._verrou:
            self.leads: dict[str, dict] = {}
            self.rdv: dict[str, dict] = {}            # clé "AAAA-MM-JJ HH:MM" -> rendez-vous
            self._idem: dict[str, dict] = {}          # clé d'idempotence -> résultat d'origine
            self._n_lead = 0
            self._n_rdv = 0
        return {"ok": True}

    def _attendre(self):
        if self.latence_s:
            time.sleep(self.latence_s)

    @staticmethod
    def _occupe_d_avance(jour: date, heure: str) -> bool:
        """Créneaux déjà pris par d'autres clients : motif déterministe, environ un sur cinq."""
        i = creneaux_du_jour().index(heure)
        return (jour.toordinal() * 7 + i * 3) % 5 == 0

    # ---- agenda ---------------------------------------------------------------
    def check_availability(self, date_iso) -> dict:
        """Créneaux libres pour un jour donné."""
        self._attendre()
        jour = parse_date(date_iso)
        if jour.weekday() >= 5:
            raise ApiError(422, "jour_ferme", f"{date_iso} tombe un week-end : agenda fermé (lundi au vendredi).")
        with self._verrou:
            libres = [h for h in creneaux_du_jour()
                      if not self._occupe_d_avance(jour, h) and f"{date_iso} {h}" not in self.rdv]
        return {"date": date_iso, "creneaux_libres": libres, "duree_min": PAS_MIN}

    def book_meeting(self, lead_id, date_iso, heure, idempotency_key: str | None = None) -> dict:
        """Réserve un créneau. Avec une clé d'idempotence, un appel répété renvoie le premier résultat."""
        self._attendre()
        with self._verrou:
            if idempotency_key and idempotency_key in self._idem:
                rejoue = dict(self._idem[idempotency_key])
                rejoue["rejoue"] = True
                return rejoue
            if lead_id not in self.leads:
                raise ApiError(404, "lead_inconnu", f"Aucun prospect avec l'identifiant {lead_id!r}.")
            jour = parse_date(date_iso)
            if jour.weekday() >= 5:
                raise ApiError(422, "jour_ferme", f"{date_iso} tombe un week-end : agenda fermé.")
            heure = parse_heure(heure)
            cle = f"{date_iso} {heure}"
            if cle in self.rdv or self._occupe_d_avance(jour, heure):
                raise ApiError(409, "creneau_indisponible", f"Le créneau {cle} n'est plus disponible.")
            self._n_rdv += 1
            rdv = {"rdv_id": f"R-{self._n_rdv:04d}", "lead_id": lead_id, "date": date_iso,
                   "heure": heure, "duree_min": PAS_MIN, "statut": "confirme"}
            self.rdv[cle] = rdv
            self.leads[lead_id]["rdv_reserve"] = True
            resultat = dict(rdv, rejoue=False)
            if idempotency_key:
                self._idem[idempotency_key] = dict(resultat)
            return resultat

    # ---- CRM ------------------------------------------------------------------
    def create_lead(self, nom, taille_entreprise, budget_mensuel, delai,
                    rdv_reserve=False, idempotency_key: str | None = None) -> dict:
        """Crée un prospect. Champs définis au module 4."""
        self._attendre()
        with self._verrou:
            if idempotency_key and idempotency_key in self._idem:
                rejoue = dict(self._idem[idempotency_key])
                rejoue["rejoue"] = True
                return rejoue
            if not isinstance(nom, str) or not nom.strip():
                raise ApiError(422, "nom_invalide", "Le nom est obligatoire.")
            if isinstance(taille_entreprise, bool) or not isinstance(taille_entreprise, int) \
                    or not 1 <= taille_entreprise <= 100_000:
                raise ApiError(422, "taille_invalide", "taille_entreprise : entier entre 1 et 100000.")
            if isinstance(budget_mensuel, bool) or not isinstance(budget_mensuel, int) or budget_mensuel < 0:
                raise ApiError(422, "budget_invalide", "budget_mensuel : entier en F CFA, positif ou nul.")
            if delai not in DELAIS_VALIDES:
                raise ApiError(422, "delai_invalide", f"delai : l'une de {', '.join(DELAIS_VALIDES)}.")
            self._n_lead += 1
            lead = {"lead_id": f"L-{self._n_lead:04d}", "nom": nom.strip(),
                    "taille_entreprise": taille_entreprise, "budget_mensuel": budget_mensuel,
                    "delai": delai, "rdv_reserve": bool(rdv_reserve)}
            self.leads[lead["lead_id"]] = lead
            resultat = dict(lead, rejoue=False)
            if idempotency_key:
                self._idem[idempotency_key] = dict(resultat)
            return resultat

    def list_leads(self) -> list[dict]:
        with self._verrou:
            return list(self.leads.values())

    def list_meetings(self) -> list[dict]:
        with self._verrou:
            return sorted(self.rdv.values(), key=lambda r: (r["date"], r["heure"]))


# ---- serveur HTTP (stdlib) --------------------------------------------------------
def _fabriquer_handler(api: BaobabAPI):
    class Handler(BaseHTTPRequestHandler):
        def _repondre(self, status: int, corps):
            data = json.dumps(corps, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _lire_json(self) -> dict:
            n = int(self.headers.get("Content-Length") or 0)
            if not n:
                return {}
            try:
                corps = json.loads(self.rfile.read(n).decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                raise ApiError(400, "json_invalide", "Corps de requête : JSON attendu.")
            if not isinstance(corps, dict):
                raise ApiError(400, "json_invalide", "Corps de requête : objet JSON attendu.")
            return corps

        def _traiter(self, methode: str):
            try:
                url = urlparse(self.path)
                requete = parse_qs(url.query)
                if methode == "GET" and url.path == "/availability":
                    return self._repondre(200, api.check_availability((requete.get("date") or [None])[0]))
                if methode == "GET" and url.path == "/leads":
                    return self._repondre(200, api.list_leads())
                if methode == "GET" and url.path == "/meetings":
                    return self._repondre(200, api.list_meetings())
                if methode == "POST" and url.path == "/reset":
                    return self._repondre(200, api.reset())
                if methode == "POST" and url.path == "/leads":
                    c = self._lire_json()
                    return self._repondre(201, api.create_lead(
                        c.get("nom"), c.get("taille_entreprise"), c.get("budget_mensuel"), c.get("delai"),
                        c.get("rdv_reserve", False), c.get("idempotency_key")))
                if methode == "POST" and url.path == "/meetings":
                    c = self._lire_json()
                    return self._repondre(201, api.book_meeting(
                        c.get("lead_id"), c.get("date"), c.get("heure"), c.get("idempotency_key")))
                raise ApiError(404, "route_inconnue", f"{methode} {url.path} n'existe pas.")
            except ApiError as e:
                self._repondre(e.status, e.to_dict())
            except Exception as e:  # on ne révèle pas les détails internes
                self._repondre(500, {"erreur": "erreur_interne", "message": type(e).__name__})

        def do_GET(self):
            self._traiter("GET")

        def do_POST(self):
            self._traiter("POST")

        def log_message(self, *args):  # silence
            pass

    return Handler


def demarrer_serveur(port: int = 8077, latence_s: float = 0.0, api: BaobabAPI | None = None):
    """Démarre le serveur dans un thread. Renvoie (serveur, api). Arrêt : serveur.shutdown()."""
    api = api or BaobabAPI(latence_s)
    serveur = ThreadingHTTPServer(("127.0.0.1", port), _fabriquer_handler(api))
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    return serveur, api


# ---- auto-test --------------------------------------------------------------------
def _autotest() -> None:
    api = BaobabAPI()
    libres = api.check_availability("2026-11-10")["creneaux_libres"]
    assert libres and all(h in creneaux_du_jour() for h in libres)
    try:
        api.check_availability("2026-11-14")          # samedi
        raise AssertionError("le week-end devrait être refusé")
    except ApiError as e:
        assert e.code == "jour_ferme"
    lead = api.create_lead("Mamadou Diop", 8, 25000, "1_mois", idempotency_key="k1")
    assert api.create_lead("Mamadou Diop", 8, 25000, "1_mois", idempotency_key="k1")["rejoue"]
    assert len(api.list_leads()) == 1
    h = libres[0]
    r1 = api.book_meeting(lead["lead_id"], "2026-11-10", h, idempotency_key="b1")
    r2 = api.book_meeting(lead["lead_id"], "2026-11-10", h, idempotency_key="b1")
    assert r1["rdv_id"] == r2["rdv_id"] and r2["rejoue"] and len(api.list_meetings()) == 1
    try:
        api.book_meeting(lead["lead_id"], "2026-11-10", h)    # sans clé : le créneau est pris
        raise AssertionError("conflit attendu")
    except ApiError as e:
        assert e.status == 409
    serveur, _ = demarrer_serveur(port=0)
    port = serveur.server_address[1]
    from urllib.request import urlopen
    with urlopen(f"http://127.0.0.1:{port}/availability?date=2026-11-10") as rep:
        assert json.loads(rep.read())["date"] == "2026-11-10"
    serveur.shutdown()
    print("Auto-test réussi.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="CRM et agenda simulés de Baobab Software")
    ap.add_argument("--port", type=int, default=8077)
    ap.add_argument("--latence", type=float, default=0.0, help="délai artificiel par requête, en secondes")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        _autotest()
    else:
        serveur, _ = demarrer_serveur(a.port, a.latence)
        print(f"Baobab API sur http://127.0.0.1:{a.port}  (Ctrl+C pour arrêter)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            serveur.shutdown()
