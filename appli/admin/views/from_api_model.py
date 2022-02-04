#
# Build a view from API model
#
import datetime
from abc import ABC
from typing import Any, Type, List, Tuple

from flask_admin.model import BaseModelView
from flask_security.forms import Form


class APIModelView(BaseModelView, ABC):

    def __init__(self, model: Any, name: str):
        # No real class for openapi generated models
        super().__init__(model=model, name=name)
        self.model = model

    def scaffold_form(self) -> Type:
        class MyForm(Form):
            pass

        return MyForm

    DEFAULT_FROM_TYPE = {'int': float("inf"),
                         'str': chr(0x10FFFF),
                         'bool': False,
                         'datetime': datetime.time.max,
                         }

    def sort_model_list(self, model_list: List, field: str, reverse: bool = False) -> None:
        """
            In-place sorting of a list of models.
            Assume it's like PG, quoting doc:
                'By default, null values sort as if larger than any non-null value;
                that is, NULLS FIRST is the default for DESC order, and NULLS LAST'
        """
        tpe = self.model.openapi_types[field]
        deflt = self.DEFAULT_FROM_TYPE[tpe]
        model_list.sort(key=lambda mdl: getattr(mdl, field) if getattr(mdl, field) is not None else deflt,
                        reverse=reverse)

    def search_in_models(self, model_list: List, search_fields: Tuple[str, ...], search: str) -> List:
        """
            In-place filtering of a list of models.
        """
        ret = []
        for mdl in model_list:
            for field in search_fields:
                field_val = getattr(mdl, field)
                if field_val is None:
                    continue
                if search in field_val:
                    ret.append(mdl)
                    break
        return ret
