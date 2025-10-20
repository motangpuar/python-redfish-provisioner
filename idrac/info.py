# idrac/info.py
from .client import RedfishClient
from typing import Dict

class SystemInfo:
    """Query system information"""
    
    def __init__(self, client: RedfishClient):
        self.client = client
        
    def get_basic_info(self) -> Dict:
        """Get basic system information"""
        systems = self.client.get("/Systems")
        system_url = systems['Members'][0]['@odata.id']
        system_data = self.client.get(system_url.replace('/redfish/v1', ''))
        
        return {
            'model': system_data.get('Model', 'Unknown'),
            'manufacturer': system_data.get('Manufacturer', 'Unknown'),
            'serial_number': system_data.get('SerialNumber', 'Unknown'),
            'power_state': system_data.get('PowerState', 'Unknown'),
            'health_status': system_data.get('Status', {}).get('Health', 'Unknown'),
            'bios_version': system_data.get('BiosVersion', 'Unknown'),
            'memory_gb': self._convert_memory(system_data.get('MemorySummary', {})),
            'cpu_count': system_data.get('ProcessorSummary', {}).get('Count', 0),
            'cpu_model': self._get_cpu_model(),
        }
        
    def get_network_info(self) -> Dict:
        """Get network adapter information"""
        systems = self.client.get("/Systems")
        system_url = systems['Members'][0]['@odata.id']
        system_data = self.client.get(system_url.replace('/redfish/v1', ''))
        
        network_info = {}
        if 'NetworkInterfaces' in system_data:
            net_url = system_data['NetworkInterfaces']['@odata.id']
            interfaces = self.client.get(net_url.replace('/redfish/v1', ''))
            
            for i, iface in enumerate(interfaces.get('Members', [])):
                iface_data = self.client.get(iface['@odata.id'].replace('/redfish/v1', ''))
                network_info[f'interface_{i}'] = {
                    'name': iface_data.get('Name', f'eth{i}'),
                    'status': iface_data.get('Status', {}).get('Health', 'Unknown')
                }
                
        return network_info
        
    def get_storage_info(self) -> Dict:
        """Get storage information"""
        systems = self.client.get("/Systems")
        system_url = systems['Members'][0]['@odata.id']
        system_data = self.client.get(system_url.replace('/redfish/v1', ''))
        
        storage_info = {}
        if 'Storage' in system_data:
            storage_url = system_data['Storage']['@odata.id']
            storage_data = self.client.get(storage_url.replace('/redfish/v1', ''))
            
            for i, storage in enumerate(storage_data.get('Members', [])):
                stor_data = self.client.get(storage['@odata.id'].replace('/redfish/v1', ''))
                storage_info[f'storage_{i}'] = {
                    'name': stor_data.get('Name', f'Storage{i}'),
                    'status': stor_data.get('Status', {}).get('Health', 'Unknown')
                }
                
        return storage_info
        
    def _convert_memory(self, memory_summary: Dict) -> int:
        """Convert memory size to GB"""
        total_mb = memory_summary.get('TotalSystemMemoryGiB', 0)
        return int(total_mb) if total_mb else 0
        
    def _get_cpu_model(self) -> str:
        """Get CPU model information"""
        try:
            systems = self.client.get("/Systems")
            system_url = systems['Members'][0]['@odata.id']
            processors_url = f"{system_url}/Processors"
            processors = self.client.get(processors_url.replace('/redfish/v1', ''))
            
            if processors.get('Members'):
                cpu_data = self.client.get(processors['Members'][0]['@odata.id'].replace('/redfish/v1', ''))
                return cpu_data.get('Model', 'Unknown')
        except:
            pass
            
        return 'Unknown'
