from assgenutils import *
from genericgenetic import *

import io
import numpy as np

class TreeGenetic(GenericGenetic):
    """Représente un individu de cristal avec son génotype"""

    def __init__(self, parent=None):
        GenericGenetic.__init__(self, parent)
        
    def random_genotype(self):
        theSeed = int(random.uniform(1, 100))
        theLevels = int(random.uniform(4, 6))
        theHight = random.uniform(0, 2.5)
        theBranchesLength = random.uniform(0, 0.5)
        theNbOfLeaves = int(random.uniform(1, 101))

        return {
            'seedG' : theSeed,
            'levelsG' : theLevels,
            'lengthG' : [theHight, theBranchesLength, 0, 0],
            'leavesG' : theNbOfLeaves
        }
        
    def compute_individual(self, location):
        """Génère un arbre"""

        bpy.context.scene.cursor_location = [0, 0, 0]
        
        if self.generated is not None:  # on supprime les anciens subcrystals s'il y en avait
            print("re-compute " + self.generated)
            bpydeselect()
            bpy.ops.object.delete()
            bpy.data.objects[self.generated].select = True
            bpy.context.scene.objects.active = bpy.data.objects[self.generated]
        else:  # ou on créée un nouveau container s'il n'y en a pas
            bpy.ops.object.add(type='EMPTY')
            bpy.context.object.name = "Tree" + '%03d' % GenericGenetic.bobject_unique_id()
            self.generated = bpy.context.object.name
            print("computed " + self.generated)

        #parent_obj = bpy.data.objects[self.generated]
        print(self.genotype)
        bpy.ops.curve.tree_add(bevel = True, showLeaves = True, seed = self.genotype['seedG'], levels = self.genotype['levelsG'], 
             length = self.genotype['lengthG'], leaves = self.genotype['leavesG'])
        #bpy.context.object.parent = parent_obj
        
class AssetsGenerator:

    def __init__(self):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpydeleteall()
        self.genotypes = []
        self.genotypes.append()
        self.genotypes[0].compute_individual((0, 0, 0))
        print("#################################################")
        print(repr(self.genotypes[0]))


if __name__ == "__main__":
    #assgen = AssetsGenerator()
    tree = TreeGenetic()
    tree.compute_individual((0,0,0))
