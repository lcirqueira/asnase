from pyvmd import *

NAME = "3eca_md1_heating"
STEP = 10

mol = System()
#mol.load("{}.gro".format(NAME))
mol.load("{}.trr".format(NAME) , step=STEP)
#mol.wrap("protein")
