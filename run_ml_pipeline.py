import sys
import time
import datetime
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.data.generator import SyntheticDataGenerator
from src.data.validator import DataValidator
from src.data.etl import ETLPipeline
from src.features.feature_engineering import FeatureEngineer
from src.models.footfall_model import train_footfall_model
from src.models.wait_time_model import train_wait_model
from src.nlp.feedback_analysis import run_feedback_analysis
from src.models.live_predictor import predict_live
from scripts.train_models import generate_service_category_analysis

def main():
    start_time = time.time()
    print("=======================================================================")
    print("  INTELLIGENT BRANCH SERVICE LOAD AND CUSTOMER EXPERIENCE OPTIMIZER")
    print("                 COMPLETE ML & DATA PIPELINE RUNNER")
    print("=======================================================================")
    print(f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # STEP 1 & 2: Generate Data
    print("STEP 1: Generating Synthetic Banking Dataset (90-day horizon)...")
    generator = SyntheticDataGenerator(seed=42, num_days=90)
    datasets = generator.generate_all()

    # STEP 3: Validate Raw Data
    print("\nSTEP 2: Validating Raw Datasets and PII Compliance...")
    validator = DataValidator()
    val_results = validator.validate_all(datasets)
    for ds_name, (is_valid, errors) in val_results.items():
        if not is_valid:
            raise ValueError(f"Validation failed for dataset {ds_name}: {errors}")
    print("  [OK] Raw data validated successfully! Zero PII detected.")
    
    # STEP 4: Run ETL Pipeline
    print("\nSTEP 3: Running ETL Pipeline (Cleaning & Normalization)...")
    etl = ETLPipeline()
    etl_res = etl.run_pipeline()
    print(f"  [OK] Processed Visits: {len(etl_res['processed_visits'])}")
    print(f"  [OK] Processed Feedback: {len(etl_res['processed_feedback'])}")

    # STEP 5: Feature Engineering
    print("\nSTEP 4: Building Feature Engineering Matrices...")
    fe = FeatureEngineer()
    footfall_df, wait_df = fe.run_feature_pipeline()
    print(f"  [OK] Footfall Feature Shape: {footfall_df.shape}")
    print(f"  [OK] Wait Time Feature Shape: {wait_df.shape}")

    # STEP 6 & 7: Model Training & Evaluation
    print("\nSTEP 5: Training ML Models & Saving Pickles...")
    print("  -> Training Footfall Model (HistGradientBoosting)...")
    ff_metrics = train_footfall_model()

    print("  -> Training Waiting Time Model (HistGradientBoosting)...")
    wt_metrics = train_wait_model()

    # STEP 8: Generate Reports
    print("\nSTEP 6: Generating Analysis Reports...")
    generate_service_category_analysis()

    # STEP 9: Customer Feedback NLP
    print("\nSTEP 7: Analyzing Customer Feedback Sentiment & Topics...")
    fb_df = run_feedback_analysis()

    # STEP 10: Sanity Test Live Predictor Interface
    print("\nSTEP 8: Validating Live Predictor Interface...")
    sample_pred = predict_live(
        branch_id="BR002",
        service_category="Loans - Payment and Sanctioning",
        current_queue=14,
        staff_available=2,
        recent_arrivals=20
    )
    print("  [OK] Sample Live Prediction Result:")
    print(f"    - Branch: {sample_pred['branch_id']} | Category: {sample_pred['service_category']}")
    print(f"    - Predicted Wait: {sample_pred['predicted_wait_minutes']} mins")
    print(f"    - Bottleneck Risk: {sample_pred['bottleneck_risk']}")
    print(f"    - Required Staff: {sample_pred['staff_required']} (Gap: {sample_pred['staff_gap']})")
    print(f"    - Explanation: {sample_pred['explanation']}")

    elapsed = round(time.time() - start_time, 2)
    print("\n=======================================================================")
    print(f"  ML PIPELINE COMPLETED SUCCESSFULLY IN {elapsed} SECONDS!")
    print("=======================================================================")

if __name__ == "__main__":
    main()
