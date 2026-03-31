import bpy
from bpy.props import StringProperty, PointerProperty
from bpy.types import PropertyGroup


class MMEProperties(PropertyGroup):
    role: StringProperty(
        name="Role",
        description="Shader role (e.g. hair, skin)",
    )  # type: ignore


def register():
    bpy.utils.register_class(MMEProperties)
    bpy.types.Material.mme = PointerProperty(type=MMEProperties)


def unregister():
    del bpy.types.Material.mme
    bpy.utils.unregister_class(MMEProperties)
