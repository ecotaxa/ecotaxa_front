# -*- coding: utf-8 -*-
import os
import shutil
import sys
from pathlib import Path
from zipfile import ZipFile

import psycopg2
from flask_security.utils import encrypt_password
from psycopg2.extras import RealDictCursor

from appli import app
from appli.database import GetAll, GetDBToolsDir

table_list = ("taxonomy", "users", "roles", "users_roles",
              "projects", "projectspriv", "process", "acquisitions", "samples",
              "obj_head", "obj_field", "images", "objectsclassifhisto", "alembic_version")

def GetColsForTable(schema: str, table: str):
    ColList = GetAll("""select a.attname from pg_namespace ns
                      join pg_class c on  relnamespace=ns.oid
                      join pg_attribute a on a.attrelid=c.oid
                      where ns.nspname='{1}' and relkind='r' and a.attname not like '%.%'
                      and attnum>0  and c.relname='{0}'  order by attnum""".format(table, schema))
    return [x[0] for x in ColList]


# #############################################################################################################
# Restore une base complete, à vocation à être appellé depuis depuis manage
def RestoreDBFull(UseExistingDatabase=False):
    print("Configuration is Database:", app.config['DB_DATABASE'])
    print("Login: ", app.config['DB_USER'], "/", app.config['DB_PASSWORD'])
    print("Host: ", app.config['DB_HOST'])
    print("Current directory: ", os.getcwd())

    if not os.path.exists("ecotaxadb.zip"):
        print("File ecotaxadb.zip must be in the current directory")
        return
    print("Connect Database")
    if UseExistingDatabase:
        conn = psycopg2.connect(user=app.config['DB_USER'], password=app.config['DB_PASSWORD'],
                                host=app.config['DB_HOST'], database=app.config['DB_DATABASE'])
    else:
        # On se loggue en postgres pour dropper/creer les bases qui doit être déclaré trust dans hba_conf
        conn = psycopg2.connect(user='postgres', host=app.config['DB_HOST'])
    cur = conn.cursor()

    print("Open ZipFile")
    if os.path.exists("DBFullRestore"):
        shutil.rmtree("DBFullRestore")
    os.mkdir("DBFullRestore")
    os.chdir("DBFullRestore")
    zfile = ZipFile("../ecotaxadb.zip", 'r', allowZip64=True)

    print("Extract schema")
    zfile.extract('schema.sql')

    conn.set_session(autocommit=True)
    if UseExistingDatabase:
        print("Drop the existing public schema")
        sql = "DROP SCHEMA public cascade"
        cur.execute(sql)
        # print("Create the public schema")  # inutile fait par l'import du schema, ça evite une erreur dans le log
        # sql = "create schema public AUTHORIZATION " + app.config['DB_USER']
        # cur.execute(sql)
    else:
        print("Drop the existing database")
        sql = "DROP DATABASE IF EXISTS " + app.config['DB_DATABASE']
        cur.execute(sql)
        print("Create the new database")
        sql = "create DATABASE " + app.config['DB_DATABASE'] + " WITH ENCODING='UTF8'  OWNER=" + app.config[
            'DB_USER'] + " TEMPLATE=template0 LC_CTYPE='C' LC_COLLATE='C' CONNECTION LIMIT=-1 "
        cur.execute(sql)

    toolsdir = GetDBToolsDir()
    os.environ["PGPASSWORD"] = app.config['DB_PASSWORD']
    cmd = os.path.join(toolsdir, "psql")
    cmd += " -h " + app.config['DB_HOST'] + " -U " + app.config['DB_USER'] + " -p " + app.config.get('DB_PORT',
                                                                                                     '5432') + " --file=schema.sql " + \
           app.config['DB_DATABASE'] + " >createschemaout.txt"
    print("Import Schema : %s", cmd)
    os.system(cmd)

    conn.close()
    conn = psycopg2.connect(user=app.config['DB_USER'], password=app.config['DB_PASSWORD'], host=app.config['DB_HOST'],
                            database=app.config['DB_DATABASE'])
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print("Encoding = ", conn.encoding)
    print("Restore data")
    for t in table_list:
        ColList = GetColsForTable('public', t)
        print("Restore table %s " % (t,))
        try:
            zfile.extract(t + ".copy")
            with open(t + ".copy", "r", encoding='latin_1') as f:
                cur.copy_from(f, 'public' + "." + t, columns=ColList)
                cur.connection.commit()
        except:
            print("Error while data restoration %s", str(sys.exc_info()))
    cur.execute("update public.users set password=%s where email='admin'", (encrypt_password('ecotaxa'),))
    cur.connection.commit()

    import manage
    manage.ResetDBSequence(cur)
    # Copie des Images
    print("Restore Images")
    cur.execute("select images.* from images ")
    # vaultroot=Path("../vault")
    vaultroot = Path(os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), R"../vault")))
    for r in cur:
        if r['file_name']:
            zipimagefile = "images/%s.img" % r['imgid']
            zfile.extract(zipimagefile)
            VaultFolder = "%04d" % (r['imgid'] // 10000)
            # creation du repertoire contenant les images si necessaire
            if not vaultroot.joinpath(VaultFolder).exists():
                vaultroot.joinpath(VaultFolder).mkdir()
            shutil.move(zipimagefile, vaultroot.joinpath(r['file_name']).as_posix())
            if r['thumb_file_name']:
                zipimagefile = "images/%s.thumb" % r['imgid']
                zfile.extract(zipimagefile)
                shutil.move(zipimagefile, vaultroot.joinpath(r['thumb_file_name']).as_posix())

    # Clean Up du repertoire
    os.chdir("")
    shutil.rmtree("DBFullRestore")
