from flask import render_template, g, flash,json,make_response,request,send_file
from appli import app,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ntcv
from wtforms  import Form, BooleanField, StringField, validators,DateTimeField,IntegerField,FloatField,SelectField,TextAreaField
from flask_login import current_user
import appli.uvp.uvp_main as umain
import matplotlib,io,math
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from appli.uvp import PartDetClassLimit,PartRedClassLimit


def GetClassLimitTxt(LimitTab,Classe):
    if LimitTab[Classe]<1:
        txt = '%.4g-%.4g µm' % (LimitTab[Classe - 1]*1000, LimitTab[Classe]*1000)
    else:
        txt='%.4g-%.4g mm'%(LimitTab[Classe-1],LimitTab[Classe])
    return txt


@app.route('/uvp/drawchart')
def uvp_drawchart():
    gpr=request.args.getlist('gpr')
    gpd=request.args.getlist('gpd')
    gctd = request.args.getlist('gctd')
    NbrChart=len(gpr)+len(gpd)+len(gctd)
    FigSizeX=NbrChart
    if NbrChart>4: FigSizeX = 4
    samples=umain.GetFilteredSamples(GetVisibleOnly=True)
    FigSizeY=math.ceil(NbrChart/FigSizeX)
    font = {'family' : 'arial','weight' : 'normal','size'   : 10}
    plt.rc('font', **font)
    plt.rcParams['lines.linewidth'] = 0.5
    Fig = plt.figure(figsize=(FigSizeX*4, FigSizeY*5), dpi=100)
    chartid=0
    # traitement des Graphes particulaire réduit
    if len(gpr)>0:
        sql="select depth y ,"+','.join(['case when watervolume>0 then class%02d/watervolume else 0 end as c%d'%(int(c),i) for i,c in enumerate(gpr)])
        sql += """ from uvp_histopart_reduit
         where usampleid=%(usampleid)s
        order by Y"""
        graph=list(range(0,len(gpr)))
        for i, c in enumerate(gpr):
            graph[i]=Fig.add_subplot(FigSizeY*100+FigSizeX*10+chartid+1)
            graph[i].set_xlabel('Particle red. class %s (%s) #/L'%(c,GetClassLimitTxt(PartRedClassLimit,int(c))))
            chartid += 1
        for rs in samples:
            DBData = database.GetAll(sql, {'usampleid': rs['usampleid']})
            data = np.empty((len(DBData), 2))
            for i, c in enumerate(gpr):
                xcolname="c%d"%i
                for rnum,r in enumerate(DBData):
                    data[rnum]=(-r['y'],r[xcolname])
                graph[i].plot(data[:,1],data[:,0])
    # traitement des Graphes particulaire réduit
    if len(gpd)>0:
        sql="select depth y ,"+','.join(['case when watervolume>0 then class%02d/watervolume else 0 end as c%d'%(int(c),i) for i,c in enumerate(gpd)])
        sql += """ from uvp_histopart_det
         where usampleid=%(usampleid)s
        order by Y"""
        graph=list(range(0,len(gpd)))
        for i, c in enumerate(gpd):
            graph[i]=Fig.add_subplot(FigSizeY*100+FigSizeX*10+chartid+1)
            graph[i].set_xlabel('Particle det. class %s (%s) #/L'%(c,GetClassLimitTxt(PartDetClassLimit,int(c))))
            chartid += 1
        for rs in samples:
            DBData = database.GetAll(sql, {'usampleid': rs['usampleid']})
            data = np.empty((len(DBData), 2))
            for i, c in enumerate(gpd):
                xcolname="c%d"%i
                for rnum,r in enumerate(DBData):
                    data[rnum]=(-r['y'],r[xcolname])
                graph[i].plot(data[:,1],data[:,0])


    Fig.tight_layout()
    png_output = io.BytesIO()
    Fig.savefig(png_output)
    png_output.seek(0)
    return send_file(png_output, mimetype='image/png')
