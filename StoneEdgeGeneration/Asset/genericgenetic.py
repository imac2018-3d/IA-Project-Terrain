import io
import math
import random

class GenericGenetic:
    """Classe abstraite pour gérer les individus"""

    def __init__(self, genotype=None, parent=None):
        """Crée un individu. Son génotype st alors aléatoirement généré, sauf s'il est envoyé en paramètre"""
        self.genotype = self.random_genotype() if genotype is None else genotype  # genotype de l'individu
        self.generated = None  # Nom de l'objet généré. None sinon.
        self.fitness = None  # Valeur de fitness (entre 0 et 1) calculée. None sinon.
        self.parentName = parent  # Nom blender de l'objet parent
        self.age = 0  # Nbr de générations à laquelle le génotype a survécu.

    def random_genotype(self):
        """Doit être redéfinie. Génère un génotype aléatoirement"""
        return None

    def compute_fitness(self):
        """Doit être redéfinie. Calcule et retourne la valeur de fitness (entre 0 et 1)"""
        return None

    def compute_individual(self, location):
        """Doit être redéfinie si un object 3D représente l'individu.
           Calcule le phénotype (l'individu). Doit retourner le nom de l'objet 3D"""
        return None

    def mutate_genotype(self):
        """Doit être redéfinie. Créée une mutation dans le génotype aléatoirement."""
        return

    @staticmethod
    def cross_genotypes(geno1, geno2):
        """Doit être redéfinie. Prend deux génotypes en paramètres et renvoie une LIST de génotypes enfants."""
        return []

    def genotype_as_string(self):
        """Doit être réimplémentée. Retourna une version string du génotype."""
        return ""

    def __str__(self):
        return str(self.generated)

    def __repr__(self):
        return str(self.genotype_as_string()) + " (" + str(self.generated) + ")"

    last_unique_boject_id = None
    @staticmethod
    def bobject_unique_id():
        if GenericGenetic.last_unique_boject_id is None:
            GenericGenetic.last_unique_boject_id = 0
        else:
            GenericGenetic.last_unique_boject_id += 1
        return GenericGenetic.last_unique_boject_id


