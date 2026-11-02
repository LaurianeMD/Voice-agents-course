"""tts_normalisation.py : normalisation du texte français avant TTS (module 7).

Transforme chiffres, dates, heures, montants, e-mails et téléphones en texte lisible à voix haute,
et applique un petit lexique de prononciation pour les noms propres.
Stdlib uniquement. Chiffres de base : règles françaises (70 = soixante-dix, 80 = quatre-vingts, 99 = quatre-vingt-dix-neuf).
"""
import re

UNITES = ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix", "onze", "douze",
          "treize", "quatorze", "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf"]
DIZAINES = {20: "vingt", 30: "trente", 40: "quarante", 50: "cinquante", 60: "soixante"}
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
        "novembre", "décembre"]


def _moins_de_cent(n):
    if n < 20:
        return UNITES[n]
    if n < 70:
        d, u = (n // 10) * 10, n % 10
        if u == 0:
            return DIZAINES[d]
        return DIZAINES[d] + (" et un" if u == 1 else "-" + UNITES[u])
    if n < 80:                                   # 70 à 79 : soixante + (10 à 19)
        r = n - 60
        return "soixante et onze" if r == 11 else "soixante-" + UNITES[r]
    if n == 80:
        return "quatre-vingts"
    return "quatre-vingt-" + UNITES[n - 80]      # 81 à 99


def _moins_de_mille(n):
    if n < 100:
        return _moins_de_cent(n)
    c, r = n // 100, n % 100
    tete = "cent" if c == 1 else UNITES[c] + " cent"
    if r == 0:
        return tete + ("s" if c > 1 else "")
    return tete + " " + _moins_de_cent(r)


def nombre_en_lettres(n):
    """Entier de 0 à 999 999 999 en lettres, en français de France (70 = soixante-dix)."""
    if not isinstance(n, int) or n < 0 or n > 999_999_999:
        raise ValueError("entier entre 0 et 999 999 999 attendu")
    if n < 1000:
        return _moins_de_mille(n)
    morceaux = []
    millions, reste = divmod(n, 1_000_000)
    milliers, unites = divmod(reste, 1000)
    if millions:
        morceaux.append("un million" if millions == 1 else _moins_de_mille(millions) + " millions")
    if milliers:
        if milliers == 1:
            morceaux.append("mille")
        else:
            mots = _moins_de_mille(milliers)
            # « vingt », « cent » et « quatre-vingt » ne prennent pas de s devant mille
            if mots.endswith("cents") or mots.endswith("quatre-vingts"):
                mots = mots[:-1]
            morceaux.append(mots + " mille")
    if unites:
        morceaux.append(_moins_de_mille(unites))
    return " ".join(morceaux)


def heure_en_lettres(h, m):
    if h in (0, 12):
        mots_h = "minuit" if h == 0 else "midi"
    elif h % 10 == 1 and h != 11:           # une heure, vingt et une heures
        mots_h = nombre_en_lettres(h) + "e heure" + ("" if h == 1 else "s")
    else:
        mots_h = nombre_en_lettres(h) + (" heure" if h == 1 else " heures")
    if m == 0:
        return mots_h
    if m == 30:
        return mots_h + " et demie" if h not in (0, 12) else mots_h + " et demi"
    if m == 15:
        return mots_h + " et quart"
    return mots_h + " " + nombre_en_lettres(m)


def date_en_lettres(j, mois):
    jour = "premier" if j == 1 else nombre_en_lettres(j)
    return f"{jour} {MOIS[mois - 1]}"


def telephone_en_lettres(chiffres):
    """Un numéro sénégalais à 9 chiffres se dit en 2-3-2-2 : 77 616 06 16 (le groupe de 3 se dit chiffre par chiffre)."""
    c = re.sub(r"\D", "", chiffres)
    if len(c) != 9:
        return ", ".join(" ".join(UNITES[int(x)] for x in c[i:i + 3]) for i in range(0, len(c), 3))
    def paire(g):
        return ("zéro " + UNITES[int(g[1])]) if g[0] == "0" else nombre_en_lettres(int(g))
    trio = " ".join(UNITES[int(x)] for x in c[2:5])
    return ", ".join([paire(c[:2]), trio, paire(c[5:7]), paire(c[7:])])


def email_en_lettres(adresse):
    local, domaine = adresse.split("@")
    def epeler(s):
        s = s.replace(".", " point ").replace("-", " tiret ").replace("_", " tiret bas ")
        return re.sub(r"\s+", " ", s).strip()
    return f"{epeler(local)} arobase {epeler(domaine)}"


LEXIQUE = {"Thiès": "Tiesse", "Ziguinchor": "Ziguinchore", "Mbagdjé": "Mbagdjé"}


def appliquer_lexique(texte, lexique=LEXIQUE):
    for mot, lu in lexique.items():
        texte = re.sub(rf"\b{re.escape(mot)}\b", lu, texte)
    return texte


def normaliser(texte, lexique=LEXIQUE):
    """Texte écrit -> texte à dire. Ordre : e-mails, montants, dates, heures, téléphones, nombres, lexique."""
    t = re.sub(r"[\w.\-]+@[\w.\-]+\.\w+", lambda m: email_en_lettres(m.group(0)), texte)
    t = re.sub(r"(\d{1,3}(?:[ \u202f\u00a0]\d{3})+|\d+)\s?(?:F\s?CFA|FCFA|XOF)",
               lambda m: nombre_en_lettres(int(re.sub(r"\D", "", m.group(1)))) + " francs CFA", t)
    t = re.sub(r"\b(\d{1,2})/(\d{1,2})\b", lambda m: date_en_lettres(int(m.group(1)), int(m.group(2))), t)
    t = re.sub(r"\b(\d{1,2})\s?(?:h|:)(?:\s?(\d{2}))?\b",
               lambda m: heure_en_lettres(int(m.group(1)), int(m.group(2) or 0)), t)
    t = re.sub(r"\b\d{2} \d{3} \d{2} \d{2}\b", lambda m: telephone_en_lettres(m.group(0)), t)
    t = re.sub(r"\b\d+\b", lambda m: nombre_en_lettres(int(m.group(0))), t)
    return appliquer_lexique(t, lexique)


if __name__ == "__main__":
    for n in [0, 21, 70, 71, 77, 80, 81, 91, 99, 100, 200, 280, 1000, 25000, 49000, 80000, 1200000]:
        print(n, "->", nombre_en_lettres(n))
    for s in ["Rendez-vous le 12/11 à 14 h 30.", "Le plan Essentiel coûte 25 000 F CFA par mois.",
              "Écrivez à fatou.sow@baobab.sn ou appelez le 77 616 06 16.", "Notre agence de Thiès et de Ziguinchor."]:
        print(s, "->", normaliser(s))
