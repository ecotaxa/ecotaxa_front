from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask_login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp,XSSEscape,ntcv
from pathlib import Path
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security import login_required
from flask_security.decorators import roles_accepted

from appli.constants import DayTimeList
from appli.search.leftfilters import getcommonfilters
import os,time,math,collections,appli,psycopg2.extras
from appli.database import GetAll,GetClassifQualClass,ExecSQL,db,GetAssoc
from appli.project.main import FilterList


######################################################################################################################
@app.route('/explore/')
def indexExplore():
    data={'pageoffset':gvg("pageoffset","0")}
    for k,v in FilterList.items():
        data[k]=gvg(k,v)
    data['inexplore']=True
    data["projid"]=gvg("projid",0)
    data["taxochild"]=gvg("taxochild",'1')
    data["sample_for_select"]=""
    if data["samples"]:
        for r in GetAll("select sampleid,orig_id from samples where sampleid =any(%s)" , ([int(x) for x in data["samples"].split(',')],),doXSSEscape=True):
            data["sample_for_select"]+="\n<option value='{sampleid}' selected>{orig_id}</option> ".format(**r)
    data["projects_for_select"]=""
    if data["projid"]:
        for r in GetAll("select projid,title from projects where projid =any(%s) and visible=true" , ([int(x) for x in data["projid"].split(',')],),doXSSEscape=True):
            data["projects_for_select"]+="\n<option value='{projid}' selected>{title}</option> ".format(**r)
    data["taxo_for_select"]=""
    if gvg("taxo[]"):
        print(gvg("taxo[]"))
        for r in GetAll("SELECT id, display_name FROM taxonomy WHERE  id =any(%s) order by name",([int(x) for x in request.args.getlist("taxo[]")],),debug=False):
            data["taxo_for_select"]+="\n<option value='{id}' selected>{display_name}</option> ".format(**r)
    data["month_for_select"] = ""
    for (k,v) in enumerate(('January','February','March','April','May','June','July','August','September','October','November','December'),start=1):
        data["month_for_select"] += "\n<option value='{1}' {0}>{2}</option> ".format('selected' if str(k) in data['month'].split(',') else '',k,v)
    data["daytime_for_select"] = ""
    for (k,v) in DayTimeList.items():
        data["daytime_for_select"] += "\n<option value='{1}' {0}>{2}</option> ".format('selected' if str(k) in data['daytime'].split(',') else '',k,v)

    right='dodefault'
    classiftab=""
    appli.AddJobsSummaryForTemplate()
    filtertab=getcommonfilters(data)
    return render_template('search/explore.html',top="",lefta=classiftab,leftb=filtertab
                           ,right=right,data=data)

