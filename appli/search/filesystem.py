import os
import time
from pathlib import Path

from flask import render_template, json

from appli import app, gvg


@app.route('/common/ServerFolderSelect')
def ServerFolderSelect():
    res = []
    # the HTML id of the element which will be updated once selection is done
    target_id = gvg("target", "ServerPath")
    return render_template('common/fileserverpopup.html', root_elements=res,
                           targetid=target_id, ziponly=gvg('ZipOnly', 'N'))


@app.route('/common/ServerFolderSelectJSON')
def ServerFolderSelectJSON():
    ServerRoot = Path(app.config['SERVERLOADAREA'])
    CurrentPath = ServerRoot
    parent = gvg("id")
    if parent != '#':
        CurrentPath = ServerRoot.joinpath(Path(parent))
    res = []
    for x in CurrentPath.iterdir():
        rr = x.relative_to(ServerRoot).as_posix()
        rc = x.relative_to(CurrentPath).as_posix()
        try:
            if x.is_dir():
                if gvg('ZipOnly') == 'Y':
                    res.append(dict(id=rr, text="<span class=v>" + rc + "</span> ", parent=parent, children=True))
                else:
                    res.append(dict(id=rr,
                                    text="<span class=v>" + rc + "</span> <span class='TaxoSel label label-default'>Select</span>",
                                    parent=parent, children=True))
            if x.suffix.lower() == ".zip":
                fi = os.stat(x.as_posix())
                fmt = (rc, fi.st_size / 1048576, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(fi.st_mtime)))
                res.append(dict(id=rr,
                                text="<span class=v>" + "%s (%.1f Mb : %s)" % fmt + "</span> <span class='TaxoSel label label-default'>Select</span>",
                                parent=parent, children=False))
        except:
            None  # le parcours des fichiers peut planter sur system volume information par exemple.
    res.sort(key=lambda val: str.upper(val['id']), reverse=False)
    return json.dumps(res)
