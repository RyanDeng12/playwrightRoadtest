from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import time, re, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from get_verification_code import get_verification_code

LASTNAME = 'FANG'
LICENSE_NO = '30402984'
KEYWORD = 'HAN'
# Define the date range
START_DATE = datetime(2024, 12, 8)
END_DATE = datetime(2024, 12, 12)
location = "Burnaby claim centre (Wayburne Drive)"
# Define the time range
START_TIME = datetime.strptime("8:30 AM", "%I:%M %p")
END_TIME = datetime.strptime("10:00 AM", "%I:%M %p")
COOLING_FACTOR = 1
def remove_ordinal_suffix(date_str):
    return re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
# Helper function to check if the date is in the specified range
def is_date_in_range(date_str, START_DATE, END_DATE):
    date_str = remove_ordinal_suffix(date_str)  # Remove the ordinal suffix
    date_obj = datetime.strptime(date_str.strip(), "%A, %B %d, %Y")
    return START_DATE <= date_obj <= END_DATE

# Helper function to check if the time is within the specified range
def is_time_in_range(time_str):
    time_obj = datetime.strptime(time_str.strip(), "%I:%M %p")
    return START_TIME <= time_obj <= END_TIME


def choseTimeSlot(date_block):
        # Get the date text for this specific date block
        try:
            # Attempt to get the inner text of the first locator
            date_text = date_block.locator("xpath=./div").inner_text().strip()
            print("Action A: Successfully located element with text:", date_text)
            # Perform Action A here (e.g., any other actions you want on the located element)
        except Exception as e:
            date_text = date_block.locator("xpath=./div[1]").inner_text().strip()
        # Perform Action B here (e.g., fallback actions)
            
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Date: {date_text}")
        if is_date_in_range(date_text, START_DATE, END_DATE):
                # Full XPath to find all time slots under this date block
                time_slots_xpath = date_block.locator("xpath=.//mat-button-toggle")

                # Get all time slots for this date
                time_slots_elements = time_slots_xpath.all()

                for time_slot in time_slots_elements:
                        time_text = time_slot.inner_text().strip()
                        print(date_text, time_text)
                        # Check if the time slot is within the desired time range
                        if is_time_in_range(time_text):
                                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}   Selected Time Slot: {time_text}")
                                # You can click the time slot here if needed, e.g.:
                                time_slot.click()
                                time.sleep(COOLING_FACTOR * 2)
                                return True
                return False
# Helper function to retry logic if a timeout occurs
def retry_on_failure(page, action, sleep_time=120):
    try:
        action()
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Error occurred: {e}. Retrying in {sleep_time} seconds...")
        time.sleep(sleep_time)
        action()
def click_close_button_if_exists(page):
    # Define a locator for the button using its unique attributes
    close_button_locator = 'button[mat-button] img[src="assets/close-cross.png"]'

    # Check if the button exists and is visible
    if page.locator(close_button_locator).is_visible():
        # Click the button
        page.locator(close_button_locator).click()
        print("Close button found and clicked.")
    else:
        print("Close button not found; proceeding without action.")

