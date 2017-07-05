from flask import render_template, g, flash,json,make_response,request,send_file
from appli import app,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ntcv
from wtforms  import Form, BooleanField, StringField, validators,DateTimeField,IntegerField,FloatField,SelectField,TextAreaField
from flask_login import current_user
import appli.part.part_main as umain
import matplotlib,io,math,traceback
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from appli.part import PartDetClassLimit,PartRedClassLimit,GetClassLimitTxt,CTDFixedColByKey
from matplotlib.ticker import FuncFormatter, MaxNLocator

DepthTaxoHistoLimit=[0,25,50,75,100,125,150,200,250,300,350,400,450,500,600,700,800,900,1000,1250,1500,1750,2000,2250,2500,2750
    ,3000,3250,3500,3750,4000,4250,4500,4750,5000,5250,5500,5750,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,20000,50000]
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

def GetTaxoHistoWaterVolumeSQLExpr(field,retval='start'):
    Res="case "
    for i in range(1,len(DepthTaxoHistoLimit)):
        Res +=" when {2}<{0} then {1}".format(DepthTaxoHistoLimit[i]
                  ,DepthTaxoHistoLimit[i-1] if retval=='start' else (DepthTaxoHistoLimit[i-1]+DepthTaxoHistoLimit[i])/2
                  ,field)
    return Res+" end"


