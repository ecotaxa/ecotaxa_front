# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
#
# flask_admin views for EcoTaxa DB
#

from flask_admin.form import SecureForm


class SecureStrippingBaseForm(SecureForm):
    """
        A form metaclass stripping values
    """

    class Meta:
        def bind_field(self, form, unbound_field, options):
            filters = unbound_field.kwargs.get('filters', [])
            filters.append(_strip_filter)
            return unbound_field.bind(form=form, filters=filters, **options)


def _strip_filter(value):
    # strip field if possible
    if value is not None and hasattr(value, 'strip'):
        return value.strip()
    return value
