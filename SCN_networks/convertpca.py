import sklearn.externals.joblib
import joblib
from pathlib import Path

P=Path('.')
for d in P.glob('*') :
    if d.is_dir():
        fsrc=d/"feature_pca.jbl"
        fdst = d / "feature_pca.old.jbl"
        if fsrc.is_file() and not fdst.is_file():
            print(fsrc)
            model=joblib.load(fsrc.open('rb'))
            fsrc.rename(fdst.as_posix())
            sklearn.externals.joblib.dump(model,fsrc.as_posix())
