from assgenutils import *
from genericgenetic import *

import io
import numpy as np

import bgl
import blf

class CrystalGenetic(GenericGenetic):
    """Représente un individu de cristal avec son génotype"""

    min_subcrystals = 1
    max_subcrystals = 4

    min_cuts = 0
    max_cuts = 50

    def __init__(self, parent=None):
        GenericGenetic.__init__(self, parent)

    def random_genotype(self):
        """génère un génotype random. Composition du génotype d'un crystal :
           [subcrytals (1-4):
                Cuts: [Cuts (0 - 50):
                    (phi, theta, r)
                ]
                Scale : (x, y, z)
                Orientation : (phi, theta)
                Offset : (w)
           ]
           """
        return [self.random_subcrystal_genotype() for a in range(self.min_subcrystals,
                                                                 random.randint(self.min_subcrystals,
                                                                                self.max_subcrystals) + 1)]

    def random_subcrystal_genotype(self):
        return {
            'cuts': [self.random_cut_genotype() for b in range(self.min_cuts,
                                                               random.randint(self.min_cuts,
                                                                              self.max_cuts) + 1)],
            'scale': self.random_scale_genotype(),
            'orientation': self.random_orientation_genotype(),
            'offset': self.random_offset_genotype()
        }

    def random_cut_genotype(self):
        return (
            random.random() * 2 * math.pi,
            random.random() * 2 * math.pi,
            random.uniform(0.5, 0.9)
        )

    def random_scale_genotype(self):
        return (
            random.uniform(0.5, 1),
            random.uniform(0.5, 1),
            random.uniform(1, 3)
        )

    def random_orientation_genotype(self):
        return (
            random.uniform(0, math.pi * 2),
            random.uniform(0, math.pi / 2),  # ici c'est seulement un quart de cercle
        )

    def random_offset_genotype(self):
        return random.uniform(-2, 0)  # c'est en gros l'enfoncement du crystal dans le sol (donc négatif)

    def genotype_as_string(self):
        buf = io.StringIO()
        buf.write("- Begin genotype (" + str(len(self.genotype)) + " subcrystals) -\n")
        for idx, subcrystal in enumerate(self.genotype):
            buf.write("#" + str(idx) + ": {\n\tcuts: [\n")
            for cut in subcrystal['cuts']:
                buf.write("\t\t" + str(cut[0]) + " " + str(cut[1]) + " " + str(cut[2]) + "\n")
            buf.write("\t]\n\tscale: "
                      + str(subcrystal['scale'][0]) + " "
                      + str(subcrystal['scale'][1]) + " "
                      + str(subcrystal['scale'][2])
                      + "\n")
            buf.write("\torientation: "
                      + str(subcrystal['orientation'][0]) + " "
                      + str(subcrystal['orientation'][1]) + "\n")
            buf.write("\toffset: " + str(subcrystal['offset']) + "\n")
            buf.write("}\n")
        buf.write("- End genotype -")

        ret = buf.getvalue()
        buf.close()
        return ret

    def compute_individual(self, location):
        """Génère un cristal"""

        bpy.context.scene.cursor_location = [0, 0, 0]

        if self.generated is not None:  # on supprime les anciens subcrystals s'il y en avait
            bpydeselect()
            for child in bpy.data.objects[self.generated].children:
                child.select = True
            bpy.ops.object.delete()
            bpy.data.objects[self.generated].select = True
        else:  # ou on créée un nouveau container s'il n'y en a pas
            bpy.ops.object.add(type='EMPTY')
            bpy.context.object.name = "Crystal" + str(GenericGenetic.bobject_unique_id())
            self.generated = bpy.context.object.name

        parent_obj = bpy.data.objects[self.generated]

        for idx, subcrystal in enumerate(self.genotype):

            # Etape 1 : on crée l'icosphere
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,
                                                  size=1,
                                                  view_align=False,
                                                  location=(0, 0, 0),
                                                  enter_editmode=False)
            bpy.context.object.parent = parent_obj
            bpy.context.object.name = "Sub" + parent_obj.name + "-" + str(idx)
            object_center = list(bpy.context.object.location)
            object_ref = bpy.context.object

            # Etape 2 : on cutte
            for cut in subcrystal['cuts']:
                plane_co = spherical_to_xyz(cut[0], cut[1], cut[2])  # point sur le plan de coupe
                plane_no = np.subtract(plane_co, object_center)  # normale du plan de coupe (pointe vers l'extérieur)
                plane_no_magnitude = math.sqrt((plane_no ** 2).sum())
                plane_no /= plane_no_magnitude
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.bisect(plane_co=plane_co,
                                    plane_no=plane_no,
                                    use_fill=True, clear_inner=False, clear_outer=True,
                                    xstart=-100, xend=100,
                                    ystart=-100, yend=100)
                bpy.ops.object.mode_set(mode='OBJECT')

            # Etape 3 : on scale l'objet
            object_ref.scale = (
                subcrystal['scale'][0],
                subcrystal['scale'][1],
                subcrystal['scale'][2]
            )

            # Etape 4 : on tourne et on positionne
            bpy.context.object.rotation_euler[0] = subcrystal['orientation'][1]
            bpy.context.object.rotation_euler[2] = subcrystal['orientation'][0]
            object_ref.location = (
                (subcrystal['scale'][2] + subcrystal['offset']) * math.sin(subcrystal['orientation'][0]) * math.sin(subcrystal['orientation'][1]),
                (subcrystal['scale'][2] + subcrystal['offset']) * -math.cos(subcrystal['orientation'][0]) * math.sin(subcrystal['orientation'][1]),
                (subcrystal['scale'][2] + subcrystal['offset']) * math.cos(subcrystal['orientation'][1])
            )

    def mutate_genotype(self):
        """Création d'une mutation : va au hasard modifier un des attributs. Possibilités :
        - Ajouter un sous-crystal
        - Supprimer un sous-crystal
        - Ajouter un cut
        - Retirer un cut
        - Modifier un cut
        - Modifier un scale
        - Modifier une orientation
        - Modifier un offset
        """
        done = False  # Evitons les mutations illégales et retentons s'il y a une erreur
        while not done:
            randomid = random.randint(0, 7)
            if randomid == 0:  # Ajouter un sous-crystal
                if len(self.genotype) < self.max_subcrystals:
                    self.genotype.append(self.random_subcrystal_genotype())
                    done = True
            elif randomid == 1:  # Supprimer un sous-crystal
                if len(self.genotype) > self.min_subcrystals:
                    self.genotype.pop(random.randint(0, len(self.genotype) - 1))
                    done = True
            elif randomid == 2:  # Ajouter un cut
                sc = self.random_subcrystal()
                if len(sc['cuts']) < self.max_cuts:
                    sc['cuts'].append(self.random_cut_genotype())
                    done = True
            elif randomid == 3:  # Retirer un cut
                sc = self.random_subcrystal()
                if len(sc['cuts']) > self.min_cuts:
                    sc['cuts'].pop(random.randint(0, len(sc['cuts']) - 1))
                    done = True
            elif randomid == 4:  # Modifier un cut
                sc = self.random_subcrystal()
                if len(sc['cuts']) > 0:
                    sc['cuts'][random.randint(0, len(sc['cuts']) - 1)] = self.random_cut_genotype()
                    done = True
            elif randomid == 5:  # Modifier un scale
                sc = self.random_subcrystal()
                sc['scale'] = self.random_scale_genotype()
                done = True
            elif randomid == 6:  # Modifier une orientation
                sc = self.random_subcrystal()
                sc['orientation'] = self.random_orientation_genotype()
                done = True
            elif randomid == 7:  # Modifier un offset
                sc = self.random_subcrystal()
                sc['offset'] = self.random_offset_genotype()
                done = True

    def random_subcrystal(self):
        """returns a random subcrystal in genotype (reference, so mutable in place)"""
        return self.genotype[random.randint(0, len(self.genotype) - 1)]