class AssetGeneticsController:
    """Gère un système génétique composé de classes implémenteés à partir de GenericGenetic.
    - genetic_class : Classe héritée de GenericGenetic sur laquelle effectuer les traitements
    - max_genotypes : nombre maximum par génération
    - parent : objet blender dans lequel placer les phénotypes générés.
    - selection_type : 'threshold', 'number' ou 'probability'
    - selection_type_param : un nombre paramètre de sélection naturelle. Voir les fonctions natural_selection_*.
    - alt_procreation : (t/F) doit utiliser la procréation alternative ou non.
    - show_mode : 'all' ou 'solo'. Mode d'affichage des phénotypes."""

    def __init__(self, genetic_class, max_genotypes=50, parent=None,
                 selection_type='threshold', selection_type_param=float('nan'),
                 alt_procreation=False, show_mode='all'):
        self.currentGeneration = 0
        self.genotypes = []
        self.maxGenotypes = max_genotypes
        self.geneticClass = genetic_class
        self.parentObject = parent
        if self.parentObject is not None:
            raise NotImplementedError()
        self.selection_type = selection_type
        self.selection_type_param = selection_type_param
        self.alt_procreation = alt_procreation
        self.show_mode = show_mode

        self.fill_genotypes()
        self.create_phenotypes(mode=self.show_mode)

    def __repr__(self):
        buf = io.StringIO()
        buf.write("| Generation " + str(self.currentGeneration) + " | " + str(len(self.genotypes)) + " elements\n")
        for item in self.genotypes:
            buf.write("- " + str(item) + " (fitness:" + str(item.fitness) + ", age:" + str(item.age) + ")\n")
        ret = buf.getvalue()
        buf.close()
        return ret

    def fill_genotypes(self):
        """Remplit les cases vides des génotypes avec de nouveaux génotypes aléatoires.
        Retourne le nombre d'objets générés"""
        start = len(self.genotypes) + 1
        end = self.maxGenotypes + 1
        for i in range(start, end):
            self.genotypes.append(self.geneticClass(parent=self.parentObject))
        return start - end

    def natural_selection_threshold(self, threshold):
        """Tue tous les génotypes dont le fitness est inférieur à threshold."""
        self.genotypes = [item for item in self.genotypes if item.fitness is not None and item.fitness >= threshold]

    def natural_selection_number(self, n):
        """Tue les génotypes les moins bons pour n'en garder que n.
        Les génotypes seront alors classés par sens décroissant."""
        self.genotypes.sort(key=lambda x: x.fitness if x.fitness is not None else 0, reverse=True)
        self.genotypes = self.genotypes[0:n]

    def natural_selection_probability(self):
        """Utilise le fitness comme valeur de probabilité de survie."""
        self.genotypes = [item for item in self.genotypes if item.fitness is not None and item.fitness >= random.random()]

    def love_season(self):
        """Chaque paire de parents va procréer. Au maximum le nombre de génotypes sera de self.maxGenotypes.
        Les génotypes les mieux classés procréront avant les autres."""
        self.genotypes.sort(key=lambda x: x.fitness if x.fitness is not None else 0, reverse=True)
        for i in range(0, len(self.genotypes) - 1, 2):
            self.genotypes += GenericGenetic.cross_genotypes(self.genotypes[i], self.genotypes[i+1]);
            if len(self.genotypes) > self.maxGenotypes:
                break  # on stoppe si on a déjà atteint les 50.
        # On clampe toutefois à maxGenotypes car les parents peuvent créer plusieurs enfants, et donc dépasser le max.
        self.genotypes = self.genotypes[0:self.maxGenotypes]

    def love_season_alt(self):
        """Chaque parent va procréer avec le suivant dans la liste.
        Au maximum le nombre de génotypes sera de self.maxGenotypes.
        Les génotypes les mieux classés procréront avant les autres."""
        self.genotypes.sort(key=lambda x: x.fitness, reverse=True)
        for i in range(0, len(self.genotypes) - 1):
            self.genotypes += GenericGenetic.cross_genotypes(self.genotypes[i], self.genotypes[i+1]);
            if len(self.genotypes) > self.maxGenotypes:
                break  # on stoppe si on a déjà atteint les 50.
        # On clampe toutefois à maxGenotypes car les parents peuvent créer plusieurs enfants, et donc dépasser le max.
        self.genotypes = self.genotypes[0:self.maxGenotypes]

    def create_phenotypes(self, mode="all"):
        """Créée les phénotypes de chaque génotype. Le mode est une façon d'afficher les phénotypes :
        - all : Affiche tous les phénotypes sur une grille
        - solo : Affiche tous les phénotypes au même endroit et les masque. Ils pourront être affichés à la main."""
        if mode == "all":
            cols = int(math.sqrt(len(self.genotypes)))
            gridsize = 4
            startx = (cols // 2) * gridsize
            print("cols="+str(cols))
            for index, item in enumerate(self.genotypes):
                row = index // cols
                col = index - row * cols
                item.compute_individual(location=(-startx + 4*col, -startx + 4*row, 0))
        elif mode == "solo":
            raise NotImplementedError()
        else:
            raise ValueError('mode must be \'all\' or \'solo\'.')


    def mutate_genotypes(self):
        """Effectue une mutation sur chaque génotype"""
        for item in self.genotypes:
            item.mutate_genotype()

    def next_generation(self):
        """Calcule une nouvelle génération en fonction des fitness placées sur les génotypes.
        Les valeurs de fitness doivent être placées à la main en faisant self.genotypes[<index>].fitness = <value>"""

        # natural selection
        if self.selection_type == 'threshold':
            if math.isnan(self.selection_type_param) or self.selection_type_param < 0 or self.selection_type_param > 1:
                raise ValueError('selection_type_param must be defined and between 0 and 1.')
            self.natural_selection_threshold(self.selection_type_param)
        elif self.selection_type == 'number':
            if math.isnan(self.selection_type_param) or self.selection_type_param < 0:
                raise ValueError('selection_type_param must be defined and be positive.')
            self.natural_selection_number(self.selection_type_param)
        elif self.selection_type == 'probability':
            self.natural_selection_probability()
        else:
            raise ValueError('selection_type must be \'threshold\', \'number\' or \'probability\'.')

        # increment age for survivants
        for item in self.genotypes:
            item.age += 1

        # mutate survivants
        self.mutate_genotypes()

        # love time !
        if self.alt_procreation:
            self.love_season_alt()
        else:
            self.love_season()

        # fill if not full
        self.fill_genotypes()

        # Finished !
        self.currentGeneration += 1
        self.create_phenotypes(mode=self.show_mode)

