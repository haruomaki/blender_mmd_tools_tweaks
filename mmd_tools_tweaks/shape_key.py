import bpy
from contextlib import contextmanager


@contextmanager
def temp_object_mode():
    """編集モードのとき、一時的にオブジェクトモードに切り替えるコンテクストマネージャ"""
    current_mode = bpy.context.mode
    try:
        if current_mode == "EDIT_MESH":
            bpy.ops.object.mode_set(mode="OBJECT")
        yield
    finally:
        if current_mode == "EDIT_MESH":
            bpy.ops.object.mode_set(mode="EDIT")


# FIXME: これ何に使うの？
@contextmanager
def preserve_selection():
    """選択状態を保存して復元するコンテクストマネージャ"""
    obj = bpy.context.active_object
    if obj and obj.type == "MESH" and bpy.context.mode == "EDIT_MESH":
        # 現在の選択状態を保存
        selected_indices = [v.index for v in obj.data.vertices if v.select]
        yield
        # 選択状態を復元
        bpy.ops.object.mode_set(mode="OBJECT")
        for v in obj.data.vertices:
            v.select = v.index in selected_indices
        bpy.ops.object.mode_set(mode="EDIT")
    else:
        yield


def require_shapekey() -> tuple[bpy.types.Object, bpy.types.Key]:
    """アクティブなシェイプキーを検証して返す。ダメなら処理を中断する"""
    obj = bpy.context.active_object
    if obj is None:
        raise RuntimeError("アクティブなオブジェクトがありません。")

    if obj.type != "MESH":
        raise RuntimeError("アクティブオブジェクトはメッシュではありません。")

    if not hasattr(obj.data, "shape_keys") or not obj.data.shape_keys:
        raise RuntimeError("シェイプキーが見つかりません。")

    active_key = obj.active_shape_key
    if not active_key:
        raise RuntimeError("アクティブなシェイプキーがありません。")

    return obj, active_key


def shape_key_info():
    """
    現在選択中のシェイプキーについて以下を表示する。

    - シェイプキー名
    - インデックス
    - 現在値
    - 変形している頂点数
    - 変形していない頂点数

    判定はリファレンスシェイプキーとの差分距離で行う。
    """

    # ------------------------------------------------------------------
    # アクティブオブジェクト・シェイプキー取得
    # ------------------------------------------------------------------
    obj, active_key = require_shapekey()
    shape_keys = obj.data.shape_keys
    active_index = obj.active_shape_key_index

    print(f"==== {active_index}番目のシェイプキー ====")
    print("名前          :", active_key.name)
    print("値            :", active_key.value)

    # リファレンスキー取得
    ref_key = shape_keys.reference_key

    # ------------------------------------------------------------------
    # 頂点変化量を集計
    # ------------------------------------------------------------------
    eps = 1e-6  # 1μm

    moved = []
    not_moved = []

    for i, (ref_vert, key_vert) in enumerate(zip(ref_key.data, active_key.data)):
        distance = (key_vert.co - ref_vert.co).length

        if distance > eps:
            moved.append(i)
        else:
            not_moved.append(i)

    # ------------------------------------------------------------------
    # 結果表示
    # ------------------------------------------------------------------
    print(f"総頂点数      : {len(active_key.data)}")
    print(f"移動する頂点数: {len(moved)}")


def select_vertices_moved_from_axis(axis="x", tolerance=0.000001):
    """
    ベースシェイプでは軸上(例: |x| < tolerance)にあったが、
    指定シェイプキーでは軸上から外れてしまった頂点を選択する。

    あるいは、ベースシェイプでは軸上から外れていたが、
    指定シェイプキーでは軸上へと動いた頂点も選択する。

    Args:
        shapekey_name: チェックするシェイプキー名（空文字ならアクティブなシェイプキー）※廃止中
        axis: チェックする軸 ("x", "y", "z")
        tolerance: 軸上とみなす許容範囲
    """
    obj, target = require_shapekey()
    print(f"アクティブなシェイプキー: {target.name}")

    # ベースシェイプ（相対キーの基準）
    basis = obj.data.shape_keys.reference_key

    axis_map = {"x": 0, "X": 0, "y": 1, "Y": 1, "z": 2, "Z": 2}
    axis_idx = axis_map.get(axis, 0)

    # 選択をリセット
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode="OBJECT")

    moved_vertices = []

    for i, v in enumerate(obj.data.vertices):
        # ベースシェイプでの座標
        base_co = basis.data[i].co
        # ターゲットシェイプキーでの座標（相対値ではなく絶対値）
        target_co = target.data[i].co

        # 軸上にあるか？
        on_axis_in_base = abs(base_co[axis_idx]) <= tolerance
        on_axis_in_target = abs(target_co[axis_idx]) <= tolerance

        # X=0 → X≠0 もしくは X≠0 → X=0 を両方検出
        if on_axis_in_base != on_axis_in_target:
            v.select = True
            moved_vertices.append(
                {
                    "index": i,
                    "base_pos": base_co[axis_idx],
                    "target_pos": target_co[axis_idx],
                    "delta": target_co[axis_idx] - base_co[axis_idx],
                }
            )

    bpy.ops.object.mode_set(mode="EDIT")

    # 結果を表示
    print(f"\n=== 検出結果 ===")
    print(f"シェイプキー: {target.name}")
    print(f"軸: {axis.upper()} (tolerance={tolerance})")
    print(f"該当頂点数: {len(moved_vertices)}")

    if moved_vertices:
        print("\n詳細（最初の10個）:")
        for mv in moved_vertices[:10]:
            print(
                f"  頂点{mv['index']}: ベース={mv['base_pos']:.8f} → ターゲット={mv['target_pos']:.8f} (移動量={mv['delta']:.8f})"
            )

    return moved_vertices


def vertex_info():
    """現在アクティブなシェイプキーの選択頂点の座標を表示"""
    obj, active_key = require_shapekey()

    with temp_object_mode():
        vs = [v.index for v in obj.data.vertices if v.select]

    if not vs:
        print("選択された頂点がありません")
        return

    print(f"=== シェイプキー '{active_key.name}' の選択頂点 ===")
    for v in vs:
        co = active_key.data[v].co
        print(f"index={v}: ({co.x:.20f} {co.y:.20f} {co.z:.20f})")


def set_selected_vertices_axis_to_value(axis="x", value=0.0):
    """選択された頂点の指定された軸の座標を任意の値に設定する（アクティブなシェイプキーに対して）"""
    obj, active_key = require_shapekey()

    axis_map = {"x": 0, "y": 1, "z": 2}
    axis_idx = axis_map.get(axis.lower())
    if axis_idx is None:
        print(f"無効な軸です: {axis}")
        return

    with temp_object_mode():
        selected_indices = [v.index for v in obj.data.vertices if v.select]

        if not selected_indices:
            print("選択された頂点がありません")
            return

        # アクティブなシェイプキーの頂点データを変更
        for idx in selected_indices:
            co = active_key.data[idx].co
            if axis_idx == 0:
                co.x = value
            elif axis_idx == 1:
                co.y = value
            else:
                co.z = value

        obj.data.update_tag()

    print(
        f"シェイプキー '{active_key.name}' の{len(selected_indices)}個の頂点の{axis.upper()}座標を{value}に設定しました"
    )
