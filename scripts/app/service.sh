#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

show_status() {
    echo -e "\n${CYAN}═══ Service Status ═══${NC}\n"
    printf "${GREEN}%-12s %-8s %-6s %s${NC}\n" "Service" "Port" "Status" "PID"
    echo "─────────────────────────────────────────"

    local services="vision:8000 rag:8010 text:8006 tts:8013 agents:8003 media:8015 web:5173 server:3000"
    for entry in $services; do
        name="${entry%%:*}"
        port="${entry##*:}"
        pid=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$pid" ]; then
            printf "%-12s %-8s ${GREEN}%-6s${NC} %s\n" "$name" "$port" "RUNNING" "$pid"
        else
            printf "%-12s %-8s ${RED}%-6s${NC} %s\n" "$name" "$port" "STOPPED" "-"
        fi
    done
    echo ""
}

start_service() {
    local name=$1
    local port=$2
    local dir=$3
    local cmd=$4

    # Check if already running
    if lsof -ti:$port >/dev/null 2>&1; then
        echo -e "${YELLOW}$name is already running on port $port${NC}"
        return 1
    fi

    local service_dir="$ROOT_DIR/$dir"

    if [ ! -d "$service_dir" ]; then
        echo -e "${RED}Service directory not found: $service_dir${NC}"
        return 1
    fi

    echo -e "${BLUE}Starting $name on port $port...${NC}"
    cd "$service_dir"

    case "$name" in
        vision|rag|text|tts)
            [ ! -d ".venv" ] && python3 -m venv .venv
            PYTHONPATH="$service_dir:$ROOT_DIR" .venv/bin/python -m uvicorn src.main:app --host 0.0.0.0 --port $port &
            ;;
        agents)
            [ ! -d ".venv" ] && python3 -m venv .venv
            PYTHONPATH="$ROOT_DIR" .venv/bin/python main.py &
            ;;
        media)
            [ ! -d ".venv" ] && python3 -m venv .venv
            .venv/bin/pip install -r requirements.txt -q 2>/dev/null || true
            .venv/bin/python app.py &
            ;;
        web|server)
            cd "$ROOT_DIR"
            pnpm --filter @ai-test/$name dev &
            ;;
    esac

    sleep 2

    if lsof -ti:$port >/dev/null 2>&1; then
        echo -e "${GREEN}✓ $name started on port $port${NC}"
    else
        echo -e "${RED}✗ $name failed to start${NC}"
    fi
}

stop_service() {
    local name=$1
    local port=$2

    echo -e "${BLUE}Stopping $name...${NC}"

    # Kill by port
    lsof -ti:$port 2>/dev/null | xargs kill -9 2>/dev/null || true

    # Also kill by process pattern
    case "$name" in
        vision) pkill -f "vision-service.*uvicorn" 2>/dev/null || true ;;
        rag) pkill -f "rag.*uvicorn" 2>/dev/null || true ;;
        text) pkill -f "text-service.*uvicorn" 2>/dev/null || true ;;
        tts) pkill -f "tts-service.*uvicorn" 2>/dev/null || true ;;
        agents) pkill -f "ai_agents.*main.py" 2>/dev/null || true ;;
        media) pkill -f "media-gen.*app.py" 2>/dev/null || true ;;
        web) pkill -f "vite.*ai-test/web" 2>/dev/null || true ;;
        server) pkill -f "tsx.*ai-test/server" 2>/dev/null || true ;;
    esac

    sleep 1
    echo -e "${GREEN}✓ $name stopped${NC}"
}

restart_service() {
    local name=$1
    local port=$2
    local dir=$3
    local cmd=$4

    stop_service "$name" "$port"
    sleep 1
    start_service "$name" "$port" "$dir" "$cmd"
}

get_service_info() {
    case "$1" in
        vision) echo "8000|services/vision-service|uvicorn" ;;
        rag) echo "8010|services/rag|uvicorn" ;;
        text) echo "8006|services/text-service|uvicorn" ;;
        tts) echo "8013|services/tts-service|uvicorn" ;;
        agents) echo "8003|services/ai_agents|python" ;;
        media) echo "8015|services/media-gen|python" ;;
        web) echo "5173|apps/web|pnpm" ;;
        server) echo "3000|apps/server|pnpm" ;;
        *) return 1 ;;
    esac
}

usage() {
    echo -e "${CYAN}AI-Test Service Manager${NC}"
    echo ""
    echo "Usage: $0 <command> [service]"
    echo ""
    echo "Commands:"
    echo "  status              Show all service status"
    echo "  start <service>     Start a specific service"
    echo "  stop <service>      Stop a specific service"
    echo "  restart <service>   Restart a specific service"
    echo ""
    echo "Services:"
    echo "  vision              Vision Service (port 8000)"
    echo "  rag                 RAG Service (port 8010)"
    echo "  text                Text Service (port 8006)"
    echo "  tts                 TTS Service (port 8013)"
    echo "  agents              AI Agents (port 8003)"
    echo "  media               Media Generation (port 8015)"
    echo "  web                 Web Frontend (port 5173)"
    echo "  server              Express Server (port 3000)"
    echo ""
    echo "Examples:"
    echo "  $0 status"
    echo "  $0 restart vision"
    echo "  $0 start rag"
}

COMMAND=${1:-}
SERVICE=${2:-}

case "$COMMAND" in
    status)
        show_status
        ;;
    start|stop|restart)
        if [ -z "$SERVICE" ]; then
            echo -e "${RED}Error: service name required${NC}"
            usage
            exit 1
        fi
        info=$(get_service_info "$SERVICE") || {
            echo -e "${RED}Unknown service: $SERVICE${NC}"
            usage
            exit 1
        }
        port="${info%%|*}"
        rest="${info#*|}"
        dir="${rest%%|*}"
        cmd="${rest##*|}"

        if [ "$COMMAND" = "start" ]; then
            start_service "$SERVICE" "$port" "$dir" "$cmd"
        elif [ "$COMMAND" = "stop" ]; then
            stop_service "$SERVICE" "$port"
        else
            restart_service "$SERVICE" "$port" "$dir" "$cmd"
        fi
        ;;
    *)
        usage
        ;;
esac