@app.route('/part/drawchart')
def part_drawchart():
    Couleurs=("#FF0000","#4385FF","#00BE00","#AA6E28","#FF9900","#FFD8B1","#808000","#FFEA00","#FFFAC8","#BEFF00",
        "#AAFFC3","#008080","#64FFFF","#000080","#800000","#820096","#E6BEFF","#FF00FF","#808080","#FFC9DE","#000000" )
    PrjColorMap={}
    PrjSampleCount={}
    PrjTitle={}
    try:
        gpr=request.args.getlist('gpr')
        gpd=request.args.getlist('gpd')
        gctd = request.args.getlist('ctd')
        gtaxo = request.args.getlist('taxolb')
        NbrChart=len(gpr)+len(gpd)+len(gctd)+len(gtaxo)
        samples=umain.GetFilteredSamples(GetVisibleOnly=True,RequiredPartVisibility='V')
        for S in samples:
            if S['pprojid'] not in PrjColorMap:
                PrjColorMap[S['pprojid']]=Couleurs[len(PrjColorMap)%len(Couleurs)]
                PrjTitle[S['pprojid']]=S['ptitle']
            PrjSampleCount[S['pprojid']]=PrjSampleCount.get(S['pprojid'],0)+1
        if len(PrjColorMap) > 1: NbrChart+=1
        FigSizeX=NbrChart
        if NbrChart>4: FigSizeX = 4
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
            # sql+=''.join([',case when watervolume>0 then class%02d/watervolume else 0 end as c%s'%(int(c[2:]),i)
            #               for i,c in enumerate(gpr) if c[0:2]=="cl"])
            sql+=''.join([',case when watervolume>0 then class%02d/watervolume else null end as c%s'%(int(c[2:]),i)
                          for i,c in enumerate(gpr) if c[0:2]=="cl"])
            sql+=''.join([',coalesce(biovol%02d) as c%s'%(int(c[2:]),i)
                          for i,c in enumerate(gpr) if c[0:2]=="bv"])
            sql += """ from part_histopart_reduit
             where psampleid=%(psampleid)s
             {}
            order by Y""".format(DepthFilter)
            graph=list(range(0,len(gpr)))
            for i, c in enumerate(gpr):
                graph[i] = Fig.add_subplot(FigSizeY  , FigSizeX , chartid + 1)
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
                    valcount=0
                    for rnum,r in enumerate(DBData):
                        if r[xcolname] is None:
                            continue
                        data[valcount]=(-r['y'],r[xcolname])
                        valcount +=1
                    # data = data[~np.isnan(data[:,1]),:] # Supprime les lignes avec une valeur à Nan et fait donc de l'extrapolation linaire
                    # sans cette ligne les null des colonnes cl devient des nan et ne sont pas tracès (rupture de ligne)
                    # cependant l'autre option est de le traiter au niveau de l'import
                    graph[i].plot(data[:valcount,1],data[:valcount,0],color=PrjColorMap[rs['pprojid']] if len(PrjColorMap)>1 else None)
            # fait après les plot pour avoir un echelle X bien callé avec les données et evite les erreurs log si la premiere serie n'as pas de valeurs
            for i, c in enumerate(gpr):
                if gvg('XScale') != 'I':
                    try:
                        if gvg('XScale') == 'O':
                            graph[i].set_xscale('log')
                        if gvg('XScale') == 'S':
                            graph[i].set_xscale('symlog')
                    except Exception as e:
                        # parfois s'il n'y a pas de données pas possible de passer en echelle log, on force alors linear sinon ça plante plus loin
                        graph[i].set_xscale('linear')
                else:
                    graph[i].set_xlim(left=0)
        # traitement des Graphes particulaire détaillés
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
                graph[i]=Fig.add_subplot(FigSizeY,FigSizeX,chartid+1)
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
                    valcount = 0
                    for rnum,r in enumerate(DBData):
                        if r[xcolname] is None:
                            continue
                        data[valcount]=(-r['y'],r[xcolname])
                        valcount +=1
                    graph[i].plot(data[:valcount,1],data[:valcount,0],color=PrjColorMap[rs['pprojid']] if len(PrjColorMap)>1 else None)
            # fait après les plot pour avoir un echelle X bien callé avec les données et evite les erreurs log si la premiere serie n'as pas de valeurs
            for i, c in enumerate(gpd):
                if gvg('XScale') != 'I':
                    try:
                        if gvg('XScale') == 'O':
                            graph[i].set_xscale('log')
                        if gvg('XScale') == 'S':
                            graph[i].set_xscale('symlog')
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
            order by lineno""".format(DepthFilter)
            graph=list(range(0,len(gctd)))
            for i, c in enumerate(gctd):
                graph[i]=Fig.add_subplot(FigSizeY,FigSizeX,chartid+1)
                graph[i].set_xlabel('CTD %s '%(CTDFixedColByKey.get(c)))
                chartid += 1
            for rs in samples:
                DBData = database.GetAll(sql, {'psampleid': rs['psampleid']})
                data = np.empty((len(DBData), 2))
                for i, c in enumerate(gctd):
                    xcolname="c%d"%i
                    valcount = 0
                    for rnum,r in enumerate(DBData):
                        if r[xcolname] is None:
                            continue
                        data[valcount]=(-r['y'],r[xcolname])
                        valcount +=1
                    graph[i].plot(data[:valcount,1],data[:valcount,0],color=PrjColorMap[rs['pprojid']] if len(PrjColorMap)>1 else None)

        # traitement des Graphes TAXO
        if len(gtaxo)>0:
            # sql = "select depth y ,1000*nbr/watervolume as x from part_histocat h "
            sql="select depth y ,nbr as x from part_histocat h "
            if gvg('taxochild')=='1':
                sql += " join taxonomy t0 on h.classif_id=t0.id "
                for i in range(1,15) :
                    sql += " left join taxonomy t{0} on t{1}.parent_id=t{0}.id ".format(i,i-1)
            # sql += " where psampleid=%(psampleid)s  and ( classif_id = %(taxoid)s and watervolume>0"
            sql += " where psampleid=%(psampleid)s  and ( classif_id = %(taxoid)s "
            if gvg('taxochild') == '1':
                for i in range(1, 15):
                    sql += " or t{}.id= %(taxoid)s".format(i)
            sql += " ){} order by Y""".format(DepthFilter)
            sqlWV =""" select {0} tranche,sum(watervolume) from part_histopart_det 
                    where psampleid=%(psampleid)s {1} group by tranche
                    """.format(GetTaxoHistoWaterVolumeSQLExpr("depth"),DepthFilter )
            graph=list(range(0,len(gtaxo)))
            for i, c in enumerate(gtaxo):
                NomTaxo = database.GetAll("""select concat(t.name,' (',p.name,')') nom 
                      from taxonomy t 
                      left JOIN taxonomy p on t.parent_id=p.id 
                      where t.id= %(taxoid)s""", {'taxoid': c})[0]['nom']
                if gvg('taxochild') == '1':
                    NomTaxo += " and children"
                graph[i]=Fig.add_subplot(FigSizeY,FigSizeX,chartid+1)
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
                    if rs['visibility'][1]>='V': # Visible ou exportable
                        DBData = database.GetAll(sql, {'psampleid': rs['psampleid'],'taxoid':c})
                        WV=database.GetAssoc2Col(sqlWV, {'psampleid': rs['psampleid']})
                    else: # si pas le droit, on fait comme s'il n'y avait pas de données.
                        DBData=[]
                        WV = {}
                    # print("{} =>{}".format(rs['psampleid'],WV))
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
                        # print(hist)
                        for ih,h in enumerate(hist):
                            if h>0:
                                if WV.get(edge[ih],0)>0:
                                    hist[ih]=1000*h/WV.get(edge[ih])
                                else: hist[ih]=0
                        # print(hist,edge)
                        # Y=-(edge[:-1]+edge[1:])/2 calcul du milieu de l'espace
                        Y = -edge[:-1]
                        # Y=categ
                        graph[i].step(hist,Y,color=PrjColorMap[rs['pprojid']] if len(PrjColorMap)>1 else None)
                        # bottom, top=graph[i].get_ylim()
                        # bottom=min(bottom,categ.min()-1)
                        # graph[i].set_ylim(bottom, top)
                    bottom, top = graph[i].get_ylim()
                    if gvg('filt_depthmin'):
                        top=-float(gvg('filt_depthmin'))
                    if gvg('filt_depthmax'):
                        bottom=-float(gvg('filt_depthmax'))
                    elif len(WV)>0:
                        bottom =min(bottom,-max(WV.keys()))
                    if top>0: top=0
                    if bottom>=top:bottom=top-10
                    graph[i].set_ylim(bottom, top)
        # generation du graphique qui liste les projets
        if len(PrjColorMap) > 1:
            data = np.empty((len(PrjSampleCount), 2))
            PrjLabel=[]
            GColor=[]
            for i,(k,v) in enumerate(PrjSampleCount.items()):
                data[i]=i,v
                PrjLabel.append(PrjTitle[k])
                GColor.append(PrjColorMap[k])
            graph = Fig.add_subplot(FigSizeY, FigSizeX, chartid + 1)
            graph.barh(data[:,0],data[:,1],color=GColor)
            graph.set_yticks(np.arange(len(PrjLabel))+0.4)
            graph.set_yticklabels(PrjLabel)
            graph.set_xlabel("Sample count per project + Legend")

        Fig.tight_layout()
    except Exception as e:
        Fig = plt.figure(figsize=(8,6), dpi=100)
        tb_list = traceback.format_tb(e.__traceback__)
        s = "%s - %s "%(str(e.__class__), str(e))
        for m in tb_list[::-1]:
            s += "\n" + m
        Fig.text(0,0.5,s)
        print(s)
    png_output = io.BytesIO()
    Fig.savefig(png_output)
    png_output.seek(0)
    return send_file(png_output, mimetype='image/png')
