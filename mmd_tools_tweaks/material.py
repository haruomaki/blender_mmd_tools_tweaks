import bpy
import bmesh


def list_opaque_materials():
    obj = bpy.context.active_object
    return [
        m.mmd_material.name_j for m in obj.data.materials if m.mmd_material.alpha < 1
    ]


def select_by_material(material_names: list[str]):
    """指定したマテリアル名リストに一致する面を選択する"""
    obj = bpy.context.active_object

    # 編集モードへ移行
    bpy.ops.object.mode_set(mode="EDIT")

    # BMeshを取得
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)

    # 名前からインデックスをセット化（高速化＆重複排除）
    target_indices = {
        i
        for i, mat in enumerate(obj.data.materials)
        if mat and mat.name in material_names
    }

    if not target_indices:
        print(f"対象マテリアルが存在しません: {material_names}")
        return

    # 面を走査して選択
    for f in bm.faces:
        if f.material_index in target_indices:
            f.select = True

    # BMeshを更新
    bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)


def find_materials_by_image(image_name: str):
    """指定画像を使っているマテリアル名を列挙"""
    obj = bpy.context.active_object

    result = []
    for mat in obj.data.materials:
        if mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image:
                    if node.image.name == image_name:
                        result.append(mat.name)
                        break
    return result
