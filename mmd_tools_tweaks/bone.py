import bpy
from collections.abc import Iterator


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


def reindex_bone_ids():
    """ボーン階層に基づいてボーンID（通し番号）を付与する"""
    i = 0
    for bone, depth in traverse_bones():
        mmd_bone = bpy.context.object.pose.bones[bone.name].mmd_bone
        mmd_bone.bone_id = i
        print(f"ID={mmd_bone.bone_id} {bone.name}")
        i += 1