def run():
    with sync_playwright() as p:
        # Launch the browser
        # browser = p.chromium.launch(headless=True)  # Set headless=False to see the browser
        browser = p.chromium.launch(headless=False)  # Set headless=False to see the browser
        context = browser.new_context()  # Create a fresh browser context
        page = context.new_page()  # Create a new page within the context
        while True:
            try:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Routing to website.")
                # Navigate to the URL
                page.reload(wait_until="networkidle")
                page.goto("https://onlinebusiness.icbc.com/webdeas-ui/login;type=driver")

                # Input last name
                page.fill('input#mat-input-0[formcontrolname="drvrLastName"]', LASTNAME)

                # Input license number
                page.fill('input#mat-input-1[formcontrolname="licenceNumber"]', LICENSE_NO)

                # Input keyword
                page.fill('input#mat-input-2[formcontrolname="keyword"]', KEYWORD)

                # Click on the checkbox (targeting the checkbox input by ID or label)
                page.click('mat-checkbox#mat-checkbox-1')  # Clicks on the checkbox itself
                time.sleep(COOLING_FACTOR * 2)

                # Click the Sign in button
                page.click('button.primary.collapsible-action-button')
                time.sleep(COOLING_FACTOR * 2)

                # Wait for the page to load (you may need to adjust the waiting logic based on your use case)
                page.wait_for_load_state('networkidle')

                # Check if the "No thanks" button is visible
                if page.is_visible('button:has-text("No thanks")'):
                        # If the button is visible, click it
                        page.click('button:has-text("No thanks")')
                        time.sleep(COOLING_FACTOR * 2)

                # Optional: Check for "Reschedule appointment" button and handle it
                try:
                    reschedule_button_selector = 'button.raised-button.primary:has-text("Reschedule appointment")'
                    # Wait for the selector to appear with a timeout of 30 seconds
                    page.wait_for_selector(reschedule_button_selector, timeout=COOLING_FACTOR * 10000)
                    print("Reschedule button is visible.")                    
                    time.sleep(COOLING_FACTOR * 1)
                    page.click(reschedule_button_selector)
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Clicked 'Reschedule appointment' button.")
                    time.sleep(COOLING_FACTOR * 1)
                        # Locate the "Yes" button by its role and name
                    yes_button = page.get_by_role("button", name="Yes")
                    # Click the "Yes" button
                    yes_button.click()
                    time.sleep(COOLING_FACTOR * 1)
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Clicked 'Yes' button.")                
                except Exception as reschedule_error:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Reschedule appointment button not found or could not be clicked: {reschedule_error}")

                # Click on the tab with id "mat-tab-label-1-1"
                page.wait_for_selector('div.mat-tab-label-content:has-text("By office")', timeout=COOLING_FACTOR * 10000)
                by_office_tab = page.locator('div.mat-tab-label-content:has-text("By office")')
                by_office_tab.click()
                print("Successfully clicked the 'By office' tab.")
                time.sleep(COOLING_FACTOR * 1)
                
                

                # Click the input field to open the autocomplete
                page.click('input#mat-input-4')

                # Wait for the autocomplete options to appear (ensure the options have time to load)
                page.wait_for_selector('mat-option', timeout=COOLING_FACTOR * 5000)  # Adjust timeout if necessary
                time.sleep(COOLING_FACTOR * 2)

                # Click the first option that matches 'Burnaby claim centre (Wayburne Drive)'
                # page.click('mat-option:has-text("Burnaby claim centre (Wayburne Drive)")')
                # page.click('mat-option:has-text("Campbell River Service BC centre")')
                page.click(f'mat-option:has-text("{location}")')
                
                # Wait for some action or for the form to update
                page.wait_for_load_state('networkidle')
                # Call the function to click the close button for cancellation fee if it exists
                click_close_button_if_exists(page)
                time.sleep(COOLING_FACTOR * 1)
                
                # Wait for the appointment listings to load
                # page.wait_for_selector('.appointment-listings')
                
                # Define the XPath for the first date
                first_date_xpath = "/html/body/div[2]/div[2]/div/mat-dialog-container/app-eligible-tests/div/div[2]/mat-button-toggle-group/div"
                page.wait_for_selector(f'xpath={first_date_xpath}', timeout=COOLING_FACTOR * 30000)
                # Locate the first date element
                first_date = page.locator(f'xpath={first_date_xpath}')
                time.sleep(COOLING_FACTOR * 1)
                if first_date.count() > 0:
                    print(f'Successfully find the first date {first_date}.')
                    # Extract the date text for the first date
                    chosen = choseTimeSlot(first_date)

                    # Handle subsequent dates (XPath pattern for other dates)
                    date_blocks_xpath = "/html/body/div[2]/div[2]/div/mat-dialog-container/app-eligible-tests/div/div[2]/mat-button-toggle-group/div/span"
                    
                    # Locate all available date blocks
                    date_blocks = page.locator(f'xpath={date_blocks_xpath}')
                    
                    # Iterate through the remaining date blocks
                    for i in range(date_blocks.count()):  # Start from 1 to skip the first date
                        if chosen:
                            break
                        date_block = date_blocks.nth(i)
                        chosen = choseTimeSlot(date_block)
                    if chosen:
                        # Locate and click the "Review Appointment" button
                        page.click('button:has-text("Review Appointment")')

                        # Optionally, wait for any required transition or navigation after the first click
                        page.wait_for_load_state("networkidle")
                        time.sleep(COOLING_FACTOR * 2)

                        # Locate and click the "Next" button
                        page.click('button.primary.collapsible-action-button')

                        # Wait for any transition or page update after the "Next" button click
                        page.wait_for_load_state("networkidle")
                        time.sleep(COOLING_FACTOR * 2)

                        # Locate and click the "Send" button
                        page.click('button.primary[type="submit"]')

                        time.sleep(COOLING_FACTOR * 20)

                        verification_code = get_verification_code(browser)
                        print(verification_code)

                        # Wait for the OTP input field to be visible and interactable
                        page.wait_for_selector('input[formcontrolname="otpField"]', timeout=COOLING_FACTOR * 20000)
                    
                        # Fill the OTP input field with the verification code
                        otp_input = page.locator('input[formcontrolname="otpField"]')
                        otp_input.fill(verification_code)

                        # Wait for the submit button to be visible
                        page.wait_for_selector('button.submit-code-button', timeout=COOLING_FACTOR * 20000)

                        time.sleep(COOLING_FACTOR * 1)
                        # Click the submit button
                        buttons = page.locator('button.submit-code-button:has-text("Submit code and book appointment")')
                        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Found {buttons.count()} buttons.")
                        submit_button = buttons.nth(0)
                        submit_button.click()
                        time.sleep(COOLING_FACTOR * 60 * 60)

                        break
                else:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} No available dates for {location}...")
            except Exception as e:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Error occurred: {e}. Retrying very soon...")
            # finally:
            #     browser.close()

# Run the function
if __name__ == "__main__":
    run()
