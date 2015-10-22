import os,subprocess,time,sys
from threading import Thread
from pathlib import Path

# Passe dans le repertoire parent qui est la racine du repertoire portable
os.chdir("..")
print("Current directory is %s"%(os.getcwd(),))
os.environ['PATH']=os.getcwd()+"\\Python34;"+os.environ['PATH']
os.environ['PGDATA']=os.getcwd()+"\\PG94\\Data\\Data"
os.environ['PGDATABASE']="postgres"
os.environ['PGLOCALEDIR']=os.getcwd()+"\\PG94\\App\\PgSQL\Share"
os.environ['PGSQL']=os.getcwd()+"\\PG94\\App\\PgSQL"
os.environ['PGLOG']=os.getcwd()+"\\PG94\\Data\\log.txt"
os.environ['PGPORT']="5432"
os.environ['PGUSER']="postgres"
os.environ['PYTHONHOME']=os.getcwd()+"\\Python34"
os.environ['PYTHONPATH']=os.getcwd()+"\\Python34\\DLLs;"+os.getcwd()+"\\Python34\\Lib;"+os.getcwd()+"\\Python34\\Lib\\site-packages;"

# Decommenter ici pour ouvrir un shell avec les bonne variables d'environnement
RunAppli=True
RunShell=False
RunFullDBRestore=False
RunApache=False

if len(sys.argv)>1:
    if sys.argv[1]=='shell':
        RunAppli=False
        RunShell=True
    if sys.argv[1]=='FullDBRestore':
        RunAppli=False
        RunFullDBRestore=True
    if sys.argv[1]=='httpd':
        RunAppli=False
        RunApache=True
        
#os.system("cmd.exe /k ")
#exit(1)
# Commandes pour start/stop manuel
# "%PGSQL%\bin\pg_ctl" -D "%PGDATA%" -l "%PGLOG%" -w start
# "%PGSQL%\bin\pg_ctl" -D "%PGDATA%" -l "%PGLOG%" -w stop
cmd=os.environ['PGSQL']+"\\bin\\pg_ctl -D "+os.environ['PGDATA']+" -l "+os.environ['PGLOG']+" -w start"
print("""
******************************************************************************
************************* WELCOME TO ECOTAXA PORTABLE ************************
******************************************************************************

""")

print("************************* Starting PostgreSQL ********************************")

if not Path(os.environ['PGDATA']).exists():
    print("********* First Use, initialise PostgreSQL ************")
    cmdinit=os.environ['PGSQL']+"\\bin\\initdb  -U postgres -A trust -E Latin1 --locale=C"
    subprocess.call(cmdinit,shell=True,universal_newlines=True,stderr=subprocess.STDOUT)
    print("********* First Use, initialisation done ************")

subprocess.call(cmd,shell=True,universal_newlines=True,stderr=subprocess.STDOUT)
print("************************* PostgreSQL Started *********************************")

def WebBrowserOpener(tempo,url):
    time.sleep(tempo) # attend le lancement du serveur web
    os.system("start "+url)
if RunAppli:    
    print("""
Close "ECOTAXA Web Server" Windows to stop the Database""")
    os.chdir("ecotaxa")
    thread = Thread(target = WebBrowserOpener,args=(5,"http://127.0.0.1:5000",))
    thread.start()
    os.system('start "ECOTAXA Web Server" /Wait   ..\\Python34\\python.exe runserver.py')
if RunShell:    
    print("""
type 'exit' to stop the database""")
    os.chdir("ecotaxa")
    os.system("cmd.exe /k ")
if RunApache:    
    print("""
Close "ECOTAXA Apache Web Server" Windows to stop the Database""")
    os.chdir("apache24\\bin")
    thread = Thread(target = WebBrowserOpener,args=(2,"http://127.0.0.1",))
    thread.start()
    os.system('start "ECOTAXA Apache Web Server" /Wait httpd.exe')
if RunFullDBRestore:
    cmd="python ecotaxa\\manage.py FullDBRestore"
    os.system(cmd)
    
print("************************* Stopping PostgreSQL ********************************")
cmd=os.environ['PGSQL']+"\\bin\\pg_ctl -D "+os.environ['PGDATA']+" -l "+os.environ['PGLOG']+" -w stop"""
print(subprocess.check_output(cmd,shell=True,universal_newlines=True))
print("************************** PostgreSQL Stopped ********************************")



