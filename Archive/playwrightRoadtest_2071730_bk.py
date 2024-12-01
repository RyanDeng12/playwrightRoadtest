from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import time, re, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from get_verification_code import get_verification_code

LASTNAME = 'zhou'
LICENSE_NO = '2071730'
KEYWORD = '980327'
# Define the date range
START_DATE = datetime(2024, 12, 7)
END_DATE = datetime(2024, 12, 21)
# LOCATIONS = ["Burnaby claim centre (Wayburne Drive)", "Vancouver driver licensing (Point Grey)"]
LOCATIONS = ["Richmond claim centre (Elmbridge Way)"]
# LOCATIONS = ["Burnaby claim centre (Wayburne Drive)", "Campbell River Service BC centre"]
# Define the time range
START_TIME = datetime.strptime("8:00 AM", "%I:%M %p")
END_TIME = datetime.strptime("6:00 PM", "%I:%M %p")
RETRY_MINUTES = 1
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
                                time.sleep(RETRY_MINUTES * 2)
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

def run():
    with sync_playwright() as p:
        # Launch the browser
        # browser = p.chromium.launch(headless=True)  # Set headless=False to see the browser
        browser = p.chromium.launch(headless=False)  # Set headless=False to see the browser
        page = browser.new_page()
        while True:
            try:
                

                # Navigate to the URL
                page.goto("https://onlinebusiness.icbc.com/webdeas-ui/login;type=driver")

                # Input last name
                page.fill('input#mat-input-0[formcontrolname="drvrLastName"]', LASTNAME)

                # Input license number
                page.fill('input#mat-input-1[formcontrolname="licenceNumber"]', LICENSE_NO)

                # Input keyword
                page.fill('input#mat-input-2[formcontrolname="keyword"]', KEYWORD)

                # Click on the checkbox (targeting the checkbox input by ID or label)
                page.click('mat-checkbox#mat-checkbox-1')  # Clicks on the checkbox itself
                time.sleep(RETRY_MINUTES * 2)

                # Click the Sign in button
                page.click('button.primary.collapsible-action-button')
                time.sleep(RETRY_MINUTES * 2)

                # Wait for the page to load (you may need to adjust the waiting logic based on your use case)
                page.wait_for_load_state('networkidle')

                # Check if the "No thanks" button is visible
                if page.is_visible('button:has-text("No thanks")'):
                        # If the button is visible, click it
                        page.click('button:has-text("No thanks")')
                        time.sleep(RETRY_MINUTES * 2)

                # Optional: Check for "Reschedule appointment" button and handle it
                try:
                    reschedule_button_selector = 'button.raised-button.primary:has-text("Reschedule appointment")'
                    while page.is_visible(reschedule_button_selector):
                        time.sleep(RETRY_MINUTES * 1)
                        page.click(reschedule_button_selector)
                        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Clicked 'Reschedule appointment' button.")
                        time.sleep(RETRY_MINUTES * 1)
                         # Locate the "Yes" button by its role and name
                        yes_button = page.get_by_role("button", name="Yes")
                        # Click the "Yes" button
                        yes_button.click()
                        time.sleep(RETRY_MINUTES * 1)
                        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Clicked 'Yes' button.")                
                except Exception as reschedule_error:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Reschedule appointment button not found or could not be clicked: {reschedule_error}")

                # Click on the tab with id "mat-tab-label-1-1"
                by_office_tab = page.locator('div.mat-tab-label-content:has-text("By office")')
                by_office_tab.click()
                print("Successfully clicked the 'By office' tab.")
                time.sleep(RETRY_MINUTES * 1)
                
                for location in LOCATIONS:

                    # Click the input field to open the autocomplete
                    page.click('input#mat-input-4')

                    # Wait for the autocomplete options to appear (ensure the options have time to load)
                    page.wait_for_selector('mat-option', timeout=5000)  # Adjust timeout if necessary
                    time.sleep(RETRY_MINUTES * 2)

                    # Click the first option that matches 'Burnaby claim centre (Wayburne Drive)'
                    # page.click('mat-option:has-text("Burnaby claim centre (Wayburne Drive)")')
                    # page.click('mat-option:has-text("Campbell River Service BC centre")')
                    page.click(f'mat-option:has-text("{location}")')
                    
                    # Wait for some action or for the form to update
                    page.wait_for_load_state('networkidle')
                    time.sleep(RETRY_MINUTES * 1)
                    # Wait for the appointment listings to load
                    # page.wait_for_selector('.appointment-listings')

                    # Define the XPath for the first date
                    first_date_xpath = "/html/body/div[2]/div[2]/div/mat-dialog-container/app-eligible-tests/div/div[2]/mat-button-toggle-group/div"
                    
                    # Locate the first date element
                    first_date = page.locator(f'xpath={first_date_xpath}')
                    time.sleep(RETRY_MINUTES * 1)
                    if first_date.count() > 0:
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
                            time.sleep(RETRY_MINUTES * 2)

                            # Locate and click the "Next" button
                            page.click('button.primary.collapsible-action-button')

                            # Wait for any transition or page update after the "Next" button click
                            page.wait_for_load_state("networkidle")
                            time.sleep(RETRY_MINUTES * 2)

                            # Locate and click the "Send" button
                            page.click('button.primary[type="submit"]')

                            time.sleep(RETRY_MINUTES * 20)

                            verification_code = get_verification_code(browser)
                            print(verification_code)

                            # Wait for the OTP input field to be visible and interactable
                            page.wait_for_selector('input[formcontrolname="otpField"]', timeout=20000)
                        
                            # Fill the OTP input field with the verification code
                            otp_input = page.locator('input[formcontrolname="otpField"]')
                            otp_input.fill(verification_code)

                            # Wait for the submit button to be visible
                            page.wait_for_selector('button.submit-code-button', timeout=20000)

                            time.sleep(RETRY_MINUTES * 1)
                            # Click the submit button
                            buttons = page.locator('button.submit-code-button:has-text("Submit code and book appointment")')
                            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Found {buttons.count()} buttons.")
                            submit_button = buttons.nth(0)
                            submit_button.click()
                            time.sleep(RETRY_MINUTES * 60 * 60)

                            break
                    else:
                        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} No available dates for {location}...")
                else:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} No favorable slots found: {e}. Retrying in {RETRY_MINUTES} minutes...")
                    time.sleep(60 * RETRY_MINUTES)  # Sleep for RETRY_MINUTES minutes before retrying
            except Exception as e:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Error occurred: {e}. Retrying in {RETRY_MINUTES} minutes...")
                time.sleep(60 * RETRY_MINUTES)  # Sleep for RETRY_MINUTES minutes before retrying
            # finally:
            #     browser.close()

# Run the function
if __name__ == "__main__":
    run()
