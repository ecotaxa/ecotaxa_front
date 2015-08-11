# -*- coding: utf-8 -*-
#TODO lien back to project
from appli import db,app,ObjectToStr,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ComputeLimitForImage
from appli.database import GetAll,GetAssoc2Col
from time import time
from flask.ext.security import login_required
from flask import flash,g
import numpy as np
import io,base64
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
from collections import Counter
from sklearn import metrics, cross_validation
import matplotlib.pyplot as plt


@app.route('/prjcm/<int:PrjId>')
@login_required
def PrjConfusionMatrix(PrjId):
    sql="""select lower(tr.name) ClassifReel,lower(tp.name) ClassifPredict
from objects o
join taxonomy tp on tp.id=o.classif_auto_id
join taxonomy tr on tr.id=o.classif_id
where projid =%d and classif_qual='V'"""%PrjId
    DBRes=np.array(GetAll(sql))
    txtbacktoproject="<a href='/prj/%d'>Back to project</a>"%PrjId
    if len(DBRes)==0:
        flash("No validated objects with prediction",'error')
        return PrintInCharte(txtbacktoproject)
    CatTrue = DBRes[:,0]
    CatPred = DBRes[:,1]
    CatAll=[x for x in set(CatPred)|set(CatTrue)]
    CatAll.sort()
    cm = metrics.confusion_matrix(y_pred=CatPred, y_true=CatTrue)
    # Version Division par axe des Réel (somme horiz)
    SommeH=cm.sum(axis=1)
    SommeV=cm.sum(axis=0)
    SommeVNoZero=cm.sum(axis=0)
    SommeVNoZero[SommeVNoZero==0]=999999 # pour eviter les division par zéro
    SommeHNoZero=cm.sum(axis=1)
    SommeHNoZero[SommeHNoZero==0]=999999 # pour eviter les division par zéro
    TotalObj=CatPred.shape[0]
    D=np.diag(cm)

    t=[txtbacktoproject+"<table class='table table-bordered table-condensed rightfixedfonttd '><tr><th>Predicted =><br>True category</th>"]
    # ligne titre des categorie
    for c in CatAll:
        t.append("<th>%s</th>"%c)
    t.append("<th>Nbr True</th><th>% True</th><th>Recall</th>")
    for c,cml,s,recall in zip(CatAll,cm,SommeH,100*D/SommeHNoZero):
        t.append("</tr><tr><th>%s</th>"%c)
        for v in cml:
            t.append("<td>%s</td>"%v)
        t.append("<td>%s</td><td>%0.1f</td><td>%0.1f</td>"%(s,100*s/TotalObj,recall)) # Ajoute le total & Pct de la ligne
    t.append("</tr><tr><th>Nbr Predicted</th>")
    for s in SommeV:
        t.append("<td>%s</td>"%(s)) # Ajoute le total de la Colonne
    t.append("</tr><tr><th>% of Predicted</th>")
    for s in SommeV:
        t.append("<td>%0.1f</td>"%(100*s/TotalObj)) # Ajoute le % de la Colonne
    t.append("</tr><tr><th>Precision</th>")
    for s in 100*D/SommeVNoZero:
        t.append("<td>%0.1f</td>"%(s)) # Ajoute la precision
    t.append("</tr></table>")


    cm_normalized = cm.astype('float') / SommeHNoZero[:, np.newaxis]
    FigSize=int(SommeHNoZero.shape[0]/3)
    if FigSize<8: FigSize=8 # 800x800 px
    g.Fig=plt.figure(figsize=(FigSize,FigSize), dpi=100)
    plot_confusion_matrix(cm_normalized,CatAll)
    RamImage = io.BytesIO()
    g.Fig.savefig(RamImage , dpi=100, format='png')
    t.append("<h4>Confusion Matrix Name On Recall</h4><img src='data:image/png;base64,{}'/>".format(base64.encodebytes(RamImage.getvalue()).decode()) )

    # Version division par axe des prediction pas de div pas zero possible et permet de voir ce que c'est devenu (somme Vert.)
    cm_normalized = cm.astype('float')/SommeVNoZero
    # plt.figure(figsize=(8,8), dpi=100) # 800x800 px
    g.Fig.clf()
    plot_confusion_matrix(cm_normalized,CatAll)
    RamImage = io.BytesIO()
    g.Fig.savefig(RamImage , dpi=100, format='png')
    t.append("<h4>Confusion Matrix On Precision</h4><img src='data:image/png;base64,{}'/>".format(base64.encodebytes(RamImage.getvalue()).decode()) )
    t.append(txtbacktoproject)
    return PrintInCharte("\n".join(t))



