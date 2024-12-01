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