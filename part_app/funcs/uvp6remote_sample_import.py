import csv
import datetime
import io
import logging
import os
import re
import shutil
import ssl
import tempfile
import urllib.request
import zipfile
from ftplib import FTP
from html.parser import HTMLParser

import numpy as np

from ..txt_utils import ntcv
from .. import database as partdatabase
from ..app import db
from ..db_utils import ExecSQL
from ..funcs import uvp_sample_import as uvp_sample_import
from ..funcs.common_sample_import import ToFloat, GenerateReducedParticleHistogram
from ..remote import EcoTaxaInstance


class ATagParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.FoundA = []

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        attr_dict = dict(attrs)
        if 'href' not in attr_dict:
            return
        href = attr_dict['href']
        if ':' in href:
            return  # on ignore les url qui respécifient un protocole
        if not href.endswith('.txt'):
            return  # on ne garde que les .txt
        fichier = os.path.basename(href)
        self.FoundA.append(fichier)


def ParseMetadataFile(MetaF):
    MetaData = {}
    for l in MetaF:
        cols = l.strip().split('\t')
        if len(cols) == 2:
            MetaData[cols[0].lower()] = cols[1]
    return MetaData


class RemoteServerFetcher:
    def __init__(self, pprojid: int):
        self.Prj = partdatabase.part_projects.query.filter_by(pprojid=pprojid).first()
        self.ftp = None

    def Connect(self):
        self.ftp = FTP(host=self.Prj.remote_url, user=self.Prj.remote_user, passwd=self.Prj.remote_password, timeout=10)
        if ntcv(self.Prj.remote_directory) != "":
            self.ftp.cwd(self.Prj.remote_directory)

    def IsHttp(self):
        return self.Prj.remote_url.startswith('http:') or self.Prj.remote_url.startswith('https:')

    def GetHTTPUrl(self, Filename=''):
        url = self.Prj.remote_url
        if (not url.endswith('/')) and (not self.Prj.remote_directory.startswith('/')):
            url += '/'
        url += self.Prj.remote_directory
        if not url.endswith('/'):
            url += '/'
        url += Filename
        return url

    def RetrieveFile(self, FileName, TempFile):
        if self.IsHttp():
            ContexteSSLSansControle = ssl.SSLContext()
            with urllib.request.urlopen(self.GetHTTPUrl(FileName), context=ContexteSSLSansControle) as response:
                html = response.read()
                TempFile.write(html)
        else:
            self.ftp.retrbinary('RETR %s' % FileName, TempFile.write)

    def GetServerFiles(self):
        """Retourne la liste des fichiers sous forme d'un dictionnaire
        clé : N° de sample value=> sampletype,files[filetype]:filename
        Exemple :
        {'SG003B': {'sampletype': 'TIME',
            'files': {'META': 'SG003B_000002LP_TIME_META.txt', 'LPM': 'SG003B_000002LP_TIME_LPM.txt', 'BLACK': 'SG003B_000002LP_TIME_BLACK.txt'}
             },
        'SG003A': {'sampletype': 'DEPTH',
            'files': {'TAXO2': 'SG003A_000002LP_DEPTH_TAXO2.txt', 'META': 'SG003A_000002LP_DEPTH_META.txt'
                    , 'LPM': 'SG003A_000002LP_DEPTH_LPM.txt', 'TAXO1': 'SG003A_000002LP_DEPTH_TAXO1.txt'
                    , 'BLACK': 'SG003A_000002LP_DEPTH_BLACK.txt'} }}
"""
        if self.IsHttp():
            lst = self.GetServerFilelistHTTP()
        else:
            lst = self.GetServerFilelistFTP()
        Samples = {}
        for entry in lst:
            if entry[-4:] != '.txt':  # premier filtrage basique et silencieux
                continue
            m = re.fullmatch("""([^_]+)_([^_]+)_([^_]+)_([^_]+)\.txt""", entry)
            if m is None:
                logging.warning("Particule RemoteServerFetcher.GetServerFiles Skip malformed file " + entry)
                continue
            SampleName = m.group(1)
            if SampleName not in Samples:
                Samples[SampleName] = {'sampletype': m.group(3), 'files': {}}
            Samples[SampleName]['files'][m.group(4)] = entry
            # print(entry, m.group(1), m.group(2), m.group(3), m.group(4))
        return Samples

    def GetServerFilelistHTTP(self):
        ContexteSSLSansControle = ssl.SSLContext()
        url = self.GetHTTPUrl()
        Req = urllib.request.Request(url)
        with urllib.request.urlopen(Req, context=ContexteSSLSansControle) as response:
            html = response.read().decode('latin-1')
            parser = ATagParser()
            parser.feed(html)
            return parser.FoundA

    def GetServerFilelistFTP(self):
        if self.ftp is None:
            self.Connect()
        return list(self.ftp.nlst())

    def FetchServerDataForProject(self, ForcedSample: list):
        if self.Prj.remote_type == 'TSV LOV':
            return self.FetchServerDataForProjectLamda(ForcedSample)

    def FetchServerDataForProjectLamda(self, ForcedSample: list):
        """
        Recupère les données d'un serveur lamba et les charge
        :param ForcedSample: Permet de forcer une liste de samplename pour ne traiter que ceux là et forcer leur rechargement même s'il existent déjà
        :return Liste des sampleid
        """
        returnedsampleid = []
        ServerSamples = self.GetServerFiles()
        DBSamples = partdatabase.part_samples.query.filter_by(pprojid=self.Prj.pprojid)
        DBSamplesNames = {s.profileid: s for s in DBSamples}
        if len(ForcedSample) == 0:
            ForcedSample = None
        TmpDir = None
        for SampleName in ServerSamples:
            if ForcedSample:  # on restreint la liste de ce qu'on traite
                if SampleName not in ForcedSample:
                    continue
            Sample = None
            if SampleName in DBSamplesNames:  # Sample existe déjà
                if ForcedSample and SampleName in ForcedSample:  # mais on souhaite reforce son chargement
                    Sample = DBSamplesNames[SampleName]
                else:
                    continue  # existe déjà sans souhait de reforcer son chargement, on saute
            if 'META' not in ServerSamples[SampleName]['files'] or 'LPM' not in ServerSamples[SampleName]['files']:
                logging.warning(
                    "Particule RemoteServerFetcher.GetServerFiles skip processing : META and LPM are required to handle sample "
                    + SampleName)
                continue
            print("Processing sample ", SampleName)
            if Sample is None:
                Sample = partdatabase.part_samples()
                db.session.add(Sample)
            TmpDir = tempfile.mkdtemp()
            with zipfile.ZipFile(TmpDir + '/raw.zip', 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                for filetype in ServerSamples[SampleName]['files']:
                    with open(TmpDir + "/" + filetype, "wb") as TmpF:
                        self.RetrieveFile(ServerSamples[SampleName]['files'][filetype], TmpF)
                    zf.write(TmpF.name, arcname=filetype + '.txt')
            with open(TmpDir + "/META", 'r') as MetaF:
                MetaData = ParseMetadataFile(MetaF)

            Sample.pprojid = self.Prj.pprojid
            Sample.profileid = SampleName
            Sample.filename = ServerSamples[SampleName]['files']['LPM']
            if 'CTD' in ServerSamples[SampleName]['files']:
                Sample.ctd_origfilename = ServerSamples[SampleName]['files']['CTD']
            Sample.instrumsn = MetaData.get('camera_ref', '')
            Sample.acq_aa = MetaData.get('aa', '')
            Sample.acq_exp = MetaData.get('exp', '')
            Sample.acq_pixel = MetaData.get('pixel_size', '')
            Sample.acq_volimage = MetaData.get('image_volume', '')
            Sample.acq_gain = MetaData.get('gain', '')
            Sample.acq_threshold = MetaData.get('threshold', '')
            Sample.acq_shutterspeed = MetaData.get('shutter', '')
            Sample.instrumsn = MetaData.get('camera_ref', '')
            # Sample.op_sample_email=MetaData.get('operator_email','')
            Sample.histobrutavailable = True
            Sample.organizedbydeepth = ServerSamples[SampleName]['sampletype'] == 'DEPTH'
            if MetaData.get('pressure_offset', '') != '':
                Sample.acq_depthoffset = ToFloat(MetaData.get('pressure_offset', ''))

            # Lat,Long et Date sont les moyennes du fichier LPM
            SamplesData = np.genfromtxt(TmpDir + "/LPM", names=True, delimiter='\t', autostrip=True
                                        , usecols=['DATE_TIME', 'LATITUDE_decimal_degree', 'LONGITUDE_decimal_degree']
                                        # ,usecols=[0,2,3]
                                        , dtype=[('DATE_TIME', 'S15'), ('LATITUDE_decimal_degree', '<f4'),
                                                 ('LONGITUDE_decimal_degree', '<f4')])
            if len(SamplesData.shape) == 0:  # s'il n'y a qu'une seul ligne genfromtxt ne retourne pas un tableau à 2 dimensions, donc ou transforme celui ci
                SamplesData = np.array([SamplesData])
            Sample.latitude = round(np.average(SamplesData['LATITUDE_decimal_degree'] + 360) - 360, 3)
            Sample.longitude = round(np.average(SamplesData['LONGITUDE_decimal_degree'] + 360) - 360, 3)
            FirstDate = datetime.datetime.strptime(SamplesData['DATE_TIME'][0].decode(), '%Y%m%dT%H%M%S')
            LastDate = datetime.datetime.strptime(SamplesData['DATE_TIME'][SamplesData.shape[0] - 1].decode(),
                                                  '%Y%m%dT%H%M%S')
            Sample.sampledate = datetime.datetime.fromtimestamp(int((FirstDate.timestamp() + LastDate.timestamp()) / 2))

            db.session.commit()
            returnedsampleid.append(Sample.psampleid)
            rawfileinvault = uvp_sample_import.GetPathForRawHistoFile(Sample.psampleid)
            shutil.copyfile(TmpDir + '/raw.zip', rawfileinvault)
            # shutil.copyfile(MetaF.name, "c:/temp/testmeta.txt")
            # shutil.copyfile(TmpDir+'/raw.zip', "c:/temp/testremote.zip")
        if TmpDir:
            shutil.rmtree(TmpDir)
        return returnedsampleid


def GenerateParticleHistogram(psampleid):
    """
    Génération de l'histogramme particulaire détaillé (45 classes) et réduit (15 classes) à partir du fichier ASC
    :param psampleid:
    :return:
    """
    PartSample = partdatabase.part_samples.query.filter_by(psampleid=psampleid).first()
    if PartSample is None:
        raise Exception("GenerateRawHistogram: Sample %d missing" % psampleid)
    Prj = partdatabase.part_projects.query.filter_by(pprojid=PartSample.pprojid).first()
    rawfileinvault = uvp_sample_import.GetPathForRawHistoFile(PartSample.psampleid)
    DepthOffset = Prj.default_depthoffset
    if DepthOffset is None:
        DepthOffset = PartSample.acq_depthoffset
    if DepthOffset is None:
        DepthOffset = 0

    with zipfile.ZipFile(rawfileinvault, "r") as zf:
        with zf.open('LPM.txt', 'r') as flpmb:
            flpm = io.TextIOWrapper(flpmb, encoding='latin_1')
            csvfile = csv.DictReader(flpm, delimiter='\t')
            NbrLine = 0
            HistoByTranche = {}
            for L in csvfile:
                NbrLine += 1
                Depth = float(L['PRES_decibar']) + DepthOffset
                Time = L['DATE_TIME']
                if PartSample.organizedbydeepth:
                    Tranche = (Depth // 5) * 5
                    DepthTranche = Tranche + 2.5
                else:
                    Tranche = Time[:-4]  # On enlève minute et secondes
                    DepthTranche = Depth  # on prend la premiere profondeur
                NbrParClasse = {}
                # GreyParClasse = {}
                NbrImg = float(L['IMAGE_NUMBER_PARTICLES'])
                for classe in range(18):
                    NbrParClasse[classe] = round(
                        ToFloat(L['NB_SIZE_SPECTRA_PARTICLES_class_%s' % (classe + 1,)]) * NbrImg)
                if Tranche not in HistoByTranche:
                    HistoByTranche[Tranche] = {'NbrImg': NbrImg, 'NbrParClasse': NbrParClasse,
                                               'DepthTranche': DepthTranche}  # ,'GreyParClasse':GreyParClasse
                else:
                    HistoByTranche[Tranche]['NbrImg'] += NbrImg
                    for classe in range(18):
                        HistoByTranche[Tranche]['NbrParClasse'][classe] += NbrParClasse[classe]
            logging.info("Line count %d" % NbrLine)

            ExecSQL("delete from part_histopart_det where psampleid=" + str(psampleid))
            sql = """insert into part_histopart_det(psampleid, lineno, depth,  watervolume,datetime
                , class17, class18, class19, class20, class21, class22, class23, class24, class25, class26, class27, class28, class29
                , class30, class31, class32, class33, class34)
            values(%(psampleid)s,%(lineno)s,%(depth)s,%(watervolume)s,%(datetime)s,%(class17)s,%(class18)s,%(class19)s,%(class20)s,%(class21)s,%(class22)s
            ,%(class23)s,%(class24)s,%(class25)s,%(class26)s,%(class27)s,%(class28)s
            ,%(class29)s,%(class30)s,%(class31)s,%(class32)s,%(class33)s,%(class34)s)"""
            sqlparam = {'psampleid': psampleid}
            Tranches = sorted(HistoByTranche.keys())
            for i, Tranche in enumerate(Tranches):
                sqlparam['lineno'] = i
                sqlparam['depth'] = round(HistoByTranche[Tranche]['DepthTranche'], 2)
                sqlparam['watervolume'] = round(HistoByTranche[Tranche]['NbrImg'] * PartSample.acq_volimage, 3)
                if PartSample.organizedbydeepth:
                    sqlparam['datetime'] = None
                else:
                    sqlparam['datetime'] = datetime.datetime.strptime(Tranche + '3000',
                                                                      "%Y%m%dT%H%M%S")  # on insère avec l'heure à 30minutes

                for classe in range(18):
                    sqlparam['class%02d' % (17 + classe)] = HistoByTranche[Tranche]['NbrParClasse'][classe]
                ExecSQL(sql, sqlparam)
    GenerateReducedParticleHistogram(psampleid)


def GenerateTaxonomyHistogram(ecotaxa_if: EcoTaxaInstance, psampleid):
    """
    Génération de l'histogramme Taxonomique
    :param psampleid:
    :return:
    """
    PartSample = partdatabase.part_samples.query.filter_by(psampleid=psampleid).first()
    if PartSample is None:
        raise Exception("GenerateTaxonomyHistogram: Sample %d missing" % psampleid)
    Prj = partdatabase.part_projects.query.filter_by(pprojid=PartSample.pprojid).first()
    rawfileinvault = uvp_sample_import.GetPathForRawHistoFile(PartSample.psampleid)
    DepthOffset = Prj.default_depthoffset
    if DepthOffset is None:
        DepthOffset = PartSample.acq_depthoffset
    if DepthOffset is None:
        DepthOffset = 0
    with zipfile.ZipFile(rawfileinvault, "r") as zf:
        with zf.open("META.txt", 'r') as MetaFb:
            MetaF = io.TextIOWrapper(MetaFb, encoding='latin_1')
            MetaData = ParseMetadataFile(MetaF)
            TaxoIds = list(range(40))
            for i in range(40):
                try:
                    TaxoIds[i] = int(MetaData.get('category_name_%d' % (i + 1), ''))
                except:
                    TaxoIds[i] = 0

            valid_ids = [x for x in TaxoIds if x > 0]
            if len(valid_ids) == 0:
                raise Exception("GenerateTaxonomyHistogram: Sample %d no valid category_name_" % psampleid)
            TaxoDB = set([tid for tid, _name in ecotaxa_if.get_taxo(valid_ids)])

            for i in range(40):
                if TaxoIds[i] > 0:
                    if TaxoIds[i] not in TaxoDB:
                        raise Exception(
                            "GenerateTaxonomyHistogram: Sample %d category_name_%d is not a known taxoid" %
                            (psampleid, (i + 1)))

        with zf.open('TAXO2.txt', 'r') as ftaxob:
            ftaxo = io.TextIOWrapper(ftaxob, encoding='latin_1')
            csvfile = csv.DictReader(ftaxo, delimiter='\t')
            NbrLine = 0
            HistoByTranche = {}
            for L in csvfile:
                if L['PRES_decibar'] == '':  # ligne vide
                    continue
                NbrLine += 1
                Depth = float(L['PRES_decibar']) + DepthOffset
                Time = L['DATE_TIME']
                if PartSample.organizedbydeepth:
                    Tranche = (Depth // 5) * 5
                    DepthTranche = Tranche + 2.5
                else:
                    Tranche = Time[:-4]  # On enlève Heure et minute
                    DepthTranche = Depth  # on prend la premiere profondeur
                NbrParClasse = {}
                SizeParClasse = {}
                NbrImg = float(L['IMAGE_NUMBER_PLANKTON'])
                for classe in range(40):
                    NbrParClasse[classe] = ToFloat(L['NB_PLANKTON_cat_%s' % (classe + 1,)])
                    SizeParClasse[classe] = ToFloat(L['SIZE_PLANKTON_cat_%s' % (classe + 1,)])
                    SizeParClasse[classe] = NbrParClasse[classe] * SizeParClasse[classe] if SizeParClasse[classe] else 0
                if Tranche not in HistoByTranche:
                    HistoByTranche[Tranche] = {'NbrImg': NbrImg, 'NbrParClasse': NbrParClasse,
                                               'DepthTranche': DepthTranche
                        , 'SizeParClasse': SizeParClasse}
                else:
                    HistoByTranche[Tranche]['NbrImg'] += NbrImg
                    for classe in range(40):
                        HistoByTranche[Tranche]['NbrParClasse'][classe] += NbrParClasse[classe]
                        HistoByTranche[Tranche]['SizeParClasse'][classe] += SizeParClasse[classe]
            for Tranche in HistoByTranche:  # fin calcul du niveau de gris moyen pas tranche/classe
                for classe in range(40):
                    if HistoByTranche[Tranche]['NbrParClasse'][classe] > 0:
                        HistoByTranche[Tranche]['SizeParClasse'][classe] /= HistoByTranche[Tranche]['NbrParClasse'][
                            classe]
            logging.info("Line count %d" % NbrLine)

            ExecSQL("delete from part_histocat_lst where psampleid=%s" % psampleid)
            ExecSQL("delete from part_histocat where psampleid=%s" % psampleid)
            sql = """INSERT INTO part_histocat(psampleid, classif_id, lineno, depth, watervolume, nbr, avgesd, totalbiovolume)
                    VALUES(%(psampleid)s,%(classif_id)s,%(lineno)s,%(depth)s,%(watervolume)s,%(nbr)s,%(avgesd)s,%(totalbiovolume)s)"""
            sqlparam = {'psampleid': psampleid}
            Tranches = sorted(HistoByTranche.keys())
            for i, Tranche in enumerate(Tranches):
                sqlparam['lineno'] = i
                sqlparam['depth'] = HistoByTranche[Tranche]['DepthTranche']
                sqlparam['watervolume'] = round(HistoByTranche[Tranche]['NbrImg'] * PartSample.acq_volimage, 3)
                for classe in range(40):
                    if TaxoIds[classe] > 0 and HistoByTranche[Tranche]['NbrParClasse'][classe] > 0:
                        sqlparam['classif_id'] = TaxoIds[classe]
                        sqlparam['nbr'] = HistoByTranche[Tranche]['NbrParClasse'][classe]
                        sqlparam['avgesd'] = HistoByTranche[Tranche]['SizeParClasse'][classe]
                        sqlparam['totalbiovolume'] = None
                        ExecSQL(sql, sqlparam)
            ExecSQL("""insert into part_histocat_lst(psampleid, classif_id) 
            select distinct psampleid,classif_id from part_histocat where psampleid=%s""" % psampleid)


if __name__ == "__main__":
    RSF = RemoteServerFetcher(1)
    # print(RSF.GetServerFiles())
    # RSF.FetchServerDataForProject(['SG003A'])
