
import requests
import logging

logger = logging.getLogger(__name__)

def analyze_email(email: str) -> dict:
    """
    Analyze email using IPQS Email Verification API
    """
    try:
        api_key = "0MWpmQ3wQZK8cJQw7bmyMsYWvAfbXhGG"
        api_url = f'https://www.ipqualityscore.com/api/json/email/{api_key}/{email}'
        
        response = requests.get(api_url)
        data = response.json()
        
        if not data.get('success'):
            return {"error": data.get('message', 'API request failed')}
            
        return data
        
    except Exception as e:
        logger.error(f"Error analyzing email: {str(e)}")
        return {"error": str(e)}
