import sys
# on fait le activate avant de lancer apache car sinon il trouve pas python 3.4 car sur mon PC default = 2.7
# #activate_this = R'D:\dev\_Client\LOV\EcoTaxa\Python\Scripts\activate_this.py'
#execfile(activate_this, dict(__file__=activate_this))
#exec(open(activate_this).read())
import sys
sys.path.insert(0, R'D:\dev\_Client\LOV\EcoTaxa\Appli')
sys.path.insert(0, R'D:\dev\_Client\LOV\EcoTaxa\Python\Lib\site-packages')
from appli import app as application
