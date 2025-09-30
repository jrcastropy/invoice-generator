import requests, os, json
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

INVOICE_GENERATOR_API_KEY = os.getenv("INVOICE_GENERATOR_API_KEY")
INVOICE_GENERATOR_URL = os.getenv("INVOICE_GENERATOR_URL", "https://invoice-generator.com")
FULL_NAME = os.getenv("FULL_NAME")
INVOICE_MAIN_PATH = os.getenv("INVOICE_MAIN_PATH", "invoices")
LOGO_URL = os.getenv("LOGO_URL")
HOURLY_RATE= os.getenv("HOURLY_RATE", 0)
ADDRESS = os.getenv("ADDRESS")
COMPANY_NAME = os.getenv("COMPANY_NAME")
COMPANY_ADDRESS = os.getenv("COMPANY_ADDRESS")
BANK_DETAILS = os.getenv("BANK_DETAILS")


def ordinal(n: int) -> str:
    """Convert an integer to its ordinal string (e.g., 1 -> 1st, 2 -> 2nd)."""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"


def get_date_range_string(today):
    year = today.year
    month_name = today.strftime("%B")
    
    if today.day <= 15:
        start_day = 1
        end_day = 15
    else:
        start_day = 16
        # Handle months with varying lengths
        if today.month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, today.month + 1, 1)
        last_day = (next_month - timedelta(days=1)).day
        end_day = last_day

    start_str = ordinal(start_day)
    end_str = ordinal(end_day)

    return f"{month_name} {start_str} - {month_name} {end_str}, {year}"


def main(number, start_day, date_range, fn, hours=80):

    headers = {
        "Authorization": f"Bearer {INVOICE_GENERATOR_API_KEY}"
    }

    data = {
        "from": f"{FULL_NAME}\n{ADDRESS}",
        "to": f"{COMPANY_NAME}\n{COMPANY_ADDRESS}",
        "logo": LOGO_URL,  # Optional: Add your logo URL here
        "number": number,
        "date": start_day,
        "items[0][name]": date_range,
        "items[0][quantity]": hours,
        "items[0][unit_cost]": HOURLY_RATE,
        "notes": f'''Please make Payment to:\n\n{FULL_NAME}\n{BANK_DETAILS}''',
    }
    print(json.dumps(data, indent=2, ensure_ascii=False))
    response = requests.post(INVOICE_GENERATOR_URL, headers=headers, data=data)

    # Save the PDF file
    with open(fn, "wb") as f:
        f.write(response.content)

if __name__ == "__main__":
    ## todo: Add parser for command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Generate an invoice.")
    parser.add_argument("--hours", type=int, default=80, help="Number of hours worked (default: 80)")
    parser.add_argument("--start_day", type=str, default=None, help="The start day of the billing period in 'YYYY-MM-DD' format, example: 2025-06-06")

    args = parser.parse_args()
    os.makedirs(INVOICE_MAIN_PATH, exist_ok=True)
    hours = args.hours  # Example: 40 hours worked
    start_day = args.start_day
    if start_day:        
        start_date = datetime.strptime(start_day, "%Y-%m-%d")
        # Convert the start_day string to "%B %d, %Y" format
        start_day = start_date.strftime("%B %d, %Y")
    else:
        # date today in YYYY-MM-DD format
        start_date = datetime.today()
        start_day = start_date.strftime("%B %d, %Y")

    date_range = get_date_range_string(start_date)

    # Get the next invoice number based on existing files
    invoices = [inv for inv in os.listdir(INVOICE_MAIN_PATH) if inv.endswith('.pdf')]
    print(f"Existing invoices: {invoices}")
    number = len(invoices) + 1 if invoices else 1
    fn = f"{INVOICE_MAIN_PATH}/invoice-{number}.pdf"
    print(f"Creating {fn}")
    # Ensure the filename is unique
    while os.path.exists(fn):
        print(f"Invoice number {number} already exists, incrementing...")
        number += 1
        fn = f"{INVOICE_MAIN_PATH}/invoice-{number}.pdf"
    print(f"Generating invoice number: {number} at {fn}")

    main(number, start_day, date_range, fn, hours=hours)  # Example: 40 hours worked