import bpy


def hello():
    print("こんにちは！")


# def good_evening():
#     print("こんばんは！")


# def nice():
#     print("いいね！")


# def modest():
#     print("そこそこですね")


# def higher():
#     print("さらなる高みへ")


# def mikan():
#     print("ミカンおいしい")


def darkness():
    print("闇の魔力")


def shape_key_info():
    # アクティブなオブジェクトを取得
    obj = bpy.context.active_object

    # アクティブなオブジェクトがメッシュであるか確認
    if obj and obj.type == "MESH":
        # メッシュのシェイプキーを取得
        shape_keys = obj.data.shape_keys
        if shape_keys:
            # 選択中のシェイプキーの情報を取得
            selected_shape_key = shape_keys.key_blocks[obj.active_shape_key_index]
            print("選択中のシェイプキー名:", selected_shape_key.name)
            print("選択中のシェイプキーのインデックス:", obj.active_shape_key_index)
            print("選択中のシェイプキーの値:", selected_shape_key.value)
        else:
            print("このオブジェクトにはシェイプキーがありません。")
    else:
        print("アクティブなオブジェクトがありませんまたはメッシュではありません。")


# https://blender.stackexchange.com/a/16528
def remove_empty_vertex_groups(obj):
    """空の頂点グループを検知して削除する"""
    """FIXME: ミラーモディファイアを利用している際、.Lや.Rのボーンが消えてしまう"""
    TOLERANCE = 0.001
    max_weights = {i.index: 0 for i in obj.vertex_groups}

    # 各頂点グループについて、ウェイトの最大値を求める
    for vertex in obj.data.vertices:
        for group in vertex.groups:
            group_index = group.group
            weight = obj.vertex_groups[group_index].weight(vertex.index)
            if weight > max_weights.get(group_index, 0):
                max_weights[group_index] = weight

    # ウェイトの最大値をインデックス降順にソート（インデックスの大きい順に削除していかないと途中でインデックスが変わってしまう）
    sorted_max_weights = dict(sorted(max_weights.items(), reverse=True))

    # ウェイトの最大値がほぼ0ならば頂点グループを削除
    for group_index, max_weight in sorted_max_weights.items():
        if max_weight < TOLERANCE:
            print(f'頂点グループ削除: "{obj.vertex_groups[group_index].name}"')
            obj.vertex_groups.remove(obj.vertex_groups[group_index])


# https://blender.stackexchange.com/a/237611
def remove_empty_shape_keys(obj):
    """空のシェイプキーを検知して削除する"""
    import numpy as np

    TOLERANCE = 0.001

    if (
        obj.type != "MESH"
        or not obj.data.shape_keys
        or not obj.data.shape_keys.use_relative
    ):
        return

    n_verts = len(obj.data.vertices)
    cache = {}  # Cache locs for rel keys since many keys have the same rel key

    locs = np.empty(3 * n_verts, dtype=np.float32)

    for key_block in obj.data.shape_keys.key_blocks:
        if key_block == key_block.relative_key:
            continue

        key_block.data.foreach_get("co", locs)

        if key_block.relative_key.name not in cache:
            rel_locs = np.empty(3 * n_verts, dtype=np.float32)
            key_block.relative_key.data.foreach_get("co", rel_locs)
            cache[key_block.relative_key.name] = rel_locs
        rel_locs = cache[key_block.relative_key.name]

        locs -= rel_locs

        # 全ての頂点がほぼ動いていないならシェイプキーを削除
        if (np.abs(locs) < TOLERANCE).all():
            delete_name = key_block.name
            print("シェイプキー削除: ", delete_name)
            obj.shape_key_remove(obj.data.shape_keys.key_blocks[delete_name])


def clean():
    """選択中のすべてのオブジェクトに対して、無駄な頂点グループとシェイプキーを削除する"""
    for obj in bpy.context.selected_objects:
        print("選択中オブジェクト:", obj.name)
        remove_empty_vertex_groups(obj)
        remove_empty_shape_keys(obj)


def merge_vertex_groups():
    """非ロック中の全ての頂点グループを選択中の頂点グループに加算マージする"""

    # 選択中の頂点グループを取得
    obj = bpy.context.active_object
    target_group = obj.vertex_groups.active
    print("マージ先:", target_group.name)

    # 非ロック中のすべての頂点グループを取得
    non_locked_groups = [
        group
        for group in obj.vertex_groups
        if not group.lock_weight and group != target_group
    ]

    # # 各グループの重みをマージ先に加算したのち削除
    for group in non_locked_groups:
        print(f'頂点グループ "{group.name}" をマージ')
        for vertex in obj.data.vertices:
            group_list = [group.group for group in vertex.groups]
            if group.index in group_list:
                weight = group.weight(vertex.index)
                target_group.add([vertex.index], weight, "ADD")
        obj.vertex_groups.remove(group)


# https://blender.stackexchange.com/a/280033
def select_one_side_axis_verts(axis="x", positive=False, tolerance=0.000001):
    """x軸が負であるすべての頂点を選択する"""
    obj = bpy.context.active_object

    # 選択状態を初期化
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")

    # スクリプト内で頂点選択をするためにオブジェクトモードにする必要がある
    bpy.ops.object.mode_set(mode="OBJECT")

    match axis:
        case "x" | "X":
            axis_index = 0
        case "y" | "Y":
            axis_index = 1
        case "z" | "Z":
            axis_index = 2
        case _:
            axis_index = 0

    # selecting the vertices
    for v in obj.data.vertices:
        if (
            positive
            and (v.co[axis_index] > tolerance)
            or not positive
            and (v.co[axis_index] < -tolerance)
        ):
            v.select = True

    bpy.ops.object.mode_set(mode="EDIT")


def scale_bone(scale_factor):
    """編集モードにて、選択中のボーンの長さを変更する"""

    # 選択されたボーンを取得
    bone = bpy.context.active_bone

    # ボーンの現在の長さを取得
    current_length = bone.length

    # テールの位置を計算
    tail_vec = bone.tail - bone.head
    new_tail = bone.head + (tail_vec * scale_factor)

    # テールの位置を更新
    bone.tail = new_tail

    # 長さを確認
    new_length = bone.length
    print(f"ボーン: {bone.name}, 長さ: {current_length:.3f} → {new_length:.3f}")
