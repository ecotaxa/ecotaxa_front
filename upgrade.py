# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
import os,shutil
from pathlib import Path
from zipfile import ZipFile

# Requiert un fichier ecotaxapatch.zip contenant l'arboresence complete depuis la racine de l'application (ce repertoire)

print("""
*********************************************************
**************** ECOTAXA UPGRADE PROCESS ****************
*********************************************************
""")
print("Current directory: ",os.getcwd())

if not os.path.exists("ecotaxapatch.zip"):
    print("File ecotaxapatch.zip must be in the current directory")
    exit()

if input("This operation will Upgrade your installation.\nAre you SURE ? Confirm by Y !").lower()!="y":
    print("Upgrade Aborted !!!")
    exit()


print("Open ZipFile")
zfile=ZipFile("ecotaxapatch.zip" , 'r',allowZip64 = True)

# TempPatch For test purpose only
# if os.path.exists("TempPatch"):
#     shutil.rmtree("TempPatch")
# os.mkdir("TempPatch")
# os.chdir("TempPatch")
# zfile=ZipFile("../ecotaxapatch.zip" , 'r',allowZip64 = True)
# End of test section

print("File Upgrade Start ")
for f in zfile.namelist():
    if '__pycache__' in f:
        continue
    if 'config.cfg' in f:
        continue
    if 'static/home' in f:
        continue
    zfile.extract(f)

print("File Upgrade Done ")

print("Now you should run python or python3 manage.py db upgrade")
print("Then restart your application server (ie uwsgi : service uwsgi restart )")
