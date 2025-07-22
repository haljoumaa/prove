# python3 run_prove.py --start-date YYYY-MM-DD --end-date YYYY-MM-DD

from ingestion.download_attachments import download_pics_main
from processing.payroll_verification import verify_payroll
import argparse

def main():
    parser = argparse.ArgumentParser(description="Run full PROVE pipeline.")
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    args = parser.parse_args()

    print("Step 1: Fetching emails and downloading attachments...")
    download_pics_main(start_date=args.start_date, end_date=args.end_date)

    print("Step 2: Verifying payroll...")
    verify_payroll()

    print("✅ All done!")

if __name__ == "__main__":
    main()
