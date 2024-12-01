from datetime import datetime
from playwright.sync_api import sync_playwright
import time, re, sys, os, argparse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append('/Users/ryandeng/Library/Mobile Documents/com~apple~CloudDocs/Documents/North_America/Job hunting/playwrightJobAutomation')
from get_verification_code import get_verification_code
from click_on_text import click_on_text
from wait_for_text import wait_for_text
# LASTNAME = 'FANG'
# LICENSE_NO = '30402984'
# KEYWORD = 'HAN'
# Define the date range
# START_DATE = datetime(2024, 12, 8)
# END_DATE = datetime(2024, 12, 12)
# location = "Burnaby claim centre (Wayburne Drive)"
# Define the time range
# START_TIME = datetime.strptime("8:30 AM", "%I:%M %p")
# END_TIME = datetime.strptime("10:00 AM", "%I:%M %p")
COOLING_FACTOR = 1
def remove_ordinal_suffix(date_str):
    return re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
# Helper function to check if the date is in the specified range
def is_date_in_range(date_str, start_date, end_date):
    date_str = remove_ordinal_suffix(date_str)  # Remove the ordinal suffix
    date_obj = datetime.strptime(date_str.strip(), "%A, %B %d, %Y")
    return start_date <= date_obj <= end_date

# Helper function to check if the time is within the specified range
def is_time_in_range(time_str, start_time, end_time):
    time_obj = datetime.strptime(time_str.strip(), "%I:%M %p")
    return start_time <= time_obj <= end_time


def choseTimeSlot(page, start_date, end_date, start_time, end_time, cooling_factor):
    
    
    # Wait for the '.date-title' selector to appear, with a 30s timeout
    page.wait_for_selector('.date-title', timeout=cooling_factor * 15000)
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Enter choseTimeSlot")
    time_to_book = None
    # Extract date and time slot information. And check whether desired.
    # Locate the date titles
    date_titles = page.query_selector_all('.date-title')

    # Check all dates
    for date_element in date_titles:
        date_text = date_element.inner_text().strip()
        time_elements = date_element.query_selector_all('~ .mat-button-toggle')
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Date: {date_text}")
        # check all time slots for current date
        for time_element in time_elements:
            time_text = time_element.inner_text().strip()
            print(f"  Time Slot: {time_text}")
            # if desired, store the time slot
            if is_date_in_range(date_text, start_date, end_date) and is_time_in_range(time_text, start_time, end_time) and not time_to_book:
                time_to_book = time_element
    # If find appropriate time slot, click
    if time_to_book:
        time_to_book.click()
        # time.sleep(cooling_factor * 2)
        # Locate and click the "Review Appointment" button
        # page.click('button:has-text("Review Appointment")')
        wait_for_text(page, 'Review Appointment')
        click_on_text('Review Appointment', page)
        # click_by_id(page, 'button.primary.collapsible-action-button')

        # Optionally, wait for any required transition or navigation after the first click
        page.wait_for_load_state("networkidle")
        # time.sleep(cooling_factor * 2)

        # Locate and click the "Next" button
        # page.click('button.primary.collapsible-action-button')
        wait_for_text(page, 'Next')
        click_on_text('Next', page)

        # Wait for any transition or page update after the "Next" button click
        # page.wait_for_load_state("networkidle")
        # time.sleep(cooling_factor * 2)

        # Locate and click the "Send" button
        # page.click('button.primary[type="submit"]')
        wait_for_text(page, 'Send')
        click_on_text('Send', page)

        time.sleep(cooling_factor * 20)
        return True
    else:
        return False

def click_close_button_if_exists(page):
    # Define a locator for the button using its unique attributes
    close_button_locator = 'button[mat-button] img[src="assets/close-cross.png"]'

    # Check if the button exists and is visible
    if page.locator(close_button_locator).is_visible():
        # Click the button
        page.locator(close_button_locator).click()
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Close button found and clicked.")
    else:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Close button not found; proceeding without action.")

