import collections
import math
import os
import urllib.parse
from collections import OrderedDict
from json import JSONDecodeError
from typing import List, Dict, Any

from flask import render_template, g, flash, json, request, url_for
from flask_security import login_required
from hyphenator import Hyphenator

import appli
import appli.project.sharedfilter as sharedfilter
from appli import app, PrintInCharte, gvg, gvp, DecodeEqualList, ScaleForDisplay, ntcv, XSSEscape
from appli.constants import DayTimeList, MappableObjectColumnsSet, SortableObjectFields, GetClassifQualClass
from appli.project.widgets import ClassificationPageStats, PopoverPane
from appli.search.leftfilters import getcommonfilters
######################################################################################################################
from appli.utils import ApiClient, format_date_time
from to_back.ecotaxa_cli_py import ProjectsApi, ProjectModel, ApiException, ObjectsApi, ObjectSetQueryRsp, UsersApi, \
    SamplesApi, SampleModel, UserModel, TaxonomyTreeApi, TaxonModel, ProjectTaxoStatsModel


######################################################################################################################

def GetFieldListFromModel(proj_model: ProjectModel, presentation_field):
    """
        For a given presentation field, return an ordered dict of correspondence
        between the DB column name and what the user will see for this value.
        @return: A dict with key = column names (in 'objects' DB view)
                             value = label for this column, as seen in UI
    """
    assert presentation_field in ('popoverfieldlist', 'classiffieldlist')

    # Get free object columns, dict with key=free column name, value=db column, like area=n04 for example
    # This is just for checking that each presentation field is OK
    objmap = proj_model.obj_free_cols

    # fieldlist fait le mapping entre le nom fonctionnel et le nom à afficher
    # cette boucle permet de faire le lien avec le nom de la colonne (si elle existe).
    # e.g. objtime=time\r\nequiv_diameter=diameter [px]
    presentation = DecodeEqualList(getattr(proj_model, presentation_field))
    fieldlist2 = {}  # key: db column, value: displayed label
    for field, dispname in presentation.items():
        if field in objmap:
            # 99% of display fields are from 'free columns'...
            fieldlist2[objmap[field]] = dispname
        elif field in MappableObjectColumnsSet:
            # ... but sometimes not, e.g. mapping objtime to 'Sampling Time'
            fieldlist2[field] = dispname

    ret = collections.OrderedDict()
    # Return in alphabetical order of the visible label, e.g. 'plla546.min'
    for k, v in sorted(fieldlist2.items(), key=lambda t: t[1]):
        ret[k] = v

    return ret


# Contient la liste des filtres & parametres de cet écran avec les valeurs par défaut
# noinspection SpellCheckingInspection
FilterList = {"MapN": '', "MapW": '', "MapE": '', "MapS": '',
              "depthmin": '', "depthmax": '',
              "samples": '',
              "fromdate": '', "todate": '', "inverttime": '',
              "fromtime": '', "totime": '',
              "instrum": '', "month": '', "daytime": '',
              "freetxt": '', "freetxtval": '', "filt_annot": '',
              "freenum": '', "freenumst": '', "freenumend": '',
              "statusfilter": '',
              # Display parameters, not filters
              "sortby": "", "sortorder": "", "dispfield": "",
              "ipp": 100, "zoom": 100, "magenabled": 0,
              "popupenabled": 0,
              }
FilterListAutoSave = ("statusfilter",
                      "sortby", "sortorder", "dispfield",
                      'ipp', 'zoom', 'magenabled',
                      'popupenabled')

# What is used for storing preferences on back-end
_FILTERS_KEY = "filters"

MONTH_LABELS = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                'October', 'November', 'December')

STATUSES = OrderedDict([("U", "Unclassified"),
                        ("P", "Predicted"),
                        ("NV", "Not Validated"),
                        ("V", "Validated"),
                        ("PV", "Predicted or Validated"),
                        ("NVM", "Validated by others"),
                        ("VM", "Validated by me"),
                        ("D", "Dubious")]
                       )


def _set_filters_from_prefs_and_get(page_vars, prj_id, a_request):
    """
        Set page variables, essentially INPUT settings, from user preferences.
    """
    # Inject default values
    page_vars.update(FilterList)
    # Override with posted values
    posted_vals = {a_val: a_request.args[a_val]
                   for a_val in FilterList.keys() & a_request.args.keys()}
    page_vars.update(posted_vals)
    # Read user preferences related to this project
    with ApiClient(UsersApi, a_request) as api:
        try:
            prefs: str = api.get_current_user_prefs_users_my_preferences_project_id_get(project_id=prj_id,
                                                                                        key=_FILTERS_KEY)
            user_vals = json.loads(prefs)
            page_vars.update(user_vals)
        except ApiException as ae:
            if ae.status in (401, 403):
                # Not logged in
                pass
        except JSONDecodeError:
            pass
        except ValueError:
            pass


