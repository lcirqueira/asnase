package require psfgen
package require solvate

topology unique_PEG.top
#topology myPEG.top


segment UPEG {
    pdb nohPEG.pdb
} 
coordpdb nohPEG.pdb UPEG
guesscoord

writepsf protoPEG.psf
writepdb protoPEG.pdb

exit
