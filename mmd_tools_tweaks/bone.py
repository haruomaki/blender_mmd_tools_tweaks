import bpy


def traverse_bones(armature):
    """ボーンを深さ優先で走査し、(ボーン, 深さ)のジェネレータを返す"""
    root_bones = [b for b in armature.bones if b.parent is None]
    stack = [(root, 0) for root in reversed(root_bones)]

    while stack:
        bone, depth = stack.pop()
        yield bone, depth
        for child in reversed(bone.children):
            stack.append((child, depth + 1))


def print_bones():
    """アクティブなアーマチュアのボーン階層をコンソールに表示"""
    obj = bpy.context.active_object
    if not obj and obj.type != "ARMATURE":
        print("[show_bones] アーマチュアを選択してください")

    for bone, depth in traverse_bones(obj.data):
        print(f"{'  ' * depth}{bone.name}")