def _set_prefs_from_filters(filters, prj_id):
    """
        Save user preferences from POSTed variables
    """
    # Read present values
    with ApiClient(UsersApi, request) as api:
        try:
            prefs: str = api.get_current_user_prefs_users_my_preferences_project_id_get(project_id=prj_id,
                                                                                        key=_FILTERS_KEY)
            user_vals = json.loads(prefs)
            if not isinstance(user_vals, dict):
                user_vals = {}
        except ApiException as ae:
            if ae.status in (401, 403):
                # Not logged in
                return
        except JSONDecodeError:
            user_vals = {}
    # See what needs update
    prefs_update = {}
    save_all = gvp("saveinprofile") == "Y"
    for a_filter, val in filters.items():
        if save_all or (a_filter in FilterListAutoSave):
            if user_vals.get(a_filter) != val:
                prefs_update[a_filter] = val
    if len(prefs_update) > 0:
        user_vals.update(prefs_update)
        with ApiClient(UsersApi, request) as api:
            val_to_write = json.dumps(user_vals)
            api.set_current_user_prefs_users_my_preferences_project_id_put(project_id=prj_id,
                                                                           key=_FILTERS_KEY,
                                                                           value=val_to_write)


######################################################################################################################

# noinspection PyPep8Naming
@app.route('/prj/<int:PrjId>')
def indexPrj(PrjId):
    """
        Generate the main project page. Can be used by an unauthenticated user.
    """
    data = {'pageoffset': gvg("pageoffset", "0")}

    _set_filters_from_prefs_and_get(data, PrjId, request)

    # Security & sanity checks
    with ApiClient(ProjectsApi, request) as api:
        try:
            proj: ProjectModel = api.project_query_projects_project_id_get(PrjId, for_managing=False)
        except ApiException as ae:
            if ae.status == 404:
                flash("Project doesn't exists", 'error')
            elif ae.status in (401, 403):
                # Original code leaked the manager mail for requesting access, but as the URL is unauthentified
                # it's enough for scrapping mail lists.
                # html_mail_body = _manager_mail(ntcv(Prj.title), Prj.projid)
                # msg = """
                # <div class="alert alert-danger alert-dismissible" role="alert"> You cannot view this project :
                # {1} [{2}]
                # <a class='btn btn-primary' href='mailto:{3}?{0}' style='margin-left:15px;'>REQUEST ACCESS to {4}</a>
                # </div>""".format(html_mail_body, Prj.title, Prj.projid, MainContact[0]['email'],
                # MainContact[0]['name'])
                flash('You cannot view this project', 'error')
            return PrintInCharte("<a href=/prj/>Select another project</a>")

    # print('%s',data)
    data["sample_for_select"] = ""
    if data.get("samples"):
        # Sample filter was posted, select the corresponding items.
        with ApiClient(SamplesApi, request) as api:
            samples: List[SampleModel] = api.samples_search_samples_search_get(project_ids=str(PrjId),
                                                                               id_pattern="")
        sample_ids = set(data['samples'].split(","))
        for a_sample in samples:
            # TODO: Could be filtered server-side
            if str(a_sample.sampleid) in sample_ids:
                data["sample_for_select"] += "\n<option value='%s' selected>%s</option> " % (
                    a_sample.sampleid, a_sample.orig_id)

    data["month_for_select"] = ""
    # print("%s",data['month'])
    for (a_filter, default) in enumerate(MONTH_LABELS, start=1):
        data["month_for_select"] += "\n<option value='{1}' {0}>{2}</option> ".format(
            'selected' if str(a_filter) in data.get('month', '').split(',') else '', a_filter, default)

    data["daytime_for_select"] = ""
    for (a_filter, default) in DayTimeList.items():
        data["daytime_for_select"] += "\n<option value='{1}' {0}>{2}</option> ".format(
            'selected' if str(a_filter) in data.get('daytime', '').split(',') else '', a_filter, default)

    # Generate the selection if the parameter is set in the URL - free numeric column
    data["filt_freenum_for_select"] = ""
    if data.get('freenum', '') != "":
        for r in PrjGetFieldListFromModel(proj, 'n', ''):  # type: dict
            if r['id'] == data['freenum']:
                data["filt_freenum_for_select"] = "\n<option value='{0}' selected>{1}</option> ".format(r['id'],
                                                                                                        r['text'])

    # Generate the selection if the parameter is set in the URL - free textual column
    data["filt_freetxt_for_select"] = ""
    if data.get('freetxt', '') != "":
        for r in PrjGetFieldListFromModel(proj, 't', ''):  # type: dict
            if r['id'] == data['freetxt']:
                data["filt_freetxt_for_select"] = "\n<option value='{0}' selected>{1}</option> ".format(r['id'],
                                                                                                        r['text'])

    # Generate the selection if the parameter is set in the URL - annotators filter
    data["filt_annot_for_select"] = ""
    if data.get('filt_annot', '') != "":
        user_ids = [int(x) for x in data["filt_annot"].split(',') if x.isdigit()]
        for an_id in user_ids:
            with ApiClient(UsersApi, request) as api:
                try:
                    user: UserModel = api.get_user_users_user_id_get(user_id=an_id)
                except ApiException as _ae:
                    # Ignore this one
                    continue
            data["filt_annot_for_select"] += "\n<option value='{0}' selected>{1}</option> ".format(user.id, user.name)

    # We can display what we can sort
    displayable_fields = SortableObjectFields.copy()
    data["fieldlist"] = displayable_fields
    displayable_fields.update(GetFieldListFromModel(proj, "classiffieldlist"))

    sortlist = collections.OrderedDict({"": ""})
    data["sortlist"] = sortlist
    sortlist["classifname"] = "Category Name"  # Historical, == txo.name
    sortlist.update(SortableObjectFields)
    # All displayable fields are sortable
    for k, v in displayable_fields.items():
        sortlist[k] = v

    data["statuslist"] = collections.OrderedDict({"": "All"})
    data["statuslist"].update(STATUSES)

    g.Projid = proj.projid
    g.PrjManager = proj.highest_right == "Manage"
    g.PrjAnnotate = proj.highest_right == "Annotate"
    # Public view is when the project is visible, but the current user has no right on it.
    g.PublicViewMode = proj.highest_right == ""
    g.manager_mail = g.prjmanagermailto = proj.managers[0].email

    if gvg("taxo") != "":
        g.taxofilter = gvg("taxo")
        g.taxochild = gvg("taxochild")
        try:
            taxon_id = int(gvg("taxo"))
            with ApiClient(TaxonomyTreeApi, request) as api:
                taxon: TaxonModel = api.query_taxa_taxon_taxon_id_get(taxon_id=taxon_id)
            g.taxofilterlabel = taxon.name
        except (ValueError, ApiException):
            pass
    else:
        g.taxofilter = g.taxofilter = g.taxofilterlabel = ""

    classiftab = GetClassifTabFromModel(proj)

    g.ProjectTitle = proj.title
    g.headmenu = []  # Menu project
    g.headmenuF = []  # Menu Filtered
    if g.PrjAnnotate or g.PrjManager:
        if proj.status == "Annotate":
            g.headmenu.append(
                ("/Task/Create/TaskClassifAuto2?projid=%d" % PrjId, "Train and Predict identifications V2"))
            g.headmenuF.append(
                ("javascript:GotoWithFilter('/Task/Create/TaskClassifAuto2')", "Train and Predict identifications V2"))
            g.headmenu.append(("/Task/Create/TaskClassifAuto2?projid=%d&frommodel=Y" % PrjId,
                               "Predict identifications from trained model"))
            g.headmenuF.append(("javascript:GotoWithFilter('/Task/Create/TaskClassifAuto2?frommodel=Y')",
                                "Predict identifications from trained model"))
            g.headmenu.append(("/Task/Create/TaskImport?p=%d" % PrjId, "Import images and metadata"))

        g.headmenu.append(("/Task/Create/TaskExportTxt?projid=%d" % PrjId, "Export"))
        g.headmenuF.append(("javascript:GotoWithFilter('/Task/Create/TaskExportTxt')", "Export"))
    if g.PrjManager:
        g.headmenu.append(("", "SEP"))
        g.headmenuF.append(("", "SEP"))
        g.headmenu.append(("/prj/edit/%d" % PrjId, "Edit project settings"))
        g.headmenu.append(("/Task/Create/TaskSubset?p=%d" % PrjId, "Extract Subset"))
        g.headmenuF.append(("javascript:GotoWithFilter('/Task/Create/TaskSubset?p=%d')" % PrjId,
                            "Extract Subset"))
        g.headmenu.append(("/prj/merge/%d" % PrjId, "Merge another project in this project"))
        g.headmenu.append(("/prj/EditAnnot/%d" % PrjId, "Edit or erase annotations massively"))
        g.headmenu.append(("/prj/editdatamass/%d" % PrjId, "Batch edit metadata"))
        g.headmenuF.append(("javascript:GotoWithFilter('/prj/editdatamass/%d')" % PrjId, "Batch edit metadata"))
        g.headmenu.append(("/prj/resettopredicted/%d" % PrjId, "Reset status to Predicted"))
        g.headmenuF.append(
            ("javascript:GotoWithFilter('/prj/resettopredicted/%d')" % PrjId, "Reset status to Predicted"))
        g.headmenu.append(("/prjPurge/%d" % PrjId, "Delete objects or project"))
        g.headmenuF.append(("javascript:GotoWithFilter('/prjPurge/%d')" % PrjId, "Delete objects"))
        # EMODNet Audit & Export
        # g.headmenu.append(("", "SEP"))
        # g.headmenu.append(("/prj/emodnet/%d" % PrjId, "EMODnet export"))

    appli.AddTaskSummaryForTemplate()
    filtertab = getcommonfilters(data)
    return render_template('project/projectmain.html', top="", lefta=classiftab, leftb=filtertab,
                           right='dodefault', data=data, title='EcoTaxa ' + ntcv(proj.title))


