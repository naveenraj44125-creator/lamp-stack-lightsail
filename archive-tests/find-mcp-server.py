#!/usr/bin/env python3

"""
Try to find the MCP server by scanning common AWS IP ranges
"""

import requests
import concurrent.futures
import ipaddress

def check_ip(ip):
    """Check if an IP has MCP server running"""
    try:
        response = requests.get(f"http://{ip}:3000/", timeout=3)
        if response.status_code == 200 and 'Lightsail Deployment MCP Server' in response.text:
            # Check for github_username
            has_github_username = 'github_username' in response.text.lower()
            version = "Unknown"
            if '1.1.1' in response.text:
                version = "1.1.1"
            elif '1.1.0' in response.text:
                version = "1.1.0"
            
            return ip, version, has_github_username
    except:
        pass
    return None

def scan_aws_ranges():
    """Scan common AWS IP ranges for MCP servers"""
    
    print("🔍 Scanning for MCP Servers in AWS IP Ranges")
    print("=" * 50)
    print("This may take a few minutes...")
    
    # Common AWS us-east-1 IP ranges (limited scan)
    ip_ranges = [
        "3.80.0.0/16",      # Common AWS range
        "3.81.0.0/16",      # Current server range
        "18.215.0.0/16",    # Another common range
        "54.144.0.0/16",    # EC2 range
    ]
    
    servers_found = []
    
    for ip_range in ip_ranges:
        print(f"\n📡 Scanning {ip_range}...")
        
        network = ipaddress.IPv4Network(ip_range)
        
        # Limit to first 256 IPs to avoid taking too long
        ips_to_check = list(network.hosts())[:256]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(check_ip, str(ip)) for ip in ips_to_check]
            
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                result = future.result()
                if result:
                    ip, version, has_github_username = result
                    print(f"✅ Found MCP server at {ip}")
                    print(f"   Version: {version}")
                    print(f"   GitHub Username Support: {'✅' if has_github_username else '❌'}")
                    servers_found.append(result)
                
                # Progress indicator
                if (i + 1) % 50 == 0:
                    print(f"   Checked {i + 1}/{len(ips_to_check)} IPs...")
    
    return servers_found

def quick_check_known_patterns():
    """Quick check of known IP patterns"""
    
    print("🔍 Quick Check of Known Patterns")
    print("=" * 40)
    
    # Check variations around known IP
    base_ip = "3.81.56"
    servers_found = []
    
    for last_octet in range(100, 130):  # Check around 119
        ip = f"{base_ip}.{last_octet}"
        result = check_ip(ip)
        if result:
            ip, version, has_github_username = result
            print(f"✅ Found MCP server at {ip}")
            print(f"   Version: {version}")
            print(f"   GitHub Username Support: {'✅' if has_github_username else '❌'}")
            servers_found.append(result)
    
    return servers_found

def main():
    print("🔧 MCP Server Discovery Tool")
    print("=" * 50)
    
    # First do a quick check
    print("Phase 1: Quick check of known patterns")
    quick_servers = quick_check_known_patterns()
    
    if quick_servers:
        print(f"\n✅ Found {len(quick_servers)} server(s) in quick check")
        
        # Check if any have the fix
        fixed_servers = [s for s in quick_servers if s[2]]  # s[2] is has_github_username
        
        if fixed_servers:
            print("🎉 Found server(s) with OIDC fix!")
            for ip, version, _ in fixed_servers:
                print(f"   • {ip} (Version: {version})")
            return True
        else:
            print("⚠️  Found servers but none have the OIDC fix yet")
    
    # If no servers found or no fix found, do broader scan
    print("\nPhase 2: Broader AWS IP range scan")
    print("⚠️  This will take several minutes...")
    
    user_input = input("Continue with broader scan? (y/N): ").lower()
    if user_input != 'y':
        print("Scan cancelled")
        return False
    
    all_servers = scan_aws_ranges()
    
    if all_servers:
        print(f"\n✅ Total servers found: {len(all_servers)}")
        
        fixed_servers = [s for s in all_servers if s[2]]
        
        if fixed_servers:
            print("🎉 Found server(s) with OIDC fix!")
            for ip, version, _ in fixed_servers:
                print(f"   • {ip} (Version: {version})")
            return True
        else:
            print("⚠️  Found servers but none have the OIDC fix")
    else:
        print("❌ No MCP servers found in scan")
    
    return False

if __name__ == "__main__":
    success = main()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 OIDC fix found!")
    else:
        print("⚠️  OIDC fix not found")
        print("💡 The deployment may still be in progress or failed")
    
    exit(0 if success else 1)