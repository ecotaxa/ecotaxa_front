import logging

from . import uvp_sample_import, lisst_sample_import, uvp6remote_sample_import


def ComputeHistoDet(psampleid, instrumtype):
    try:
        if instrumtype in ('uvp5', 'uvp6'):
            uvp_sample_import.GenerateParticleHistogram(psampleid)
            return " Detailed & reduced Histogram computed"
        elif instrumtype == 'lisst':
            lisst_sample_import.GenerateParticleHistogram(psampleid)
            return " Detailed & reduced Histogram computed"
        elif instrumtype == 'uvp6remote':
            uvp6remote_sample_import.GenerateParticleHistogram(psampleid)
            return " Detailed & reduced Histogram computed"
        else:
            Msg = 'Invalid instrument'
    except Exception as E:
        Msg = str(E)
    return " <span style='color: red;'>" + Msg + "</span>"


def ComputeHistoRed(psampleid, instrumtype):
    return uvp_sample_import.GenerateReducedParticleHistogram(psampleid)


def ComputeZooHisto(psampleid, instrumtype):
    try:
        if instrumtype == 'uvp6remote':
            uvp6remote_sample_import.GenerateTaxonomyHistogram(psampleid)
        else:
            uvp_sample_import.GenerateTaxonomyHistogram(psampleid)
        return " Taxonomy Histogram computed"
    except Exception as E:
        logging.exception("Taxonomy Histogram can't be computed ")
        return " <span style='color: red;'>Taxonomy Histogram can't be computed : %s </span>" % (E)