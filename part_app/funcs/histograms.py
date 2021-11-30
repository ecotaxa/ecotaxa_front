import logging

from . import uvp_sample_import, lisst_sample_import, uvp6remote_sample_import
from ..remote import EcoTaxaInstance


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


def ComputeZooHisto(ecotaxa_if: EcoTaxaInstance, psampleid, instrumtype):
    try:
        if instrumtype == 'uvp6remote':
            uvp6remote_sample_import.GenerateTaxonomyHistogram(ecotaxa_if, psampleid)
        else:
            uvp_sample_import.GenerateTaxonomyHistogram(ecotaxa_if, psampleid)
        return " Taxonomy Histogram computed"
    except Exception as E:
        logging.exception("Taxonomy Histogram can't be computed (%s)", E)
        return " <span style='color: red;'>Taxonomy Histogram can't be computed : %s </span>" % str(E)
