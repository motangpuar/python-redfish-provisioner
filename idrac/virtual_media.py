# idrac/virtual_media.py
from .client import RedfishClient
from typing import List, Dict, Optional

class VirtualMediaManager:
    """Handle virtual media operations"""
    
    def __init__(self, client: RedfishClient):
        self.client = client
        
    def get_virtual_media_info(self) -> List[Dict]:
        """Get all virtual media devices"""
        managers = self.client.get("/Managers")
        manager_url = managers['Members'][0]['@odata.id']
        vm_response = self.client.get(f"{manager_url}/VirtualMedia".replace('/redfish/v1', ''))
        
        media_info = []
        for media in vm_response.get('Members', []):
            media_data = self.client.get(media['@odata.id'].replace('/redfish/v1', ''))
            media_info.append({
                'id': media_data.get('Id', 'Unknown'),
                'name': media_data.get('Name', 'Unknown'),
                'media_types': media_data.get('MediaTypes', []),
                'connected': media_data.get('Connected', False),
                'inserted': media_data.get('Inserted', False)
            })
            
        return media_info
        
    def mount_iso(self, iso_url: str) -> bool:
        """Mount ISO image"""
        try:
            # Find CD/DVD virtual media
            cd_media = self._find_cd_media()
            if not cd_media:
                raise Exception("No CD/DVD virtual media found")
                
            # Mount the ISO
            insert_endpoint = f"{cd_media['@odata.id']}/Actions/VirtualMedia.InsertMedia"
            data = {
                "Image": iso_url,
                "WriteProtected": True
            }
            
            response = self.client.post(insert_endpoint.replace('/redfish/v1', ''), data)
            return response.status_code in [200, 202, 204]
            
        except Exception as e:
            self.client.logger.error(f"Failed to mount ISO: {e}")
            return False
            
    def unmount_iso(self) -> bool:
        """Unmount ISO image"""
        try:
            cd_media = self._find_cd_media()
            if not cd_media:
                return True  # Nothing to unmount
                
            eject_endpoint = f"{cd_media['@odata.id']}/Actions/VirtualMedia.EjectMedia"
            response = self.client.post(eject_endpoint.replace('/redfish/v1', ''), {})
            return response.status_code in [200, 202, 204]
            
        except Exception as e:
            self.client.logger.error(f"Failed to unmount ISO: {e}")
            return False
            
    def _find_cd_media(self) -> Optional[Dict]:
        """Find CD/DVD virtual media device"""
        managers = self.client.get("/Managers")
        manager_url = managers['Members'][0]['@odata.id']
        vm_response = self.client.get(f"{manager_url}/VirtualMedia".replace('/redfish/v1', ''))
        
        for media in vm_response.get('Members', []):
            media_data = self.client.get(media['@odata.id'].replace('/redfish/v1', ''))
            media_types = media_data.get('MediaTypes', [])
            
            if 'CD' in media_types or 'DVD' in media_types:
                return media_data
                
        return None
