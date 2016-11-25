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
import matplotlib
matplotlib.use('Agg')
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
    th {
      vertical-align: bottom !important;
      background-color: #ddd
    }
    .table > tbody > tr > th.rotate {
      height: 140px;
      white-space: nowrap;
    }
    .table > tbody > tr > th.row_header{
      height: 140px;
      white-space: nowrap;
      vertical-align: top !important;
    }
    th.rotate > div {
      transform:
        rotate(270deg);
      width: 15px;
    }
    th.row_header > div {
      transform:
        translate(0px, 200px)
        rotate(270deg);
      width: 15px;
    }
  .margin {
      font-style: italic;
    }
  </style>
  <h2>Confusion matrix</h2>
  <p>This matrix is refreshed every time you access it. For more information on confusion statistics, please see the <a href='https://en.wikipedia.org/wiki/Precision_and_recall'>very well written Wikipedia page</a>.</p>
  
    <table class='table table-bordered table-hover table-condensed' style='font-size:12px;'>
    <tr>
      <th>&nbsp;</th>
      <th>&nbsp;</th>
      <th class='column_header' colspan='1000'>Predicted category</th>
    </tr>
    <tr>
      <th class='row_header' rowspan='1000'><div>True category</div></th>
      <th>&nbsp;</th>
    """]
    # ligne titre des categorie
    for c in CatAll:
        t.append("<th class='rotate'><div>%s</div></th>"%c)
    t.append("<th>Nb. true</th><th>% true</th><th><a href='https://en.wikipedia.org/wiki/Precision_and_recall#Recall' target='_blank'>Recall</a></th>")
    for c,cml,s,recall in zip(CatAll,cm,SommeH,100*D/SommeHNoZero):
        t.append("</tr><tr><th>%s</th>"%c)
        for v in cml:
            t.append("<td>%s</td>"%v)
        t.append("<td class='margin'>%s</td><td class='margin'>%0.1f</td class='margin'><td>%0.1f</td>"%(s,100*s/TotalObj,recall)) # Ajoute le total & Pct de la ligne
    t.append("</tr><tr><th>Nb. predicted</th>")
    for s in SommeV:
        t.append("<td class='margin'>%s</td>"%(s)) # Ajoute le total de la Colonne
    t.append("</tr><tr><th>% of predicted</th>")
    for s in SommeV:
        t.append("<td class='margin'>%0.1f</td>"%(100*s/TotalObj)) # Ajoute le % de la Colonne
    t.append("</tr><tr><th><a href='https://en.wikipedia.org/wiki/Precision_and_recall#Precision' target='_blank' >Precision</a></th>")
    for s in 100*D/SommeVNoZero:
        t.append("<td class='margin'>%0.1f</td>"%(s)) # Ajoute la precision
    t.append("</tr></table>")


    cm_normalized = cm.astype('float') / SommeHNoZero[:, np.newaxis]
    FigSize=int(SommeHNoZero.shape[0]/3)
    if FigSize<8: FigSize=8 # 800x800 px
    g.Fig=plt.figure(figsize=(FigSize,FigSize), dpi=100)
    plot_confusion_matrix(cm_normalized,CatAll)
    RamImage = io.BytesIO()
    g.Fig.savefig(RamImage , dpi=100, format='png')
    t.append("<h3>Confusion matrix divided by sum of lines</h3><p>The diagonal contains the <a href='https://en.wikipedia.org/wiki/Precision_and_recall#Recall' target='_blank'>recall</a> rate.</p><img src='data:image/png;base64,{}'/>".format(base64.encodebytes(RamImage.getvalue()).decode()) )

    # Version division par axe des prediction pas de div pas zero possible et permet de voir ce que c'est devenu (somme Vert.)
    cm_normalized = cm.astype('float')/SommeVNoZero
    # plt.figure(figsize=(8,8), dpi=100) # 800x800 px
    g.Fig.clf()
    plot_confusion_matrix(cm_normalized,CatAll)
    RamImage = io.BytesIO()
    g.Fig.savefig(RamImage , dpi=100, format='png')
    t.append("<h3>Confusion matrix divided by sum of columns</h3><p>The diagonal contains the <a href='https://en.wikipedia.org/wiki/Precision_and_recall#Precision' target='_blank'>precision</a> rate.</p><img src='data:image/png;base64,{}'/>".format(base64.encodebytes(RamImage.getvalue()).decode()) )
    # t.append("<br>"+txtbacktoproject)
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

