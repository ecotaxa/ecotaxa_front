# -*- coding: utf-8 -*-
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
    Prj=database.Projects.query.filter_by(projid=PrjId).first()
    g.headcenter="<h4><a href='/prj/{0}'>{1}</a></h4>".format(Prj.projid,Prj.title)
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

    t=["""<style>
th.rotate {
  /* Something you can count on */
  height: 140px;
  white-space: nowrap;
  vertical-align: bottom !important;
}

th.rotate > div {
  transform:
    rotate(270deg);
  width: 15px;
}
  </style>
  This matrix is refreshed every time you access it.
    <table class='table table-bordered table-verycondensed rightfixedfonttd' style='font-size:12px;'><tr><th>Predicted =><br>True category</th>"""]
    # ligne titre des categorie
    for c in CatAll:
        t.append("<th  class=rotate><div>%s</div></th>"%c)
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
    t.append("<br>"+txtbacktoproject)
    return PrintInCharte("\n".join(t))



def plot_confusion_matrix(cm, labels, cmap=plt.cm.YlGnBu):
    ax = g.Fig.add_subplot(111)
    cax=ax.imshow(cm, interpolation='nearest', cmap=cmap)
    g.Fig.colorbar(cax)
    tick_marks = np.arange(len(labels))
    # ax.xticks(tick_marks, labels, rotation=45, rotation_mode='anchor', ha='right')
    ax.set_xticks(tick_marks)
    ax.set_xticklabels(labels, rotation=45, rotation_mode='anchor', ha='right',size=9)
    # g.Fig.yticks(tick_marks, labels)
    ax.set_yticks(tick_marks)
    ax.set_yticklabels(labels,size=9,rotation=45,verticalalignment ='top')
    g.Fig.tight_layout()
    ax.set_ylabel('True category')
    ax.set_xlabel('Predicted category')
    g.Fig.subplots_adjust(bottom=0.2, left=0.25)

