import bl_ui
import bpy
from . import ICON_VOLUME


class LuxCoreMaterialHeader(bl_ui.properties_material.MaterialButtonsPanel, bpy.types.Panel):
    """
    Material UI Panel
    """
    COMPAT_ENGINES = "LUXCORE"
    bl_label = ""
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (context.material or context.object) and (engine == "LUXCORE")

    def draw(self, context):
        layout = self.layout

        mat = context.material
        ob = context.object
        slot = context.material_slot
        space = context.space_data

        # Re-create the Blender material UI, but without the surface/wire/volume/halo buttons
        if ob:
            row = layout.row()

            row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=2)

            col = row.column(align=True)
            col.operator("object.material_slot_add", icon="ZOOMIN", text="")
            col.operator("object.material_slot_remove", icon="ZOOMOUT", text="")

            col.menu("MATERIAL_MT_specials", icon="DOWNARROW_HLT", text="")

            if ob.mode == "EDIT":
                row = layout.row(align=True)
                row.operator("object.material_slot_assign", text="Assign")
                row.operator("object.material_slot_select", text="Select")
                row.operator("object.material_slot_deselect", text="Deselect")

        split = layout.split(percentage=0.68)

        if ob:
            # We use our custom new material operator here
            split.template_ID(ob, "active_material", new="luxcore.material_new")

            if slot:
                row = split.row()
                row.prop(slot, "link", text="")
            else:
                row = split.row()
                row.label()
        elif mat:
            split.template_ID(space, "pin_id")
            split.separator()

        if mat:
            # Node tree is attached to object as fallback for now because of Blender bug.
            # This only allows to have one material per object.
            # TODO: waiting for a fix: https://developer.blender.org/T53509
            layout.label("If something does not work, make sure that", icon="ERROR")
            layout.label("both pointers below point to the same node tree")
            layout.separator()
            layout.label("Material Nodes (buggy):")
            layout.template_ID(mat.luxcore, "node_tree", new="luxcore.mat_nodetree_new")
            mat = context.object

            # Material node tree
            layout.label("Material Nodes (workaround):")
            layout.template_ID(mat.luxcore, "node_tree", new="luxcore.mat_nodetree_new")

            # Warning if not the right node tree type
            if mat.luxcore.node_tree and mat.luxcore.node_tree.bl_idname != "luxcore_material_nodes":
                layout.label("Not a material node tree!", icon="ERROR")
