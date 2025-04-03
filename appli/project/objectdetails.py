import datetime
import html
import urllib.parse
from typing import List

from flask import render_template, g, flash, request
from flask_login import current_user, login_required
from markupsafe import escape

from appli import (
    app,
    PrintInCharte,
    gvg,
    gvp,
    ntcv,
    ComputeLimitForImage,
    nonetoformat,
    XSSEscape,
)
from appli.constants import ClassifQual, DayTimeList

# noinspection SpellCheckingInspection
from appli.utils import ApiClient, ScaleForDisplay
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import (
    ObjectApi,
    ProjectsApi,
    TaxonomyTreeApi,
    UsersApi,
    SamplesApi,
    ProcessesApi,
    AcquisitionsApi,
    ObjectsApi,
)
from to_back.ecotaxa_cli_py.models import (
    ObjectModel,
    ProjectModel,
    SampleModel,
    AcquisitionModel,
    UserModelWithRights,
    TaxonModel,
    MinUserModel,
    ProcessModel,
    HistoricalClassification,
    BulkUpdateReq,
)


@app.route("/objectdetails/<int:objid>")
def objectdetails(objid):
    # récuperation et ajustement des dimensions de la zone d'affichage
    try:
        page_width = (
            int(gvg("w")) - 40
        )  # on laisse un peu de marge à droite et la scrollbar
        if page_width < 200:
            page_width = 20000
        window_height = int(gvg("h")) - 40  # on laisse un peu de marge en haut
        if window_height < 200:
            window_height = 20000
    except ValueError:
        page_width = 20000
        window_height = 20000

    # Security & sanity checks
    with ApiClient(ObjectApi, request) as oapi:
        try:
            obj: ObjectModel = oapi.object_query(objid)
        except ApiException as ae:
            if ae.status == 404:
                return "Object doesn't exists"
            elif ae.status in (401, 403):
                flash("You cannot read this object", "error")
                return PrintInCharte("<a href=/>Back to home</a>")
    # Project info
    with ApiClient(ProjectsApi, request) as papi:
        obj_proj: ProjectModel = papi.project_query(obj.project_id, for_managing=False)
    # User info
    current_user_id = -1  # Anonymous
    g.TaxonCreator = False
    # current_user is either an ApiUserWrapper or an anonymous one from flask
    if current_user.is_authenticated:
        logged_user: UserModelWithRights = current_user.api_user
        current_user_id = logged_user.id
        g.TaxonCreator = 4 in logged_user.can_do

    page = list()
    # Dans cet écran on utilise ElevateZoom car sinon en mode popup il y a conflit avec les images sous la popup
    page.append("<script src='/static/jquery.elevatezoom.js'></script>")
    g.Projid = obj_proj.projid
    g.manager_mail = ""
    prj_managers = [(m.email, m.name) for m in obj_proj.managers]
    page.append(
        "<p>Project: <b><a href='/prj/%d'>%s</a></b> (managed by : %s)"
        % (
            obj_proj.projid,
            XSSEscape(obj_proj.title),
            ",".join(("<a href ='mailto:%s'>%s</a>" % m for m in prj_managers)),
        )
    )
    if len(prj_managers) > 0:
        page.append(
            "<br>To report a mistake, contact <a href ='mailto:{0}?subject=Ecotaxa%20mistake%20notification&body={2}'"
            ">{1}</a>".format(
                prj_managers[0][0],
                prj_managers[0][1],
                urllib.parse.quote(
                    "Hello,\n\nI have discovered a mistake on this page "
                    + request.base_url
                    + "\n"
                ),
            )
        )
        mgr_email, mgr_name = prj_managers[0]
        g.manager_mail = f"<a href='mailto:{mgr_email}'>{mgr_name} ({mgr_email})</a>"
    # //window.location="mailto:?subject=Ecotaxa%20page%20share&body="+
    # encodeURIComponent("Hello,\n\nAn Ecotaxa user want share this page with you \n"+url);

    # Injected data for taxo select
    g.PrjManager = obj_proj.highest_right == "Manage"
    g.PrjAnnotate = obj_proj.highest_right == "Annotate"

    page.append("</p><p>Classification :")
    taxon_name = None
    taxon_type = None
    if obj.classif_id:
        with ApiClient(TaxonomyTreeApi, request) as api:
            taxon: TaxonModel = api.query_taxa(taxon_id=obj.classif_id)
        taxon_name = XSSEscape(taxon.display_name)
        taxon_type = taxon.type
        page.append("<br>&emsp;<b>%s</b>" % taxon_name)
        page.append(
            "<br>&emsp;" + (" &lt; ".join(taxon.lineage)) + " (id=%s)" % obj.classif_id
        )
    else:
        page.append("<br>&emsp;<b>Unknown</b>")

    classifier_name = None
    if obj.classif_who is not None:
        page.append(
            "<br>&emsp;%s " % (ClassifQual.get(obj.classif_qual, "To be classified"))
        )
        if current_user_id != -1:
            # No name for anonymous viewer
            with ApiClient(UsersApi, request) as api:
                contributor: MinUserModel = api.get_user(user_id=obj.classif_who)
            classifier_name = contributor.name
            page.append(" by %s (%s) " % (classifier_name, contributor.email))
        if obj.classif_when is not None:
            page.append(" on %s " % obj.classif_when.replace(microsecond=0))
    page.append("</p>")

    if obj.object_link is not None:
        page.append(
            "<p>External link :<a href='{0}' target=_blank> {0}</a></p>".format(
                obj.object_link
            )
        )

    page.append(
        "<table><tr>"
        "<td valign=top>Complementary information <a href='javascript:gotocommenttab();' "
        "> ( edit )</a>: </td>"
        "<td> <span id=spancomplinfo> {0}</span></td></tr></table>".format(
            ntcv(obj.complement_info).replace("\n", "<br>\n")
        )
    )

    # On affiche la liste des images, en selectionnant une image on changera le contenu de l'image Img1 + Redim
    # l'approche avec des onglets de marchait pas car les images sont superposées
    obj.images.sort(key=lambda x: x.imgrank)
    page.append("""<p>Image list : """)
    for img in obj.images:
        (width, height) = ComputeLimitForImage(
            img.width, img.height, page_width, window_height
        )
        if img.thumb_file_name:
            minifile = img.thumb_file_name
            (miniwidth, miniheight) = ComputeLimitForImage(
                img.thumb_width, img.thumb_height, 30, 30
            )
        else:
            minifile = img.file_name
            (miniwidth, miniheight) = ComputeLimitForImage(
                img.width, img.height, 30, 30
            )
        page.append(
            """<a href="javascript:SwapImg1('{1}',{2},{3});" >{0} <img src=/vault/{4}
        width={5} height={6}></a> """.format(
                img.imgrank + 1,
                img.file_name,
                width,
                height,
                minifile,
                miniwidth,
                miniheight,
            )
        )
    # Ajout de la 1ère image
    (width, height) = ComputeLimitForImage(
        obj.images[0].width, obj.images[0].height, page_width, window_height
    )
    page.append(
        "</p><p><img id=img1 src=/vault/{1} data-zoom-image=/vault/{1} width={2} height={0}></p>".format(
            height, obj.images[0].file_name, width
        )
    )

    # Affichage de la ligne de classification
    if g.PrjAnnotate or g.PrjManager:
        page.append(
            """
<table><tr><td>Set a new classification :</td>
 <td style="width: 230px;">
     <div class="input-group">
       <select id="taxolbpop" name="taxolbpop" style="width: 200px" class='taxolb' > </select>"""
        )
        page.append("<br>")
        page.append(
            """</div><!-- /input-group -->
 <span id=PendingChangesPop></span></td><td width=30px></td><td valign=top>
    <button type="button" class="btn btn-success btn-xs" onclick="Save1Object('V');">Save as Validated</button>
    <button type="button" class="btn btn-warning btn-xs" onclick="Save1Object('D');">Save as dubious</button>
    <!-- --functionality disabled--<button id=btenableedit type="button" class="btn btn-gris btn-xs" onclick="EnableEdit();">Enable Editing</button>-->
    <button type="button" class="btn btn-default btn-xs"  onclick="$('#PopupDetails').modal('hide');">Close</button>
    </td></tr></table>
    """
        )

    # Ajout des Onglets sous l'image
    page.append(
        """<br><div><ul class="nav nav-tabs" role="tablist">
    <li role="presentation" class="active"><a href="#tabdobj" aria-controls="tabdobj" role="tab" data-toggle="tab"
    > Object details</a></li>
    <li role="presentation" ><a href="#tabdsample" aria-controls="tabdsample" role="tab" data-toggle="tab"
    > Sample details</a></li>
    <li role="presentation" ><a href="#tabdacquis" aria-controls="tabdacquis" role="tab" data-toggle="tab"
    > Acquisition details</a></li>
    <li role="presentation" ><a href="#tabdprocess" aria-controls="tabdprocess" role="tab" data-toggle="tab"
    > Processing details</a></li>
    <li role="presentation" ><a href="#tabdclassiflog" aria-controls="tabdclassiflog" role="tab" data-toggle="tab"
    >Classification change log</a></li>
    <li role="presentation" ><a href="#tabdmap" aria-controls="tabdmap" role="tab" data-toggle="tab" id=atabdmap
    style="background: #5CB85C;color:white;">Map</a></li>
    """
    )
    if g.PrjAnnotate or g.PrjManager:
        page.append(
            """<li role="presentation" ><a id=linktabdaddcomments href="#tabdaddcomments"
            aria-controls="tabdaddcomments" role="tab" data-toggle="tab">Edit complementary informations</a></li>"""
        )

    if obj.classif_auto_id:
        with ApiClient(TaxonomyTreeApi, request) as tapi:
            taxon2: TaxonModel = tapi.query_taxa(taxon_id=obj.classif_auto_id)
        classif_auto_name = taxon2.lineage[0]
        if obj.classif_auto_score:
            classif_auto_name += " (%0.3f)" % (obj.classif_auto_score,)
    else:
        classif_auto_name = ""

    page.append(
        """</ul>
    <div class="tab-content">
    <div role="tabpanel" class="tab-pane active" id="tabdobj">
    <table class='table table-bordered table-condensed' data-table='object'><tr>
    <td style=' background-color: #f2f2f2;' data-edit='longitude'><b>longitude</td><td>{0}</td>
    <td style=' background-color: #f2f2f2;' data-edit='latitude'><b>latitude</td><td>{1}</td>
    <td style=' background-color: #f2f2f2;' data-edit='objdate'><b>Date</td><td>{2}</td>
    <td style=' background-color: #f2f2f2;'><b>Time (daytime)</td><td>{3} ({10})</td>
    </tr><tr><td style=' background-color: #f2f2f2;' data-edit='depth_min'><b>Depth min</td><td>{4}</td>
    <td style=' background-color: #f2f2f2;' data-edit='depth_max'><b>Depth max</td><td>{5}</td>
    <td><b>Classif auto</td><td>{6}</td><td><b>Classif auto when</td><td>{7}</td>
    </tr><tr><td><b>Object #</td><td>{8}</td>
    <td data-edit='orig_id'><b>Original Object ID</td><td colspan=5>{9}</td></tr><tr>""".format(
            nonetoformat(obj.longitude, ".5f"),
            nonetoformat(obj.latitude, ".5f"),
            obj.objdate,
            obj.objtime,
            obj.depth_min,
            obj.depth_max,
            classif_auto_name,
            obj.classif_auto_when,
            objid,
            obj.orig_id,
            DayTimeList.get(obj.sunpos, "?"),
        )
    )

    cpt = 0
    # Insertion des champs object
    for k, v in obj_proj.obj_free_cols.items():
        if cpt > 0 and cpt % 4 == 0:
            page.append("</tr><tr>")
        cpt += 1
        # noinspection PyUnresolvedReferences
        page.append(
            "<td data-edit='{2}'><b>{0}</td><td>{1}</td>".format(
                k, ScaleForDisplay(obj.free_columns.get(k, "???")), v
            )
        )
    page.append("</tr></table></div>")

    # insertion des champs Sample, Acquisition & Processing dans leurs onglets respectifs
    with ApiClient(SamplesApi, request) as api:
        sample: SampleModel = api.sample_query(sample_id=obj.sample_id)
    with ApiClient(AcquisitionsApi, request) as api:
        acquisition: AcquisitionModel = api.acquisition_query(
            acquisition_id=obj.acquisid
        )
    with ApiClient(ProcessesApi, request) as api:
        process: ProcessModel = api.process_query(process_id=obj.acquisid)

    for entity_desc in (
        ("Sample", sample, "sample", obj_proj.sample_free_cols),
        ("Acquisition", acquisition, "acquis", obj_proj.acquisition_free_cols),
        ("Processing", process, "process", obj_proj.process_free_cols),
    ):
        page.append(
            '<div role="tabpanel" class="tab-pane" id="tabd'
            + entity_desc[2]
            + '">'
            + entity_desc[0]
            + " details :<table class='table table-bordered table-condensed'  data-table='"
            + entity_desc[2]
            + "'><tr>"
        )
        cpt = 0
        if entity_desc[1]:
            if entity_desc[2] == "sample":
                page.append(
                    """<td data-edit='orig_id'><b>{0}</td><td colspan=3>{1}</td>
                    <td data-edit='longitude'><b>{2}</td><td>{3}</td>
                    <td data-edit='latitude'><b>{4}</td><td>{5}</td></tr><tr>""".format(
                        "Original ID",
                        html.escape(sample.orig_id),
                        "longitude",
                        ScaleForDisplay(sample.longitude),
                        "latitude",
                        ScaleForDisplay(sample.latitude),
                    )
                )
            elif entity_desc[2] == "acquis":
                page.append(
                    """<td data-edit='orig_id'><b>{0}</td><td colspan=3>{1}</td>
                    <td data-edit='instrument'><b>{2}</td><td>{3}</td></tr><tr>""".format(
                        "Original ID",
                        html.escape(acquisition.orig_id),
                        "Instrument",
                        ScaleForDisplay(acquisition.instrument),
                    )
                )
            else:
                orig_id = html.escape(process.orig_id)
                page.append(
                    "<td data-edit='orig_id'><b>{0}</td><td>{1}</td></tr><tr>".format(
                        "Original ID.", orig_id
                    )
                )
            # Display free columns
            for k, v in entity_desc[3].items():
                if cpt > 0 and cpt % 4 == 0:
                    page.append("</tr><tr>")
                cpt += 1
                # noinspection PyUnresolvedReferences
                page.append(
                    "<td data-edit='{2}'><b>{0}</td><td>{1}</td>".format(
                        k, ScaleForDisplay(entity_desc[1].free_columns.get(k, "???")), v
                    )
                )
            if entity_desc[2] == "sample":
                page.append(
                    "</tr><tr><td><b>{0}</td><td colspan=7>{1}</td></tr><tr>".format(
                        "Dataportal Desc.",
                        ScaleForDisplay(
                            html.escape(ntcv(sample.dataportal_descriptor))
                        ),
                    )
                )
        else:
            page.append("<td>No {0}</td>".format(entity_desc[0]))
        page.append("</tr></table></div>")

    # Affichage de l'historique des classifications
    with ApiClient(ObjectApi, request) as api:
        history: List[HistoricalClassification] = api.object_query_history(objid)

    dte = (
        obj.classif_when
        if obj.classif_qual in ("D", "V")
        else (obj.classif_auto_when if obj.classif_qual == "P" else None)
    )
    page.append(
        """<div role="tabpanel" class="tab-pane" id="tabdclassiflog">
    History :
    <table class='table table-bordered table-condensed'><tr>
    <td>Date</td><td>Type</td><td>Taxo</td><td>Author</td><td>Quality</td></tr>"""
    )
    # Current classification in first
    current = HistoricalClassification(
        classif_date=dte,
        classif_qual=obj.classif_qual,
        user_name=classifier_name,
        classif_type=None,
        taxon_name=taxon_name,
    )
    history.sort(key=lambda r: r.classif_date, reverse=True)
    history.insert(0, current)
    for classif_desc in history:
        if classif_desc.user_name is None:
            classif_desc.classif_type = "Automatic"
        else:
            classif_desc.classif_type = "Manual"
        vals = [
            getattr(classif_desc, fld)
            for fld in (
                "classif_date",
                "classif_type",
                "taxon_name",
                "user_name",
                "classif_qual",
            )
        ]
        vals[0] = vals[0].replace(microsecond=0) if vals[0] else vals[0]
        vals = [escape(str(a_val)) if a_val is not None else "-" for a_val in vals]
        page.append("<tr><td>" + ("</td><td>".join(vals)) + "</td></tr>")
    page.append("</table></div>")

    # Complementary information tab
    if g.PrjAnnotate or g.PrjManager:
        page.append(
            """<div role="tabpanel" class="tab-pane" id="tabdaddcomments">
        <textarea id=compinfo rows=5 cols=120 autocomplete=off>%s</textarea><br>
        <button type="button" class='btn btn-primary' onclick="UpdateComment();">Save additional comment</button>
        <span id=ajaxresultcomment></span>
        """
            % (ntcv(obj.complement_info),)
        )
    page.append("</div>")

    # Affichage de la carte
    page.append(
        """
    <div role="tabpanel" class="tab-pane" id="tabdmap">
<div id="map2" class="map2" style="width: 100%; height: 450px;">
  Displaying Map requires Internet Access to load map from https://server.arcgisonline.com
</div>"""
    )

    page.append("</table></div>")
    page.append(
        render_template(
            "common/objectdetailsscripts.html", Prj=obj_proj, objid=objid, obj=obj
        )
    )

    # En mode popup ajout en haut de l'écran d'un hyperlien pour ouvrir en fenetre isolée
    # Sinon affichage sans lien dans la charte.
    html_page = "\n".join(page)
    if gvg("ajax", "0") == "1":
        return (
            """<table width=100% style='margin: 3px'><tr><td><a href='/objectdetails/{0}?w={1}&h={2}' target=_blank>
        <b>Open in a separate window</b> (right click to copy link)</a>
        </td><td align='right'><button type="button" class="btn btn-default"
        onclick="$('#PopupDetails').modal('hide');">Close</button>&nbsp;&nbsp;
        </td></tr></table><div style='margin: 0 5px;'>""".format(
                objid, gvg("w"), gvg("h")
            )
            + html_page
        )
    return PrintInCharte(
        "<div style='margin-left:10px;'>"
        + html_page
        + render_template("common/taxopopup.html")
    )


