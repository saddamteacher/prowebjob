# PyInstaller spec for the PROWEB HR Windows build. Run via desktop/build.ps1.
# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ROOT = Path(SPECPATH).parent
SRC = ROOT / "jobhunter_crm"
SKIP_DIRS = {"__pycache__", "staticfiles", "static", "media", "logs", "tests", "templates", "nginx", "icons"}


def project_modules() -> list[str]:
    """Every module of the Django project, so PyInstaller follows their imports
    (apps, migrations, template tags and management commands are loaded by name)."""
    modules = []
    for path in SRC.rglob("*.py"):
        rel = path.relative_to(SRC)
        if SKIP_DIRS & set(rel.parts[:-1]) or "." in path.stem:  # e.g. gunicorn.conf.py
            continue
        parts = list(rel.with_suffix("").parts)
        if parts[-1] == "__init__":
            parts = parts[:-1]
        if parts and parts != ["manage"]:
            modules.append(".".join(parts))
    return sorted(modules)


def project_data() -> list[tuple[str, str]]:
    """Templates next to their apps + collected static files (served by whitenoise)."""
    data = []
    for tpl in SRC.rglob("templates"):
        if tpl.is_dir() and "staticfiles" not in tpl.parts:
            data.append((str(tpl), str(tpl.relative_to(SRC))))
    staticfiles = SRC / "staticfiles"
    if not (staticfiles / "css" / "app.css").exists():
        raise SystemExit("Run `manage.py collectstatic` first (desktop/build.ps1 does it).")
    data.append((str(staticfiles), "staticfiles"))
    data.append((str(SRC / "static"), "static"))
    return data


hiddenimports = (
    project_modules()
    + collect_submodules("django_apscheduler")
    + collect_submodules("django_htmx")
    + collect_submodules("whitenoise")
    + collect_submodules("waitress")
)
datas = (
    project_data()
    + collect_data_files("django")
    + collect_data_files("django_apscheduler")
)

a = Analysis(
    [str(ROOT / "desktop" / "launcher.py")],
    pathex=[str(SRC)],
    hiddenimports=hiddenimports,
    datas=datas,
    excludes=["tkinter", "pytest", "IPython", "matplotlib", "numpy.tests"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ProwebHR",
    icon=str(ROOT / "desktop" / "prowebhr.ico"),
    console=True,  # the window shows the address and stops the program when closed
    upx=False,
)
coll = COLLECT(exe, a.binaries, a.datas, name="ProwebHR", upx=False)