def run(lastname, license_no, keyword, start_date, end_date, start_time, end_time, location, cooling_factor):
    with sync_playwright() as p:
        # Launch the browser
        # browser = p.chromium.launch(headless=True)  # Set headless=False to see the browser
        browser = p.chromium.launch(headless=False)  # Set headless=False to see the browser
        context = browser.new_context()  # Create a fresh browser context
        page = context.new_page()  # Create a new page within the context
        completed = False
        while not completed:
            try:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Routing to website.")
                # Navigate to the URL
                page.reload(wait_until="networkidle")
                page.goto("https://onlinebusiness.icbc.com/webdeas-ui/login;type=driver")

                # Input last name
                page.fill('input#mat-input-0[formcontrolname="drvrLastName"]', lastname)

                # Input license number
                page.fill('input#mat-input-1[formcontrolname="licenceNumber"]', license_no)

                # Input keyword
                page.fill('input#mat-input-2[formcontrolname="keyword"]', keyword)

                # Click on the checkbox (targeting the checkbox input by ID or label)
                page.click('mat-checkbox#mat-checkbox-1')  # Clicks on the checkbox itself
                time.sleep(cooling_factor * 2)

                # Click the Sign in button
                page.click('button.primary.collapsible-action-button')
                time.sleep(cooling_factor * 2)

                # Wait for the page to load (you may need to adjust the waiting logic based on your use case)
                page.wait_for_load_state('networkidle')

                # Check if the "No thanks" button is visible
                if page.is_visible('button:has-text("No thanks")'):
                        # If the button is visible, click it
                        page.click('button:has-text("No thanks")')
                        time.sleep(cooling_factor * 2)

                # Optional: Check for "Reschedule appointment" button and handle it
                try:
                    reschedule_button_selector = 'button.raised-button.primary:has-text("Reschedule appointment")'
                    # Wait for the selector to appear with a timeout of 30 seconds
                    page.wait_for_selector(reschedule_button_selector, timeout=cooling_factor * 10000)
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Reschedule button is visible.")                    
                    time.sleep(cooling_factor * 1)
                    page.click(reschedule_button_selector)
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Clicked 'Reschedule appointment' button.")
                    time.sleep(cooling_factor * 1)
                        # Locate the "Yes" button by its role and name
                    yes_button = page.get_by_role("button", name="Yes")
                    # Click the "Yes" button
                    yes_button.click()
                    time.sleep(cooling_factor * 1)
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Clicked 'Yes' button.")                
                except Exception as reschedule_error:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Reschedule appointment button not found or could not be clicked: {reschedule_error}")

                # Click on the tab with id "mat-tab-label-1-1"
                page.wait_for_selector('div.mat-tab-label-content:has-text("By office")', timeout=cooling_factor * 10000)
                by_office_tab = page.locator('div.mat-tab-label-content:has-text("By office")')
                by_office_tab.click()
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Successfully clicked the 'By office' tab.")
                time.sleep(cooling_factor * 1)
                
                

                # Click the input field to open the autocomplete
                page.click('input#mat-input-4')

                # Wait for the autocomplete options to appear (ensure the options have time to load)
                page.wait_for_selector('mat-option', timeout=cooling_factor * 5000)  # Adjust timeout if necessary
                time.sleep(cooling_factor * 2)

                # Click the first option that matches 'Burnaby claim centre (Wayburne Drive)'
                # page.click('mat-option:has-text("Burnaby claim centre (Wayburne Drive)")')
                # page.click('mat-option:has-text("Campbell River Service BC centre")')
                page.click(f'mat-option:has-text("{location}")')
                
                # Wait for some action or for the form to update
                page.wait_for_load_state('networkidle')
                # Call the function to click the close button for cancellation fee if it exists
                click_close_button_if_exists(page)
                time.sleep(cooling_factor * 1)
                
                # Wait for the appointment listings to load
                # page.wait_for_selector('.appointment-listings')
                
                if choseTimeSlot(page, start_date, end_date, start_time, end_time, cooling_factor):
                    verification_code = get_verification_code(browser)
                    print(verification_code)

                    # Wait for the OTP input field to be visible and interactable
                    page.wait_for_selector('input[formcontrolname="otpField"]', timeout=cooling_factor * 20000)

                    # Fill the OTP input field with the verification code
                    otp_input = page.locator('input[formcontrolname="otpField"]')
                    otp_input.fill(verification_code)

                    # Wait for the submit button to be visible
                    page.wait_for_selector('button.submit-code-button', timeout=cooling_factor * 20000)

                    time.sleep(cooling_factor * 1)
                    # Click the submit button
                    buttons = page.locator('button.submit-code-button:has-text("Submit code and book appointment")')
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Found {buttons.count()} buttons.")
                    submit_button = buttons.nth(0)
                    submit_button.click()
                    time.sleep(cooling_factor * 60 * 60)
                    completed = True
                    while completed:
                        print(f"************{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Successfully booked for {license_no}**************************************************************")
                        time.sleep(cooling_factor * 60 * 30)
                else:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} No available time slots for {location}...")
            except Exception as e:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Error occurred: {e}. Retrying very soon...")
            # finally:
            #     browser.close()

# Command-line argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ICBC Road Test Appointment Script")
    parser.add_argument("--lastname", required=True, help="Last name")
    parser.add_argument("--license_no", required=True, help="License number")
    parser.add_argument("--keyword", required=True, help="Keyword")
    parser.add_argument("--start_date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end_date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--start_time", required=True, help="Start time (e.g., '8:30 AM')")
    parser.add_argument("--end_time", required=True, help="End time (e.g., '10:00 AM')")
    parser.add_argument("--location", required=True, help="Test location")
    parser.add_argument("--cooling_factor", required=True, help="Cooling factor to control the speed of operations")

    args = parser.parse_args()

    # Convert dates and times to datetime objects
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    start_time = datetime.strptime(args.start_time, "%I:%M %p")
    end_time = datetime.strptime(args.end_time, "%I:%M %p")
    cooling_factor = float(args.cooling_factor)

    run(args.lastname, args.license_no, args.keyword, start_date, end_date, start_time, end_time, args.location, cooling_factor)
