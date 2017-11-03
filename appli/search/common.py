# -*- coding: utf-8 -*-
from pathlib import Path
import os,time
from flask import  render_template,request,json
from appli import app,gvg, database,DecodeEqualList


@app.route('/search/users')
def searchusers():
    term=gvg("q")
    if len(term)<2:
        return "[]"
    term=R"%"+term+R"%"
    res = database.GetAll("SELECT id, name FROM users WHERE  name ILIKE %s and active=true order by name limit 1000", (term,),debug=False)
    return json.dumps([dict(id=r[0],text=r[1]) for r in res])


@app.route("/search/samples")
def searchsamples():
    term="%"+gvg("q")+"%"
    projid=""
    if gvg("projid")!="":
        projid=str(int(gvg("projid")))
    if gvg("projid[]")!="":
        projid=",".join([str(int(x)) for x in request.args.getlist("projid[]")])
    if projid=="":
        return "[]"
    res = database.GetAll("SELECT sampleid, orig_id FROM samples WHERE  projid in ({0}) and orig_id like %s order by orig_id limit 2000".format(projid), (term,))
    if gvg("format",'J')=='J': # version JSon par defaut
        return json.dumps([dict(id=r[0],text=r[1]) for r in res])
    return render_template('search/samples.html', samples=res)

@app.route("/search/exploreproject")
def searchexploreproject():
    term=("%"+gvg("q")+"%").lower()
    res = database.GetAll("SELECT projid, title FROM projects WHERE  lower(title) like %s and visible=true order by lower(title) ", (term,),debug=True)
    return json.dumps([dict(id=r[0],text=r[1]) for r in res])


@app.route('/common/ServerFolderSelect')
def ServerFolderSelect():
    res = []
    return render_template('common/fileserverpopup.html',root_elements=res,targetid=gvg("target","ServerPath"),ziponly=gvg('ZipOnly','N'))

@app.route('/common/ServerFolderSelectJSON')
def ServerFolderSelectJSON():
    ServerRoot=Path(app.config['SERVERLOADAREA'])
    CurrentPath=ServerRoot
    parent=gvg("id")
    if parent!='#':
        CurrentPath=ServerRoot.joinpath(Path(parent))
    res=[]
    for x in CurrentPath.iterdir():
        rr=x.relative_to(ServerRoot).as_posix()
        rc=x.relative_to(CurrentPath).as_posix()
        try:
            if x.is_dir():
                if gvg('ZipOnly')=='Y':
                    res.append(dict(id=rr,text="<span class=v>"+rc+"</span> ",parent=parent,children=True))
                else:
                    res.append(dict(id=rr,text="<span class=v>"+rc+"</span> <span class='TaxoSel label label-default'>Select</span>",parent=parent,children=True))
            if x.suffix.lower()==".zip":
                fi=os.stat( x.as_posix())
                res.append(dict(id=rr,text="<span class=v>"+"%s (%.1f Mb : %s)"%(rc,fi.st_size/1048576,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(fi.st_mtime)))+"</span> <span class='TaxoSel label label-default'>Select</span>",parent=parent,children=False))
        except:
            None # le parcours des fichier peu planter sur system volume information par exemple.
    res.sort(key=lambda val: str.upper(val['id']),reverse=False)
    return json.dumps(res)

@app.route("/search/instrumlist")
def searchinstrumlist():
    sql="select DISTINCT lower(instrument) from acquisitions where instrument is not null and instrument!='' "
    if gvg("projid")!="":
        sql += " and projid="+str(int(gvg("projid")))
    res = database.GetAll(sql+" order by 1")
    txt="List of available Intruments : <hr><ul id=InstrumList>"
    for r in res:
        txt +="\n<li>{0}</li>".format(r[0])
    txt += """</ul>
    <hr>
    &nbsp;<button type="button" class="btn btn-default btn-"  onclick="$('#PopupDetails').modal('hide');">Close</button>
    <br><br>
    <script>
    $('#InstrumList li').click(function(){
        $('#filt_instrum').val($(this).text());
        $('#PopupDetails').modal('hide');
    }).css('cursor','pointer');
    </script>
    """
    return txt

@app.route("/search/gettaxomapping")
def searchgettaxomapping():
    Prj = database.Projects.query.filter_by(projid=int(gvg("projid"))).first()
    classifsettings = DecodeEqualList(Prj.classifsettings)
    PostTaxoMapping=classifsettings.get("posttaxomapping","")
    res={'mapping':{},'taxo':{}}
    if PostTaxoMapping!='':
        res['mapping'] = {el[0].strip(): el[1].strip() for el in
                           [el.split(':') for el in PostTaxoMapping.split(',') if el != '']}
        sql = """SELECT tf.id, tf.name||case when p1.name is not null and tf.name not like '%% %%'  then ' ('||p1.name||')' else ' ' end as name
                 FROM taxonomy tf
                left join taxonomy p1 on tf.parent_id=p1.id
                WHERE  tf.id = any (%s) 
                order by tf.name limit 2000"""
        res['taxo'] = {x[0]:x[1] for x in database.GetAll(sql,([int(x) for x in res['mapping'].values()],))}

    return json.dumps(res)
