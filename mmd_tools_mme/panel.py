import bpy
from bpy.types import Panel


class MME_PT_material_panel(Panel):
    bl_label = "MME"
    bl_idname = "MME_PT_material_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        mat = context.material

        if not mat:
            layout.label(text="No Material")
            return

        mme = mat.mme
        layout.prop(mme, "effect_path")


def register():
    bpy.utils.register_class(MME_PT_material_panel)


def unregister():
    bpy.utils.unregister_class(MME_PT_material_panel)
