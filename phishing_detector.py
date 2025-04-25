
import requests
import logging
import json
import urllib.parse

logger = logging.getLogger(__name__)

class IPQS:
    def __init__(self):
        self.key = '0MWpmQ3wQZK8cJQw7bmyMsYWvAfbXhGG'
        
    def scan_url(self, url: str, strictness: int = 0) -> dict:
        """Scan URL using IPQS API with configurable strictness"""
        try:
            api_url = f'https://www.ipqualityscore.com/api/json/url/{self.key}/{urllib.parse.quote_plus(url)}'
            response = requests.get(api_url, params={'strictness': strictness})
            return response.json()
        except Exception as e:
            logger.error(f"Error scanning URL: {str(e)}")
            return {"success": False, "message": str(e)}

def check_phishing_url(url: str):
    """
    Check if a URL is potentially a phishing site using IPQualityScore API.
    Returns (is_unsafe, risk_score, details)
    """
    try:
        ipqs = IPQS()
        result = ipqs.scan_url(url)
        
        if not result.get('success'):
            return False, 0, {"error": result.get('message', 'API request failed')}
            
        is_unsafe = any([
            result.get('malware', False),
            result.get('phishing', False),
            result.get('suspicious', False),
            result.get('unsafe', False)
        ])
        
        risk_score = result.get('risk_score', 0)
        
        details = {
            'domain': result.get('domain', ''),
            'ip_address': result.get('ip_address', ''),
            'country_code': result.get('country_code', ''),
            'server': result.get('server', ''),
            'domain_rank': result.get('domain_rank', 0),
            'risk_indicators': {
                'malware': result.get('malware', False),
                'phishing': result.get('phishing', False),
                'suspicious': result.get('suspicious', False),
                'adult': result.get('adult', False),
                'spamming': result.get('spamming', False),
                'risky_tld': result.get('risky_tld', False)
            },
            'domain_info': {
                'dns_valid': result.get('dns_valid', False),
                'domain_age': result.get('domain_age', {}),
                'domain_trust': result.get('domain_trust', ''),
                'category': result.get('category', '')
            },
            'security': {
                'spf_record': result.get('spf_record', False),
                'dmarc_record': result.get('dmarc_record', False)
            },
            'technologies': result.get('technologies', []),
            'dns_records': {
                'a_records': result.get('a_records', []),
                'mx_records': result.get('mx_records', []),
                'ns_records': result.get('ns_records', [])
            },
            'content': {
                'page_size': result.get('page_size', 0),
                'content_type': result.get('content_type', ''),
                'page_title': result.get('page_title', ''),
                'language_code': result.get('language_code', '')
            }
        }
        
        return is_unsafe, risk_score, details
        
    except Exception as e:
        logger.error(f"Error checking URL: {str(e)}")
        return False, 0, {"error": str(e)}
