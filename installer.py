# installer.py
import time
import logging
import yaml
from idrac.client import RedfishClient
from idrac.power import PowerManager
from idrac.virtual_media import VirtualMediaManager
from idrac.boot import BootManager
from idrac.info import SystemInfo
from typing import Dict

class SimpleInstaller:
    """Simple server installer using iDRAC"""
    
    def __init__(self, config_file: str):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('SimpleInstaller')
        
    def query_server_info(self, server_name: str) -> Dict:
        """Query comprehensive server information"""
        server = self._get_server_config(server_name)
        if not server:
            return {"error": "Server not found"}
            
        try:
            client = RedfishClient(server['idrac_host'], server['idrac_user'], server['idrac_pass'])
            info = SystemInfo(client)
            power = PowerManager(client)
            boot = BootManager(client)
            vm = VirtualMediaManager(client)
            
            return {
                'server_name': server_name,
                'basic_info': info.get_basic_info(),
                'network_info': info.get_network_info(),
                'storage_info': info.get_storage_info(),
                'boot_info': boot.get_boot_info(),
                'virtual_media': vm.get_virtual_media_info(),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {"error": str(e)}
            
    def install_server(self, server_name: str) -> bool:
        """Install single server"""
        server = self._get_server_config(server_name)
        if not server:
            self.logger.error(f"Server {server_name} not found")
            return False
            
        try:
            # Initialize components
            client = RedfishClient(server['idrac_host'], server['idrac_user'], server['idrac_pass'])
            power = PowerManager(client)
            vm = VirtualMediaManager(client)
            boot = BootManager(client)
            
            self.logger.info(f"Starting installation for {server_name}")
            
            # Step 1: Power off if needed
            if power.get_power_state() != 'Off':
                self.logger.info("Powering off server")
                if not power.force_power_off():
                    raise Exception("Failed to power off")
                if not power.wait_for_power_state('Off', 60):
                    raise Exception("Server did not power off")
                    
            # Step 2: Mount ISO
            self.logger.info(f"Mounting ISO: {server['iso_url']}")
            if not vm.mount_iso(server['iso_url']):
                raise Exception("Failed to mount ISO")
                
            # Step 3: Set boot order
            self.logger.info("Setting boot order to CD")
            if not boot.set_boot_source('Cd', 'Once'):
                raise Exception("Failed to set boot order")
                
            # Step 4: Power on
            self.logger.info("Powering on server")
            if not power.power_on():
                raise Exception("Failed to power on")
                
            # Step 5: Wait for SSH (if configured)
            if self.config.get('wait_for_ssh', False):
                self._wait_for_ssh(server['target_host'])
                
            # Step 6: Cleanup
            self.logger.info("Cleaning up virtual media")
            vm.unmount_iso()
            
            self.logger.info(f"Installation completed for {server_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Installation failed for {server_name}: {e}")
            return False
            
    def _get_server_config(self, server_name: str) -> Dict:
        """Get server configuration by name"""
        for server in self.config.get('servers', []):
            if server['name'] == server_name:
                return server
        return None
        
    def _wait_for_ssh(self, host: str, timeout: int = 1800):
        """Wait for SSH to become available"""
        import socket
        
        self.logger.info(f"Waiting for SSH on {host}")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                if sock.connect_ex((host, 22)) == 0:
                    self.logger.info(f"SSH available on {host}")
                    sock.close()
                    return
                sock.close()
            except:
                pass
            time.sleep(30)
            
        self.logger.warning(f"SSH timeout for {host}")
