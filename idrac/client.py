# idrac/client.py
import requests
import urllib3
import logging
from typing import Dict, Optional

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class RedfishClient:
    """Simple Redfish API client"""
    
    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.base_url = f"https://{host}/redfish/v1"
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = False
        self.session.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.logger = logging.getLogger(f"Redfish-{host}")
        
    def get(self, endpoint: str) -> Dict:
        """GET request to Redfish endpoint"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"GET {endpoint} failed: {response.status_code}")
            
        return response.json()
        
    def post(self, endpoint: str, data: Dict) -> requests.Response:
        """POST request to Redfish endpoint"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=data, timeout=30)
        
        if response.status_code not in [200, 201, 202, 204]:
            raise Exception(f"POST {endpoint} failed: {response.status_code} - {response.text}")
            
        return response
        
    def patch(self, endpoint: str, data: Dict) -> requests.Response:
        """PATCH request to Redfish endpoint"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.patch(url, json=data, timeout=30)
        
        if response.status_code not in [200, 202, 204]:
            raise Exception(f"PATCH {endpoint} failed: {response.status_code}")
            
        return response
