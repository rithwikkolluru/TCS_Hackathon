import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.generator import SyntheticDataGenerator
from src.data.validator import DataValidator

def main():
    print("==========================================")
    print("  SYNTHETIC BANKING DATA GENERATOR")
    print("==========================================")
    generator = SyntheticDataGenerator(seed=42, num_days=90)
    datasets = generator.generate_all()

    print("\nValidating generated data for PII and schema integrity...")
    validator = DataValidator()
    val_results = validator.validate_all(datasets)

    all_passed = True
    for ds_name, (is_valid, errors) in val_results.items():
        if is_valid:
            print(f"  [PASS] {ds_name} passed all validation and PII checks.")
        else:
            print(f"  [FAIL] {ds_name} validation failed:")
            for err in errors:
                print(f"    - {err}")
            all_passed = False

    if all_passed:
        print("\nAll datasets generated and validated successfully!")
    else:
        print("\nValidation issues found. Please inspect generated data.")

if __name__ == "__main__":
    main()
