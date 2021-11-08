PartDetClassLimit=[0.001000, 0.001260, 0.001590, 0.002000, 0.002520, 0.003170, 0.004000, 0.005040, 0.006350, 0.008000
        , 0.010100, 0.012700, 0.016000, 0.020200, 0.025400, 0.032000, 0.040300, 0.050800, 0.064000, 0.080600
        , 0.102000, 0.128000, 0.161000, 0.203000, 0.256000, 0.323000, 0.406000, 0.512000, 0.645000, 0.813000
        , 1.020000, 1.290000, 1.630000, 2.050000, 2.580000, 3.250000, 4.100000, 5.160000, 6.500000, 8.190000
        , 10.300000, 13.000000, 16.400000, 20.600000, 26.0, 10E7]
PartRedClassLimit=[0.001000,0.002000,0.004000,0.008000,0.016000,0.032000,0.064000,0.128000,0.256000,0.512000,1.020000,2.050000,4.100000,8.190000,16.400000,10E7]
CTDFixedCol={
        "chloro fluo [mg chl m-3]": "chloro_fluo",
        "conductivity [ms cm-1]": "conductivity",
        "cpar [%]": "cpar",
        "depth [m]": "depth_salt_water",
        "fcdom [ppb qse]": "fcdom_factory",
        "in situ density anomaly [kg m-3]": "in_situ_density_anomaly",
        "nitrate [umol l-1]": "nitrate",
        "oxygen [umol kg-1]": "oxygen_mass",
        "oxygen [ml l-1]": "oxygen_vol",
        "par [umol m-2 s-1]": "par",
        "potential density anomaly [kg m-3]": "potential_density_anomaly",
        "potential temperature [degc]": "potential_temperature",
        "practical salinity [psu]": "practical_salinity",
        "pressure [db]": "depth",
        "qc flag": "qc_flag",
        "spar [umol m-2 s-1]": "spar",
        "temperature [degc]": "temperature",
        "time [yyyymmddhhmmssmmm]": "datetime"
    }
CTDFixedColByKey={v:k for k,v in CTDFixedCol.items()}
LstInstrumType=('uvp5','uvp6','lisst','uvp6remote')