class AssetsGenerator:

    def __init__(self):
        self.ensure_delete_all()

        self.genotypes = []
        self.genotypes.append(CrystalGenetic())
        self.genotypes[0].compute_individual((0, 0, 0))
        print("#################################################")
        print(repr(self.genotypes[0]))

    def ensure_delete_all(self):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,  # l'ajout d'objet sert uniquement à ce que le reste ne
                                              size=1,  # plante pas si la scène est vide au départ.
                                              view_align=False,
                                              location=(0, 0, 0),
                                              enter_editmode=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpydeleteall()


# ======================================================================================================================
# GESTION DU CRYSTAL MUTATE MODAL OPERATOR
# ======================================================================================================================


class CrystalMutateModalOperator(bpy.types.Operator):
    """Move an object with the mouse, example"""
    bl_idname = "object.crystal_mutate_modal_operator"
    bl_label = "Crystal Mutate Modal Operator"

    def __init__(self):
        self.genotype = None

    def modal(self, context, event):

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            print("left mouse pressed")
            self.genotype.mutate_genotype()
            self.genotype.compute_individual((0, 0, 0))
            return {'RUNNING_MODAL'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            print("right mouse or escape pressed")
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        print("invoke modal")
        args = (context,)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_text, args, 'WINDOW', 'POST_PIXEL')
        bpydeleteall()
        self.genotype = CrystalGenetic()
        self.genotype.compute_individual((0, 0, 0))

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def draw_callback_text(self, context):
        font_id = 0  # XXX, need to find out how best to get this.
        # draw some text
        blf.position(font_id, 15, 30, 0)
        blf.size(font_id, 16, 72)
        blf.draw(font_id, "Crystal Mutate Operator. Left click to mutate. Esc or Right click to exit.")

