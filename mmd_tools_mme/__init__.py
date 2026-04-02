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


def read_json():
    import os
    import json

    # 1. 現在の.blendファイルのディレクトリパスを取得
    # bpy.path.abspath("//") は現在保存されているファイルの場所を絶対パスで返します
    blend_dir = bpy.path.abspath("//")

    # 2. jsonファイルのフルパスを作成
    json_path = os.path.join(blend_dir, "mme.json")

    # 3. ファイルが存在するか確認して読み込む
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # print("JSONの読み込みに成功しました:", data)
        return dict(data)
    else:
        print("ファイルが見つかりません:", json_path)


def dump_effects(n=None):
    role_map = read_json()
    char = "◯" if n is None else str(n)
    for i, m in enumerate(traverse_materials()):
        role = m.mme.role
        path = role_map.get(role, "none")
        print(f"Pmd{char}[{i}] = {path}")


def register():
    properties.register()
    panel.register()
    builtins.mme = type("mme", (), {})()
    builtins.mme.trav = traverse_materials
    builtins.mme.read_json = read_json
    builtins.mme.dump = dump_effects


def unregister():
    del builtins.mme
    panel.unregister()
    properties.unregister()
