"""
mmd_tools_mme/__init__.py
"""

import builtins
import bpy
from . import properties, panel


def get_mmd_root() -> bpy.types.Object | None:
    """選択したオブジェクトが含まれるMMD物体のルートを返す"""
    obj = bpy.context.active_object
    while obj != None:
        if obj.mmd_type == "ROOT":
            return obj
        obj = obj.parent
    return None


def traverse_materials():
    root = get_mmd_root()
    arm = bpy.data.objects[f"{root.name}_arm"]
    mats = set()
    for obj in arm.children:
        for slot in obj.material_slots:
            m = slot.material
            if m not in mats:
                mats.add(m)
                yield m


def dump_effects(n=None):
    char = "◯" if n is None else str(n)
    for i, m in enumerate(traverse_materials()):
        print(f"Pmd{char}[{i}] = {m.mme.effect_path}")


def register():
    properties.register()
    panel.register()
    builtins.mme = type("mme", (), {})()
    builtins.mme.trav = traverse_materials
    builtins.mme.dump = dump_effects


def unregister():
    del builtins.mme
    panel.unregister()
    properties.unregister()
