"""Exécute les corrigés hors ligne, sans modifier les notebooks du cours."""

import json
from importlib.metadata import version
import os
from pathlib import Path
import subprocess
import sys

import nbformat
from nbclient import NotebookClient


def main():
    racine = Path(__file__).resolve().parents[1]
    corriges = sorted((racine / "notebooks" / "formateur").glob("*.ipynb"))
    if not corriges:
        raise SystemExit("Les corrigés sont requis dans notebooks/formateur/ pour cette validation. "
                         "Ils sont conservés localement par le formateur et ne sont pas publiés.")
    sortie = racine / ".validation"
    noyau = sortie / "jupyter" / "kernels" / "course-validation"
    noyau.mkdir(parents=True, exist_ok=True)
    (noyau / "kernel.json").write_text(json.dumps({
        "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
        "display_name": "Validation du cours", "language": "python",
    }), encoding="utf-8")
    os.environ["JUPYTER_PATH"] = str(sortie / "jupyter")
    os.environ["JUPYTER_RUNTIME_DIR"] = str(sortie / "runtime")
    os.environ["IPYTHONDIR"] = str(sortie / "ipython")
    os.environ["MPLCONFIGDIR"] = str(sortie / "matplotlib")
    os.environ.pop("OPENAI_API_KEY", None)
    for chemin in sorted((racine / "notebooks").glob("*/*.ipynb")):
        nbformat.validate(nbformat.read(chemin, as_version=4))
    resultats = []
    for chemin in corriges:
        print(f"Exécution : {chemin.name}", flush=True)
        notebook = nbformat.read(chemin, as_version=4)
        nbformat.validate(notebook)
        client = NotebookClient(notebook, timeout=120, kernel_name="course-validation",
                                allow_errors=True,
                                resources={"metadata": {"path": str(chemin.parent)}})
        try:
            client.execute()
            erreurs = [{"cellule": i + 1, "type": o["ename"], "message": o["evalue"]}
                       for i, cellule in enumerate(notebook.cells)
                       for o in cellule.get("outputs", []) if o.output_type == "error"]
        except Exception as exc:
            erreurs = [{"type": type(exc).__name__, "message": str(exc)}]
        nbformat.write(notebook, sortie / chemin.name)
        resultats.append({"notebook": chemin.relative_to(racine).as_posix(),
                          "erreurs": erreurs})
        print(f"  {len(erreurs)} erreur(s)", flush=True)
    crm = subprocess.run([sys.executable, str(racine / "code" / "baobab_api.py"), "--selftest"],
                         capture_output=True, text=True, timeout=60)
    rapport = {"python": sys.version.split()[0], "mode": "hors ligne, clé OpenAI désactivée",
               "versions": {nom: version(nom) for nom in
                            ("numpy", "scipy", "matplotlib", "websockets", "nbclient", "nbformat")},
               "notebooks": resultats,
               "crm": {"code_retour": crm.returncode, "sortie": crm.stdout, "erreur": crm.stderr}}
    (sortie / "rapport.json").write_text(json.dumps(rapport, ensure_ascii=False, indent=2),
                                        encoding="utf-8")
    print(f"Rapport : {sortie / 'rapport.json'}", flush=True)
    return int(any(r["erreurs"] for r in resultats) or crm.returncode != 0)


if __name__ == "__main__":
    raise SystemExit(main())
