"""
mmd_tools_mme/__init__.py
"""

import builtins
import bpy
from . import properties, panel

# from . import tw


def register():
    # インタラクティブコンソールの名前空間に追加
    # print("registerです")
    properties.register()
    panel.register()
    # builtins.tw = tw


def unregister():
    # print("unregisterです")
    panel.unregister()
    properties.unregister()
    # if hasattr(builtins, "tw"):
    # del builtins.tw