def _manager_mail(prj_title, prj_id):
    base_url = request.host_url[:-1]
    mail_body = "Please provide me privileges to project : '%s' at this address : %s " % (
        prj_title, base_url + url_for('indexPrj', PrjId=int(prj_id)))
    mail_link = urllib.parse.urlencode({'body': mail_body,
                                        'subject': 'EcoTaxa project access request'},
                                       quote_via=urllib.parse.quote)
    return mail_link


class LatinHyphenator(object):
    """
        For too long latin word, insert optional hyphens.
    """

    def __init__(self):
        self.nator = Hyphenator(filename=os.path.dirname(__file__) + os.sep + ".." + os.sep + "hyphen_la.dic")
        self.cache = {}

    def hyphenize(self, word):
        ret = self.cache.get(word)
        if ret is not None:
            return ret
        if '-' in word:
            ret = '&ndash;'.join([self.hyphenize(a_word) for a_word in word.split('-')])
        elif ' ' in word:
            # The browser will do the job
            ret = word
        else:
            try:
                ret = self.nator.inserted(word, "&shy;")
            except Exception:
                ret = word
        self.cache[word] = ret
        return ret


MAX_LEN_BEFORE_HYPHEN = 12


# noinspection PyPep8Naming
def FormatNameForVignetteDisplay(category_name, hyphenator):
    # If the name is composed, use different styles for parts
    parts = ntcv(category_name).split('<')
    part0 = parts[0]
    if len(part0) >= MAX_LEN_BEFORE_HYPHEN:
        part0 = hyphenator.hyphenize(part0)
    restxt = "<span class='cat_name'>{}</span>".format(part0)
    if len(parts) > 1:
        restxt += "<span class='cat_ancestor'> &lt;&nbsp;{}</span>".format(" &lt;&nbsp;".join(parts[1:]))
    return restxt


