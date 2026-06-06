import bpy


def shape_key_info():
    """
    現在選択中のシェイプキーについて以下を表示する。

    - シェイプキー名
    - インデックス
    - 現在値
    - 変形している頂点数
    - 変形していない頂点数

    判定は Basis(ベース)との差分距離で行う。
    """

    # ------------------------------------------------------------------
    # アクティブオブジェクト取得
    # ------------------------------------------------------------------
    obj = bpy.context.active_object

    if obj is None:
        print("アクティブなオブジェクトがありません。")
        return

    if obj.type != "MESH":
        print("アクティブオブジェクトはメッシュではありません。")
        return

    # ------------------------------------------------------------------
    # シェイプキー取得
    # ------------------------------------------------------------------
    shape_keys = obj.data.shape_keys

    if shape_keys is None:
        print("このオブジェクトにはシェイプキーがありません。")
        return

    # ------------------------------------------------------------------
    # 選択中シェイプキー取得
    # ------------------------------------------------------------------
    active_index = obj.active_shape_key_index
    active_key = shape_keys.key_blocks[active_index]

    print(f"==== {active_index}番目のシェイプキー ====")
    print("名前          :", active_key.name)
    print("値            :", active_key.value)

    # Basisキー取得
    # 日本語環境では「ベース」になっていることもあるが、
    # Blender内部的には通常先頭がBasisなのでそれを利用する。
    basis_key = shape_keys.key_blocks[0]

    # ------------------------------------------------------------------
    # 頂点変化量を集計
    # ------------------------------------------------------------------
    eps = 1e-6  # 1μm

    moved = []
    not_moved = []

    for i, (basis_vert, key_vert) in enumerate(
        zip(basis_key.data, active_key.data)
    ):
        distance = (key_vert.co - basis_vert.co).length

        if distance > eps:
            moved.append(i)
        else:
            not_moved.append(i)

    # ------------------------------------------------------------------
    # 結果表示
    # ------------------------------------------------------------------
    print(f"総頂点数      : {len(active_key.data)}")
    print(f"移動する頂点数: {len(moved)}")
