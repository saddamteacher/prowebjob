"""PROWEB HR — Windows desktop launcher.

Starts the Django app on 127.0.0.1 with waitress and opens the browser.
User data (database, settings, logs) lives in %LOCALAPPDATA%\\ProwebHR, so
reinstalling or updating the program keeps every vacancy and account.
Closing the console window stops the program.
"""

import logging
import logging.handlers
import os
import secrets
import socket
import sys
import threading
import traceback
import webbrowser
from pathlib import Path
from urllib.request import urlopen

APP_TITLE = "PROWEB HR"
DEFAULT_PORT = 8470
FROZEN = getattr(sys, "frozen", False)

if not FROZEN:  # running from source: python desktop/launcher.py
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "jobhunter_crm"))

log = logging.getLogger("prowebhr.launcher")

ENV_TEMPLATE = """\
# PROWEB HR sozlamalari. O'zgartirgandan keyin dasturni qayta oching.

# Groq AI kaliti (ixtiyoriy): https://console.groq.com
GROQ_API_KEY=
GROQ_MODEL=llama-3.1-8b-instant

# Dastur porti (band bo'lsa keyingi bo'sh port olinadi)
PROWEBHR_PORT={port}

LOG_LEVEL=INFO

# Maxfiy kalit — o'zgartirmang, aks holda hamma login sessiyalari o'chadi
DJANGO_SECRET_KEY={secret}
"""


def data_dir() -> Path:
    override = os.environ.get("PROWEBHR_DATA_DIR")
    base = Path(override) if override else Path(os.environ.get("LOCALAPPDATA", Path.home())) / "ProwebHR"
    (base / "logs").mkdir(parents=True, exist_ok=True)
    (base / "media").mkdir(exist_ok=True)
    return base


def prepare_env(base: Path) -> None:
    env_file = base / "settings.env"
    if not env_file.exists():
        env_file.write_text(
            ENV_TEMPLATE.format(port=DEFAULT_PORT, secret=secrets.token_urlsafe(50)),
            encoding="utf-8",
        )
    from dotenv import load_dotenv
    load_dotenv(env_file, override=True)

    # Fixed for the desktop build — not user-tunable.
    os.environ.update({
        "DJANGO_SETTINGS_MODULE": "jobhunter_crm.settings",
        "PROWEBHR_DESKTOP": "True",
        "DJANGO_DEBUG": "False",
        "DJANGO_ALLOWED_HOSTS": "127.0.0.1,localhost",
        "DATABASE_PATH": str(base / "db.sqlite3"),
        "MEDIA_ROOT": str(base / "media"),
    })


def setup_file_logging(base: Path) -> None:
    handler = logging.handlers.RotatingFileHandler(
        base / "logs" / "prowebhr.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s"))
    for name in ("", "django", "parsers", "services", "search", "waitress", "prowebhr"):
        logging.getLogger(name).addHandler(handler)
    logging.getLogger("prowebhr").setLevel(logging.INFO)


def running_instance_url(base: Path) -> str | None:
    """URL of an already running PROWEB HR, if there is one."""
    port_file = base / "server.port"
    if not port_file.exists():
        return None
    url = f"http://127.0.0.1:{port_file.read_text().strip()}/"
    try:
        with urlopen(url + "login/", timeout=2) as response:
            if b"PROWEB" in response.read(4096):
                return url
    except OSError:
        pass
    return None


def free_port(preferred: int) -> int:
    for port in range(preferred, preferred + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError(f"{preferred}-{preferred + 49} oralig'ida bo'sh port topilmadi")


def prepare_database() -> None:
    import django
    from django.core.management import call_command

    django.setup()
    call_command("migrate", interactive=False, verbosity=0)

    from platforms.models import Platform
    if not Platform.objects.exists():  # first run only: keeps the user's on/off choices
        call_command("init_data", verbosity=0)

    # A search that was running when the program closed will never finish.
    from search.models import SearchJob
    SearchJob.objects.filter(status__in=["pending", "running"]).update(
        status="error", error="Dastur yopilgani uchun qidiruv to'xtadi."
    )


def open_browser(url: str) -> None:
    if os.environ.get("PROWEBHR_NO_BROWSER") != "1":  # set by automated checks
        webbrowser.open(url)


def set_console_title(title: str) -> None:
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        except Exception:
            pass


def main() -> None:
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    set_console_title(APP_TITLE)

    base = data_dir()
    existing = running_instance_url(base)
    if existing:
        print(f"{APP_TITLE} allaqachon ishlamoqda: {existing}")
        open_browser(existing)
        return

    prepare_env(base)
    setup_file_logging(base)
    print(f"{APP_TITLE} ishga tushmoqda...")
    prepare_database()

    port = free_port(int(os.environ.get("PROWEBHR_PORT") or DEFAULT_PORT))
    (base / "server.port").write_text(str(port))
    url = f"http://127.0.0.1:{port}/"

    print()
    print("=" * 60)
    print(f"  {APP_TITLE} ishlamoqda:  {url}")
    print(f"  Ma'lumotlar papkasi:  {base}")
    print()
    print("  Brauzer o'zi ochiladi. Bu oynani YOPMANG —")
    print("  oyna yopilsa, dastur to'xtaydi.")
    print("=" * 60)
    print()
    log.info("Starting on %s (data: %s)", url, base)

    from django.core.wsgi import get_wsgi_application
    from waitress import serve

    application = get_wsgi_application()
    threading.Timer(1.5, open_browser, [url]).start()
    serve(application, host="127.0.0.1", port=port, threads=8, ident=APP_TITLE)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
        log.exception("Launcher crashed")
        print("\nXatolik yuz berdi. Batafsil: %LOCALAPPDATA%\\ProwebHR\\logs\\prowebhr.log")
        try:
            input("Yopish uchun Enter bosing...")
        except EOFError:
            pass
        sys.exit(1)
