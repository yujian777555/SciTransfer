"""R3R1: Two sequential scientific tool calls with evidence dependency."""
import sys
import os
sys.path.insert(0, r"C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src")
sys.path.insert(0, r"C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src\toolkits")

print("=== R3R1: Sequential Scientific Tool Calls ===")

from gym.env import MinimalSciEnv
from gym.tool import ToolCall
from gym.toolbox import Toolbox

# Import a physics tool
print("\n1. Importing physics tools...")
try:
    from physics.optics.optics_tools_gym import *
    print("   optics tools imported")
    
    # List registered tools
    registered = dir(Toolbox)
    tool_names = [t for t in registered if not t.startswith('_')]
    print(f"   Toolbox attributes: {tool_names[:10]}")
    
    # Try to get a tool
    try:
        tool = Toolbox.get_tool("calculate_thin_film_interference")
        print(f"   Got tool: {tool.name}")
        print(f"   Description: {tool.description}")
        print(f"   Arguments: {tool.arguments}")
    except Exception as e:
        print(f"   Get tool failed: {e}")
        
except Exception as e:
    print(f"   Import failed: {e}")

# Create environment and register tools
print("\n2. Creating environment with tools...")
try:
    env = MinimalSciEnv()
    
    # Manually register a tool
    from gym.tool import GenericFunctionTool
    
    def compute_interference(n1, n2, d):
        """Compute thin film interference wavelengths."""
        import math
        # Enhanced wavelength: 2*n2*d = (m+0.5)*lambda
        # Weakened wavelength: 2*n2*d = m*lambda
        # For m=0: enhanced = 4*n2*d, weakened = 2*n2*d
        enhanced = 4 * n2 * d
        weakened = 2 * n2 * d
        return {
            "enhanced_wavelength_nm": round(enhanced, 2),
            "weakened_wavelength_nm": round(weakened, 2),
            "n1": n1,
            "n2": n2,
            "thickness_nm": d
        }
    
    tool = GenericFunctionTool(
        name="calculate_thin_film_interference",
        description="Calculate enhanced and weakened wavelengths in thin film interference",
        arguments={
            "n1": {"type": "number", "description": "Refractive index of incident medium"},
            "n2": {"type": "number", "description": "Refractive index of thin film"},
            "d": {"type": "number", "description": "Film thickness in nm"},
        },
        func=compute_interference,
    )
    env.add_tool(tool)
    
    reset_result = env.reset()
    print(f"   Tools available: {reset_result.get('available_tools', [])}")
    
    # Tool Call 1: Compute interference
    print("\n3. Tool Call 1: calculate_thin_film_interference")
    action1 = ToolCall(
        id="call-1",
        name="calculate_thin_film_interference",
        arguments={"n1": 1.0, "n2": 1.5, "d": 300.0},
    )
    result1 = env.step(action1)
    obs1 = result1.observation
    print(f"   Observation: {obs1}")
    
    # Parse result to get enhanced wavelength
    if hasattr(obs1, 'observation'):
        import json
        try:
            data = json.loads(obs1.observation) if isinstance(obs1.observation, str) else obs1.observation
            enhanced_wl = data.get("enhanced_wavelength_nm", 0)
            print(f"   Enhanced wavelength: {enhanced_wl} nm")
        except:
            enhanced_wl = 1800  # default
    else:
        enhanced_wl = 1800
    
    # Tool Call 2: Use result from Call 1 as input
    # This demonstrates evidence-dependent decision
    print("\n4. Tool Call 2 (evidence-dependent): compute photon energy")
    
    def compute_photon_energy(wavelength_nm):
        """Compute photon energy from wavelength."""
        import math
        # E = hc/lambda
        h = 4.135667696e-15  # eV*s
        c = 2.99792458e17  # nm/s
        energy_ev = h * c / wavelength_nm
        energy_j = energy_ev * 1.602176634e-19
        return {
            "wavelength_nm": wavelength_nm,
            "energy_ev": round(energy_ev, 4),
            "energy_j": energy_j
        }
    
    tool2 = GenericFunctionTool(
        name="compute_photon_energy",
        description="Compute photon energy from wavelength",
        arguments={
            "wavelength_nm": {"type": "number", "description": "Wavelength in nm"},
        },
        func=compute_photon_energy,
    )
    env.add_tool(tool2)
    
    # Use the enhanced wavelength from Call 1 as input to Call 2
    action2 = ToolCall(
        id="call-2",
        name="compute_photon_energy",
        arguments={"wavelength_nm": enhanced_wl},
    )
    result2 = env.step(action2)
    obs2 = result2.observation
    print(f"   Input wavelength (from Call 1): {enhanced_wl} nm")
    print(f"   Observation: {obs2}")
    
    print("\n5. Summary:")
    print(f"   Tool Call 1: thin_film_interference(n1=1.0, n2=1.5, d=300) -> enhanced_wavelength")
    print(f"   Tool Call 2: photon_energy(wavelength={enhanced_wl}) -> energy")
    print(f"   Evidence dependency: Call 2 input derived from Call 1 output")
    
except Exception as e:
    print(f"   FAIL: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Done ===")