@app.route("/objectdetailsupdate/<int:objid>", methods=["GET", "POST"])
@login_required
def objectdetailsupdate(objid):
    # noinspection PyStatementEffect
    request.form  # Force la lecture des données POST sinon il y a une erreur 504

    with ApiClient(ObjectApi, request) as api:
        obj: ObjectModel = api.object_query(objid)

    table = gvp("table")
    field = gvp("field")
    new_value = gvp("newval")
    if field == "objdate":
        try:
            new_value = datetime.date(
                int(new_value[0:4]), int(new_value[5:7]), int(new_value[8:10])
            )
        except ValueError:
            return '<span class="label label-danger">Wrong date</span>'
    if new_value == "":
        new_value = None
    updates = [{"ucol": field, "uval": new_value}]
    try:
        if table == "object":
            with ApiClient(ObjectsApi, request) as api:
                api.update_object_set(
                    BulkUpdateReq(target_ids=[objid], updates=updates)
                )
        elif table == "process":
            with ApiClient(ProcessesApi, request) as api:
                api.update_processes(
                    BulkUpdateReq(target_ids=[obj.acquisid], updates=updates)
                )
        elif table == "acquis":
            with ApiClient(AcquisitionsApi, request) as api:
                api.update_acquisitions(
                    BulkUpdateReq(target_ids=[obj.acquisid], updates=updates)
                )
        elif table == "sample":
            with ApiClient(SamplesApi, request) as api:
                api.update_samples(
                    BulkUpdateReq(target_ids=[obj.sample_id], updates=updates)
                )
    except Exception as E:
        exc = str(E)
        for exc_line in exc.split("\n"):
            if exc_line.startswith("Exception"):
                exc = exc_line
                break
        return '<span class="label label-danger">Update error %s</span>' % exc[0:100]

    return "<span class='label label-success'>changed value to '%s'" % new_value
