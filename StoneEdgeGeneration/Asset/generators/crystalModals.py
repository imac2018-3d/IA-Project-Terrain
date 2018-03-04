import bpy
from StoneEdgeGeneration import bpyutils
from StoneEdgeGeneration.Asset.generators.crystals import CrystalGenetic
from StoneEdgeGeneration.Asset.genericgenetic import *

import blf
# ======================================================================================================================
# GESTION DU CRYSTAL GENERATE MODAL OPERATOR
# ======================================================================================================================

class CrystalMutateModalOperator(bpy.types.Operator):
    """Move an object with the mouse, example"""
    bl_idname = "object.crystal_mutate_modal_operator"
    bl_label = "Crystal Mutate Modal Operator"

    def __init__(self):
        self.genotype = None

    def modal(self, context, event):

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.genotype.mutate_genotype()
            self.genotype.compute_individual((0, 0, 0))
            return {'RUNNING_MODAL'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        args = (context,)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_text, args, 'WINDOW', 'POST_PIXEL')
        bpyutils.ensure_delete_all()
        self.genotype = CrystalGenetic()
        self.genotype.compute_individual((0, 0, 0))

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def draw_callback_text(self, context):
        font_id = 0  # XXX, need to find out how best to get this.
        # draw some text
        blf.position(font_id, 50, 30, 0)
        blf.size(font_id, 16, 48)
        blf.draw(font_id, "Crystal Mutate Operator. Left click to mutate. Esc or Right click to exit.")

class CrystalGenerateModalOperator(bpy.types.Operator):
    """Move an object with the mouse, example"""
    bl_idname = "object.crystal_generate_modal_operator"
    bl_label = "Crystal Generate Modal Operator"

    def __init__(self):
        self.genotype = None

    def modal(self, context, event):

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            bpyutils.ensure_delete_all()
            self.genotype = CrystalGenetic()
            self.genotype.compute_individual((0, 0, 0))
            return {'RUNNING_MODAL'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        args = (context,)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_text, args, 'WINDOW', 'POST_PIXEL')
        bpyutils.bpydeleteall()
        self.genotype = CrystalGenetic()
        self.genotype.compute_individual((0, 0, 0))

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def draw_callback_text(self, context):
        font_id = 0  # XXX, need to find out how best to get this.
        # draw some text
        blf.position(font_id, 50, 30, 0)
        blf.size(font_id, 16, 48)
        blf.draw(font_id, "Crystal Generate Operator. Left click to generate. Esc or Right click to exit.")


# ======================================================================================================================
# GESTION DU CRYSTAL CROSS MODAL OPERATOR
# ======================================================================================================================


class CrystalCrossModalOperator(bpy.types.Operator):
    """Move an object with the mouse, example"""
    bl_idname = "object.crystal_cross_modal_operator"
    bl_label = "Crystal Cross Modal Operator"

    def __init__(self):
        self.genotype1 = None
        self.genotype2 = None
        self.genotypeChildren = None

    def modal(self, context, event):

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            bpyutils.ensure_delete_all()
            self.genotype1 = CrystalGenetic()
            self.genotype2 = CrystalGenetic()
            self.genotypeChildren = CrystalGenetic.cross_genotypes(self.genotype1.genotype, self.genotype2.genotype)
            self.genotype1.compute_individual((-8, 0, 0))
            self.genotype2.compute_individual((8, 0, 0))
            for i, g in enumerate(self.genotypeChildren):
                g.compute_individual((0, -5 + 5 * i, 0))
            return {'RUNNING_MODAL'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        args = (context,)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_text, args, 'WINDOW', 'POST_PIXEL')
        bpyutils.ensure_delete_all()
        self.genotype1 = CrystalGenetic()
        self.genotype2 = CrystalGenetic()
        self.genotypeChildren = CrystalGenetic.cross_genotypes(self.genotype1.genotype, self.genotype2.genotype)
        self.genotype1.compute_individual((-8, 0, 0))
        self.genotype2.compute_individual((8, 0, 0))
        for i, g in enumerate(self.genotypeChildren):
            g.compute_individual((0, -5 + 5 * i, 0))

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def draw_callback_text(self, context):
        font_id = 0  # XXX, need to find out how best to get this.
        # draw some text
        blf.position(font_id, 50, 30, 0)
        blf.size(font_id, 16, 48)
        blf.draw(font_id, "Crystal Cross Operator. Left click to regen. Esc or Right click to exit.")


# ======================================================================================================================
# GESTION DU CRYSTAL GENERATIONAL MODAL
# ======================================================================================================================


class CrystalGenerationalModalOperator(bpy.types.Operator):
    """Move an object with the mouse, example"""
    bl_idname = "object.crystal_generational_modal_operator"
    bl_label = "Crystal Generational Modal Operator"

    def __init__(self):
        return

    def modal(self, context, event):

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':

            self.generator.next_generation()
            self.generator.genotypes[2].fitness = 0.8
            self.generator.genotypes[4].fitness = 0.8
            self.generator.genotypes[8].fitness = 0.8
            self.generator.genotypes[0].fitness = 0.8
            print("")
            print(repr(self.generator))

            return {'RUNNING_MODAL'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        args = (context,)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_text, args, 'WINDOW', 'POST_PIXEL')
        bpyutils.ensure_delete_all()

        self.generator = AssetGeneticsController(
            genetic_class=CrystalGenetic,
            max_genotypes=9,
            selection_type="number",
            selection_type_param=4,
            show_mode='all'
        )

        self.generator.genotypes[2].fitness = 0.8
        self.generator.genotypes[4].fitness = 0.8
        self.generator.genotypes[8].fitness = 0.8
        self.generator.genotypes[0].fitness = 0.8

        print(repr(self.generator))

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def draw_callback_text(self, context):
        font_id = 0  # XXX, need to find out how best to get this.
        # draw some text
        blf.position(font_id, 50, 30, 0)
        blf.size(font_id, 16, 48)
        blf.draw(font_id, "Crystal Generational Operator. Left click to next generation. Esc or Right click to exit.")

# ======================================================================================================================
# REGISTER MODALS
# ======================================================================================================================


def register():
    bpy.utils.register_class(CrystalMutateModalOperator)
    bpy.utils.register_class(CrystalGenerateModalOperator)
    bpy.utils.register_class(CrystalCrossModalOperator)
    bpy.utils.register_class(CrystalGenerationalModalOperator)


def unregister():
    bpy.utils.unregister_class(CrystalMutateModalOperator)
    bpy.utils.unregister_class(CrystalGenerateModalOperator)
    bpy.utils.unregister_class(CrystalCrossModalOperator)
    bpy.utils.unregister_class(CrystalGenerationalModalOperator)

if __name__ == "__main__":
    register()

    # test call
    # bpy.ops.object.crystal_mutate_modal_operator('INVOKE_DEFAULT')
    # bpy.ops.object.crystal_generate_modal_operator('INVOKE_DEFAULT')
    # bpy.ops.object.crystal_cross_modal_operator('INVOKE_DEFAULT')
    bpy.ops.object.crystal_generational_modal_operator('INVOKE_DEFAULT')

    #unregister()