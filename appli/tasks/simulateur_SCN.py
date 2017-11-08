import os,math
from pathlib import Path

infilename=Path(os.environ["UNLABELED_DATA_FN"])
outfilename=Path(os.environ["OUTPUT_DIR"])/'unlabeled_features.csv'

print("in = ",infilename.as_posix())
print("out = ",outfilename.as_posix())

LigFeat=",".join((str(round(x*0.1,2)) for x in range(447)))
print(LigFeat)
with outfilename.open("w") as outfile,infilename.open("r") as infile:
    for l in infile:
        lig=l.split(',')
        print(lig[0])
        outfile.write("%s,-1,%s,%s\n"%(lig[0],round((math.fmod(float(lig[0]),1000)/10),1),LigFeat))

