# idrac/power.py
import time
from .client import RedfishClient

class PowerManager:
    """Handle power operations"""
    
    def __init__(self, client: RedfishClient):
        self.client = client
        
    def get_power_state(self) -> str:
        """Get current power state"""
        systems = self.client.get("/Systems")
        system_url = systems['Members'][0]['@odata.id']
        system_data = self.client.get(system_url.replace('/redfish/v1', ''))
        return system_data.get('PowerState', 'Unknown')
        
    def power_on(self) -> bool:
        """Power on the server"""
        return self._power_action('On')
        
    def power_off(self) -> bool:
        """Graceful power off"""
        return self._power_action('GracefulShutdown')
        
    def force_power_off(self) -> bool:
        """Force power off"""
        return self._power_action('ForceOff')
        
    def restart(self) -> bool:
        """Restart the server"""
        return self._power_action('GracefulRestart')
        
    def force_restart(self) -> bool:
        """Force restart"""
        return self._power_action('ForceRestart')
        
    def _power_action(self, action: str) -> bool:
        """Execute power action"""
        try:
            systems = self.client.get("/Systems")
            system_url = systems['Members'][0]['@odata.id']
            reset_endpoint = f"{system_url}/Actions/ComputerSystem.Reset"
            
            data = {"ResetType": action}
            response = self.client.post(reset_endpoint.replace('/redfish/v1', ''), data)
            
            return response.status_code in [200, 202, 204]
        except Exception as e:
            self.client.logger.error(f"Power action {action} failed: {e}")
            return False
            
    def wait_for_power_state(self, target_state: str, timeout: int = 300) -> bool:
        """Wait for specific power state"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            current_state = self.get_power_state()
            if current_state == target_state:
                return True
            time.sleep(5)
            
        return False
