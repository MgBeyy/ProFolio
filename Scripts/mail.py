import requests


def send_mail_via_mailgun(to_email, subject, message):
    api_key = "4fd724f7874d57edbecdeb76e23a8f41-67bd41c2-735f01a7"
    api_url = "https://api.mailgun.net/v3/sandbox237ffd3f5b544b73add818ea19ff3402.mailgun.org/messages"

    try:
        response = requests.post(
            api_url,
            auth=("api", api_key),
            data={
                "from": "Mailgun Sandbox <postmaster@sandbox237ffd3f5b544b73add818ea19ff3402.mailgun.org>",
                "to": to_email,
                "subject": subject,
                "text": message,
            },
        )

        if response.status_code == 200:
            return True, response
        else:
            return False, response

    except Exception as e:
        return False, str(e)
