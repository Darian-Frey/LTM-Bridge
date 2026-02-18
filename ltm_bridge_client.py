import sys
import os
import json
import time
import subprocess
import pyperclip # Required: pip install pyperclip
from datetime import datetime

# --- Option 3: Self-Aware Pathing ---
# Ensures the script can find the 'tools' directory regardless of where it's called.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tools.ltm_scanner import LTMScanner

class LTMBridgeClient:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.scanner = LTMScanner()
        self.last_state = None

    def _run_git(self, args):
        """Helper to execute git commands within the repo."""
        try:
            result = subprocess.run(
                ["git"] + args, 
                cwd=self.repo_path, 
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"[!] Git Error: {e.stderr}")
            return None

    def get_diff(self, new_data):
        """Semantic diff between the last synchronized state and new incoming data."""
        if not self.last_state:
            return "[First Snapshot of Session]"
        
        diff_report = []
        
        # 1. Check for New Risks
        old_rsk = {r['id'] for r in self.last_state.get('RSK', [])}
        new_rsk = {r['id'] for r in new_data.get('RSK', [])}
        added_rsk = new_rsk - old_rsk
        if added_rsk:
            diff_report.append(f"⚠️  NEW RISKS: {', '.join(added_rsk)}")

        # 2. Check Task Progress (Unresolved Vectors)
        old_uv = {u[0] for u in self.last_state.get('UV', [])}
        new_uv = {u[0] for u in new_data.get('UV', [])}
        completed = old_uv - new_uv
        started = new_uv - old_uv
        if completed:
            diff_report.append(f"✅ COMPLETED: {len(completed)} task(s)")
        if started:
            diff_report.append(f"🚀 STARTED: {len(started)} task(s)")

        # 3. Check Progress Payload
        old_pct = self.last_state.get('PAY', {}).get('pct', 0)
        new_pct = new_data.get('PAY', {}).get('pct', 0)
        if new_pct != old_pct:
            diff_report.append(f"📈 PROGRESS: {old_pct}% -> {new_pct}%")

        return " | ".join(diff_report) if diff_report else "No semantic changes detected."

    def commit_snapshot(self, snapshot_data, project_name):
        """Audits, diffs, saves, and pushes a snapshot to the ledger."""
        
        # 1. Validation & Auto-Audit
        if not self.scanner.validate_schema(snapshot_data):
            print("[!] ABORT: Snapshot failed schema validation.")
            return False
            
        # 2. Critical Risk Escallation
        critical_risks = [r for r in snapshot_data.get('RSK', []) if r.get('level') == 'critical']
        if critical_risks:
            # Bold Red Terminal Alert
            print("\033[91m\033[1m[!!!] CRITICAL RISK DETECTED [!!!]\033[0m")
            for r in critical_risks:
                print(f" >> {r['id']}: {r['desc']}")

        # 3. Generate Semantic Diff
        change_summary = self.get_diff(snapshot_data)
        print(f"[#] DIFF: {change_summary}")

        # 4. File Persistence
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"snapshots/{project_name}_{timestamp}.json"
        filepath = os.path.join(self.repo_path, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(snapshot_data, f, indent=2)
        
        # 5. Git Automation
        print(f"[#] Syncing {filename} to Remote...")
        self._run_git(["add", filename])
        
        # Trim commit message for CLI neatness
        clean_summary = change_summary.replace("⚠️ ", "").replace("✅ ", "").replace("🚀 ", "").replace("📈 ", "")
        commit_msg = f"sync: {project_name} - {clean_summary[:50]}"
        
        if self._run_git(["commit", "-m", commit_msg]):
            if self._run_git(["push", "origin", "main"]) is not None:
                self.last_state = snapshot_data 
                print(f"[+ SUCCESS] State synchronized to GitHub.")
                return True
        return False

class LTMAutomator(LTMBridgeClient):
    def watch_clipboard(self, project_name):
        """Background loop to detect and sync LTM-Bridge JSON blobs."""
        print(f"[*] LTM-Bridge Watcher Active: {project_name}")
        print("[*] Monitoring clipboard for valid State Blobs...")
        
        last_paste = ""
        try:
            while True:
                current_paste = pyperclip.paste().strip()
                # Check if new content is JSON-like and changed
                if current_paste != last_paste and current_paste.startswith("{"):
                    try:
                        data = json.loads(current_paste)
                        # Identify as LTM-Bridge via schema keys
                        if any(k in data for k in ["ST_H", "v", "ALN"]):
                            print(f"\n[!] Snapshot Detected at {datetime.now().strftime('%H:%M:%S')}")
                            if self.commit_snapshot(data, project_name):
                                last_paste = current_paste 
                            print("[*] Monitoring...")
                    except json.JSONDecodeError:
                        pass 
                time.sleep(1) # Polling interval
        except KeyboardInterrupt:
            print("\n[!] Watcher stopped by user.")

if __name__ == "__main__":
    automator = LTMAutomator()
    if "--watch" in sys.argv:
        # Default to Global_Ledger if no project name provided
        project = sys.argv[2] if len(sys.argv) > 2 else "Global_Ledger"
        automator.watch_clipboard(project)
    else:
        print("--- LTM-Bridge Middleware Client v0.2 ---")
        print("Usage: python3 ltm_bridge_client.py --watch <project_name>")
