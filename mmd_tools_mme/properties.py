import bpy
from bpy.props import StringProperty, PointerProperty
from bpy.types import PropertyGroup


class MMEProperties(PropertyGroup):
    effect_path: StringProperty(
        name="Effect",
        description="Path to .fx file",
        subtype="FILE_PATH",  # ← これがファイル選択UIになる
    )  # type: ignore


def register():
    bpy.utils.register_class(MMEProperties)
    bpy.types.Material.mme = PointerProperty(type=MMEProperties)


def unregister():
    del bpy.types.Material.mme
    bpy.utils.unregister_class(MMEProperties)
