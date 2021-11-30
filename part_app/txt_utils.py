def GetClassLimitTxt(LimitTab, Classe):
    if Classe >= len(LimitTab) - 1:
        return '>%.4g mm' % LimitTab[Classe - 1]
    if Classe == 0:
        return '<=%.4g µm' % (LimitTab[0] * 1000)
    if LimitTab[Classe] < 1:
        txt = '%.4g-%.4g µm' % (LimitTab[Classe - 1] * 1000, LimitTab[Classe] * 1000)
    else:
        txt = '%.4g-%.4g mm' % (LimitTab[Classe - 1], LimitTab[Classe])
    return txt


def GetPartClassLimitListText(LimitTab):
    res = ""
    for i in range(len(LimitTab) - 1):
        if i == 0:
            res = '%.4g µm' % (LimitTab[0] * 1000)
        elif LimitTab[i] < 1:
            res += ', %.4g µm' % (LimitTab[i] * 1000)
        else:
            res += ', %.4g mm' % (LimitTab[i])
    return res