from playwright.sync_api import sync_playwright
import re
import time

def get_verification_code(browser):

    page_verification_code = browser.new_page()

    # Go to Mailinator inbox
    inbox_name = "roadtestryan"
    page_verification_code.goto(f"https://www.mailinator.com/v4/public/inboxes.jsp?to={inbox_name}")

    # Wait for the inbox to load
    page_verification_code.wait_for_selector("table.table-striped", timeout=10000)
    time.sleep(3)
    # Get all emails from the inbox
    emails = page_verification_code.locator("tr.ng-scope")

    # Find the most recent email received less than 5 minutes ago with the subject "Verification code to book a road test"
    recent_email = None
    for email in emails.all():
        # Extract subject and received time
        subject = email.locator("td:nth-child(3)").inner_text()
        received_time = email.locator("td:nth-child(4)").inner_text()

        # Check if the subject matches and the email was received in the last 2 minutes
        if "Verification code to book a road test" in subject:
            recent_email = email
            break

    # If we found the recent email, click it
    if recent_email:
        recent_email.click()
        time.sleep(3)

        # Wait for the iframe containing the email body to be available
        page_verification_code.wait_for_selector("iframe#html_msg_body", timeout=10000)

        # Get the iframe and switch to it
        iframe = page_verification_code.frame(name="html_msg_body")
        time.sleep(3)
        # Wait for the <h2> element inside the iframe to be available
        iframe.wait_for_selector('h2', timeout=20000)  # General selector to check h2 element
        time.sleep(3)
        # Extract the verification code from the <h2> element
        verification_code_element = iframe.locator('h2')
        verification_code = verification_code_element.inner_text()

        # Print and return the verification code
        print(f"Verification Code: {verification_code}")
        time.sleep(3)
        # Close the page_verification_code
        page_verification_code.close()
        return verification_code
    else:
        print("No recent verification email found.")
        # Close the page_verification_code
        page_verification_code.close()
        return None

    

# Run the function
if __name__ == "__main__":
    get_verification_code()

