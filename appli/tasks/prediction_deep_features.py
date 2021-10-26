#
# Temporary source for the deep learning features of prediction AKA automatic classification V2
# Will disappear when back-end does the same using TensorFlow
#

# -*- coding: utf-8 -*-
import json
import logging
import os
import sys
import time
from pathlib import Path
from subprocess import Popen, TimeoutExpired, DEVNULL, PIPE

import numpy as np
from sklearn.externals import joblib

from appli import db, database, app, TempTaskDir
from appli.database import CSVIntStringToInClause
from to_back.ecotaxa_cli_py import ProjectModel
from .taskclassifauto2 import TaskClassifAuto2


def ComputeSCNFeatures(pred_task: TaskClassifAuto2, Prj: ProjectModel):
    logging.info("Start SCN features Computation ")
    # Minimal sanity check
    if Prj.cnn_network_id is None or len(Prj.cnn_network_id) == 0:
        logging.error("No SCN Network set for this project. See settings.")
        pred_task.task.taskstate = "Error"
        return False
    # Build the list of project that we need features computed from
    if pred_task.param.BaseProject != '':
        PrjListInClause = CSVIntStringToInClause(pred_task.param.BaseProject + ',' + str(pred_task.param.ProjectId))
    else:
        PrjListInClause = str(pred_task.param.ProjectId)
    # Find the _potentially_ useful for SCN rows and update their cnn_feature lines
    sql = """select objid,file_name from (
            select obj.objid,  images.file_name,rank() over(partition by obj.objid order by images.imgid) rang
                from objects obj
                join images on images.objid=obj.objid
                left join obj_cnn_features cnn on obj.objid=cnn.objcnnid                    
                where obj.projid in({0}) and cnn.objcnnid is NULL
                ) Q 
                where rang=1
                """.format(PrjListInClause)
    pred_task.pgcur.execute(sql)
    WorkDir = Path(pred_task.GetWorkingDir())
    scn_input = WorkDir / "scn_input.csv"
    output_dir = WorkDir / "scn_output"
    if not output_dir.exists():
        output_dir.mkdir()
    vaultdir = (Path(TempTaskDir) / "../vault/").resolve().as_posix() + "/"
    # Configure the execution
    scn_model_dir = Path(os.path.normpath((Path(TempTaskDir) / "../SCN_networks" / Prj.cnn_network_id).as_posix())). \
        resolve()
    meta = json.load((scn_model_dir / "meta.json").open('r'))
    TStep = time.time()
    NbrLig = 0
    with scn_input.open('w') as finput:
        while True:
            # recupère les images des objets à calculer
            DBRes = pred_task.pgcur.fetchmany(1000)
            if len(DBRes) == 0:
                break
            NbrLig += len(DBRes)
            finput.writelines(("%s,%s%s\n" % (r[0], vaultdir, r[1]) for r in DBRes))
    if NbrLig == 0:
        logging.info("No Missing SCN Features")
        return True
    TStep = time.time()
    env = {
        "MODEL_DIR": scn_model_dir.as_posix(),
        "OUTPUT_DIR": output_dir.resolve().as_posix(),
        # input data
        "UNLABELED_DATA_FN": scn_input.as_posix(),
        # start at the last epoch (NB: this is the previous STOP_EPOCH - 1 because of 0-based indexing)
        "EPOCH": str(meta['epoch']),
        # stop early = do not train
        "STOP_EPOCH": "0",
        # whether to compute features on the input file
        "DUMP_FEATURES": "1"
    }
    # display the current environment
    for k, v in env.items():
        logging.info("{}: {}".format(k, v))

    # time out for the communication with the binary
    # beware, this is for the full execution event while execution can be long for training
    timeout_in_s = 1200

    scn_binary = app.config['SCN_BINARY']
    # recopie toutes les variables d'environnement utile pour l'environnement simulé
    for k, v in os.environ.items():
        env[k] = v
    # TEST sur le PC de laurent avec script de simulation
    if scn_binary == 'TEST_PC_LAURENT':
        # for extra in ['PATH','SYSTEMROOT']:
        #     env[extra]= os.environ[extra]
        scn_binary = sys.executable + " " + (
                Path(TempTaskDir) / "../appli/tasks/simulateur_SCN.py").resolve().as_posix()

    shelloption = scn_binary.endswith('.sh')

    logging.info("scn_binary=" + scn_binary)
    # bufsize=1: Line buffering
    with Popen(scn_binary, shell=shelloption, stdin=DEVNULL, stdout=PIPE, stderr=PIPE, env=env,
               universal_newlines=True, bufsize=1) as p:
        try:
            outs, errs = p.communicate(timeout=timeout_in_s)
        except TimeoutExpired:
            p.kill()
            outs, errs = p.communicate()
    logging.info("Return code: {}".format(p.returncode))
    logging.info("Output: \n%s", outs)
    logging.info("Errors: %s", errs)
    if p.returncode != 0:
        logging.info("Something went wrong during SCN Features generation")
        return False

    upcur = db.engine.raw_connection().cursor()
    InsSQL = """insert into obj_cnn_features(objcnnid, cnn01, cnn02, cnn03, cnn04, cnn05, cnn06, cnn07, cnn08, cnn09, cnn10, cnn11, cnn12, cnn13, cnn14, cnn15, cnn16, cnn17, cnn18, cnn19, cnn20, cnn21, cnn22, cnn23, cnn24, cnn25, cnn26, cnn27, cnn28, cnn29, cnn30, cnn31, cnn32, cnn33, cnn34, cnn35, cnn36, cnn37, cnn38, cnn39, cnn40, cnn41, cnn42, cnn43, cnn44, cnn45, cnn46, cnn47, cnn48, cnn49, cnn50) 
                values(%(objcnnid)s,%(cnn01)s,%(cnn02)s,%(cnn03)s,%(cnn04)s,%(cnn05)s,%(cnn06)s,%(cnn07)s,%(cnn08)s,%(cnn09)s,%(cnn10)s,%(cnn11)s,%(cnn12)s,%(cnn13)s,%(cnn14)s,%(cnn15)s,%(cnn16)s,%(cnn17)s,%(cnn18)s,%(cnn19)s,%(cnn20)s,%(cnn21)s,%(cnn22)s,%(cnn23)s,%(cnn24)s,%(cnn25)s,%(cnn26)s,%(cnn27)s,%(cnn28)s,%(cnn29)s,%(cnn30)s,%(cnn31)s,%(cnn32)s,%(cnn33)s,%(cnn34)s,%(cnn35)s,%(cnn36)s,%(cnn37)s,%(cnn38)s,%(cnn39)s,%(cnn40)s,%(cnn41)s,%(cnn42)s,%(cnn43)s,%(cnn44)s,%(cnn45)s,%(cnn46)s,%(cnn47)s,%(cnn48)s,%(cnn49)s,%(cnn50)s )"""

    pca = joblib.load(scn_model_dir / "feature_pca.jbl")

    def ProcessLig():
        nonlocal LigData, InsSQL, upcur, LigID, pca
        # pour générer un fichier de test
        # pca = PCA(n_components=50)
        # pca.fit(np.array(LigData))
        # pca_fn = model_dir/"feature_pca.jbl"
        # joblib.dump(pca, pca_fn)

        pcares = pca.transform(np.array(LigData))
        SQLParam = [{"cnn%02d" % (i + 1): float(x) for i, x in enumerate(feat)} for feat in pcares]
        for i in range(len(SQLParam)):
            SQLParam[i]['objcnnid'] = LigID[i]
        database.ExecSQL("delete from obj_cnn_features where objcnnid= any(%s)", (LigID,))
        upcur.executemany(InsSQL, SQLParam)
        upcur.connection.commit()
        LigData = []
        LigID = []

    with (output_dir / 'unlabeled_features.csv').open('r') as fout:
        LigID = []
        LigData = []
        for l in fout:
            Lig = l.split(',')
            LigID.append(int(Lig[0]))
            LigData.append([float(x) for x in Lig[2:]])
            if len(LigData) > 100:
                ProcessLig()
    if len(LigData) > 0:
        ProcessLig()
    return True