def plot_confusion_matrix(cm, labels, cmap=plt.cm.YlGnBu):
    ax = g.Fig.add_subplot(111)
    cax=ax.imshow(cm, interpolation='nearest', cmap=cmap)
    g.Fig.colorbar(cax)
    tick_marks = np.arange(len(labels))
    # ax.xticks(tick_marks, labels, rotation=45, rotation_mode='anchor', ha='right')
    ax.set_xticks(tick_marks)
    ax.set_xticklabels(labels, rotation=45, rotation_mode='anchor', ha='right')
    # g.Fig.yticks(tick_marks, labels)
    ax.set_yticks(tick_marks)
    ax.set_yticklabels(labels)
    g.Fig.tight_layout()
    ax.set_ylabel('True category')
    ax.set_xlabel('Predicted category')
    g.Fig.subplots_adjust(bottom=0.2, left=0.25)

if __name__ == '__main__':
    np.set_printoptions(precision=4,linewidth =180)
    def Test1():
        print ("Learning Test")
        TInit = time()
        Vars=GetAll("""select objid,n01,n02,n03,n04,n05,n06,n07,n08,n09,n10,n11,n12,n13 from objects
                        where classif_id is not null and classif_qual='V'
                        and projid=4
                        and classif_id in (select classif_id from objects
                        where classif_id is not null and classif_qual='V'
                        and projid=4 group by classif_id having count(*) >10)
                        order by objid""")
        Classif=GetAll("""select classif_id from objects
                        where classif_id is not null and classif_qual='V'
                        and projid=4
                        and classif_id in (select classif_id from objects
                        where classif_id is not null and classif_qual='V'
                        and projid=4 group by classif_id having count(*) >10)
                        order by objid""")
        # print(Vars)
        # print(Classif)
        print ('DB Extract', time() - TInit, 's')
        Ids = np.array(Vars)[:,0] # Que l'objid
        learn = np.array(Vars)[:,1:] # exclu l'objid
        Vars=None # libere la mémoire
        learn_cat = np.array(Classif)[:,0]
        Classif=Vars=None # libere la mémoire
        print ('DB Conversion to NP', time() - TInit, 's')
        print(learn.shape)
        print(learn_cat.shape)
        # Note : La multiplication des jobs n'est pas forcement plus performente, en tous cas sur un petit ensemble.
        rf = RandomForestClassifier(n_estimators=300, min_samples_leaf=5, min_samples_split=10, n_jobs=1)
        # rf = svm.SVC()
        TStep = time()
        rf.fit(learn, learn_cat)
        print ('Learning ', time() - TStep, 's')
        TStep = time()
        # Result=rf.predict(learn)
        Result=rf.predict_proba(learn)
        ResultMaxCol=np.argmax(Result,axis=1)
        ResultClass=rf.classes_[ResultMaxCol]
        Classes1=rf.classes_
        ResultProba=Result[ResultMaxCol] #marche pas
        print ('Prediction ', time() - TStep, 's')
        print("learned ",Counter(learn_cat))
        print("result ",Counter(ResultClass))


        NbrOk=NbrDiff=0
        for a,b,i in zip(learn_cat,ResultClass,range(0,10000)):
            if a==b : NbrOk+=1
            else:
                # print(a,b,c,i,Result[i])
                NbrDiff+=1

        print("OK=",NbrOk," Diff=",NbrDiff)
        cm = metrics.confusion_matrix(learn_cat,ResultClass)
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print('Normalized confusion matrix')
        print(cm_normalized)
        plt.figure()
        plot_confusion_matrix(cm_normalized,rf.classes_)
        plt.show()

    #     scores =cross_validation.cross_val_score(rf,learn, learn_cat)
    #     print ('scores ', time() - TStep, 's')
    #
    #     cv = cross_validation.StratifiedKFold(learn_cat, n_folds=5)
    # s = time()
    # pred_cat = []
    # true_cat = []
    # epsilon = 10**-20       # pour éviter les divisions par 0
    # e = epsilon
    # for train_idx, test_idx in cv :
    #     def plot_confusion_matrix(cm, labels, cmap=plt.cm.YlGnBu):
    #         plt.imshow(cm, interpolation='nearest', cmap=cmap)
    #         plt.colorbar()
    #         tick_marks = np.arange(len(labels))
    #         plt.xticks(tick_marks, labels, rotation=45, rotation_mode='anchor', ha='right')
    #         plt.yticks(tick_marks, labels)
    #         plt.tight_layout()
    #         plt.ylabel('True category')
    #         plt.xlabel('Predicted category')
    #         plt.subplots_adjust(bottom=0.15, left=0.2)
    #
    #
    #     rf.fit(learn[train_idx], learn_cat[train_idx])
    #     pred_cat = np.append(pred_cat, rf.predict(learn[test_idx]))
    #     # NB: ici, le nombre d'images étant petit, on peut faire la prédiction d'un coup
    #     #     mais dans l'absolu, il vaudrait mieux écrire un wrapper pour rf.predict qui découpe en morceaux de taille configurable pour rentrer en RAM et l'utiliser systématiquement
    #     true_cat = np.append(true_cat, learn_cat[test_idx])
    #     print ('Computed 5x cross-validation of learning set in', time() - s, 's')
    #
    #     # et ensuite on applique les mêmes stats de performance
    #     categories = rf.classes_
    #     cm = metrics.confusion_matrix(y_true=true_cat, y_pred=pred_cat, labels=categories)
    #
    #     plt.figure(figsize=(12, 10), dpi=100)
    #     plot_confusion_matrix(cm * 1.0 / (np.sum(cm, 0) + e), categories)
    #     plt.savefig('confusion_matrix-cross_val-norm_by_col.png', dpi=100)
    #
    #     plt.figure(figsize=(12, 10), dpi=100)
    #     plot_confusion_matrix(cm * 1.0 / (np.sum(cm, 1) + e), categories)
    #     plt.savefig('confusion_matrix-cross_val-norm_by_line.png', dpi=100)
    def Test2():
        sql="""select lower(tr.name) ClassifReel,lower(tp.name) ClassifPredict
from objects o
join taxonomy tp on tp.id=o.classif_auto_id
join taxonomy tr on tr.id=o.classif_id
where projid =4"""
        DBRes=np.array(GetAll(sql))
        CatPred = DBRes[:,0]
        CatTrue = DBRes[:,1]
        print("result ",Counter(CatTrue))
        CatAll=[x for x in set(CatPred)|set(CatTrue)]
        CatAll.sort()
        print('CatAll',CatAll)
        # CatAll=GetAssoc2Col("select id,name from taxonomy where id = any(%s) ",(CatAll,))
        cm = metrics.confusion_matrix(CatTrue,CatPred)
        # Version Division par axe des Réel (somme horiz)
        Somme=cm.sum(axis=1)
        Somme[Somme==0]=999999
        cm_normalized = cm.astype('float') / Somme[:, np.newaxis]
        # Version division par axe des prediction pas de div pas zero possible et permet de voir ce que c'est devenu (somme Vert.)
        #cm_normalized = cm.astype('float')/cm.sum(axis=0)

        print(cm)
        print(Somme)
        print('Normalized confusion matrix')
        print(cm_normalized)
        plt.figure()
        plot_confusion_matrix(cm_normalized,CatAll)
        file_like = io.BytesIO()
        plt.savefig(file_like , dpi=100, format='png')

        plt.show()

    Test2()