from pyvmd import *

IN = "molefacture_original"
SEGNAME = "UPEG"

CONVERT_DIC = {'C' : 'C',
               'O' : 'O',
               'C2': 'CA',
               'C3': 'CB',
               'C4': 'CP1',
               'O2': 'OP1',
               'C5': 'CP2',
               'C6': 'CP3',
               'O3': 'OP2',
               'C7': 'CP4'}

mol = System()
mol.load("{}.pdb".format(IN))

mol.all['segname'] = SEGNAME
mol.all['resname'] = SEGNAME

nohsel = mol.selectAtoms("all and noh")

for idx in nohsel:
    tmpsel = mol.selectAtoms("index {}".format(idx))
    conv_key = tmpsel['name'][0]

    tmpsel['name'] = CONVERT_DIC[conv_key]

nohsel.write("pdb" , "nohPEG.pdb")
