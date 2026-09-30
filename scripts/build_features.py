import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.features.feature_engineering import FeatureEngineer

def main():
    print("==========================================")
    print("  BUILDING ML FEATURE DATASETS")
    print("==========================================")
    fe = FeatureEngineer()
    footfall_df, wait_df = fe.run_feature_pipeline()
    print(f"Footfall Feature Matrix Shape: {footfall_df.shape}")
    print(f"Wait Time Feature Matrix Shape: {wait_df.shape}")

if __name__ == "__main__":
    main()
