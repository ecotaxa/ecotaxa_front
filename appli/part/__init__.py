# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.

from . import database

PartDetClassLimit=[0.001000,0.001260,0.001590,0.002000,0.002520,0.003170,0.004000,0.005040,0.006350,0.008000
        ,0.010100,0.012700,0.016000,0.020200,0.025400,0.032000,0.040300,0.050800,0.064000,0.080600
        ,0.102000,0.128000,0.161000,0.203000,0.256000,0.323000,0.406000,0.512000,0.645000,0.813000
        ,1.020000,1.290000,1.630000,2.050000,2.580000,3.250000,4.100000,5.160000,6.500000,8.190000
        ,10.300000,13.000000,16.400000,20.600000,26.0, 10E7]
PartRedClassLimit=[0.001000,0.002000,0.004000,0.008000,0.016000,0.032000,0.064000,0.128000,0.256000,0.512000,1.020000,2.050000,4.100000,8.190000,16.400000,10E7]

def GetClassLimitTxt(LimitTab,Classe):
    if Classe>=len(LimitTab)-1:
        return '>%.4g mm'%LimitTab[Classe-1]
    if Classe==0:
        return '<=%.4g µm' % (LimitTab[0]*1000)
    if LimitTab[Classe]<1:
        txt = '%.4g-%.4g µm' % (LimitTab[Classe - 1]*1000, LimitTab[Classe]*1000)
    else:
        txt='%.4g-%.4g mm'%(LimitTab[Classe-1],LimitTab[Classe])
    return txt

CTDFixedCol={
        "chloro fluo [mg chl/m3]": "chloro_fluo",
        "conductivity [ms/cm]": "conductivity",
        "cpar [%]": "cpar",
        "depth [salt water, m]": "depth_salt_water",
        "fcdom factory [ppb qse]": "fcdom_factory",
        "in situ density anomaly [kg/m3]": "in_situ_density_anomaly",
        "neutral density [kg/m3]": "neutral_density",
        "nitrate [µmol/l]": "nitrate",
        "oxygen [µmol/kg]": "oxygen_mass",
        "oxygen [ml/l]": "oxygen_vol",
        "par [µmol m-2 s-1]": "par",
        "part backscattering coef 470 nm [m-1]": "part_backscattering_coef_470_nm",
        "pot. temperature [degc] (any ref.)": "pot_temperature",
        "potential density anomaly [kg/m3]": "potential_density_anomaly",
        "potential temperature [degc]": "potential_temperature",
        "practical salinity [psu]": "practical_salinity",
        "practical salinity from conductivity": "practical_salinity__from_conductivity",
        "pressure in water column [db]": "depth",
        "qc flag": "qc_flag",
        "sound speed c [m/s]": "sound_speed_c",
        "spar [µmol m-2 s-1]": "spar",
        "temperature [degc]": "temperature"
    }
CTDFixedColByKey={v:k for k,v in CTDFixedCol.items()}

LstInstrumType=('uvp5','lisst')