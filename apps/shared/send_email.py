import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from config.config import settings

def send_email_from_server_from_brevo(to_email, content):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_EMAIL_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to_email}],
        sender={"email": settings.BREVO_EMAIL_API_EMAIL, "name": "Your App"},
        subject="Otp",
        html_content=content,
    )

    try:
        response = api_instance.send_transac_email(email)
        return response
    except ApiException as e:
        print("Error sending email:", e)
        return None

# send_email("sirojiddinovsolohiddin961@gmail.com","Welcome","<h3>Thanks for joining!</h3>")
