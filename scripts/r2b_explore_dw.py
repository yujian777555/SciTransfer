"""Explore DiscoveryWorldAPI structure."""
import warnings
warnings.filterwarnings("ignore")

import discoveryworld.DiscoveryWorldAPI as dw
print("Module contents:", dir(dw))

for attr_name in dir(dw):
    attr = getattr(dw, attr_name)
    if isinstance(attr, type):
        methods = [m for m in dir(attr) if not m.startswith("_")]
        print(f"Class: {attr_name}")
        print(f"  methods: {methods}")
