from typing import List

from flask import render_template, json, request

from appli import app, gvg
from to_back.ecotaxa_cli_py import FilesApi, DirectoryModel, DirectoryEntryModel
from utils import ApiClient


@app.route('/common/ServerFolderSelect')
def ServerFolderSelect():
    res = []
    # the HTML id of the element which will be updated once selection is done
    target_id = gvg("target", "ServerPath")
    return render_template('common/fileserverpopup.html', root_elements=res,
                           targetid=target_id, ziponly=gvg('ZipOnly', 'N'))


@app.route('/common/ServerFolderSelectJSON')
def ServerFolderSelectJSON():
    # Get posted vars
    parent = gvg("id")
    zip_only = gvg('ZipOnly') == 'Y'
    # The explored part
    if parent == '#':
        current_path = ""  # root
    else:
        current_path = parent
    # Call back-end for directory content
    with ApiClient(FilesApi, request) as api:
        # List files remotely
        dir_desc: DirectoryModel = api.list_common_files_common_files_get(path=current_path)
        entries_in_dir: List[DirectoryEntryModel] = dir_desc.entries

    res = []
    for entry in entries_in_dir:
        path_to_root = (current_path + "/" if current_path else "") + entry.name
        entry_name = entry.name
        if entry.type == "D":
            if zip_only:
                res.append(dict(id=path_to_root,
                                text="<span class=v>" + entry_name + "</span> ",
                                parent=parent, children=True))
            else:
                res.append(dict(id=path_to_root,
                                text="<span class=v>" + entry_name + "</span>" +
                                     " <span class='TaxoSel label label-default'>Select</span>",
                                parent=parent, children=True))
        if entry.name.lower().endswith(".zip"):
            # For zip files we have details, the date is a bit too precise however
            fmt = (entry_name, entry.size / 1048576, entry.mtime[:-7])
            res.append(dict(id=path_to_root,
                            text="<span class=v>" + "%s (%.1f Mb : %s)" % fmt + "</span>" +
                                 " <span class='TaxoSel label label-default'>Select</span>",
                            parent=parent, children=False))
    res.sort(key=lambda val: str.upper(val['id']), reverse=False)
    return json.dumps(res)