# ======================================================================================================================
# GESTION DU CRYSTAL GENERATE MODAL OPERATOR
# ======================================================================================================================


class CrystalGenerateModalOperator(bpy.types.Operator):
    """Move an object with the mouse, example"""
    bl_idname = "object.crystal_generate_modal_operator"
    bl_label = "Crystal Generate Modal Operator"

    def __init__(self):
        self.genotype = None

    def modal(self, context, event):

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            print("left mouse pressed")
            bpydeleteall()
            self.genotype = CrystalGenetic()
            self.genotype.compute_individual((0, 0, 0))
            return {'RUNNING_MODAL'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            print("right mouse or escape pressed")
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        print("invoke modal")
        args = (context,)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_text, args, 'WINDOW', 'POST_PIXEL')
        bpydeleteall()
        self.genotype = CrystalGenetic()
        self.genotype.compute_individual((0, 0, 0))

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def draw_callback_text(self, context):
        font_id = 0  # XXX, need to find out how best to get this.
        # draw some text
        blf.position(font_id, 15, 30, 0)
        blf.size(font_id, 16, 72)
        blf.draw(font_id, "Crystal Generate Operator. Left click to generate. Esc or Right click to exit.")

# ======================================================================================================================
# REGISTER MODALS
# ======================================================================================================================


def register():
    bpy.utils.register_class(CrystalMutateModalOperator)
    bpy.utils.register_class(CrystalGenerateModalOperator)


def unregister():
    bpy.utils.unregister_class(CrystalMutateModalOperator)
    bpy.utils.unregister_class(CrystalGenerateModalOperator)

if __name__ == "__main__":
    register()

    # test call
    # bpy.ops.object.crystal_mutate_modal_operator('INVOKE_DEFAULT')
    bpy.ops.object.crystal_generate_modal_operator('INVOKE_DEFAULT')

    #unregister()
