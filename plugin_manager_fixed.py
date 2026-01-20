"""
✅ SIMPLE PLUGIN MANAGER - ERROR FREE
"""

import os
import sys

class SimplePluginManager:
    def __init__(self):
        self.plugins = {}
        print("✅ Plugin Manager initialized")
    
    def load_compliance_checker(self):
        """Direct load of compliance checker"""
        try:
            # Add plugins directory to path
            plugins_path = os.path.join(os.path.dirname(__file__), "builtin")
            if plugins_path not in sys.path:
                sys.path.append(plugins_path)
            
            # Import directly
            import compliance_checker
            plugin = compliance_checker.ComplianceChecker()
            
            self.plugins["compliance_checker"] = plugin
            print(f"✅ Loaded: {plugin.name} v{plugin.version}")
            return plugin
            
        except Exception as e:
            print(f"❌ Failed to load compliance checker: {e}")
            return None
    
    def run_compliance_check(self, domain="test.com", days=365):
        """Run compliance check"""
        if "compliance_checker" not in self.plugins:
            print("Loading compliance checker...")
            self.load_compliance_checker()
        
        if "compliance_checker" in self.plugins:
            return self.plugins["compliance_checker"].check_certificate(
                domain=domain, 
                days=days
            )
        return None

# Quick test
if __name__ == "__main__":
    print("🧪 Testing Fixed Plugin Manager")
    print("="*50)
    
    manager = SimplePluginManager()
    result = manager.run_compliance_check("example.com", 400)
    
    if result:
        print(f"\n✅ Compliance check completed!")
        print(f"Status: {'Compliant' if result['compliant'] else 'Non-compliant'}")
    else:
        print("\n❌ Compliance check failed")