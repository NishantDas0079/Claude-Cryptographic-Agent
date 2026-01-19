# Core Plugin Interface
# File: plugins/core/base_plugin.py

```
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import json

class PluginType(Enum):
    """Types of plugins supported"""
    COMPLIANCE = "compliance"
    SECURITY = "security"
    MONITORING = "monitoring"
    INTEGRATION = "integration"
    TOOL = "tool"

@dataclass
class PluginMetadata:
    """Metadata for plugin registration"""
    name: str
    version: str
    author: str
    description: str
    plugin_type: PluginType
    dependencies: List[str] = None
    config_schema: Dict[str, Any] = None

class BasePlugin(ABC):
    """Base class for all cryptographic plugins"""
    
    def __init__(self, metadata: PluginMetadata):
        self.metadata = metadata
        self.config = {}
        self.enabled = True
        
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]):
        """Initialize plugin with configuration"""
        self.config = config
        
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin logic"""
        pass
    
    @abstractmethod
    async def validate(self, data: Dict[str, Any]) -> bool:
        """Validate input data"""
        pass
    
    @abstractmethod
    async def cleanup(self):
        """Cleanup resources"""
        pass
    
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata"""
        return self.metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plugin to dictionary"""
        return {
            "name": self.metadata.name,
            "version": self.metadata.version,
            "type": self.metadata.plugin_type.value,
            "enabled": self.enabled,
            "config": self.config
        }
```

# Plugin Manager
# File: plugins/core/plugin_manager.py

```
import asyncio
import importlib
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from .base_plugin import BasePlugin, PluginMetadata, PluginType

class PluginManager:
    """Manages plugin lifecycle and discovery"""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, BasePlugin] = {}
        self.enabled_plugins: List[str] = []
        
    async def discover_plugins(self) -> List[str]:
        """Discover available plugins"""
        discovered = []
        
        # Scan built-in plugins
        builtin_path = self.plugins_dir / "builtin"
        if builtin_path.exists():
            for plugin_dir in builtin_path.iterdir():
                if plugin_dir.is_dir() and (plugin_dir / "plugin.yaml").exists():
                    discovered.append(f"builtin.{plugin_dir.name}")
        
        # Scan third-party plugins
        third_party_path = self.plugins_dir / "third-party"
        if third_party_path.exists():
            for plugin_dir in third_party_path.iterdir():
                if plugin_dir.is_dir() and (plugin_dir / "plugin.yaml").exists():
                    discovered.append(f"third-party.{plugin_dir.name}")
        
        return discovered
    
    async def load_plugin(self, plugin_path: str) -> Optional[BasePlugin]:
        """Load a specific plugin"""
        try:
            # Parse plugin path
            if "." in plugin_path:
                category, plugin_name = plugin_path.split(".", 1)
            else:
                category, plugin_name = "builtin", plugin_path
            
            # Load plugin metadata
            plugin_dir = self.plugins_dir / category / plugin_name
            metadata_file = plugin_dir / "plugin.yaml"
            
            if not metadata_file.exists():
                print(f"❌ Plugin metadata not found: {plugin_path}")
                return None
            
            with open(metadata_file, 'r') as f:
                metadata_dict = yaml.safe_load(f)
            
            # Create metadata object
            metadata = PluginMetadata(
                name=metadata_dict['name'],
                version=metadata_dict['version'],
                author=metadata_dict.get('author', 'Unknown'),
                description=metadata_dict['description'],
                plugin_type=PluginType(metadata_dict['type']),
                dependencies=metadata_dict.get('dependencies', []),
                config_schema=metadata_dict.get('config_schema', {})
            )
            
            # Import plugin module
            module_path = f"plugins.{category}.{plugin_name}.plugin"
            module = importlib.import_module(module_path)
            
            # Instantiate plugin
            plugin_class = getattr(module, metadata_dict['class'])
            plugin = plugin_class(metadata)
            
            # Load configuration
            config_file = plugin_dir / "config.yaml"
            config = {}
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
            
            # Initialize plugin
            await plugin.initialize(config)
            
            # Register plugin
            self.plugins[plugin_path] = plugin
            
            print(f"✅ Loaded plugin: {metadata.name} v{metadata.version}")
            return plugin
            
        except Exception as e:
            print(f"❌ Failed to load plugin {plugin_path}: {str(e)}")
            return None
    
    async def load_all_plugins(self):
        """Load all discovered plugins"""
        print("🔌 Loading plugins...")
        plugin_paths = await self.discover_plugins()
        
        tasks = [self.load_plugin(path) for path in plugin_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        loaded_count = sum(1 for r in results if r is not None)
        print(f"✅ Loaded {loaded_count}/{len(plugin_paths)} plugins")
    
    async def execute_plugin(self, plugin_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific plugin"""
        if plugin_name not in self.plugins:
            raise ValueError(f"Plugin not found: {plugin_name}")
        
        plugin = self.plugins[plugin_name]
        
        if not plugin.enabled:
            return {"success": False, "error": "Plugin is disabled"}
        
        try:
            result = await plugin.execute(context)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def execute_plugins_by_type(self, plugin_type: PluginType, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute all plugins of a specific type"""
        results = []
        
        for plugin_name, plugin in self.plugins.items():
            if plugin.metadata.plugin_type == plugin_type and plugin.enabled:
                try:
                    result = await plugin.execute(context)
                    results.append({
                        "plugin": plugin_name,
                        "success": True,
                        "result": result
                    })
                except Exception as e:
                    results.append({
                        "plugin": plugin_name,
                        "success": False,
                        "error": str(e)
                    })
        
        return results
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins"""
        return [
            {
                "name": plugin.metadata.name,
                "version": plugin.metadata.version,
                "type": plugin.metadata.plugin_type.value,
                "enabled": plugin.enabled,
                "description": plugin.metadata.description
            }
            for plugin in self.plugins.values()
        ]
```

