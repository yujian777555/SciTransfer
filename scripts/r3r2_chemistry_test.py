"""R3R2: Second discipline (chemistry) native tool test."""
import sys
import os
import json
sys.path.insert(0, r"C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src")
sys.path.insert(0, r"C:\Users\于舰\XiaomiMiMoProjects\SciAgentGYM-src\toolkits")

print("=== R3R2: Second Discipline (Chemistry) ===")

# Import chemistry tools
print(f"\n1. Importing chemistry tools...")
try:
    import chemistry.physical_chemistry.physical_chemistry_tools_gym as chem
    print(f"   chemistry module: {chem.__file__}")
    
    # List registered tools
    from gym.toolbox import Toolbox
    from gym.tool import GenericFunctionTool
    
    # Find chemistry tools
    import inspect
    source = inspect.getsource(chem)
    import re
    tool_names = re.findall(r'name\s*=\s*["\'](\w+)["\']', source)
    print(f"   Chemistry tool names: {tool_names[:5]}")
    
    # Get a native chemistry tool
    if tool_names:
        tool_name = tool_names[0]
        tool = Toolbox.get_tool(tool_name)
        print(f"   Tool: {tool.name}")
        print(f"   Type: {type(tool).__name__}")
        print(f"   Module: {type(tool).__module__}")
        assert not isinstance(tool, GenericFunctionTool), "Tool is GenericFunctionTool!"
        print(f"   Native (not GenericFunctionTool): OK")
        
        # Execute the chemistry tool
        print(f"\n2. Executing {tool.name}...")
        from gym.env import MinimalSciEnv
        from gym.tool import ToolCall
        
        env = MinimalSciEnv()
        env.add_tool(tool)
        env.reset()
        
        # Check tool arguments
        print(f"   Arguments: {tool.arguments}")
        
        # Make a simple call
        action = ToolCall(
            id="chem-1",
            name=tool.name,
            arguments={},  # Try empty first to see error
        )
        result = env.step(action)
        obs = result.observation
        print(f"   Result: {str(obs)[:200]}")
        
except Exception as e:
    print(f"   Chemistry: FAIL - {e}")
    import traceback
    traceback.print_exc()

print(f"\n=== Done ===")
