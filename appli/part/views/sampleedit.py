from pathlib import Path

from flask import flash, request
from flask import render_template, redirect
from wtforms import Form, BooleanField, StringField, validators, DateTimeField, IntegerField, FloatField, TextAreaField

from appli import gvp
from appli.database import db
from ..ecopart_blueprint import part_app, part_PrintInCharte, PART_URL, ECOTAXA_URL
from ..db_utils import ExecSQL
from ..funcs import histograms, uvp_sample_import as sample_import
from ..remote import EcoTaxaInstance
from . import prj
from .. import database as partdatabase


class UvpSampleForm(Form):
    pprojid = StringField("Part. project ID", [validators.DataRequired()])
    profileid = StringField("Profile ID", [validators.DataRequired()])
    filename = StringField("Filename", [validators.DataRequired(), validators.Length(min=5)])
    sampleid = IntegerField("Ecotaxa SampleID", [validators.Optional(strip_whitespace=True)])
    latitude = FloatField("Latitude [DD.DDDD] (- for South)", [validators.Optional(strip_whitespace=True)])
    longitude = FloatField("Longitude [DDD.DDDD] (- for West)", [validators.Optional(strip_whitespace=True)])
    organizedbydeepth = BooleanField("Profile Type Depth")
    integrationtime = IntegerField("Integration time (Time profile) [s]", [validators.Optional(strip_whitespace=True)])
    histobrutavailable = BooleanField("Raw histogram available ")
    qualitytaxo = StringField("Taxonomy QC")
    qualitypart = StringField("Particles QC")
    daterecalculhistotaxo = DateTimeField("Histogram process date & time", [validators.Optional(strip_whitespace=True)])
    winddir = IntegerField("Wind direction [°] (0-360)", [validators.Optional(strip_whitespace=True)])
    winspeed = IntegerField("Wind speed [knots]", [validators.Optional(strip_whitespace=True)])
    seastate = IntegerField("Sea state (1-12)", [validators.Optional(strip_whitespace=True)])
    nebuloussness = IntegerField("Nebuloussness (0-8)", [validators.Optional(strip_whitespace=True)])
    comment = StringField("Comment")
    stationid = StringField("Station ID")
    firstimage = IntegerField("First image Ok", [validators.Optional(strip_whitespace=True)])
    lastimg = IntegerField("Last img Ok", [validators.Optional(strip_whitespace=True)])
    lastimgused = IntegerField("Last image utilized", [validators.Optional(strip_whitespace=True)])
    bottomdepth = IntegerField("Bottom depth [m]", [validators.Optional(strip_whitespace=True)])
    yoyo = BooleanField("yoyo")
    sampledate = DateTimeField("Profile UTC date & time ", [validators.Optional(strip_whitespace=True)])
    ctd_desc = TextAreaField("CTD desc")
    ctd_origfilename = StringField("CTD filename (import)")
    ctd_import_name = StringField("CTD name (import)")
    ctd_import_email = StringField("CTD email (import)")
    ctd_import_datetime = DateTimeField("CTD date & time (import)", [validators.Optional(strip_whitespace=True)])
    ctd_status = StringField("CTD status")
    instrumsn = StringField("Instrument SN")
    acq_aa = FloatField("Aa (for UVP6, value is divided by 10<sup>6</sup>)",
                        [validators.Optional(strip_whitespace=True)])
    acq_exp = FloatField("Exp", [validators.Optional(strip_whitespace=True)])
    acq_volimage = FloatField("Image Volume [L]", [validators.Optional(strip_whitespace=True)])
    acq_depthoffset = FloatField("Depth Offset [M]", [validators.Optional(strip_whitespace=True)])
    acq_pixel = FloatField("Pixel size [mm]", [validators.Optional(strip_whitespace=True)])
    acq_shutterspeed = IntegerField("Acq Shutter speed", [validators.Optional(strip_whitespace=True)])
    acq_smzoo = IntegerField("Vignettes minimum size [Pixels]", [validators.Optional(strip_whitespace=True)])
    acq_exposure = IntegerField("Acq Exposure", [validators.Optional(strip_whitespace=True)])
    acq_gain = IntegerField("Acq Gain", [validators.Optional(strip_whitespace=True)])
    acq_filedescription = StringField("Acq Description", [validators.Optional(strip_whitespace=True)])
    acq_eraseborder = IntegerField("Acq Erase border (0/1)", [validators.Optional(strip_whitespace=True)])
    acq_tasktype = IntegerField("Acq Task type", [validators.Optional(strip_whitespace=True)])
    acq_threshold = IntegerField("Acq Threshold", [validators.Optional(strip_whitespace=True)])
    acq_choice = IntegerField("Acq Choice", [validators.Optional(strip_whitespace=True)])
    acq_disktype = IntegerField("Acq Disk type", [validators.Optional(strip_whitespace=True)])
    acq_smbase = IntegerField("Particle minimum size [pixels]", [validators.Optional(strip_whitespace=True)])
    acq_ratio = IntegerField("Acq Ratio", [validators.Optional(strip_whitespace=True)])
    acq_descent_filter = BooleanField("acq_descent_filter")
    acq_presure_gain = FloatField("Presure gain", [validators.Optional(strip_whitespace=True)])
    acq_xsize = IntegerField("Acq Xsize", [validators.Optional(strip_whitespace=True)])
    acq_ysize = IntegerField("Acq Ysize", [validators.Optional(strip_whitespace=True)])
    acq_barcode = StringField("Barcode")
    proc_datetime = DateTimeField("Process datetime", [validators.Optional(strip_whitespace=True)])
    proc_gamma = FloatField("Process gamma", [validators.Optional(strip_whitespace=True)])
    proc_soft = StringField("Images post process")
    op_sample_name = StringField("Operator name")
    op_sample_email = StringField("Operator email")
    lisst_zscat_filename = StringField("zscat filename")
    lisst_kernel = StringField("Kernel")
    proc_process_ratio = IntegerField("Process ratio", [validators.Optional(strip_whitespace=True)])
    imp_removed_empty_slice = IntegerField("Removed empty slice", [validators.Optional(strip_whitespace=True)])
    imp_descent_filtered_row = IntegerField("Descent filtered row", [validators.Optional(strip_whitespace=True)])