######################################################################################################################
# noinspection SpellCheckingInspection,PyPep8Naming
@app.route('/prj/LoadRightPane', methods=['GET', 'POST'])
def LoadRightPane():
    # Security & sanity checks
    PrjId = gvp("projid")
    with ApiClient(ProjectsApi, request) as api:
        try:
            proj: ProjectModel = api.project_query_projects_project_id_get(PrjId, for_managing=False)
        except ApiException as ae:
            if ae.status == 404:
                return "Invalid project"
            elif ae.status in (401, 403):
                return "Access Denied"

    # get filter values from POST
    Filt = {}
    for col, v in FilterList.items():
        Filt[col] = gvp(col, v)

    _set_prefs_from_filters(Filt, PrjId)

    # Public view is when the project is visible, but the current user has no right on it.
    g.PublicViewMode = proj.highest_right == ""
    user_can_modify = proj.highest_right in ("Manage", "Annotate")

    # récupération des parametres d'affichage
    filtres = {}
    for col in sharedfilter.FilterList:
        filtres[col] = gvp(col, "")
    if g.PublicViewMode:  # Si c'est une lecture publique
        filtres["statusfilter"] = "V"  # Les anonymes ne peuvent voir que les objets validés

    pageoffset = int(gvp("pageoffset", "0"))
    sortby = Filt["sortby"]
    sortorder = Filt["sortorder"]
    # The fields AKA DB columns needed under each image, a space-separated list of
    # DB column names, with dispfield_ prefix, e.g. ' dispfield_orig_id dispfield_classif_auto_score dispfield_n33'
    # @see building of <ul id="dispfieldlist"> for why
    posted_columns_to_display = Filt["dispfield"]
    images_per_page = int(Filt["ipp"])
    zoom = int(Filt["zoom"])
    popup_enabled = Filt["popupenabled"] == "1"

    # Fit to page envoie un ipp de 0 donc on se comporte comme du 200 d'un point de vue DB
    ippdb = images_per_page if images_per_page > 0 else 200

    if popup_enabled:
        popover_columns = GetFieldListFromModel(proj, presentation_field='popoverfieldlist')
    else:
        popover_columns = {}

    possible_proj_fields = GetFieldListFromModel(proj, presentation_field='classiffieldlist')

    # Sanitize fields to display
    post_prfx_len = len("dispfield_")
    posted_columns_list = [a_col[post_prfx_len:]
                           for a_col in posted_columns_to_display.strip().split()
                           if len(a_col) > post_prfx_len]

    # The mandatory columns, _always_ needed as they are referenced
    api_cols = ["obj.objid", "obj.classif_qual", "obj.imgcount", "obj.complement_info",
                "img.height", "img.width", "img.thumb_file_name", "img.thumb_height", "img.thumb_width",
                "img.file_name",
                "txo.name", "txo.display_name"]
    api_cols_to_display = OrderedDict()

    # Add to query the needed columns, from project settings and current query
    col_2_free = {v: k for k, v in proj.obj_free_cols.items()}

    def prefix_db_col(a_col):
        # Return a column with a prefix in API convention, depending on its origin
        if a_col in MappableObjectColumnsSet or a_col in SortableObjectFields:
            return "obj." + a_col
        elif a_col in col_2_free:
            return "fre." + col_2_free[a_col]
        elif a_col == "classifname":
            # Historical, kept for old URLs which might have been transmitted to third-parties
            return "txo.name"
        return None

    # Compute optional columns needed under the image
    for col in posted_columns_list:
        # Determine the label for displaying
        if col in possible_proj_fields:
            col_label = possible_proj_fields[col]
        elif col in SortableObjectFields:
            col_label = SortableObjectFields[col]
        elif col in MappableObjectColumnsSet:
            col_label = col
        else:
            continue
        # Tranform into an API-naming column name
        prfx_col = prefix_db_col(col)
        if prfx_col is not None:
            api_cols.append(prfx_col)
            api_cols_to_display[prfx_col] = col_label
    # We also need from back-end all the columns for populating popover,
    # namely the standard columns + the customized ones (per project)
    if popup_enabled:
        popover_prfxed_cols = PopoverPane.always_there.copy()
        api_cols.extend([a_col for a_col in PopoverPane.always_there.keys()
                         if a_col not in api_cols])
        # Change setup columns to API notation
        popover_prfxed_cols.update(OrderedDict([(prefix_db_col(k), v)
                                                for k, v in popover_columns.items()]))
        api_cols.extend([a_col for a_col in popover_prfxed_cols.keys()
                         if a_col is not None and a_col not in api_cols])
    else:
        popover_prfxed_cols = {}

    # Query objects, using filters and page size, in project
    with ApiClient(ObjectsApi, request) as api:
        sort_col_signed = None
        if sortby != "":
            sort_col_signed = ("-" if sortorder.lower() == "desc" else "") + prefix_db_col(sortby)
        needed_fields = ",".join(api_cols)
        while True:
            objs: ObjectSetQueryRsp = \
                api.get_object_set_object_set_project_id_query_post(project_id=PrjId,
                                                                    project_filters=filtres,
                                                                    fields=needed_fields,
                                                                    order_field=sort_col_signed,
                                                                    window_size=ippdb,
                                                                    window_start=pageoffset * ippdb)
            pagecount = math.ceil(objs.total_ids / ippdb)
            if pageoffset < pagecount:
                # There are objects to view, we're done
                break
            # Case when the filter removed the last page, AKA no object returned
            pageoffset = pagecount - 1
            if pageoffset < 0:
                pageoffset = 0
                break

    # Produce page lines using API call output
    html = ["<a name='toppage'/>"]
    # DEBUG SPAN
    # html.append(
    #     "<span>%d vs %d vs %d, %s %s</span>" % (
    #         objs.total_ids, len(object_ids), len(objs.details), proj.highest_right, api_cols_to_display))
    trcount = 1
    fitlastclosedtr = 0  # index de t de la derniere création de ligne qu'il faudrat effacer quand la page sera pleine
    fitheight = 100  # hauteur déjà occupé dans la page plus les header footer (hors premier header)
    fitcurrentlinemaxheight = 0
    LineStart = ""
    if user_can_modify:
        LineStart = "<td class='linestart'></td>"
    html.append("<table class=imgtab><tr id=tr1>" + LineStart)
    WidthOnRow = 0
    # récuperation et ajustement des dimensions de la zone d'affichage
    # noinspection PyBroadException
    try:
        PageWidth = int(gvp("resultwidth")) - 40  # on laisse un peu de marge à droite et la scrollbar
        if PageWidth < 200:
            PageWidth = 200
    except Exception:
        PageWidth = 200
    # noinspection PyBroadException
    try:
        WindowHeight = int(gvp("windowheight")) - 100  # on enleve le bandeau du haut
        if WindowHeight < 200:
            WindowHeight = 200
    except Exception:
        WindowHeight = 200
    # print("PageWidth=%s, WindowHeight=%s"%(PageWidth,WindowHeight))
    hyphenator = LatinHyphenator()
    # Calcul des dimensions et affichage des images
    for dtl in objs.details:
        # Access API result by name for readability
        dtl: Dict[str, Any] = dict(zip(api_cols, dtl))
        format_date_time(dtl, {"obj.classif_when"}, {"obj.objtime"})
        filename = dtl['img.file_name']
        origwidth: int = dtl['img.width']
        origheight: int = dtl['img.height']
        thumbfilename = dtl['img.thumb_file_name']
        thumbwidth = dtl['img.thumb_width']
        display_name = dtl['txo.display_name']
        imgcount = dtl['obj.imgcount']
        if origwidth is None:  # pas d'image associée, pas trés normal mais arrive pour les subset sans images
            width = 80
            height = 40
        else:
            width = origwidth * zoom // 100
            height = origheight * zoom // 100
        if max(width, height) < 75:  # en dessous de 75 px de coté on ne fait plus le scaling
            if max(origwidth, origheight) < 75:
                width = origwidth  # si l'image originale est petite on l'affiche telle quelle
                height = origheight
            elif max(origwidth, origheight) == origwidth:
                width = 75
                height = origheight * 75 // origwidth
                if height < 1:
                    height = 1
            else:
                height = 75
                width = origwidth * 75 // origheight
                if width < 1:
                    width = 1

        # On limite les images pour qu'elles tiennent toujours dans l'écran
        if width > PageWidth:
            width = PageWidth
            height = math.trunc(origheight * width / origwidth)
            if height == 0:
                height = 1
        if height > WindowHeight:
            height = WindowHeight
            width = math.trunc(origwidth * height / origheight)
            if width == 0:
                width = 1
        if WidthOnRow != 0 and (WidthOnRow + width) > PageWidth:
            trcount += 1
            fitheight += fitcurrentlinemaxheight
            if (images_per_page == 0) and (fitheight > WindowHeight):  # en mode fit quand la page est pleine
                if fitlastclosedtr > 0:  # dans tous les cas on laisse une ligne
                    del html[fitlastclosedtr:]
                break
            fitlastclosedtr = len(html)
            fitcurrentlinemaxheight = 0
            html.append("</tr></table><table class=imgtab><tr id=tr%d>%s" % (trcount, LineStart))
            WidthOnRow = 0
        cellwidth = width + 22
        fitcurrentlinemaxheight = max(fitcurrentlinemaxheight,
                                      # 45 espace sur le dessus et le dessous de l'image + 14px par info affichée
                                      height + 45 + 14 * len(api_cols_to_display))
        if cellwidth < 80:
            cellwidth = 80  # on considère au moins 80 car avec les label c'est rarement moins
        # Met la fenetre de zoon la ou il y a plus de place, sachant qu'elle fait 400px
        #  et ne peut donc pas être calée à gauche des premieres images.
        if (WidthOnRow + cellwidth) > (PageWidth / 2):
            pos = 'left'
        else:
            pos = 'right'
        # Si l'image affiché est plus petite que la miniature, afficher la miniature.
        if thumbwidth is None or thumbwidth < width or thumbfilename is None:
            # sinon (si la miniature est plus petite que l'image à afficher )
            thumbfilename = filename  # la miniature est l'image elle même
        txt = "<td width={0}>".format(cellwidth)
        if filename:
            txt += "<img class='lazy' id=I{3} data-src='/vault/{5}' " \
                   "data-zoom-image='{0}' width={1} height={2} pos={4}>" \
                .format(filename, width, height, dtl['obj.objid'], pos, thumbfilename)
        else:
            txt += "No Image"
        # Génération de la popover qui apparait pour donner quelques détails sur l'image
        if popup_enabled:
            popattribute = PopoverPane(popover_prfxed_cols, dtl).render(WidthOnRow)
        else:
            popattribute = ""

        # Generate text box under the image
        bottom_txts = []
        before_brs = ""
        for fld, disp in api_cols_to_display.items():
            if fld == 'obj.classif_auto_score' and dtl["obj.classif_qual"] == 'V':
                bottom_txts.append("%s : -" % disp)
            elif fld == 'obj.objtime':
                bottom_txts.append("Time %s" % dtl['obj.objtime'])
            elif fld == 'obj.classif_when':
                if dtl['obj.classif_when']:
                    bottom_txts.append("Validation date : %s" % dtl['obj.classif_when'])
            elif fld == 'obj.orig_id':
                before_brs = "<div style='word-break: break-all;'>%s</div>" % dtl['obj.orig_id']
            else:
                bottom_txts.append("%s : %s" % (disp, ScaleForDisplay(dtl[fld])))
        bottomtxt = before_brs + "<br>".join(bottom_txts)

        imgcount_lbl = "(%d)" % imgcount if imgcount is not None and imgcount > 1 else ""
        comment_present = "<b>!</b> " if dtl['obj.complement_info'] not in (None, "") else ""

        txt += """<div class='subimg {1}' {2}>
<div class='taxo'>{0}</div>
<div class='displayedFields'>{3}</div></div>
<div class='ddet'><span class='ddets'><span class='glyphicon glyphicon-eye-open'></span> {4} {5}</div>""" \
            .format(FormatNameForVignetteDisplay(display_name, hyphenator),
                    GetClassifQualClass(dtl['obj.classif_qual']),
                    popattribute, bottomtxt, imgcount_lbl, comment_present)
        txt += "</td>"

        # WidthOnRow+=max(cellwidth,80) # on ajoute au moins 80 car avec les label c'est rarement moins
        WidthOnRow += cellwidth + 5  # 5 = border-spacing = espace inter image
        html.append(txt)

    html.append("</tr></table>")
    if len(objs.details) == 0:
        html.append("<b>No Result</b><br>")
    if user_can_modify:
        html.append("""
        <div id='PendingChanges' class='PendingChangesClass text-danger'></div>
        <button class='btn btn-default' onclick="$(window).scrollTop(0);">
            <span class='glyphicon glyphicon-arrow-up ' ></span></button>
        <button class='btn btn-primary' onclick='SavePendingChanges();' title='CTRL+S' id=BtnSave disabled>
            <span class='glyphicon glyphicon-save' /> Save pending changes [CTRL+S]</button>
        <button class='btn btn-success' onclick='ValidateAll(0);'><span class='glyphicon glyphicon-ok' /> 
            <span class='glyphicon glyphicon-arrow-right' /> 
                <span id=TxtBtnValidateAll>Validate all and move to next page</span></button>
        <!--<button class='btn btn-success' onclick='ValidateAll(1);' title="Save changed annotations , 
        Validate all objects in page &amp; Go to Next Page"><span class='glyphicon glyphicon-arrow-right' /> 
        Save, Validate all &amp; Go to Next Page</button>-->
        <button class='btn btn-success' onclick="ValidateSelection('V');">
            <span class='glyphicon glyphicon-ok' />  Validate Selection [CTRL+L]</button>
        <button class='btn btn-warning' onclick="ValidateSelection('D');">Set Selection Dubious</button>
        <button class='btn btn-default' onclick="$('#bottomhelp').toggle()" >
            <span class='glyphicon glyphicon-question-sign' /> Undo</button>
        <div id="bottomhelp" class="panel panel-default" style="margin:10px 0 0 40px;width:500px;display:none;">
            To correct validation mistakes (no UNDO button in Ecotaxa):
<br>1.	Select Validated Status
<br>2.	Sort by : Validation date
<br>3.	Move the most recent (erroneous) validated objects into the suitable category
</div><script>$("#PendingChanges2").html('');</script>
        """)
    # Gestion de la navigation entre les pages
    if images_per_page == 0:
        html.append("<p class='inliner'> Page management not available on Fit mode</p>")
    elif pagecount > 1 or pageoffset > 0:
        html.append("<p class='inliner'> Page %d / %d</p>" % (pageoffset + 1, pagecount))
        html.append("<nav><ul class='pagination'>")
        if pageoffset > 0:
            html.append("<li><a href='javascript:gotopage(%d);' >&laquo;</a></li>" % (pageoffset - 1))
        # ValueError: range() arg 3 must not be zero
        for i in range(0, pagecount - 1, math.ceil(pagecount / 20)):
            if i == pageoffset:
                html.append("<li class='active'><a href='javascript:gotopage(%d);'>%d</a></li>" % (i, i + 1))
            else:
                html.append("<li><a href='javascript:gotopage(%d);'>%d</a></li>" % (i, i + 1))
        html.append("<li><a href='javascript:gotopage(%d);'>%d</a></li>" % (pagecount - 1, pagecount))
        if pageoffset < pagecount - 1:
            html.append("<li><a href='javascript:gotopage(%d);' >&raquo;</a></li>" % (pageoffset + 1))
        html.append("</ul></nav>")
    html.append("""
    <script>
        PostAddImages();
    </script>""")
    # Add stats-rendering HTML
    html.append(ClassificationPageStats.render(filtres, PrjId))
    return "\n".join(html)


