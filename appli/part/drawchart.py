from flask import render_template, g, flash,json,make_response,request,send_file
from appli import app,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ntcv
from wtforms  import Form, BooleanField, StringField, validators,DateTimeField,IntegerField,FloatField,SelectField,TextAreaField
from flask_login import current_user
import appli.part.part_main as umain
import matplotlib,io,math
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from appli.part import PartDetClassLimit,PartRedClassLimit,GetClassLimitTxt,CTDFixedColByKey
from matplotlib.ticker import FuncFormatter, MaxNLocator

DepthTaxoHistoLimit=[0,25,50,75,100,150,200,250,500,750,1000,2000,3000,4000,5000,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,20000,50000]
def GetTaxoHistoLimit(MaxDepth):
    Res=[]
    BreakOnNext=False
    for d in DepthTaxoHistoLimit:
        Res.append(d)
        if BreakOnNext:
            break
        if d>MaxDepth:
            BreakOnNext=True
    return Res

@app.route('/part/drawchart')
def part_drawchart():
    gpr=request.args.getlist('gpr')
    gpd=request.args.getlist('gpd')
    gctd = request.args.getlist('ctd')
    gtaxo = request.args.getlist('taxolb')
    NbrChart=len(gpr)+len(gpd)+len(gctd)+len(gtaxo)
    FigSizeX=NbrChart
    if NbrChart>4: FigSizeX = 4
    samples=umain.GetFilteredSamples(GetVisibleOnly=True)
    FigSizeY=math.ceil(NbrChart/FigSizeX)
    font = {'family' : 'arial','weight' : 'normal','size'   : 10}
    plt.rc('font', **font)
    plt.rcParams['lines.linewidth'] = 0.5
    Fig = plt.figure(figsize=(FigSizeX*4, FigSizeY*5), dpi=100)
    chartid=0
    DepthFilter=""
    if gvg('filt_depthmin'):
        DepthFilter += " and depth>=%d"%int(gvg('filt_depthmin'))
    if gvg('filt_depthmax'):
        DepthFilter += " and depth<=%d"%int(gvg('filt_depthmax'))
    # traitement des Graphes particulaire réduit
    if len(gpr)>0:
        sql="select depth y "
        sql+=''.join([',case when watervolume>0 then class%02d/watervolume else 0 end as c%s'%(int(c[2:]),i)
                      for i,c in enumerate(gpr) if c[0:2]=="cl"])
        sql+=''.join([',coalesce(biovol%02d) as c%s'%(int(c[2:]),i)
                      for i,c in enumerate(gpr) if c[0:2]=="bv"])
        sql += """ from part_histopart_reduit
         where psampleid=%(psampleid)s
         {}
        order by Y""".format(DepthFilter)
        graph=list(range(0,len(gpr)))
        for i, c in enumerate(gpr):
            graph[i]=Fig.add_subplot(FigSizeY*100+FigSizeX*10+chartid+1)
            if c[0:2] == "cl":
                graph[i].set_xlabel('Particle red. class %s (%s) #/l'%(c,GetClassLimitTxt(PartRedClassLimit,int(c[2:]))))
            if c[0:2] == "bv":
                graph[i].set_xlabel('Biovolume red. class %s (%s) µl/l'%(c,GetClassLimitTxt(PartRedClassLimit,int(c[2:]))))
            chartid += 1
        for rs in samples:
            DBData = database.GetAll(sql, {'psampleid': rs['psampleid']})
            data = np.empty((len(DBData), 2))
            for i, c in enumerate(gpr):
                xcolname="c%d"%i
                for rnum,r in enumerate(DBData):
                    data[rnum]=(-r['y'],r[xcolname])
                graph[i].plot(data[:,1],data[:,0])
        # fait après les plot pour avoir un echelle X bien callé avec les données et evite les erreurs log si la premiere serie n'as pas de valeurs
        for i, c in enumerate(gpr):
            if gvg('XLog') == 'Y':
                try:
                    graph[i].set_xscale('log')
                except Exception as e:
                    # parfois s'il n'y a pas de données pas possible de passer en echelle log, on force alors linear sinon ça plante plus loin
                    graph[i].set_xscale('linear')
            else:
                graph[i].set_xlim(left=0)
    # traitement des Graphes particulaire réduit
    if len(gpd)>0:
        sql="select depth y "
        sql+=''.join([',case when watervolume>0 then class%02d/watervolume else 0 end as c%s'%(int(c[2:]),i)
                      for i,c in enumerate(gpd) if c[0:2]=="cl"])
        sql+=''.join([',coalesce(biovol%02d) as c%s'%(int(c[2:]),i)
                      for i,c in enumerate(gpd) if c[0:2]=="bv"])
        sql += """ from part_histopart_det
         where psampleid=%(psampleid)s
         {}
        order by Y""".format(DepthFilter)
        graph=list(range(0,len(gpd)))
        for i, c in enumerate(gpd):
            graph[i]=Fig.add_subplot(FigSizeY*100+FigSizeX*10+chartid+1)
            if c[0:2] == "cl":
                graph[i].set_xlabel('Particle det. class %s (%s) #/l'%(c,GetClassLimitTxt(PartDetClassLimit,int(c[2:]))))
            if c[0:2] == "bv":
                graph[i].set_xlabel('Biovolume det. class %s (%s) µl/l'%(c,GetClassLimitTxt(PartDetClassLimit,int(c[2:]))))
            chartid += 1
        for rs in samples:
            DBData = database.GetAll(sql, {'psampleid': rs['psampleid']})
            data = np.empty((len(DBData), 2))
            for i, c in enumerate(gpd):
                xcolname="c%d"%i
                for rnum,r in enumerate(DBData):
                    data[rnum]=(-r['y'],r[xcolname])
                graph[i].plot(data[:,1],data[:,0])
        # fait après les plot pour avoir un echelle X bien callé avec les données et evite les erreurs log si la premiere serie n'as pas de valeurs
        for i, c in enumerate(gpd):
            if gvg('XLog') == 'Y':
                try:
                    graph[i].set_xscale('log')
                except Exception as e:
                    # parfois s'il n'y a pas de données pas possible de passer en echelle log, on force alors linear sinon ça plante plus loin
                    graph[i].set_xscale('linear')
            else:
                graph[i].set_xlim(left=0)

    # traitement des Graphes CTD
    if len(gctd)>0:
        sql="select depth y ,"+','.join(['%s as c%d'%(c,i) for i,c in enumerate(gctd)])
        sql += """ from part_ctd
         where psampleid=%(psampleid)s
         {}
        order by Y""".format(DepthFilter)
        graph=list(range(0,len(gctd)))
        for i, c in enumerate(gctd):
            graph[i]=Fig.add_subplot(FigSizeY*100+FigSizeX*10+chartid+1)
            graph[i].set_xlabel('CTD %s '%(CTDFixedColByKey.get(c)))
            chartid += 1
        for rs in samples:
            DBData = database.GetAll(sql, {'psampleid': rs['psampleid']})
            data = np.empty((len(DBData), 2))
            for i, c in enumerate(gctd):
                xcolname="c%d"%i
                for rnum,r in enumerate(DBData):
                    data[rnum]=(-r['y'],r[xcolname])
                graph[i].plot(data[:,1],data[:,0])

    # traitement des Graphes TAXO
    if len(gtaxo)>0:
        sql="select depth y ,nbr as x from part_histocat h "
        if gvg('taxochild')=='1':
            sql += " join taxonomy t0 on h.classif_id=t0.id "
            for i in range(1,15) :
                sql += " left join taxonomy t{0} on t{1}.parent_id=t{0}.id ".format(i,i-1)
        sql += " where psampleid=%(psampleid)s  and ( classif_id = %(taxoid)s "
        if gvg('taxochild') == '1':
            for i in range(1, 15):
                sql += " or t{}.id= %(taxoid)s".format(i)
        sql += " ){} order by Y""".format(DepthFilter)
        graph=list(range(0,len(gtaxo)))
        for i, c in enumerate(gtaxo):
            NomTaxo = database.GetAll("""select concat(t.name,' (',p.name,')') nom 
                  from taxonomy t 
                  left JOIN taxonomy p on t.parent_id=p.id 
                  where t.id= %(taxoid)s""", {'taxoid': c})[0]['nom']
            if gvg('taxochild') == '1':
                NomTaxo += " and childs"
            graph[i]=Fig.add_subplot(FigSizeY*100+FigSizeX*10+chartid+1)
            graph[i].set_xlabel('%s #/m3'%(NomTaxo))
            # graph[i].set_yscale('log')
            def format_fn(tick_val, tick_pos):
                if -int(tick_val) <len(DepthTaxoHistoLimit) and -int(tick_val) >=0:
                    return DepthTaxoHistoLimit[-int(tick_val)]
                else:
                    return ''


            ##graph[i].yaxis.set_major_formatter(FuncFormatter(format_fn))
            # graph[i].set_yticklabels(GetTaxoHistoLimit(20000))
            # graph[i].set_yticklabels(["a","b","c"])
            # graph[i].yticks(np.arange(5), ('Tom', 'Dick', 'Harry', 'Sally', 'Sue'))
            ##graph[i].set_yticks(np.arange(0,-20,-1))
            chartid += 1
            for isample,rs in enumerate(samples):
                DBData = database.GetAll(sql, {'psampleid': rs['psampleid'],'taxoid':c})
                if len(DBData)>0:
                    data = np.empty((len(DBData), 2))
                    for rnum,r in enumerate(DBData):
                        data[rnum]=(r['y'],r['x'])
                    # hist,edge=np.histogram(data[:,0],bins=GetTaxoHistoLimit(data[:,0].max()),weights=data[:,1])
                    # Y=(edge[:-1]+edge[1:])/2
                    # graph[i].step(hist,Y)
                    # graph[i].hist(data[:,0],bins=GetTaxoHistoLimit(data[:,0].max()),weights=data[:,1],histtype ='step',orientation ='horizontal')
                    bins=GetTaxoHistoLimit(data[:,0].max())
                    categ=-np.arange(len(bins)-1) #-isample*0.1
                    hist,edge=np.histogram(data[:,0],bins=bins,weights=data[:,1])
                    print(hist,edge)
                    Y=-(edge[:-1]+edge[1:])/2
                    # Y=categ
                    graph[i].step(hist,Y)
                    #TODO Calculer les concentration et non pas les NBR
                    # bottom, top=graph[i].get_ylim()
                    # bottom=min(bottom,categ.min()-1)
                    # graph[i].set_ylim(bottom, top)
    Fig.tight_layout()
    png_output = io.BytesIO()
    Fig.savefig(png_output)
    png_output.seek(0)
    return send_file(png_output, mimetype='image/png')
