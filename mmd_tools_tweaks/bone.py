import bpy
from collections.abc import Iterator

from .mmd import get_mmd_root


def traverse_bones() -> Iterator[tuple[bpy.types.Bone, int]]:
    """ボーンを深さ優先で走査し、(ボーン, 深さ)のジェネレータを返す"""
    obj = bpy.context.active_object
    if not obj and obj.type != "ARMATURE":
        print("[traverse_bones] アーマチュアを選択してください")

    armature = obj.data
    root_bones = [b for b in armature.bones if b.parent is None]
    stack = [(root, 0) for root in reversed(root_bones)]

    while stack:
        bone, depth = stack.pop()
        yield bone, depth
        for child in reversed(bone.children):
            stack.append((child, depth + 1))


def print_bones():
    """アクティブなアーマチュアのボーン階層をコンソールに表示"""
    for bone, depth in traverse_bones():
        mmd_bone = bpy.context.object.pose.bones[bone.name].mmd_bone
        print(f"{'  ' * depth}{bone.name} (ID: {mmd_bone.bone_id})")


def map_bone_ids(old_to_new: dict[int, int]):
    """ボーンIDを新たなものに挿げ替える"""
    # ボーン本体と付与親ボーンのIDを変更
    for bone in bpy.context.object.pose.bones:
        mmd_bone = bone.mmd_bone

        # ボーンIDの変更
        old = mmd_bone.bone_id
        mmd_bone.bone_id = old_to_new[old]

        # 付与親ボーンIDの変更
        old = mmd_bone.additional_transform_bone_id
        mmd_bone.additional_transform_bone_id = old_to_new[old]

    # ボーンモーフが参照しているボーンIDを変更
    # for d in tw.get_mmd_root().mmd_root.bone_morphs[0].data: d.id_data
    for morph in get_mmd_root().mmd_root.bone_morphs:
        for data in morph.data:
            old = data.bone_id
            data.bone_id = old_to_new[old]


def reindex_bone_ids():
    """ボーン階層に基づいてボーンID（通し番号）を付与する"""
    old_to_new = {-1: -1}  # ボーンが存在しなかったら写像後もボーン無し
    for i, (bone, depth) in enumerate(traverse_bones()):
        old = bpy.context.object.pose.bones[bone.name].mmd_bone.bone_id
        old_to_new[old] = i
        print(f"{old:3} -> {i:3}  {bone.name}")
    map_bone_ids(old_to_new)
