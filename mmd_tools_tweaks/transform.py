import bpy
import bmesh
import math
import mathutils
from mathutils import Vector


def trans_rotation_00x(p: Vector, vec: Vector):
    """点pを原点に、ベクトルvecを(0,0,?)に移す座標変換を表す行列を得る"""
    src = vec
    dst = Vector((0, 0, 1))
    # print(f"p: {p}, vec: {vec}, src: {src}, dst: {dst}")
    θ = src.angle(dst)
    # print(f"角度: {θ / math.pi * 180}°")
    rotation_axis = src.cross(dst)  # TODO: 正規化はいらないかも
    # print("回転軸:", rotation_axis)
    quat = mathutils.Quaternion(rotation_axis, θ)
    rotation_matrix = quat.to_matrix()
    # print("回転行列:", rotation_matrix)

    # 平行移動したあと回転
    rotation_matrix.resize_4x4()
    transform = rotation_matrix @ mathutils.Matrix.Translation(-p)
    # print("最終的な変換行列:", transform)
    return transform


def __spherify_standard(vert: Vector) -> Vector:
    """原点中心、z軸正を法線として球面変換"""
    x, y, z = vert
    θ = math.sqrt(x**2 + y**2) / z
    φ = math.atan2(y, x)
    # print("__bent_standard_oneです:", theta / math.pi * 180, phi / math.pi * 180)
    new_vert = z * Vector(
        (math.sin(θ) * math.cos(φ), math.sin(θ) * math.sin(φ), math.cos(θ))
    )
    return new_vert


def spherify_one(vert: Vector, center=Vector(), normal=Vector((0, 0, 1))) -> Vector:
    """中心(0,0,0)、軸(0,0,1)になるよう座標変換したのち球面変換"""
    transform = trans_rotation_00x(center, normal)
    vertt = transform @ vert
    ret = __spherify_standard(vertt)
    return transform.inverted() @ ret


def spherify(center=Vector(), normal=Vector((0, 0, 1))):
    """編集モードにて、選択中の各頂点に球面変換を施す"""
    obj = bpy.context.active_object
    mesh = obj.data

    # BMeshを作成
    bm = bmesh.from_edit_mesh(mesh)

    # 選択された頂点を取得
    selected_verts = [v for v in bm.verts if v.select]

    # 選択された各頂点を球面変換する
    for vert in selected_verts:
        vert.co = spherify_one(vert.co, center, normal)

    # BMeshを更新
    bmesh.update_edit_mesh(mesh)


def cylindrify(pivot=Vector(), direction=Vector((0, 0, 1)), normal=Vector((1, 0, 0))):
    """編集モードにて、選択中の各頂点に円筒変換を施す
    デフォルトではz軸方向の円筒に巻き付くように、x軸正方向に山ができる"""
    obj = bpy.context.active_object
    mesh = obj.data

    # この平面上にある点は、すべて同じ球中心とともにspherifyされる
    plane_normal = direction.cross(normal).cross(normal)
    # print("plane_normal:", plane_normal)

    p1, p2, p3 = pivot
    d1, d2, d3 = direction
    n1, n2, n3 = plane_normal

    # BMeshを作成
    bm = bmesh.from_edit_mesh(mesh)

    # 選択された頂点を取得
    selected_verts = [v for v in bm.verts if v.select]

    # 選択された各頂点の球中心を求め、球面変換することで円筒状に形成できる
    for vert in selected_verts:
        # l: 点pivotを通り方向ベクトルdirectionを持つ直線
        # S: 点vert.coを通り法線ベクトルnormalを持つ平面
        # lとSの交点が、spherifyの中心となる
        x, y, z = vert.co
        t = (n1 * (x - p1) + n2 * (y - p2) + n3 * (z - p3)) / (
            n1 * d1 + n2 * d2 + n3 * d3
        )
        center = Vector((p1 + t * d1, p2 + t * d2, p3 + t * d3))
        # print(f"center: {center}, normal: {normal}")
        vert.co = spherify_one(vert.co, center, normal)

    # BMeshを更新
    bmesh.update_edit_mesh(mesh)
