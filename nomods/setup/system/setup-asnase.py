"""
Script to setup a new system using CHARMM 36
and reducing number of water molecules.
"""
import numpy as np
from pyvmd import *
from pylbtc.misc import evalbash, rmfile

INPUT = "/home/lcirqueira/Simulations/asnase/md1_heating/3eca_md1_heating_from_trr.pdb"
INP_FRAME = 0
INP_CHAIN = ['A' , 'B' , 'C' , 'D']

OUT_NAME = "lnase.0"
WATER_LAYER = 15
CATION , ANION = "POT" , "CLA"


evaltcl("""
package require psfgen
topology /home/lcirqueira/Simulations/namd/charmm/toppar_c36/top_all36_prot.rtf
topology /home/lcirqueira/Simulations/namd/charmm/toppar_c36/toppar_water_ions.str
pdbalias residue HIS HSD
pdbalias atom ILE CD1 CD
pdbalias atom HOH O OH2
pdbalias residue HOH TIP3
       """)

tempsys = System()
tempsys.load(INPUT , first=INP_FRAME , last=INP_FRAME)
for frame in tempsys.trajectory:
    tempsys.all.moveby(-tempsys.all.center)
    

for chain in INP_CHAIN:
    ch_sel = tempsys.selectAtoms("chain {}".format(chain))
    ch_sel['segname'] = 'PTN{}'.format(chain)
    ch_sel.write("pdb" , "tempchain_{}.pdb".format(chain))

    evaltcl("""
segment PTN{0} {{
    pdb tempchain_{0}.pdb
}}
coordpdb tempchain_{0}.pdb PTN{0}
""".format(chain))

    evaltcl("patch DISU PTN{0}:77 PTN{0}:105".format(chain))

evaltcl("""
guesscoor
writepsf temp_nowat.psf
writepdb temp_nowat.pdb
""")


evaltcl("""package require solvate
solvate temp_nowat.psf temp_nowat.pdb -o temp_waterbox -b 2 -s WAT -t {}""".format(WATER_LAYER))


resid = 1
segnum = 1
wtsegname = "WAT{}"

for i, molid in enumerate((3,)): #solvate plugin mol ID outputs (must be checked manually)
    beg_seg = segnum
    watersys = System(id=molid)
    watsel = watersys.selectAtoms("water")
    wt_res_list = set(watsel["residue"])
    for res in wt_res_list:
        tempsel = watersys.selectAtoms("water and residue {}".format(res))
        tempsel["resid"] = resid
        tempsel["segname"] = wtsegname.format(segnum)
        resid += 1
        if resid > 9999:
            resid = 1
            segnum += 1
    resid = 1
    segnum += 1
    for n in range(beg_seg,segnum):
        segsel = watersys.selectAtoms("segname WAT{}".format(n))
        segsel.write("pdb", "wat{}.pdb".format(n))



for i in range(1,segnum):
    evaltcl("""
    segment WAT{0} {{
        pdb wat{0}.pdb
        auto none
    }}
    coordpdb wat{0}.pdb WAT{0}
    """.format(i))

evaltcl("""
guesscoord
writepsf solvated.psf
writepdb solvated.pdb
""")


evaltcl("""
package require autoionize
autoionize -psf solvated.psf -pdb solvated.pdb -sc 0.15 -cation {} -anion {} -o ionized
""".format(CATION, ANION))

ionsys = System(id=5) #autoionize plugin mol ID output (must be checked manually)
ionsys.selectAtoms("ion").write("pdb" , "temp_ion.pdb")
evaltcl("""
segment ION {
    pdb temp_ion.pdb
}
coordpdb temp_ion.pdb
""")

evaltcl("""
guesscoord
writepsf temp_nocentersys.psf
writepdb temp_nocentersys.pdb
""")


finalsys = System()
finalsys.load("temp_nocentersys.psf")
finalsys.load("temp_nocentersys.pdb")

finalsys.all.moveby(-finalsys.all.center)

finalsys.all.write("psf" , "{}.0.psf".format(OUT_NAME))
finalsys.all.write("pdb" , "{}.0.pdb".format(OUT_NAME))

rmfile("temp*", "solvated*" , "ionized*", "wat*.pdb")
exit()