# Example Plugin: Compliance Checker
# File: plugins/builtin/compliance-checker/plugin.yaml

```yaml
name: "compliance-checker"
version: "1.0.0"
author: "Cryptographic Agent Team"
description: "Checks cryptographic operations against compliance standards"
type: "compliance"
class: "ComplianceCheckerPlugin"
dependencies:
  - "policy-enforcer"
config_schema:
  standards:
    type: "array"
    items:
      type: "string"
    default: ["NIST-800-57", "PCI-DSS", "FIPS-140-3"]
  strict_mode:
    type: "boolean"
    default: true
```

# File: plugins/builtin/compliance-checker/plugin.py

```
from plugins.core.base_plugin import BasePlugin, PluginMetadata, PluginType
from typing import Dict, Any, List
import json

class ComplianceCheckerPlugin(BasePlugin):
    """Compliance checking plugin"""
    
    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        self.standards = []
        self.strict_mode = True
        
    async def initialize(self, config: Dict[str, Any]):
        """Initialize plugin"""
        await super().initialize(config)
        self.standards = config.get('standards', ['NIST-800-57'])
        self.strict_mode = config.get('strict_mode', True)
        
        print(f"✅ Compliance Checker initialized with standards: {self.standards}")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute compliance check"""
        operation = context.get('operation')
        parameters = context.get('parameters', {})
        
        print(f"🔍 Checking compliance for {operation}")
        
        violations = []
        
        # Check key compliance
        if 'key' in parameters:
            key_violations = await self._check_key_compliance(parameters['key'])
            violations.extend(key_violations)
        
        # Check certificate compliance
        if 'certificate' in parameters:
            cert_violations = await self._check_certificate_compliance(parameters['certificate'])
            violations.extend(cert_violations)
        
        # Check algorithm compliance
        if 'algorithm' in parameters:
            algo_violations = await self._check_algorithm_compliance(parameters['algorithm'])
            violations.extend(algo_violations)
        
        result = {
            "operation": operation,
            "timestamp": context.get('timestamp'),
            "standards_checked": self.standards,
            "violations_found": len(violations),
            "violations": violations,
            "compliant": len(violations) == 0
        }
        
        if violations and self.strict_mode:
            result["action"] = "BLOCKED - Compliance violation"
        elif violations:
            result["action"] = "ALLOWED with warnings"
        else:
            result["action"] = "ALLOWED - Compliant"
        
        return result
    
    async def _check_key_compliance(self, key_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check key compliance"""
        violations = []
        
        # Check RSA key size
        if key_info.get('type') == 'RSA':
            key_size = key_info.get('size', 0)
            if key_size < 2048:
                violations.append({
                    "standard": "NIST-800-57",
                    "requirement": "RSA key size >= 2048 bits",
                    "actual": f"{key_size} bits",
                    "severity": "HIGH"
                })
        
        # Check ECC curve
        elif key_info.get('type') == 'ECC':
            curve = key_info.get('curve', '')
            approved_curves = ['P-256', 'P-384', 'P-521']
            if curve not in approved_curves:
                violations.append({
                    "standard": "NIST-800-57",
                    "requirement": f"ECC curve must be one of {approved_curves}",
                    "actual": curve,
                    "severity": "HIGH"
                })
        
        return violations
    
    async def _check_certificate_compliance(self, cert_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check certificate compliance"""
        violations = []
        
        # Check validity period
        validity_days = cert_info.get('validity_days', 0)
        if validity_days > 825:  # Approximately 2 years
            violations.append({
                "standard": "CAB Forum",
                "requirement": "TLS certificate validity <= 825 days",
                "actual": f"{validity_days} days",
                "severity": "MEDIUM"
            })
        
        # Check key usage
        if 'server_auth' in cert_info.get('extended_key_usage', []):
            if 'digital_signature' not in cert_info.get('key_usage', []):
                violations.append({
                    "standard": "RFC 5280",
                    "requirement": "Server certificates must have digitalSignature key usage",
                    "actual": "Missing digitalSignature",
                    "severity": "HIGH"
                })
        
        return violations
    
    async def validate(self, data: Dict[str, Any]) -> bool:
        """Validate input data"""
        required_fields = ['operation', 'parameters']
        return all(field in data for field in required_fields)
    
    async def cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up Compliance Checker plugin")
```

