#!/bin/bash

# X32 Recorder Service Management Script
# Manages both the Django web server (gunicorn) and the controller process

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_DIR="$SCRIPT_DIR/pids"
LOG_DIR="$SCRIPT_DIR/logs"
GUNICORN_PID="$PID_DIR/gunicorn.pid"
CONTROLLER_PID="$PID_DIR/controller.pid"
GUNICORN_LOG="$LOG_DIR/gunicorn.log"
CONTROLLER_LOG="$LOG_DIR/controller.log"

# Create directories if they don't exist
mkdir -p "$PID_DIR"
mkdir -p "$LOG_DIR"

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed or not in PATH"
    echo "Please install uv first: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Function to start services
start_services() {
    echo "Starting X32 Recorder services..."
    
    # Check if services are already running
    if is_gunicorn_running; then
        echo "Gunicorn is already running (PID: $(cat $GUNICORN_PID))"
    else
        echo "Starting Gunicorn web server..."
        cd "$SCRIPT_DIR"
        uv run gunicorn --chdir x32recorder \
            --bind 0.0.0.0:8000 \
            --workers 3 \
            --access-logfile "$GUNICORN_LOG" \
            --error-logfile "$GUNICORN_LOG" \
            --pid "$GUNICORN_PID" \
            --daemon \
            x32recorder.wsgi:application
        
        # Wait a moment for PID file to be created
        sleep 1
        
        if [[ -f "$GUNICORN_PID" ]]; then
            echo "Gunicorn started (PID: $(cat $GUNICORN_PID))"
        else
            echo "Warning: Gunicorn started but PID file not found"
        fi
    fi
    
    if is_controller_running; then
        echo "Controller is already running (PID: $(cat $CONTROLLER_PID))"
    else
        echo "Starting Controller..."
        cd "$SCRIPT_DIR"
        nohup uv run python x32recorder/controller.py > "$CONTROLLER_LOG" 2>&1 &
        echo $! > "$CONTROLLER_PID"
        echo "Controller started (PID: $(cat $CONTROLLER_PID))"
    fi
    
    echo "Services started successfully!"
    echo "Web interface: http://localhost:8000"
    echo "Logs: $LOG_DIR"
}

# Function to stop services
stop_services() {
    echo "Stopping X32 Recorder services..."
    
    if is_gunicorn_running; then
        echo "Stopping Gunicorn..."
        kill "$(cat $GUNICORN_PID)" 2>/dev/null || true
        rm -f "$GUNICORN_PID"
        echo "Gunicorn stopped"
    else
        echo "Gunicorn is not running"
    fi
    
    if is_controller_running; then
        echo "Stopping Controller..."
        kill "$(cat $CONTROLLER_PID)" 2>/dev/null || true
        rm -f "$CONTROLLER_PID"
        echo "Controller stopped"
    else
        echo "Controller is not running"
    fi
    
    echo "Services stopped"
}

# Function to check if gunicorn is running
is_gunicorn_running() {
    if [[ -f "$GUNICORN_PID" ]] && kill -0 "$(cat $GUNICORN_PID)" 2>/dev/null; then
        return 0
    else
        [[ -f "$GUNICORN_PID" ]] && rm -f "$GUNICORN_PID"
        return 1
    fi
}

# Function to check if controller is running
is_controller_running() {
    if [[ -f "$CONTROLLER_PID" ]] && kill -0 "$(cat $CONTROLLER_PID)" 2>/dev/null; then
        return 0
    else
        [[ -f "$CONTROLLER_PID" ]] && rm -f "$CONTROLLER_PID"
        return 1
    fi
}

# Function to show status
show_status() {
    echo "X32 Recorder Service Status:"
    echo "=========================="
    
    if is_gunicorn_running; then
        echo "✓ Gunicorn: Running (PID: $(cat $GUNICORN_PID))"
        echo "  Web interface: http://localhost:8000"
    else
        echo "✗ Gunicorn: Not running"
    fi
    
    if is_controller_running; then
        echo "✓ Controller: Running (PID: $(cat $CONTROLLER_PID))"
    else
        echo "✗ Controller: Not running"
    fi
    
    echo ""
    echo "Log files:"
    echo "  Gunicorn: $GUNICORN_LOG"
    echo "  Controller: $CONTROLLER_LOG"
}

# Function to show logs
show_logs() {
    echo "=== Gunicorn Logs (last 20 lines) ==="
    if [[ -f "$GUNICORN_LOG" ]]; then
        tail -n 20 "$GUNICORN_LOG"
    else
        echo "No gunicorn log file found"
    fi
    
    echo ""
    echo "=== Controller Logs (last 20 lines) ==="
    if [[ -f "$CONTROLLER_LOG" ]]; then
        tail -n 20 "$CONTROLLER_LOG"
    else
        echo "No controller log file found"
    fi
}

# Function to restart services
restart_services() {
    echo "Restarting X32 Recorder services..."
    stop_services
    sleep 2
    start_services
}

# Main script logic
case "${1:-}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start both Gunicorn and Controller services"
        echo "  stop    - Stop both services"
        echo "  restart - Restart both services"
        echo "  status  - Show status of both services"
        echo "  logs    - Show recent logs from both services"
        exit 1
        ;;
esac