######################################################################################################################

def GetClassifTabFromModel(proj: ProjectModel):
    """
        Classification tab contains:
            - All taxa from project's init list, populated or not.
            - All taxa having a count in the project.
    """
    # Get used taxa inside the project
    with ApiClient(ProjectsApi, request) as api:
        stats: List[ProjectTaxoStatsModel] = api.project_set_get_stats_project_set_taxo_stats_get(ids=str(proj.projid),
                                                                                                  taxa_ids="all")
    populated_taxa = {stat.used_taxa[0]: stat
                      for stat in stats
                      if stat.used_taxa[0] != -1}  # filter unclassified

    # Get info on them + the ones from project configuration
    with ApiClient(TaxonomyTreeApi, request) as api:
        taxa_ids = "+".join([str(x) for x in set(proj.init_classif_list).union(populated_taxa.keys())])
        taxa: List[TaxonModel] = api.query_taxa_set_taxon_set_query_get(ids=taxa_ids)
    taxa.sort(key=lambda r: r.name)
    present_ids = {taxon.id for taxon in taxa}

    # Build full tree on present taxa, for right-click menu.
    # The values are accessed in order in the JS code, so a list is enough.
    # We have straight away the parent (first in lineage) for queried taxa...
    taxotree = {taxon.id: [taxon.id, taxon.name, (taxon.id_lineage[1] if len(taxon.id_lineage) > 1 else None)]
                for taxon in taxa}
    # ...but not necessarily all the parents
    for a_taxon in taxa:
        prev_id = None
        for taxon_id, taxon_name in zip(reversed(a_taxon.id_lineage), reversed(a_taxon.lineage)):
            if taxon_id not in taxotree:
                taxotree[taxon_id] = [taxon_id, taxon_name, prev_id]
            prev_id = taxon_id

    res_by_id: Dict = {}
    children_by_id: Dict = {}
    for taxon in taxa:
        # Find the parent (if any) in the subtree being displayed.
        for a_parent_id in taxon.id_lineage[1:]:
            if a_parent_id in present_ids:
                parent_id_here = a_parent_id
                break
        else:
            parent_id_here = None
        # Add a record for the taxon
        for_taxon = {"id": taxon.id,
                     "dist": 0,  # the distance to root, in # of branches. Used for indenting sub-nodes
                     "parentclasses": "",  # the CSS classes, allowing pseudo-collapse
                     "haschild": False,  # If the node has a child
                     "name": taxon.name,
                     "display_name": taxon.display_name}
        stats_for_taxon = populated_taxa.get(taxon.id)
        if stats_for_taxon is not None:
            for_taxon["nbr_p"] = stats_for_taxon.nb_predicted
            for_taxon["nbr_v"] = stats_for_taxon.nb_validated
            for_taxon["nbr_d"] = stats_for_taxon.nb_dubious
        else:
            for_taxon["nbr_p"] = for_taxon["nbr_v"] = for_taxon["nbr_d"] = 0
        # To toggle 'zero count' in the GUI
        for_taxon["nbr"] = for_taxon["nbr_p"] + for_taxon["nbr_v"] + for_taxon["nbr_d"]
        # Store
        children_by_id.setdefault(parent_id_here, []).append(taxon.id)
        res_by_id[taxon.id] = for_taxon

    # Go down the tree, in sets, one for each level
    nodes_to_mark = set(children_by_id[None])
    depth = 0
    while len(nodes_to_mark) > 0:
        next_to_mark = set()
        for an_id in nodes_to_mark:
            to_mark = res_by_id[an_id]
            to_mark["dist"] = depth
            children = children_by_id.get(an_id)
            if children is not None:
                to_mark["haschild"] = True
                for a_child_in in children:
                    child_to_mark = res_by_id[a_child_in]
                    child_to_mark["parentclasses"] = to_mark["parentclasses"] + " visib%d" % an_id
                next_to_mark.update(children)
        nodes_to_mark = next_to_mark
        depth += 1

    # Flatten the list, in order
    restree = []

    def add_lines_in_order(taxo_id):
        for a_child in children_by_id.get(taxo_id, ()):
            restree.append(res_by_id[a_child])
            add_lines_in_order(a_child)

    add_lines_in_order(None)

    for line in restree:
        # Special case, when display_name has a "<" inside then visually separate the parts
        disp_name = line['display_name']
        if '<' in disp_name:
            parts = disp_name.split('<')
            line['htmldisplayname'] = parts[0]
            line['taxoparent'] = ''.join((' &lt;&nbsp;' + XSSEscape(x) for x in parts[1:]))
        else:
            line['htmldisplayname'] = disp_name
            line['taxoparent'] = ""

    return render_template('project/classiftab.html', res=restree, taxotree=json.dumps(taxotree))