######################################################################################################################
@app.route('/explore/LoadRightPane', methods=['GET', 'POST'])
def ExploreLoadRightPane():
    # récupération des parametres d'affichage
    Filt={}
    for k,v in FilterList.items():
        Filt[k]=gvp(k,v)
    ipp=int(Filt["ipp"])
    zoom=int(Filt["zoom"])
    t=["<a name='toppage'/>"]
    sqlparam={'projid':gvp("projid")}

    whereclause=""
    sql="""select o.objid,o.classif_qual  ,o.objdate,to_char(o.objtime,'HH24:MI') objtime
    ,o.classif_id,o.classif_who,o.sampleid,random_value,o.projid,o.orig_id
   from objects o
where o.classif_qual='V'
"""
    if gvp("taxo[]"):
        taxoids=",".join((str(int(x)) for x in request.form.getlist("taxo[]")))
        if gvp("taxochild")=="1":
            # whereclause+=""" and o.classif_id in (WITH RECURSIVE rq(id) as ( select id FROM taxonomy where id in(%s)
            #                         union
            #                         SELECT t.id FROM rq JOIN taxonomy t ON rq.id = t.parent_id and (t.nbrobjcum>0 or t.nbrobj>0)
            #                         ) select id from rq)"""%(taxoids,)
            # Sur les petits nombres de ref le in est plus performant que la sous requete
            taxoids=",".join((str(int(x[0])) for x in GetAll("""WITH RECURSIVE rq(id) as ( select id FROM taxonomy where id in(%s)
                                    union
                                    SELECT t.id FROM rq JOIN taxonomy t ON rq.id = t.parent_id 
                                    ) select id from rq """%(taxoids,))))
            whereclause+=" and o.classif_id in ("+taxoids+")" # optimisation qui provoque de faux résultats : and (t.nbrobjcum>0 or t.nbrobj>0)
        else:
            whereclause+=" and o.classif_id in ("+taxoids+")"

    if gvp("MapN")!="" and gvp("MapW")!="" and gvp("MapE")!="" and gvp("MapS")!="":
        whereclause+=" and o.latitude between %(MapS)s and %(MapN)s and o.longitude between %(MapW)s and %(MapE)s  "
        sqlparam['MapN']=gvp("MapN")
        sqlparam['MapW']=gvp("MapW")
        sqlparam['MapE']=gvp("MapE")
        sqlparam['MapS']=gvp("MapS")

    if gvp("depthmin")!="" and gvp("depthmax")!="" :
        whereclause+=" and o.depth_min between %(depthmin)s and %(depthmax)s and o.depth_max between %(depthmin)s and %(depthmax)s  "
        sqlparam['depthmin']=gvp("depthmin")
        sqlparam['depthmax']=gvp("depthmax")

    if gvp("samples")!="":
        whereclause+=" and o.sampleid= any (%(samples)s) "
        sqlparam['samples']=[int(x) for x in gvp("samples").split(',')]

    if gvp("instrum")!="":
        whereclause += " and o.acquisid in (select acq.acquisid from acquisitions acq, samples sam where acq.acq_sample_id = sam.sampleid and acq.instrument ilike %(instrum)s "+\
                       ("and sam.projid= any (%(projid)s)" if gvp("projid")!="" else "")+\
                       " )"
        sqlparam['instrum']='%'+gvp("instrum")+'%'
    PageTopProjectLink=MapForProject=None
    if gvp("projid")!="":
        whereclause+=" and o.projid= any (%(projid)s) "
        sqlparam['projid']=[int(x) for x in gvp("projid").split(',')]
        if len(sqlparam['projid'])==1:
            PageTopProjectLink = "<p class='bg-info' style='font-size: larger;font-weight: bold;'>You can explore this project in more details on its <a href='/prj/{0}'>dedicated page</a></p>".format(str(sqlparam['projid'][0]))
    if gvp("fromdate")!="":
        whereclause+=" and o.objdate>= to_date(%(fromdate)s,'YYYY-MM-DD') "
        sqlparam['fromdate']=gvp("fromdate")
    if gvp("todate")!="":
        whereclause+=" and o.objdate<= to_date(%(todate)s,'YYYY-MM-DD') "
        sqlparam['todate']=gvp("todate")
    if gvp("month")!="":
        whereclause+=" and extract(month from o.objdate) = any (%(month)s) "
        sqlparam['month']=[int(x) for x in gvp("month").split(',')]
    if gvp("daytime")!="":
        whereclause+=" and o.sunpos= any (%(daytime)s) "
        sqlparam['daytime']=[x for x in gvp("daytime").split(',')]

    if gvp("inverttime")=="1":
        if gvp("fromtime")!="" and gvp("totime")!="":
            whereclause+=" and (o.objtime<= time %(fromtime)s or o.objtime>= time %(totime)s)"
            sqlparam['fromtime']=gvp("fromtime")
            sqlparam['totime']=gvp("totime")
    else:
        if gvp("fromtime")!="":
            whereclause+=" and o.objtime>= time %(fromtime)s "
            sqlparam['fromtime']=gvp("fromtime")
        if gvp("totime")!="":
            whereclause+=" and objtime<= time %(totime)s "
            sqlparam['totime']=gvp("totime")
    sql+=whereclause
    ExtraEndScript=""
    if whereclause=="": # si aucune clause, on prend un projet au hasard
        randomproject=GetAll("select projid,title from projects where visible=true and pctvalidated>1 order by random() limit 1")
        if randomproject:
            randomproject=randomproject[0]
            MapForProject = str(randomproject[0])
            sql+=" and o.projid= %s "%(randomproject[0])
            ExtraEndScript="""$('#headersubtitle').html('Randomly selected project : <a href="?projid={0}">{1}</a>');""".format(randomproject['projid'],XSSEscape(randomproject['title']))
    sql+="  order by random_value Limit %d"%(2*ipp,)
    # pour de meilleure perf plus de random ici et du coup on prend 20xipp pour créer un peu d'aléa
    # sql+="  Limit %d"%(20*ipp,) # desactivé suite à split table objects mais pourrait devoir revenir.

    #filt_fromdate,#filt_todate
    sql="""select o.*,t.display_name taxoname,u.name classifwhoname,i.file_name,s.orig_id samplename
                  ,i.height,i.width,i.thumb_file_name,i.thumb_height,i.thumb_width,o.orig_id,
                  (SELECT COUNT(img.imgrank) FROM images img WHERE img.objid = o.objid) AS imgcount
                  from ("""+sql+""")o
left Join images i on o.objid=i.objid and i.imgrank = (select min(imgrank) from images img where img.objid = o.objid)
left JOIN taxonomy t on o.classif_id=t.id
LEFT JOIN users u on o.classif_who=u.id
LEFT JOIN  samples s on o.sampleid=s.sampleid
left Join obj_field ofi on ofi.objfid=o.objid
where o.projid in (select projid from projects where visible=true)"""
    # if whereclause!="": # on ne tri pas en random global s'il n'y a aucune criteres, impact de perf
    sql+=" order by random_value  "
    # sql+=" order by random()  "
    sql+=" Limit %d  "%(ipp,)
    res=GetAll(sql,sqlparam,debug=False,doXSSEscape=True)
    trcount=1
    LineStart=""
    if(PageTopProjectLink):
        t.append(PageTopProjectLink)
    if MapForProject:
        t.append(render_template("search/explore_inserted_popup.html",Projid=MapForProject))
    t.append("<table class=imgtab><tr id=tr1>"+LineStart)
    WidthOnRow=0
    #récuperation et ajustement des dimensions de la zone d'affichage
    try:
        PageWidth=int(gvp("resultwidth"))-40 # on laisse un peu de marge à droite et la scroolbar
        if PageWidth<200 : PageWidth=200
    except:
        PageWidth=200
    try:
        WindowHeight=int(gvp("windowheight"))-100 # on enleve le bandeau du haut
        if WindowHeight<200 : WindowHeight=200
    except:
        WindowHeight=200
    #print("PageWidth=%s, WindowHeight=%s"%(PageWidth,WindowHeight))
    # Calcul des dimmensions et affichage des images
    for r in res:
        filename=r['file_name']
        origwidth=r['width']
        origheight=r['height']
        thumbfilename=r['thumb_file_name']
        thumbwidth=r['thumb_width']
        if origwidth is None: # pas d'image associé, pas trés normal mais arrive pour les subset sans images
            width=80
            height=40
        else:
            width=origwidth*zoom//100
            height=origheight*zoom//100
        if max(width,height)<120: # en dessous de 120 px de coté on ne fait plus le scaling
            if max(origwidth,origheight)<120:
                width=origwidth   # si l'image originale est petite on l'affiche telle quelle
                height=origheight
            elif max(origwidth,origheight)==origwidth:
                width=120
                height=origheight*120//origwidth
                if height<1 : height=1
            else:
                height=120
                width=origwidth*120//origheight
                if width<1 : width=1

        # On limite les images pour qu'elles tiennent toujours dans l'écran
        if width>PageWidth:
            width=PageWidth
            height=math.trunc(r['height']*width/r['width'])
            if height==0: height=1
        if height>WindowHeight:
            height=WindowHeight
            width=math.trunc(r['width']*height/r['height'])
            if width==0: width=1
        if WidthOnRow!=0 and (WidthOnRow+width)>PageWidth:
            trcount+=1
            t.append("</tr></table><table class=imgtab><tr id=tr%d>%s"%(trcount,LineStart))
            WidthOnRow=0
        cellwidth=width+22
        if cellwidth<80: cellwidth=80 # on considère au moins 80 car avec les label c'est rarement moins
        # Met la fenetre de zoon la ou il y plus de place, sachant qu'elle fait 400px et ne peut donc pas être callée à gauche des premieres images.
        if (WidthOnRow+cellwidth)>(PageWidth/2):
            pos='left'
        else: pos='right'
        #Si l'image affiché est plus petite que la miniature, afficher la miniature.
        if thumbwidth is None or thumbwidth<width or thumbfilename is None: # sinon (si la miniature est plus petite que l'image à afficher )
            thumbfilename=filename # la miniature est l'image elle même
        txt="<td width={0}>".format(cellwidth)
        if filename:
            txt+="<img class='lazy' id=I{3} data-src='/vault/{5}' data-zoom-image='{0}' width={1} height={2} pos={4}>"\
                .format(filename,width,height,r['objid'],pos,thumbfilename)
        else:
            txt+="No Image"
        # Génération de la popover qui apparait pour donner quelques détails sur l'image
        poptitletxt="%s"%(r['orig_id'],)
        # poptxt="%s"%(r['taxoname'],)
        poptxt=""
        if r['classifwhoname']!="":
            poptxt+="<em>by</em> %s"%(r['classifwhoname'])
        poptxt+="<br><em>in</em> "+ntcv(r['samplename'])
        popattribute="data-title=\"{0}\" data-content=\"{1}\" data-placement='{2}'".format(poptitletxt, poptxt, 'left' if WidthOnRow > 500 else 'right')

        txt+="""<div class='subimg {1}' {2}>
<div class='taxo'>{0}</div> </div>
<div class=ddet><span class=ddets><span class='glyphicon glyphicon-eye-open'></span> {3}</div>"""\
            .format(r['taxoname'],"",popattribute
                    ,"(%d)"%(r['imgcount'],) if r['imgcount'] is not None and r['imgcount']>1 else "")
        txt+="</td>"

        # WidthOnRow+=max(cellwidth,80) # on ajoute au moins 80 car avec les label c'est rarement moins
        WidthOnRow+=cellwidth+5 # 5 = border-spacing = espace inter image
        t.append(txt)

    t.append("</tr></table>")
    if len(res)==0:
        t.append("""<div class='alert alert-warning' role='alert' style='margin: 10px;font-size:larger;' >
        <span class='glyphicon glyphicon-remove-sign' style='color:#DD2222;'></span>
        Your selection does not return any object. <br>It may be too limited by the selected filters. <br>Try again releasing the selection criteria</div>""")
    t.append("""
    <script>
        PostAddImages();
        %s
    </script>"""%ExtraEndScript)
    return "\n".join(t)

