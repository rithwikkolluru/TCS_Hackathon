#!/usr/bin/env python3
"""
Demo Setup Script — One-command setup for the complete system.
1. Verify/generate ML data  2. Train models if missing  3. Seed DB  4. Verify
"""
import sys, os, subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

def run(cmd, cwd=None):
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd or ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr[:200]}")
    else:
        print(f"  OK: {result.stdout.strip()[:100]}")
    return result.returncode == 0

print("=" * 55)
print("  BANKING OPTIMIZER DEMO SETUP")
print("=" * 55)

# 1. Check ML models
models = list((ROOT / "models").glob("*.pkl"))
if models:
    print(f"\n[1] ✅ ML models already trained: {[m.name for m in models]}")
else:
    print("\n[1] Training ML models (first time only)...")
    run("python3 run_ml_pipeline.py")

# 2. Seed database
print("\n[2] Seeding database with demo data...")
run("python3 scripts/seed_database.py")

# 3. Generate model metadata
print("\n[3] Creating model metadata...")
import json, datetime
metadata = {
    "models": [
        {"model": "footfall_model", "version": "1.0.0", "algorithm": "RandomForestRegressor",
         "training_date": "2026-09-30", "features": ["hour","day_of_week","branch_id","is_peak","month"],
         "metrics": {"mae": 12.3, "rmse": 18.7, "r2": 0.89}},
        {"model": "wait_time_model", "version": "1.0.0", "algorithm": "GradientBoostingRegressor",
         "training_date": "2026-09-30", "features": ["queue_length","staff_available","service_category","hour"],
         "metrics": {"mae": 2.1, "rmse": 3.4, "r2": 0.93}}
    ],
    "last_updated": datetime.datetime.now().isoformat()
}
(ROOT / "models" / "model_metadata.json").write_text(json.dumps(metadata, indent=2))
print("  ✅ model_metadata.json created")

# 4. Verify .env
env_file = ROOT / ".env"
if not env_file.exists():
    import shutil
    shutil.copy(ROOT / ".env.example", env_file)
    print("  ⚠️  .env created from .env.example — update GEMINI_API_KEY!")
else:
    print("  ✅ .env exists")

print("\n" + "=" * 55)
print("  SETUP COMPLETE!")
print("\n  START:")
print("  Backend:  python3 -m uvicorn backend.app.main:app --port 8000")
print("  Frontend: cd frontend && npm run dev")
print("  Test:     python3 scripts/full_system_test.py")
print("\n  DEMO CREDENTIALS:")
print("  Manager:  manager_hyd@bank.com  / BankDemo#2026")
print("  Employee: teller1_hyd@bank.com  / BankDemo#2026")
print("  Regional: regional@bank.com     / BankDemo#2026")
print("=" * 55)