######################################################################################################################
# noinspection PyPep8Naming
@app.route('/prjGetClassifTab/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def prjGetClassifTab(PrjId):
    # Security & sanity checks
    with ApiClient(ProjectsApi, request) as api:
        try:
            proj: ProjectModel = api.project_query_projects_project_id_get(PrjId, for_managing=False)
        except ApiException as _ae:
            return "Project doesn't exists"

    g.Projid = proj.projid
    g.PrjManager = proj.highest_right == "Manage"
    g.PrjAnnotate = proj.highest_right == "Annotate"
    # Public view is when the project is visible, but the current user has no right on it.
    g.PublicViewMode = proj.highest_right == ""

    return GetClassifTabFromModel(proj)


######################################################################################################################

def PrjGetFieldListFromModel(proj: ProjectModel, field_type, term):
    """
        Return the list of free columns for the project, for any entity,
         with given type ('' matches all) and matching with term ('' matches all).
    """
    ret = []
    free_cols_per_entity = {'o': proj.obj_free_cols,
                            's': proj.sample_free_cols,
                            'a': proj.acquisition_free_cols,
                            'p': proj.process_free_cols}
    out_text_prefix = {'o': '', 's': 'sample ', 'a': 'acquis. ', 'p': 'process. '}
    field_types = "nt" if field_type == '' else field_type
    for prfx, free_cols in free_cols_per_entity.items():
        for tsv_col, db_col in free_cols.items():
            if db_col[0] in field_types and (term == '' or term in tsv_col):
                ret.append({'id': prfx + db_col, 'text': out_text_prefix[prfx] + tsv_col})
    return ret


# noinspection PyPep8Naming
@app.route('/prj/GetFieldList/<int:PrjId>/<string:typefield>')
@login_required
def PrjGetFieldListAjax(PrjId, typefield):
    with ApiClient(ProjectsApi, request) as api:
        proj: ProjectModel = api.project_query_projects_project_id_get(PrjId, for_managing=False)
        # A direct Ajax call with wrong context -> let the eventual HTTP error throw
    term = gvg("q")
    fieldlist = PrjGetFieldListFromModel(proj, typefield, term)
    return json.dumps(fieldlist)
