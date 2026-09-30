import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.etl import ETLPipeline

def main():
    print("==========================================")
    print("  RUNNING REPRODUCIBLE ETL PIPELINE")
    print("==========================================")
    pipeline = ETLPipeline()
    res = pipeline.run_pipeline()
    print(f"Processed Visits Count: {len(res['processed_visits'])}")
    print(f"Processed Feedback Count: {len(res['processed_feedback'])}")

if __name__ == "__main__":
    main()
