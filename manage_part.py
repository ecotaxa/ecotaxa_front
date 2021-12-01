#
# EcoPart manage application
#
import sys

from flask import g
from flask_script import Manager

import part_app
import part_app.database as partdatabase
import part_app.funcs.common_sample_import as common_import
import part_app.funcs.histograms
import part_app.funcs.uvp6remote_sample_import as uvp6remote_sample_import
import part_app.views.prj as prj
from part_app.app import part_app, db
from part_app import db_utils
from part_app.funcs.histograms import ComputeHistoDet, ComputeHistoRed, ComputeZooHisto
from part_app.remote import EcoTaxaInstance, log_in_ecotaxa

manager = Manager(part_app)


# TODO one day: add DB management commands


@manager.command
def ResetDBSequence(cur=None):
    with part_app.app_context():  # Création d'un contexte pour utiliser les fonction GetAll,ExecSQL qui mémorisent
        g.db = None
        print("Start Sequence Reset")
        if cur is None:
            cur = db.session
        cur.execute("SELECT setval('seq_temp_tasks', (SELECT max(id) FROM temp_tasks), true)")
        cur.execute("SELECT setval('part_projects_pprojid_seq', (SELECT max(pprojid) FROM part_projects), true)")
        cur.execute("SELECT setval('part_samples_psampleid_seq', (SELECT max(psampleid) FROM part_samples), true)")
        print("Sequence Reset Done")


@manager.option('-p', '--projectid', dest='ProjectID', type=int, default=None, required=True,
                help="Particle project ID")
@manager.option('-w', '--what', dest='What', default=None, required=True,
                help="""What should be recomputed, a set of letter i.e : DRMTC
D : Compute detailed histogram 
R : Compute Reduced histogram
M : Match Ecotaxa sample
T : Compute taxonomy histogram
C : CTD import""")
@manager.option('-u', '--user', dest='User', default=None, help="User Name for CTD Import")
@manager.option('-e', '--email', dest='Email', default=None, help="Email for CTD Import")
@manager.option('-xu', '--ecotaxa-user', dest='ecotaxa_user', help="EcoTaxa username")
@manager.option('-xp', '--ecotaxa-pass', dest='ecotaxa_password', help="EcoTaxa password")
def RecomputePart(ProjectID, What, User, Email, ecotaxa_user, ecotaxa_password):
    cookie = log_in_ecotaxa(ecotaxa_user, ecotaxa_password)
    if cookie is None:
        print("EcoTaxa login failed")
        quit(-1)
    ecotaxa_if = EcoTaxaInstance(cookie)
    if 'C' in What:
        if User is None or Email is None:
            print("-u and -e options are required for CTD import")
            quit(-1)
    with part_app.app_context():  # Création d'un contexte pour utiliser les fonction GetAll,ExecSQL qui mémorisent
        g.db = None
        Prj = partdatabase.part_projects.query.filter_by(pprojid=ProjectID).first()
        Samples = db_utils.GetAll("select psampleid,profileid from part_samples where pprojid=(%s)", [ProjectID])
        for S in Samples:
            print("Processing particle sample %s:%s" % (S['psampleid'], S['profileid']))
            if 'D' in What:
                print("Det=", ComputeHistoDet(S['psampleid'], Prj.instrumtype))
            if 'R' in What:
                print("Red=", ComputeHistoRed(S['psampleid'], Prj.instrumtype))
            if 'M' in What:
                print("Match=", prj.ComputeZooMatch(ecotaxa_if, S['psampleid'], Prj.projid))
            if 'C' in What:
                print("CTD=", "Imported" if common_import.ImportCTD(S['psampleid'], User, Email) else 'CTD No file')
        Samples = db_utils.GetAll("select psampleid,profileid,sampleid from part_samples where pprojid=(%s)",
                                  [ProjectID])
        for S in Samples:
            if 'T' in What and S['sampleid']:
                print("Zoo for particle sample %s:%s=" % (S['psampleid'], S['profileid']),
                      ComputeZooHisto(ecotaxa_if, S['psampleid'], Prj.instrumtype))


@manager.command
def partpoolserver():
    with part_app.app_context():  # Création d'un contexte pour utiliser les fonction GetAll,ExecSQL qui mémorisent
        g.db = None
        Lst = db_utils.GetAll(
            """select pprojid,ptitle from part_projects where coalesce(remote_type,'')!='' and coalesce(remote_url,'')!='' """)
        for P in Lst:
            print("pollserver for project {pprojid} : {ptitle}".format(**P))
            try:
                RSF = uvp6remote_sample_import.RemoteServerFetcher(P['pprojid'])
                LstSampleID = RSF.FetchServerDataForProject([])
                if not LstSampleID:
                    continue
                for psampleid in LstSampleID:
                    print("uvp6remote Sample %d Metadata processed, Détailled histogram in progress" % (psampleid,))
                    uvp6remote_sample_import.GenerateParticleHistogram(psampleid)
                    print("Try to import CTD")
                    print(common_import.ImportCTD(psampleid, "Automatic", ""))
            except:
                print('Error : ' + str(sys.exc_info()))


if __name__ == "__main__":
    manager.run()
