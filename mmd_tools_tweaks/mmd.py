import bpy


def get_mmd_root() -> bpy.types.Object | None:
    """選択したオブジェクトが含まれるMMD物体のルートを返す"""
    obj = bpy.context.active_object
    while obj != None:
        if obj.mmd_type == "ROOT":
            return obj
        obj = obj.parent
    return None


def rename_mesh():
    """現在選択中のMMD物体について、オブジェクト名に合わせてメッシュデータ名を変更する"""
    # TODO: とりあえずアーマチュア配下だけ。rigidbodyのリネームも今後考える
    root = get_mmd_root()

    # 剛体&ジョイント以外のオブジェクトのみ対象
    armature = None
    for child in root.children:
        if child.mmd_type != "RIGID_GRP_OBJ" and child.mmd_type != "JOINT_GRP_OBJ":
            armature = child

    for obj in armature.children_recursive:
        if obj.type == "MESH":
            old_name = obj.data.name
            new_name = obj.name
            if old_name == new_name:
                print(f"既に名称は揃っています: {new_name}")
            else:
                obj.data.name = new_name
                print(f"メッシュデータの名称を変更しました: {old_name} → {new_name}")


def rename_material():
    """すべてのMMD物体について、マテリアル名に合わせてMMDマテリアル名を変更する"""

    for m in bpy.data.materials:
        old_name = m.mmd_material.name_j
        new_name = m.name
        if old_name == new_name:
            print(f"既に名称は揃っています: {new_name}")
        else:
            m.mmd_material.name_j = new_name
            print(f"マテリアルの名称を変更しました: {old_name} → {new_name}")
