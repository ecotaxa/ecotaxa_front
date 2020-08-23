from flask import Blueprint, render_template, g, flash, request, url_for, json
from flask_login import current_user
from appli import app, ObjectToStr, PrintInCharte, database, gvg, gvp, user_datastore, DecodeEqualList, ScaleForDisplay, \
    ComputeLimitForImage
from pathlib import Path
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security import login_required
from flask_security.decorators import roles_accepted
from collections import OrderedDict
import os, time, math, collections, appli
from appli.database import GetAll, GetClassifQualClass, ExecSQL, db, GetAssoc2Col
from appli.project.main import RecalcProjectTaxoStat


def MakeHTMLSelect(selname, Values, SelValue="", ExtraTags="", AddEmptyLineFirst=False, SortByValues=False):
    txt = "<select name={0} id={0} {1} >".format(selname, ExtraTags)
    if AddEmptyLineFirst:
        txt += "<option/>"
    if SortByValues:
        Vals = OrderedDict(sorted(Values.items(), key=lambda t: t[1]))
    else:
        Vals = Values
    for k, v in Values.items():
        txt += "<option value={0} {1}>{2}</option>".format(k, "selected" if k == v else "", v)
    txt += "</select>"
    return txt;


######################################################################################################################
@app.route('/prj/EditAnnot/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def PrjEditAnnot(PrjId):
    Prj = database.Projects.query.filter_by(projid=PrjId).first()
    if Prj is None:
        flash("Project doesn't exists", 'error')
        return PrintInCharte("<a href=/prj/>Select another project</a>")
    if not Prj.CheckRight(2):  # Level 0 = Read, 1 = Annotate, 2 = Admin
        flash('You cannot edit settings for this project', 'error')
        return PrintInCharte("<a href=/prj/>Select another project</a>")
    g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(Prj.projid, Prj.title)

    txt = "<h3>Project Edit / Erase annotation massively </h3>"
    ################ 1er Ecran
    if not gvg('NewAuthor') or not gvg('OldAuthor'):
        LstUser = GetAssoc2Col("select id,name from users order by lower(name)")
        LstUserOld = OrderedDict({'anyuser': "Any User"})
        for k, v in LstUser.items(): LstUserOld[k] = v
        LstUserNew = OrderedDict({'lastannot': "Previous Annotation available, or prediction, or Nothing"})
        for k, v in LstUser.items(): LstUserNew[k] = v
        LBOld = MakeHTMLSelect("OldAuthor", LstUserOld, AddEmptyLineFirst=True)
        LBNew = MakeHTMLSelect("NewAuthor", LstUserNew, AddEmptyLineFirst=True)
        txt += """<form method=get>
                  <table>
                  <tr><td>Replace the identification done by : </td><td>{0}</td></tr>
                  <tr><td>By the identification done by : </td><td>{1}</td></tr>
                  <tr><td>Since the (optional) :</td><td> <input type="text" style="width: 80px" id="filt_date" name="filt_date" autocomplete="off">
                                    at <input type="text" style="width: 25px" id="filt_hour" name="filt_hour" autocomplete="off"> h
                                    <input type="text" style="width: 25px" id="filt_min" name="filt_min" autocomplete="off"> m
                            </td></tr>
                  </table>
                    <br>
                  <input type=submit class='btn btn-primary' value="Compute an estimation of the impact"><br>
                    On the next screen you will be able to apply the change only on some categories
                  <form>
<br><br>
<div class='panel panel-default' style="width:1000px;margin-left:10px;">
This correction tool permits to erase the validation jobs for selected categories, selected Annotators and period of time and replace it by the one of a selected Annotator<br>
EXAMPLES of possibilities :<br>
<ul>
<li>Replace validation done by Mr X for all Copepoda by the validation done by Mrs. Y whos is well known specialist of this group
<li>Replace validation done by Mr W before 2015 November, 15th (which is the date of his taxonomy training course) by prediction or validation by anyone else
</ul>
</div>

<script>
$(document).ready(function() {{
      $( "#filt_fromdate,#filt_date" ).datepicker({{
      showButtonPanel: true,changeMonth: true,changeYear: true,dateFormat:"yy-mm-dd",
    }});
}});
</script>
                """.format(LBOld, LBNew)
        return PrintInCharte(txt)

    sqlclause = {"projid": Prj.projid, 'retrictsq': "", 'retrictq': "", 'jointype': ""}
    if gvg('OldAuthor') == "anyuser":
        OldAuthor = None
        txt += "Replace all classification<br>"
    else:
        OldAuthor = database.users.query.filter_by(id=int(gvg('OldAuthor'))).first()
        if OldAuthor is None:
            flash("Invalid new author", 'error')
            return PrintInCharte("URL Hacking ?")
        sqlclause['retrictsq'] += " and och.classif_who!=%s " % gvg('OldAuthor')
        sqlclause['retrictq'] += " and o.classif_who=%s " % gvg('OldAuthor')
        txt += "Replace classification done by <b>%s</b><br>" % OldAuthor.name
    if gvg('NewAuthor') == "lastannot":
        NewAuthor = None
        txt += "By the last classification of any other author<br>"
        sqlclause['jointype'] = 'left'
    else:
        NewAuthor = database.users.query.filter_by(id=int(gvg('NewAuthor'))).first()
        if NewAuthor is None:
            flash("Invalid new author", 'error')
            return PrintInCharte("URL Hacking ?")
        sqlclause['retrictsq'] += " and och.classif_who=%s " % gvg('NewAuthor')
        sqlclause['retrictq'] += " and o.classif_who!=%s " % gvg('NewAuthor')
        txt += "By classification done by <b>%s</b><br>" % NewAuthor.name

    if gvg('filt_date'):
        sqlclause['retrictq'] += " and o.classif_when>=to_date('" + gvg('filt_date')
        if gvg('filt_hour'):
            sqlclause['retrictq'] += " " + gvg('filt_hour')
        if gvg('filt_min'):
            sqlclause['retrictq'] += ":" + gvg('filt_min')
        sqlclause['retrictq'] += " ','YYYY-MM-DD HH24:MI')"

    # Protection désactivé en V1.1
    # if OldAuthor is None and NewAuthor is None:
    #     flash("This request doesn't make sense, you want replace the last classification of every one by the last classification",'error')
    #     return PrintInCharte("Invalid Request")

    ################ 2nd Ecran, affichage liste des categories & estimations
    if not gvg('Process'):
        txt += """<form method=post action=?OldAuthor={0}&NewAuthor={1}&filt_date={2}&filt_hour={3}&filt_min={4}&Process=Y>
        """.format(gvg('OldAuthor'), gvg('NewAuthor'), gvg('filt_date'), gvg('filt_hour'), gvg('filt_min'))
        sql = """
        select t.id,concat(t.name,' (',t2.name,')') as name, count(*) Nbr
        from obj_head o
        {jointype} join (select rank() over(PARTITION BY och.objid order by och.classif_date desc) ochrank,och.*
              from objectsclassifhisto och
              join obj_head ooch on ooch.objid=och.objid and ooch.projid={projid}
        where och.classif_type='M' {retrictsq}) newclassif on newclassif.objid=o.objid and newclassif.ochrank=1
        join taxonomy t on o.classif_id=t.id
        left join taxonomy t2 on t.parent_id=t2.id
        where o.projid={projid} {retrictq}
        GROUP BY t.id,concat(t.name,' (',t2.name,')')
        order BY t.name
        """.format(**sqlclause)
        data = GetAll(sql, debug=False)
        txt += """
        <input type=submit class='btn btn-warning' value="Process the replacement. WARNING : It's irreversible !!!!"><br>
        Below the estimation of each impacted category, select categories you want replace on these source categories list<br>
Select <a name="tbltop" href="#tbltop" onclick="$('#TblTaxo input').prop( 'checked', true )">All</a>
    / <a href="#tbltop" onclick="$('#TblTaxo input').prop( 'checked', false );">None</a>
<table class="table table-bordered table-condensed" style="width: auto" id="TblTaxo">
    <tr><th >Select</th><th width="200">Name</th><th >Nbr</th></tr>
        """
        for r in data:
            txt += "<tr><td><input type='checkbox' value='Y' name='taxo{0}' ></td><td>{1}</td><td class='rightfixedfont'>{2}</td></tr>".format(
                *r)
        txt += "</table>"
        return PrintInCharte(txt)

    ################ 3eme Ecran Execution Requetes
    if gvg('Process') == 'Y':
        sqlclause['taxoin'] = ",".join((x[4:] for x in request.form if x[0:4] == "taxo"))
        if sqlclause['taxoin'] == "":
            flash("You must select at least one categorie to do the replacement", 'error')
            return PrintInCharte("<a href='#' onclick='history.back();'>Back</a>")
        sql = """
        update obj_head as ou
            set classif_who=newclassif.classif_who,
            classif_when=coalesce(newclassif.classif_date,ou.classif_auto_when),
            classif_id=coalesce(newclassif.classif_id,ou.classif_auto_id),
            classif_qual=case when newclassif.classif_qual is not null then newclassif.classif_qual
                                 when ou.classif_auto_id is not null then 'P'
                                 else null end
        from obj_head o {jointype} join
        (select rank() over(PARTITION BY och.objid order by och.classif_date desc) ochrank,och.*
              from objectsclassifhisto och
              join obj_head ooch on ooch.objid=och.objid and ooch.projid={projid}
        where och.classif_type='M' {retrictsq}) newclassif on newclassif.objid=o.objid and newclassif.ochrank=1
        join taxonomy t on o.classif_id=t.id
        where  o.projid={projid} {retrictq} and o.classif_id in ({taxoin})
        and o.objid=ou.objid

        """.format(**sqlclause)
        RowCount = ExecSQL(sql, debug=True)
        RecalcProjectTaxoStat(Prj.projid)
        txt += "<div class='alert alert-success' role='alert'>Annotation replacement Done successfully. Updated %d Row</div>" % RowCount
        txt += "<br><a class='btn btn-lg btn-primary' href='/prj/%s'>Back to target project</a>" % Prj.projid
        return PrintInCharte(txt)
