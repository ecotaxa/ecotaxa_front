from unittest import TestCase


class TestCalcAstralDayTime(TestCase):
    def test_CalcAstralDayTime(self):
        from appli import CalcAstralDayTime
        from datetime import date, time
        Date = date(2015, 1, 1)
        Latitude = 15
        print("Test CalcAstralDayTime")
        # Test Longitude 0° 'dawn/aube':15h35 ,'sunrise/levé': 6h25  , 'sunset/coucher': 17h41, 'dusk/crepuscule':18h31
        self.assertEqual(CalcAstralDayTime(Date, time(12,0,0), Latitude, 0 ),'D') # 12h Day
        self.assertEqual(CalcAstralDayTime(Date, time(23,0,0), Latitude, 0 ),'N') # 12h Night
        self.assertEqual(CalcAstralDayTime(Date, time( 1,0,0), Latitude, 0 ),'N') #  1h Night
        self.assertEqual(CalcAstralDayTime(Date, time( 6,0,0), Latitude, 0 ),'A') #  6h Dawn
        self.assertEqual(CalcAstralDayTime(Date, time(18,0,0), Latitude, 0 ),'U') # 18h Dusk
        # 'dawn/aube':17h36 ,'sunrise/levé': 18h26  , 'sunset/coucher': 5h41, 'dusk/crepuscule':6h31
        self.assertEqual(CalcAstralDayTime(Date, time(12, 0, 0), Latitude, -180), 'N')  # 12h 180 Nigth
        self.assertEqual(CalcAstralDayTime(Date, time(18, 0, 0), Latitude, -180), 'A')  # 18h 180 Dawn
        self.assertEqual(CalcAstralDayTime(Date, time(19, 0, 0), Latitude, -180), 'D')  # 19h 180 Day
        self.assertEqual(CalcAstralDayTime(Date, time( 2, 0, 0), Latitude, -180), 'D')  #  2h 180 Day
        self.assertEqual(CalcAstralDayTime(Date, time( 6, 0, 0), Latitude, -180), 'U')  #  6h 180 dusk
        self.assertEqual(CalcAstralDayTime(Date, time( 7, 0, 0), Latitude, -180), 'N')  #  7h 180 Nigth

    def test_LectureDegrees(self):
        from appli.tasks.importcommon import ConvTextDegreeToDecimalDegree
        # Test du format decimal historique/Degrée minute utilisée dans les fichiers header de la partie ecopart
        self.assertEqual(ConvTextDegreeToDecimalDegree("1.3", False), 1.5)
        self.assertEqual(ConvTextDegreeToDecimalDegree("-1.3", False), -1.5)
        # Test de la limitation à 5 décimales car les division par 60 on tendance à créer des rationnels.
        self.assertEqual(ConvTextDegreeToDecimalDegree("10.4583", False), 10.76383)
        # Test du format degrée décimal utilisé dans les objets depuis toujours
        self.assertEqual(ConvTextDegreeToDecimalDegree("1.5"), 1.5)
        self.assertEqual(ConvTextDegreeToDecimalDegree("-1.5"), -1.5)
        # Test du format  DD°MM SS utilisé par UVP App
        self.assertEqual(ConvTextDegreeToDecimalDegree("1°30 00"), 1.5)
        self.assertEqual(ConvTextDegreeToDecimalDegree("-1°30 00"), -1.5)
        # Test de la limitation à 5 décimales
        self.assertEqual(ConvTextDegreeToDecimalDegree("1°30 1"), 1.50028)
        self.assertEqual(ConvTextDegreeToDecimalDegree("-1°30 1"), -1.50028)



