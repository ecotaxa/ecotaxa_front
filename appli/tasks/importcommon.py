from appli import ntcv
from appli.database import GetAll
import re,logging

# object_annotation_category_id
PredefinedTables=['obj_field','sample','process','acq']
# PredefinedTypes={'[float]':'n','[int]':'n','[text]':'t'}
PredefinedTypes={'[f]':'n','[t]':'t'}
PredefinedFields={
    'object_id':{'table':'obj_field','field':'orig_id','type':'t'},
    'sample_id':{'table':'sample','field':'orig_id','type':'t'},
    'acq_id':{'table':'acq','field':'orig_id','type':'t'},
    'process_id':{'table':'process','field':'orig_id','type':'t'},
    'object_lat':{'table':'obj_head','field':'latitude','type':'n'},
    'object_lon':{'table':'obj_head','field':'longitude','type':'n'},
    'object_date':{'table':'obj_head','field':'objdate','type':'t'},
    'object_time':{'table':'obj_head','field':'objtime','type':'t'},
    'object_link':{'table':'obj_head','field':'object_link','type':'t'},
    'object_depth_min':{'table':'obj_head','field':'depth_min','type':'n'},
    'object_depth_max':{'table':'obj_head','field':'depth_max','type':'n'},
    'object_annotation_category':{'table':'obj_head','field':'classif_id','type':'t'},
    'object_annotation_category_id':{'table':'obj_head','field':'classif_id','type':'n'},
    'object_annotation_person_email':{'table':'obj_head','field':'tmp_annotemail','type':'t'},
    'object_annotation_date':{'table':'obj_head','field':'classif_when','type':'t'},
    'object_annotation_time':{'table':'obj_head','field':'tmp_annottime','type':'t'},
    'object_annotation_person_name':{'table':'obj_head','field':'classif_who','type':'t'},
    'object_annotation_status':{'table':'obj_head','field':'classif_qual','type':'t'},
    'img_rank':{'table':'image','field':'imgrank','type':'n'},
    'img_file_name':{'table':'image','field':'orig_file_name','type':'t'},
    'annotation_person_first_name':{'table':'obj_head','field':'tmp_todelete1','type':'t'},
    'sample_dataportal_descriptor':{'table':'sample','field':'dataportal_descriptor','type':'t'},
    'acq_instrument': {'table': 'acq', 'field': 'instrument', 'type': 't'},
}
# Purge les espace et converti le Nan en vide
def CleanValue(v):
    if v is None:
        return ''
    v=v.strip()
    if (v.lower() == 'nan') or (v.lower() == 'na'):
        v=''
    return v
# retourne le flottant image de la chaine en faisant la conversion ou None
def ToFloat(value):
    if value=='': return None
    try:
        return float(value)
    except ValueError:
        return None

def ResolveTaxoFound(TaxoFound,o_NotFoundTaxo):
    lowertaxonlist = []
    regexsearchparenthese = re.compile('(.+) \((.+)\)$')
    for lowertaxon in TaxoFound.keys():
        TaxoFound[lowertaxon]={'nbr':0,'id' : None }
        lowertaxonlist.append(lowertaxon)
        resregex = regexsearchparenthese.match(lowertaxon)
        if resregex:  # Si on trouve des parenthèse à la fin
            lowertaxonLT = resregex.group(1) + '<' + resregex.group(2)
            TaxoFound[lowertaxon]['alterdisplayname'] = lowertaxonLT
            lowertaxonlist.append(lowertaxonLT)

    TaxonsFromDB = GetAll(
        """SELECT t.id,lower(t.name) AS name,lower(t.display_name) display_name,lower(t.name)||'<'||lower(p.name) AS computedchevronname 
            FROM taxonomy t
            LEFT JOIN taxonomy p on t.parent_id=p.id
            WHERE lower(t.name) = ANY(%s) OR lower(t.display_name) = ANY(%s) or lower(t.name)||'<'||lower(p.name) = ANY(%s) """
        , [lowertaxonlist, lowertaxonlist, lowertaxonlist])
    for recTaxon in TaxonsFromDB:
        for FoundK, FoundV in TaxoFound.items():
            if (FoundK == recTaxon['name']) or (FoundK == recTaxon['display_name']) or (FoundK == recTaxon['computedchevronname']) \
                    or (('alterdisplayname' in FoundV) and (FoundV['alterdisplayname'] == recTaxon['display_name'])):
                TaxoFound[FoundK]['nbr'] += 1
                TaxoFound[FoundK]['id'] = recTaxon['id']
    logging.info("Taxo Found = %s", TaxoFound)
    for FoundK, FoundV in TaxoFound.items():
        if FoundV['nbr'] == 0:
            logging.info("Taxo '%s' Not Found", FoundK)
            o_NotFoundTaxo.append(FoundK)
        elif FoundV['nbr'] > 1:
            logging.info("Taxo '%s' Found more than once", FoundK)  # traité comme si pas trouvé
            o_NotFoundTaxo.append(FoundK)
            TaxoFound[FoundK]['id'] = None
    for FoundK, FoundV in TaxoFound.items():
        TaxoFound[FoundK]=FoundV['id'] # in fine on ne garde que l'id, les autres champs etaient temporaires.

