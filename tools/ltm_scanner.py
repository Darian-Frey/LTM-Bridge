import json
import sys
import os
from datetime import datetime

class LTMScanner:
    def __init__(self):
        self.version = "1.0.0"
        self.required_symbols = ["ALN", "MR", "UV", "CTX", "OBJ", "CON", "PAY", "ST_H"]
        self.v12_symbols = ["DEP", "RSK", "BC"]

    def validate_schema(self, data):
        """Checks if the blob follows SCHEMA_V5 v1.2 specifications."""
        print(f"[#] Validating LTM-Bridge Schema...")
        missing = [s for s in self.required_symbols if s not in data]
        
        if missing:
            print(f"[!] ERROR: Missing core symbols: {missing}")
            return False
            
        v12_active = all(s in data for s in self.v12_symbols)
        status = "v1.2 (Risk-Aware)" if v12_active else "v1.1 (Standard)"
        print(f"[+] Schema detected: {status}")
        return True

    def calculate_metrics(self, data):
        """Calculates Token Density and Context Complexity."""
        print(f"[#] Calculating Metrics...")
        
        # Estimate token count (rough char-based approx for CLI)
        raw_str = json.dumps(data)
        est_tokens = len(raw_str) / 4
        
        uv_count = len(data.get("UV", []))
        rsk_count = len(data.get("RSK", []))
        dep_count = len(data.get("DEP", []))
        
        print(f"--- BENCHMARK DATA ---")
        print(f"| Est. Tokens:  {est_tokens:.2f}")
        print(f"| Logical UVs:  {uv_count}")
        print(f"| Risk Nodes:   {rsk_count}")
        print(f"| Dependencies: {dep_count}")
        print(f"----------------------")

    def run_audit_template(self, data):
        """Generates a checklist for the user to verify AI re-hydration."""
        print(f"\n[#] Generating Handshake Audit Checklist...")
        print("Provide the following to the Target AI and check off results:")
        print(f"1. [ ] Did the AI acknowledge ST_H: {data.get('ST_H')}?")
        
        for rsk in data.get("RSK", []):
            print(f"2. [ ] Did the AI mitigate RSK {rsk['id']} ({rsk['level']})?")
            
        for dep in data.get("DEP", []):
            print(f"3. [ ] Did the AI verify DEP {dep['id']} ({dep['comp']})?")

    def scan(self, file_path):
        if not os.path.exists(file_path):
            print(f"[!] File not found: {file_path}")
            return

        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"[!] Failed to parse JSON in {file_path}")
                return

        if self.validate_schema(data):
            self.calculate_metrics(data)
            self.run_audit_template(data)
            print(f"\n[+] Scan Complete. System Time: {datetime.now().isoformat()}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 ltm_scanner.py <path_to_snapshot.json>")
    else:
        scanner = LTMScanner()
        scanner.scan(sys.argv[1])
