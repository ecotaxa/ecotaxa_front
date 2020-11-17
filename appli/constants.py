ClassifQual = {'P': 'predicted', 'D': 'dubious', 'V': 'validated'}

DayTimeList = {'A': 'Dawn', 'D': 'Day', 'U': 'Dusk', 'N': 'Night'}

def GetClassifQualClass(q):
    return 'status-' + ClassifQual.get(q, "unknown")
