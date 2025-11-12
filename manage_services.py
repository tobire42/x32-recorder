#!/usr/bin/env python3
"""
X32 Recorder Service Management Script
Cross-platform service manager for both Django web server (waitress) and controller process
Works on Windows, Linux, and macOS
"""

import os
import sys
import time
import subprocess
import signal
import platform
import argparse
from pathlib import Path


class ServiceManager:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.pid_dir = self.script_dir / "pids"
        self.log_dir = self.script_dir / "logs"
        
        # Platform-specific settings
        self.is_windows = platform.system() == "Windows"
        
        if self.is_windows:
            self.waitress_pid = self.pid_dir / "waitress.pid"
            self.controller_pid = self.pid_dir / "controller.pid"
            self.waitress_log = self.log_dir / "waitress.log"
            self.controller_log = self.log_dir / "controller.log"
        else:
            self.waitress_pid = self.pid_dir / "waitress.pid"
            self.controller_pid = self.pid_dir / "controller.pid"
            self.waitress_log = self.log_dir / "waitress.log"
            self.controller_log = self.log_dir / "controller.log"
        
        # Create directories if they don't exist
        self.pid_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
    
    def check_uv(self):
        """Check if uv is available"""
        try:
            subprocess.run(["uv", "--version"], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: uv is not installed or not in PATH")
            if self.is_windows:
                print("Please install uv first: https://docs.astral.sh/uv/getting-started/installation/")
            else:
                print("Please install uv first: curl -LsSf https://astral.sh/uv/install.sh | sh")
            return False
    
    def is_process_running(self, pid_file):
        """Check if a process is running based on PID file"""
        if not pid_file.exists():
            return False
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            if self.is_windows:
                # On Windows, use tasklist to check if process is running
                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}"],
                    capture_output=True, text=True
                )
                return str(pid) in result.stdout
            else:
                # On Unix-like systems, use kill -0
                os.kill(pid, 0)
                return True
                
        except (ValueError, OSError, ProcessLookupError):
            # Remove stale PID file
            if pid_file.exists():
                pid_file.unlink()
            return False
    
    def kill_process(self, pid_file):
        """Kill a process based on PID file"""
        if not pid_file.exists():
            return False
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            if self.is_windows:
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], 
                             capture_output=True)
            else:
                os.kill(pid, signal.SIGTERM)
                # Give it a moment to terminate gracefully
                time.sleep(1)
                try:
                    os.kill(pid, 0)  # Check if still running
                    os.kill(pid, signal.SIGKILL)  # Force kill if necessary
                except ProcessLookupError:
                    pass  # Already terminated
            
            pid_file.unlink()
            return True
            
        except (ValueError, OSError, ProcessLookupError):
            if pid_file.exists():
                pid_file.unlink()
            return False
    
    def start_waitress(self):
        """Start waitress web server"""
        if self.is_process_running(self.waitress_pid):
            with open(self.waitress_pid, 'r') as f:
                pid = f.read().strip()
            print(f"Waitress is already running (PID: {pid})")
            return True
        
        print("Starting Waitress web server...")
        
        # Change to project directory
        os.chdir(self.script_dir / "x32recorder")
        
        # Prepare command
        cmd = [
            "uv", "run", "waitress-serve",
            "--host=0.0.0.0",
            "--port=8000",
            "--threads=6",
            "x32recorder.wsgi:application"
        ]
        
        try:
            # Start waitress
            if self.is_windows:
                # On Windows, we need to handle this differently
                process = subprocess.Popen(
                    cmd,
                    stdout=open(self.waitress_log, 'w'),
                    stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                # On Unix-like systems
                process = subprocess.Popen(
                    cmd,
                    stdout=open(self.waitress_log, 'w'),
                    stderr=subprocess.STDOUT,
                    preexec_fn=os.setsid
                )
            
            # Save PID
            with open(self.waitress_pid, 'w') as f:
                f.write(str(process.pid))
            
            print(f"Waitress started (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"Failed to start waitress: {e}")
            return False
    
    def start_controller(self):
        """Start controller process"""
        if self.is_process_running(self.controller_pid):
            with open(self.controller_pid, 'r') as f:
                pid = f.read().strip()
            print(f"Controller is already running (PID: {pid})")
            return True
        
        print("Starting Controller...")
        
        # Change to project directory
        os.chdir(self.script_dir)
        
        cmd = ["uv", "run", "python", "x32recorder/controller.py"]
        
        try:
            if self.is_windows:
                process = subprocess.Popen(
                    cmd,
                    stdout=open(self.controller_log, 'w'),
                    stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                process = subprocess.Popen(
                    cmd,
                    stdout=open(self.controller_log, 'w'),
                    stderr=subprocess.STDOUT,
                    preexec_fn=os.setsid
                )
            
            # Save PID
            with open(self.controller_pid, 'w') as f:
                f.write(str(process.pid))
            
            print(f"Controller started (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"Failed to start controller: {e}")
            return False
    
    def start_services(self):
        """Start both services"""
        if not self.check_uv():
            return False
        
        print("Starting X32 Recorder services...")
        
        waitress_ok = self.start_waitress()
        controller_ok = self.start_controller()
        
        if waitress_ok and controller_ok:
            print("Services started successfully!")
            print("Web interface: http://localhost:8000")
            print(f"Logs: {self.log_dir}")
            return True
        else:
            print("Some services failed to start. Check logs for details.")
            return False
    
    def stop_services(self):
        """Stop both services"""
        print("Stopping X32 Recorder services...")
        
        if self.is_process_running(self.waitress_pid):
            print("Stopping Waitress...")
            if self.kill_process(self.waitress_pid):
                print("Waitress stopped")
            else:
                print("Failed to stop Waitress")
        else:
            print("Waitress is not running")
        
        if self.is_process_running(self.controller_pid):
            print("Stopping Controller...")
            if self.kill_process(self.controller_pid):
                print("Controller stopped")
            else:
                print("Failed to stop Controller")
        else:
            print("Controller is not running")
        
        print("Services stopped")
    
    def restart_services(self):
        """Restart both services"""
        print("Restarting X32 Recorder services...")
        self.stop_services()
        time.sleep(2)
        self.start_services()
    
    def show_status(self):
        """Show status of both services"""
        print("X32 Recorder Service Status:")
        print("==========================")
        
        if self.is_process_running(self.waitress_pid):
            with open(self.waitress_pid, 'r') as f:
                pid = f.read().strip()
            print(f"✓ Waitress: Running (PID: {pid})")
            print("  Web interface: http://localhost:8000")
        else:
            print("✗ Waitress: Not running")
        
        if self.is_process_running(self.controller_pid):
            with open(self.controller_pid, 'r') as f:
                pid = f.read().strip()
            print(f"✓ Controller: Running (PID: {pid})")
        else:
            print("✗ Controller: Not running")
        
        print()
        print("Log files:")
        print(f"  Waitress: {self.waitress_log}")
        print(f"  Controller: {self.controller_log}")
    
    def show_logs(self):
        """Show recent logs from both services"""
        print("=== Waitress Logs (last 20 lines) ===")
        if self.waitress_log.exists():
            try:
                with open(self.waitress_log, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-20:]:
                        print(line.rstrip())
            except Exception as e:
                print(f"Error reading waitress log: {e}")
        else:
            print("No waitress log file found")
        
        print()
        print("=== Controller Logs (last 20 lines) ===")
        if self.controller_log.exists():
            try:
                with open(self.controller_log, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-20:]:
                        print(line.rstrip())
            except Exception as e:
                print(f"Error reading controller log: {e}")
        else:
            print("No controller log file found")


def main():
    parser = argparse.ArgumentParser(
        description="X32 Recorder Service Management Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  start   - Start both Waitress and Controller services
  stop    - Stop both services
  restart - Restart both services
  status  - Show status of both services
  logs    - Show recent logs from both services
        """
    )
    parser.add_argument(
        'command',
        choices=['start', 'stop', 'restart', 'status', 'logs'],
        help='Command to execute'
    )
    
    args = parser.parse_args()
    
    manager = ServiceManager()
    
    try:
        if args.command == 'start':
            success = manager.start_services()
            sys.exit(0 if success else 1)
        elif args.command == 'stop':
            manager.stop_services()
        elif args.command == 'restart':
            manager.restart_services()
        elif args.command == 'status':
            manager.show_status()
        elif args.command == 'logs':
            manager.show_logs()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
