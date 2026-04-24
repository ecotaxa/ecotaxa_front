from flask_babel import _

py_messages = {
    "collectioncreated": _("Collection created"),
    "collectionupdated": _("Collection updated"),
    "collectionnotyours": _("Uou cannot manage this collection."),
    "collectionpublished": _(
        "Collection is published. Modifications and Erase are forbidden."
    ),
    "collectioneraseerror": _("error in erasing collection "),
    "selectothercollection": _("Select another collection"),
    "collection404": _("Collection does not exist"),
}
