"""R3R2: Find and register native upstream tools."""
import sys
import os
sys.path.insert(0, r"C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src")
sys.path.insert(0, r"C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src\toolkits")

print("=== R3R2: Find Native Upstream Tools ===")

# Check how tools are registered
from gym.toolbox import Toolbox

print(f"1. Toolbox methods: {[m for m in dir(Toolbox) if not m.startswith('_')]}")

# Try importing physics optics module
print(f"\n2. Importing physics optics tools...")
try:
    import physics.optics.optics_tools_gym as optics
    print(f"   Module loaded: {optics.__file__}")
    print(f"   Module attributes: {[a for a in dir(optics) if not a.startswith('_')][:10]}")
    
    # Check registered tools after import
    try:
        tool = Toolbox.get_tool("calculate_thin_film_interference")
        print(f"   Tool found after import: {tool.name}")
    except Exception as e:
        print(f"   Tool not found after import: {e}")
        
except Exception as e:
    print(f"   Import failed: {e}")

# Check what's in the optics module
print(f"\n3. Checking optics module contents...")
optics_path = r"C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src\toolkits\physics\optics\optics_tools_gym.py"
with open(optics_path, 'r', encoding='utf-8') as f:
    content = f.read()
    
# Find tool registrations
import re
registrations = re.findall(r'@Toolbox\.register.*?class\s+(\w+)', content, re.DOTALL)
print(f"   Registered classes: {registrations}")

# Find tool names
tool_names = re.findall(r'name\s*=\s*["\'](\w+)["\']', content)
print(f"   Tool names: {tool_names[:5]}")

print(f"\n=== Done ===")
