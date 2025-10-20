# main.py
#!/usr/bin/env python3
import argparse
import json
from installer import SimpleInstaller

def main():
    parser = argparse.ArgumentParser(description='Simple iDRAC Remote Installer')
    parser.add_argument('-c', '--config', required=True, help='Config YAML file')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Query server information')
    info_parser.add_argument('server', help='Server name')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install server')
    install_parser.add_argument('server', help='Server name')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List configured servers')
    
    args = parser.parse_args()
    
    installer = SimpleInstaller(args.config)
    
    if args.command == 'info':
        info = installer.query_server_info(args.server)
        print(json.dumps(info, indent=2))
        
    elif args.command == 'install':
        success = installer.install_server(args.server)
        print(f"Installation {'SUCCESS' if success else 'FAILED'}")
        
    elif args.command == 'list':
        with open(args.config, 'r') as f:
            import yaml
            config = yaml.safe_load(f)
        
        print("Configured servers:")
        for server in config.get('servers', []):
            print(f"  - {server['name']} (iDRAC: {server['idrac_host']}, Target: {server['target_host']})")
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
