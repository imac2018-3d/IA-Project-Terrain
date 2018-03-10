from StoneEdgeGeneration.Asset.genericgenetic import *
import json
import io
import numpy as np
import copy

id_tree = None

class TreeGenetic(GenericGenetic):
    """Représente l'individu d'un avec son génotype"""

    def __init__(self, parent=None):
        GenericGenetic.__init__(self, parent)

# Genotype generation --------------------------------------------------------------------------------------------------
        
    def random_genotype(self):
        return {
            'seedG' : self.random_seed(),
            'levelsG' : self.random_levels(),
            'lengthG' : self.random_length(),
            'leavesG' : self.random_leaves(),
            'branchSplittingG' : self.random_branchSplitting()
        }

    def random_seed(self):
        return int(random.uniform(1, 100))

    def random_levels(self):
        return int(random.uniform(4, 6))

    def random_length(self):
        return [random.uniform(1, 2.5), random.uniform(0.1, 0.7), random.uniform(0.1, 0.7), random.uniform(0.1, 1)]

    def random_leaves(self):
        return int(random.uniform(40, 101))

    def random_branchSplitting(self):
        return int(random.uniform(0, 6))

# Phenotype generation -------------------------------------------------------------------------------------------------
    
    def process_individual_data(self):
        return json.dumps({"genotype": self.genotype})

    @staticmethod
    def net_compute_individual(location, data):
        return \
            "from StoneEdgeGeneration.Asset.generators.Tree import TreeGenetic\n" \
            "TreeGenetic.compute_individual(("+str(location[0])+","+str(location[1])+","+str(location[0])+"),'" \
            + data + "')"

    @staticmethod
    def camera_position():
        return (-30, -15, 70)

    @staticmethod
    def compute_individual(location, data):
        import bpy
        import StoneEdgeGeneration.bpyutils as bpyutils
        """Génère un arbre"""

        values = json.loads(data)
        genotype = values['genotype']
            
        bpy.ops.curve.tree_add(bevel = True, showLeaves = True, seed = genotype['seedG'], levels = genotype['levelsG'], 
             length = genotype['lengthG'], leaves = genotype['leavesG'], baseSplits = genotype['branchSplittingG'])
        
  
# Genotype cross generation --------------------------------------------------------------------------------------------
    @staticmethod
    def cross_genotype(geno1, geno2):
        """Créée un enfant composé de la moitié des subcristaux de chaque parent"""
        child = {}
        itm1 = list(geno1.items())
        itm2 = list(geno2.items())
        for sc in itm1[:1 + (len(geno2) - 1) // 2]:
            child[sc[0]] = copy.deepcopy(sc[1])
        for sc in itm2[len(geno1) // 2:]:
            child[sc[0]] = copy.deepcopy(sc[1])
        return [child]
    
# Genotype mutation ----------------------------------------------------------------------------------------------------

    def mutate_genotype(self):
        """Création d'une mutation : va au hasard modifier un des attributs. """
        nbAttribs = len(self.genotype)
        attribRandom = int(random.uniform(0, nbAttribs))

        if(attribRandom == 0):
            print("modifions seed")
            self.genotype['seedG'] = self.random_seed()
        elif (attribRandom == 1):
            print("modifions level")
            self.genotype['levelsG'] = self.random_levels()
        elif (attribRandom == 2):
            print("modifions length")
            self.genotype['lengthG'] = self.random_length()
        elif (attribRandom == 3):
            print("modifions le nombre de feuiles")
            self.genotype['leavesG'] = self.random_leaves()
        elif (attribRandom == 4):
            print("modifions le branchSplitting")
            self.genotype['branchSplittingG'] = self.random_branchSplitting()