"""
Clean and verify ports 8000, 8501, and 3000 to prevent cross-workspace port collisions (FAULT-08).
Terminates orphan processes occupying Sahayaka application ports.
"""
import sys
import subprocess
import os

PORTS = [8000, 8501, 3000]

def get_listening_pids(port: int):
    """Finds PIDs listening on a given TCP port on Windows."""
    try:
        output = subprocess.check_output(
            f"powershell -NoProfile -Command \"(Get-NetTCPConnection -LocalPort {port} -State Listen -ErrorAction SilentlyContinue).OwningProcess\"",
            shell=True,
            text=True,
        ).strip()
        pids = [int(p) for p in output.split() if p.isdigit()]
        return pids
    except Exception:
        return []

def terminate_pid(pid: int):
    """Terminates a process by PID."""
    current_pid = os.getpid()
    if pid == current_pid:
        return False
    try:
        subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
        print(f"Terminated stale process PID {pid}")
        return True
    except Exception as e:
        print(f"Failed to terminate PID {pid}: {e}")
        return False

def clean_all(kill: bool = True):
    found = False
    for port in PORTS:
        pids = get_listening_pids(port)
        if pids:
            found = True
            print(f"Port {port} is occupied by PID(s): {pids}")
            if kill:
                for pid in pids:
                    terminate_pid(pid)
        else:
            print(f"Port {port} is free.")
    if not found:
        print("All target ports (8000, 8501, 3000) are completely clear.")

if __name__ == "__main__":
    should_kill = "--check-only" not in sys.argv
    clean_all(kill=should_kill)

