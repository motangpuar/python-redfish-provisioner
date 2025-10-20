# idrac/boot.py
from .client import RedfishClient
from typing import Dict

class BootManager:
    """Handle boot order and configuration"""
    
    def __init__(self, client: RedfishClient):
        self.client = client
        
    def set_boot_source(self, source: str = 'Cd', enabled: str = 'Once') -> bool:
        """Set boot source for next boot"""
        try:
            systems = self.client.get("/Systems")
            system_url = systems['Members'][0]['@odata.id']
            
            boot_data = {
                "Boot": {
                    "BootSourceOverrideEnabled": enabled,
                    "BootSourceOverrideTarget": source
                }
            }
            
            response = self.client.patch(system_url.replace('/redfish/v1', ''), boot_data)
            return response.status_code in [200, 202, 204]
            
        except Exception as e:
            self.client.logger.error(f"Failed to set boot source: {e}")
            return False
            
    def get_boot_info(self) -> Dict:
        """Get current boot configuration"""
        systems = self.client.get("/Systems")
        system_url = systems['Members'][0]['@odata.id']
        system_data = self.client.get(system_url.replace('/redfish/v1', ''))
        
        boot_info = system_data.get('Boot', {})
        return {
            'current_source': boot_info.get('BootSourceOverrideTarget', 'None'),
            'enabled': boot_info.get('BootSourceOverrideEnabled', 'Disabled'),
            'supported_sources': boot_info.get('BootSourceOverrideTarget@Redfish.AllowableValues', [])
        }
