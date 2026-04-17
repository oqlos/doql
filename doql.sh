#!/bin/bash
# Doql CLI Shell - Generuj aplikacje z pliku app.doql
# Użycie: ./doql.sh <plik.doql> [target]

set -e

# Kolory
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Funkcja pomocnicza
usage() {
    echo -e "${BLUE}Doql CLI Shell - Generator aplikacji${NC}"
    echo ""
    echo "Użycie: $0 <plik.doql> [target]"
    echo ""
    echo "Argumenty:"
    echo "  plik.doql   Plik specyfikacji Doql"
    echo "  target      Opcjonalny: api, web, mobile, desktop, infra (domyślnie: all)"
    echo ""
    echo "Przykłady:"
    echo "  $0 app.doql                    # Generuj wszystko"
    echo "  $0 app.doql api                # Tylko API"
    echo "  $0 app.doql web                # Tylko web"
    echo "  $0 app.doql desktop            # Tylko desktop"
    echo ""
    exit 1
}

# Sprawdź argumenty
if [ $# -lt 1 ]; then
    usage
fi

DOQL_FILE="$1"
TARGET="${2:-all}"

# Sprawdź czy plik istnieje
if [ ! -f "$DOQL_FILE" ]; then
    echo -e "${RED}Błąd: Plik '$DOQL_FILE' nie istnieje${NC}"
    exit 1
fi

# Pobierz katalog pliku
DIR="$(cd "$(dirname "$DOQL_FILE")" && pwd)"
FILE="$(basename "$DOQL_FILE")"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Doql CLI Shell${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Plik: ${GREEN}$DOQL_FILE${NC}"
echo -e "Target: ${GREEN}$TARGET${NC}"
echo -e "Katalog: ${GREEN}$DIR${NC}"
echo ""

# Przejdź do katalogu projektu
cd "$DIR"

# Walidacja specyfikacji
echo -e "${BLUE}[1/4] Walidacja specyfikacji...${NC}"
source /home/tom/github/oqlos/venv/bin/activate
python -m doql.cli validate
if [ $? -ne 0 ]; then
    echo -e "${RED}Walidacja nieudana${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Walidacja OK${NC}"
echo ""

# Planowanie
echo -e "${BLUE}[2/4] Planowanie generacji...${NC}"
python -m doql.cli plan
echo -e "${GREEN}✓ Planowanie OK${NC}"
echo ""

# Generacja
echo -e "${BLUE}[3/4] Generacja ($TARGET)...${NC}"
python -m doql.cli build
if [ $? -ne 0 ]; then
    echo -e "${RED}Generacja nieudana${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Generacja OK${NC}"
echo ""

# Podsumowanie
echo -e "${BLUE}[4/4] Podsumowanie${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Aplikacja wygenerowana pomyślnie!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Wygenerowane katalogi:"
if [ "$TARGET" = "all" ] || [ "$TARGET" = "api" ]; then
    echo -e "  ${GREEN}→ build/api/${NC}     (FastAPI backend)"
fi
if [ "$TARGET" = "all" ] || [ "$TARGET" = "web" ]; then
    echo -e "  ${GREEN}→ build/web/${NC}     (React frontend)"
fi
if [ "$TARGET" = "all" ] || [ "$TARGET" = "desktop" ]; then
    echo -e "  ${GREEN}→ build/desktop/${NC} (Tauri desktop)"
fi
if [ "$TARGET" = "all" ] || [ "$TARGET" = "mobile" ]; then
    echo -e "  ${GREEN}→ build/mobile/${NC}  (PWA)"
fi
echo ""

# Automatyczne uruchomienie
echo -e "${BLUE}[5/5] Uruchamianie aplikacji...${NC}"
if [ "$TARGET" = "api" ]; then
    echo -e "Uruchamiam API backend..."
    cd "$DIR/build/api"
    source /home/tom/github/oqlos/venv/bin/activate
    echo -e "${BLUE}API uruchomione na http://localhost:8000${NC}"
    echo -e "Dokumentacja: ${BLUE}http://localhost:8000/docs${NC}"
    uvicorn main:app --reload --port 8000
elif [ "$TARGET" = "web" ]; then
    echo -e "Uruchamiam Web frontend..."
    cd "$DIR/build/web"
    echo -e "${BLUE}Web uruchomione na http://localhost:4173${NC}"
    npm run preview
elif [ "$TARGET" = "desktop" ]; then
    echo -e "Uruchamiam Desktop (Tauri)..."
    cd "$DIR/build/desktop"
    
    # Sprawdź zależności Tauri v2
    if ! pkg-config --exists libsoup-3.0 2>/dev/null; then
        echo -e "${RED}Błąd: Brak libsoup-3.0-dev${NC}"
        echo -e "${YELLOW}Zainstaluj zależności dla Tauri v2:${NC}"
        echo -e "  sudo apt-get install -y libsoup-3.0-dev libwebkit2gtk-4.1-dev libgtk-3-dev"
        exit 1
    fi
    
    # Sprawdź czy npm install został wykonany
    if [ ! -d "node_modules" ]; then
        echo -e "${BLUE}Instalowanie zależności npm...${NC}"
        npm install
    fi
    
    echo -e "${BLUE}Uruchamianie Tauri Desktop (okno aplikacji)...${NC}"
    npm run dev
elif [ "$TARGET" = "all" ]; then
    echo -e "Uruchamiam API backend..."
    cd "$DIR/build/api"
    source /home/tom/github/oqlos/venv/bin/activate
    nohup uvicorn main:app --reload --port 8000 > /tmp/api.log 2>&1 &
    echo -e "${GREEN}✓ API uruchomione na http://localhost:8000${NC}"
    sleep 2
    
    echo -e "Uruchamiam Web frontend..."
    cd "$DIR/build/web"
    nohup npm run preview > /tmp/web.log 2>&1 &
    echo -e "${GREEN}✓ Web uruchomione na http://localhost:4173${NC}"
    sleep 2
    
    # Sprawdź czy desktop jest zdefiniowany w app.doql
    if grep -q "INTERFACE desktop" "$DIR/app.doql"; then
        echo -e "Uruchamiam Desktop (Tauri)..."
        cd "$DIR/build/desktop"
        
        # Sprawdź zależności Tauri v2
        if pkg-config --exists libsoup-3.0 2>/dev/null; then
            # Sprawdź czy npm install został wykonany
            if [ ! -d "node_modules" ]; then
                echo -e "${BLUE}Instalowanie zależności npm...${NC}"
                npm install
            fi
            
            nohup npm run dev > /tmp/desktop.log 2>&1 &
            echo -e "${GREEN}✓ Desktop uruchomione (okno Tauri)${NC}"
            sleep 2
        else
            echo -e "${YELLOW}⚠ Desktop pominięty (brak libsoup-3.0-dev)${NC}"
        fi
    fi
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Wszystkie usługi uruchomione!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "  API:    ${BLUE}http://localhost:8000/docs${NC}"
    echo -e "  Web:    ${BLUE}http://localhost:4173${NC}"
    echo -e "  Desktop: ${BLUE}Okno aplikacji Tauri${NC}"
    echo ""
    echo "Zatrzymaj poleceniem: pkill -f uvicorn && pkill -f vite && pkill -f tauri"
else
    echo "Brak automatycznego uruchomienia dla target: $TARGET"
    echo ""
    echo "Aby uruchomić ręcznie:"
    echo -e "  API:    ${BLUE}cd build/api && uvicorn main:app --reload${NC}"
    echo -e "  Web:    ${BLUE}cd build/web && npm run preview${NC}"
    echo -e "  Desktop: ${BLUE}cd build/desktop && npm run dev${NC}"
fi
echo ""
