# Intelligent Branch Service Load and Customer Experience Optimizer
## Member 1 Module: Data Engineering & Machine Learning Foundation

This repository contains the complete, production-grade **Data Engineering and Machine Learning Foundation** for the **Intelligent Branch Service Load and Customer Experience Optimizer** project.

It provides robust synthetic data generation, reproducible ETL, advanced feature engineering, trained Machine Learning models (footfall prediction & waiting time prediction), bottleneck risk detection, staff requirement optimization, customer feedback NLP sentiment analysis, digital channel redirection, and live surge simulation capabilities.

---

## 🏛️ Enforced Service Categories (14 Categories)
- Loans - Payment and Sanctioning
- Insurance
- Deposit
- Withdrawal
- Account Opening
- Credit Card
- Debit Card
- Locker Issuing
- Cheque Withdrawal
- KYC Related
- Money Transfer
- Aadhaar Linking
- PAN Linking
- Other

---

## 🏙️ Indian Banking Context Branches
- `BR001`: Hyderabad Central
- `BR002`: Hyderabad Kukatpally
- `BR003`: Hyderabad Secunderabad
- `BR004`: Warangal Main
- `BR005`: Vijayawada Main
- `BR006`: Karimnagar Main
- `BR007`: Visakhapatnam Central
- `BR008`: Tirupati Main

---

## 🚀 Execution & Command Reference

### Master Pipeline Execution (One-Click)
```bash
python run_ml_pipeline.py
```

### Individual Step Scripts
```bash
python scripts/generate_data.py          # Synthetic dataset generation (90 days, zero PII)
python scripts/run_etl.py                 # Data cleaning, timestamp & category normalization
python scripts/build_features.py          # Lag, rolling, temporal, & ratio feature engineering
python scripts/train_models.py            # Train models, export metrics & service analysis
python scripts/validate_data.py           # PII and schema validation
python scripts/live_event_simulator.py    # Live surge & event stream simulator
```

### Run Automated Tests
```bash
python -m pytest
```

---

## 📊 Directory Structure

```text
tcs_hacki/
├── data/
│   ├── raw/                  # Raw synthetic CSV & Parquet files
│   ├── processed/            # Cleaned, PII-verified datasets
│   └── features/             # Aggregated ML feature matrices
├── models/                   # Saved .pkl trained model pipelines
│   ├── footfall_model.pkl
│   └── wait_time_model.pkl
├── reports/                  # JSON metrics & CSV analysis reports
│   ├── footfall_metrics.json
│   ├── wait_time_metrics.json
│   ├── service_category_analysis.csv
│   └── feedback_analysis.csv
├── src/
│   ├── data/                 # Data generator, validator, ETL pipeline
│   ├── features/             # Lag, rolling, and temporal feature engineering
│   ├── models/               # Footfall, wait time, bottleneck detector, live predictor
│   ├── nlp/                  # Customer feedback sentiment and topic extraction
│   ├── recommendation/       # Staff requirement & digital redirection logic
│   └── utils/                # Config and plain-language explainability
├── scripts/                  # Command-line execution scripts
├── tests/                    # Unit & integration pytest suite
├── docs/
│   └── ML_INTEGRATION.md     # Team integration guide for Members 2, 3, and 4
├── run_ml_pipeline.py        # Master pipeline executor
└── requirements.txt
```

---

## 🤝 Integration for Members 2, 3, and 4

See [docs/ML_INTEGRATION.md](file:///c:/Users/mssas/OneDrive/Desktop/tcs_hacki/docs/ML_INTEGRATION.md) for complete details and code examples on how to consume the predictions, bottleneck analysis, staff calculations, and live prediction interfaces in FastAPI or WebSocket services.
