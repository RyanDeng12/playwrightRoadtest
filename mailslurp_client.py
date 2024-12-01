# pip install mailslurp-client
import mailslurp_client
# create a mailslurp configuration
configuration = mailslurp_client.Configuration()
configuration.api_key['x-api-key'] = "7abbf86225a9f67cc1073b40b4f460305283915a5d6ebb100792010be63c5b54"
with mailslurp_client.ApiClient(configuration) as api_client:
    # create an inbox
    inbox_controller = mailslurp_client.InboxControllerApi(api_client)
    inbox = inbox_controller.create_inbox()
