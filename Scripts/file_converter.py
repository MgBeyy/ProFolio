import requests
from decouple import config

def convert_html_to_pdf(html_string):
    response = requests.post(
        'https://api.pdfshift.io/v3/convert/pdf',
        headers={ 'X-API-Key': config('PDFSHIFT_API_KEY') },
        json={
            "source": html_string,
            "landscape": False,
            "use_print": False
        }
    )

    if response.status_code != 200:
        raise Exception(f"Failed to convert HTML to PDF: {response.text}")
    
    return response.content