def delete_sample(psampleid):
    RawHistoFile = Path(sample_import.GetPathForRawHistoFile(psampleid))
    if RawHistoFile.exists():
        RawHistoFile.unlink()
    model = partdatabase.part_samples.query.filter_by(psampleid=psampleid).first()
    for t in ('part_histopart_reduit', 'part_histopart_det', 'part_histocat', 'part_histocat_lst', 'part_ctd'):
        ExecSQL("delete from " + t + " where psampleid=" + str(model.psampleid))
    db.session.delete(model)
    db.session.commit()


@part_app.route('/sampleedit/<int:psampleid>', methods=['get', 'post'])
def part_sampleedit(psampleid):
    ecotaxa_if = EcoTaxaInstance(ECOTAXA_URL, request)
    ecotaxa_user = ecotaxa_if.get_current_user()
    assert ecotaxa_user is not None  # @login_required
    model = partdatabase.part_samples.query.filter_by(psampleid=psampleid).first()
    form = UvpSampleForm(request.form, model)
    if gvp('delete') == 'Y':
        delete_sample(psampleid)
        return redirect("%sprj/" % PART_URL + str(model.pprojid))
    if request.method == 'POST' and form.validate():
        for k, v in form.data.items():
            setattr(model, k, v)
        db.session.commit()
        if gvp('forcerecalc') == 'Y':
            zoo_projid = model.project.projid
            instrumtype = model.project.instrumtype
            psampleid =  model.psampleid
            histograms.ComputeHistoDet(psampleid, instrumtype)
            histograms.ComputeHistoRed(psampleid, instrumtype)
            prj.ComputeZooMatch(ecotaxa_if, psampleid, zoo_projid)
            flash("Histograms have been recomputed", "success")
        return redirect("%sprj/" % PART_URL + str(model.pprojid))
    return part_PrintInCharte(ecotaxa_if, render_template("part/sampleedit.html", form=form, prjid=model.pprojid,
                                                          psampleid=model.psampleid,
                                                          acq_descent_filter=model.acq_descent_filter))
