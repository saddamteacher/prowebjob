#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  PROWEB HR — Hetzner Server Auto Setup
#  Ishlatish: bash setup_server.sh
# ═══════════════════════════════════════════════════════════════
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
info() { echo -e "${YELLOW}[..] $1${NC}"; }
err()  { echo -e "${RED}[!!] $1${NC}"; exit 1; }

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   PROWEB HR — Server Setup           ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── 1. System update ──────────────────────────────────────────
info "Tizim yangilanmoqda..."
apt-get update -qq && apt-get upgrade -y -qq
ok "Tizim yangilandi"

# ── 2. Docker ────────────────────────────────────────────────
if ! command -v docker &> /dev/null; then
    info "Docker o'rnatilmoqda..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    ok "Docker o'rnatildi"
else
    ok "Docker allaqachon o'rnatilgan: $(docker --version)"
fi

# ── 2.5 Firewall — port 80 ochish (Oracle Cloud / Ubuntu) ─────
info "Port 80 ochilmoqda..."
# Oracle/Ubuntu iptables standart REJECT qoidasini chetlab o'tish
iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT 2>/dev/null || true
# Qoidani saqlash (qayta yuklanganda yo'qolmasligi uchun)
if command -v netfilter-persistent &> /dev/null; then
    netfilter-persistent save 2>/dev/null || true
else
    apt-get install -y iptables-persistent -qq 2>/dev/null || true
    netfilter-persistent save 2>/dev/null || true
fi
# UFW bo'lsa ham ochish
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp 2>/dev/null || true
fi
ok "Port 80 ochildi"

# ── 3. Project — GitHub'dan clone/pull ────────────────────────
PROJECT_DIR="/opt/proweb-hr"
REPO_URL="https://github.com/saddamteacher/prowebjob.git"

if ! command -v git &> /dev/null; then
    apt-get install -y git -qq
fi

if [ -d "$PROJECT_DIR/.git" ]; then
    info "Loyiha yangilanmoqda (git pull)..."
    cd "$PROJECT_DIR" && git pull
else
    info "Loyiha yuklanmoqda (git clone)..."
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi
ok "Loyiha kodi tayyor"

# ── 4. .env file ──────────────────────────────────────────────
if [ ! -f ".env" ]; then
    info ".env fayl yaratilmoqda..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))" 2>/dev/null || \
                 tr -dc 'a-zA-Z0-9!@#$%^&*(-_=+)' < /dev/urandom | head -c 50)
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')

    cat > .env << EOF
# ─── Django ────────────────────────────────────────
DJANGO_SECRET_KEY=${SECRET_KEY}
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=${SERVER_IP},localhost,127.0.0.1

# ─── Groq AI ───────────────────────────────────────
GROQ_API_KEY=${GROQ_API_KEY:-your_groq_api_key_here}
GROQ_MODEL=llama-3.1-8b-instant
AI_COMPANY_CHECK_ENABLED=True
AI_DUPLICATE_CHECK_ENABLED=True

# ─── Parser ────────────────────────────────────────
PARSER_INTERVAL=30
DAILY_TOTAL_LIMIT=200
LOG_LEVEL=INFO
EOF
    ok ".env fayl yaratildi"
    echo -e "${YELLOW}  Eslatma: nano /opt/proweb-hr/.env — GROQ_API_KEY ni qo'ying${NC}"
else
    ok ".env fayl mavjud"
fi

# ── 5. Build & run ────────────────────────────────────────────
info "Docker container qurilmoqda (3-5 daqiqa)..."
docker compose down 2>/dev/null || true
docker compose up -d --build
ok "Container ishga tushdi"

# ── 6. Wait for startup ───────────────────────────────────────
info "Tizim ishga tushishini kutmoqda..."
sleep 8

# ── 7. Superuser check ────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════╗"
echo "║   Admin foydalanuvchi yaratish       ║"
echo "╚══════════════════════════════════════╝"
docker exec -it jobhunter-crm python manage.py createsuperuser

# ── 8. Status ─────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════╗"
echo "║   Holat tekshiruvi                   ║"
echo "╚══════════════════════════════════════╝"
docker ps | grep jobhunter

SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  MUVAFFAQIYAT!                           ${NC}"
echo -e "${GREEN}  Sayt:  http://${SERVER_IP}              ${NC}"
echo -e "${GREEN}  Admin: http://${SERVER_IP}/admin/       ${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Foydali buyruqlar:"
echo "  docker logs jobhunter-crm -f    # loglarni ko'rish"
echo "  docker restart jobhunter-crm    # qayta ishga tushirish"
echo "  docker compose down             # to'xtatish"
echo ""
