bl_info = {
    "name": "MMD Tools Tweaks 🔨",
    "author": "Haruomaki",
    "version": (0, 0, 1),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > MyTab",
    "category": "Object",
}


import builtins
import mmd_tools_tweaks.tw


def register():
    # インタラクティブコンソールの名前空間に追加
    builtins.tw = mmd_tools_tweaks.tw  # type: ignore


def unregister():
    if hasattr(builtins, "tw"):
        del builtins.tw  # type: ignore