# Plugin Configuration File
# File: plugins/config.yaml

```yaml
# Global plugin configuration
plugin_settings:
  auto_discovery: true
  hot_reload: false
  log_level: "INFO"
  plugin_dir: "./plugins"

# Enabled plugins
enabled_plugins:
  - "builtin.compliance-checker"
  - "builtin.expiry-monitor"
  - "builtin.policy-enforcer"
  - "third-party.ca-letsencrypt"

# Plugin-specific configurations
plugin_configs:
  compliance-checker:
    standards:
      - "NIST-800-57"
      - "PCI-DSS"
      - "FIPS-140-3"
    strict_mode: true
  
  expiry-monitor:
    check_interval: 86400  # 24 hours in seconds
    warning_threshold: 30  # days
    critical_threshold: 7  # days
  
  policy-enforcer:
    policies_path: "./config/policies"
    auto_remediate: false
  
  ca-letsencrypt:
    api_url: "https://acme-v02.api.letsencrypt.org/directory"
    staging: false
    account_email: "admin@example.com"
```

# Plugin Template for Developers
# File: plugins/templates/plugin-template/plugin.yaml

```yaml
# Plugin Metadata
name: "your-plugin-name"
version: "1.0.0"
author: "Your Name/Organization"
description: "Brief description of what this plugin does"
type: "compliance|security|monitoring|integration|tool"

# Plugin Class
class: "YourPluginClass"

# Dependencies
dependencies:
  - "other-plugin-name"

# Configuration Schema
config_schema:
  setting1:
    type: "string"
    description: "Description of setting1"
    default: "default_value"
  setting2:
    type: "integer"
    description: "Description of setting2"
    default: 100
  setting3:
    type: "boolean"
    description: "Description of setting3"
    default: true
```


