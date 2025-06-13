import requests, os
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
        end_day = today.day
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


def main(number, date, fn, hours=40):

    formatted_date_today = date.strftime("%b %d, %Y")
    formatted_date_range = get_date_range_string(date)

    headers = {
        "Authorization": f"Bearer {INVOICE_GENERATOR_API_KEY}"
    }

    data = {
        "from": f"{FULL_NAME}\n{ADDRESS}",
        "to": f"{COMPANY_NAME}\n{COMPANY_ADDRESS}",
        "logo": LOGO_URL,  # Optional: Add your logo URL here
        "number": number,
        "date": formatted_date_today,
        "items[0][name]": formatted_date_range,
        "items[0][quantity]": hours,
        "items[0][unit_cost]": HOURLY_RATE,
        "notes": f'''Please make Payment to:\n\n{FULL_NAME}\n{BANK_DETAILS}''',
    }

    response = requests.post(INVOICE_GENERATOR_URL, headers=headers, data=data)

    # Save the PDF file
    with open(fn, "wb") as f:
        f.write(response.content)

if __name__ == "__main__":
    ## todo: Add parser for command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Generate an invoice.")
    parser.add_argument("--hours", type=int, default=40, help="Number of hours worked (default: 40)")

    args = parser.parse_args()
    os.makedirs(INVOICE_MAIN_PATH, exist_ok=True)
    hours = args.hours  # Example: 40 hours worked
    
    # Get the next invoice number based on existing files
    invoices = os.listdir(INVOICE_MAIN_PATH)
    number = len(invoices) + 1 if invoices else 1
    fn = f"{INVOICE_MAIN_PATH}/invoice-{number}.pdf"
    # Ensure the filename is unique
    while os.path.exists(fn):
        print(f"Invoice number {number} already exists, incrementing...")
        number += 1
        fn = f"{INVOICE_MAIN_PATH}/invoice-{number}.pdf"
    print(f"Generating invoice number: {number} at {fn}")

    date_today = datetime.today()

    main(number, date_today, fn, hours=hours)  # Example: 40 hours worked