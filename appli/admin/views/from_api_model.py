#
# Build a view from API model
#
import datetime
from typing import Any, Type, List, Tuple, Final, Dict

from flask_admin.model import BaseModelView
from flask_admin.model.helpers import prettify_name
from flask_security.forms import Form
from wtforms import StringField, BooleanField, DateField, IntegerField
from wtforms.validators import DataRequired


class APIModelView(BaseModelView):
    STR_TO_TYPE: Final = {'int': int,
                          'str': str,
                          'bool': bool,
                          'datetime': datetime.datetime,
                          'list[int]': List[int],
                          'list[ProjectSummaryModel]': List[Any]
                          }

    def __init__(self, model: Type, name: str):
        # Map openapi types to real ones
        self.types = {}
        for an_attrib, its_type in model.openapi_types.items():
            self.types[an_attrib] = self.STR_TO_TYPE[its_type]
        # Call super() _after_ at it calls, in turn, some methods here
        super().__init__(model=model, name=name, endpoint=name)

    def ui_class_from_type(self, attr_type: str) -> Type:
        """
            We have very little information on the model in openapi specs.
        """
        if attr_type == int:
            ret = IntegerField
        elif attr_type == str:
            ret = StringField
        elif attr_type == bool:
            ret = BooleanField
        elif attr_type == datetime.datetime:
            ret = DateField
        else:
            raise Exception("Not known:" + str(attr_type))
        return ret

    def scaffold_form(self) -> Type:

        field_dict: Dict[str, Type] = dict()
        for an_attrib, its_type in self.types.items():
            if an_attrib in self.form_excluded_columns:  # Comply with interface
                continue
            ui_elem_clazz = self.form_overrides.get(an_attrib)  # Comply with interface
            if ui_elem_clazz is None:
                ui_elem_clazz = self.ui_class_from_type(its_type)  # type:ignore
            if ui_elem_clazz:
                label = prettify_name(an_attrib)
                validators = [DataRequired()] if an_attrib in self.mandatory_columns else []
                ui_elem = ui_elem_clazz(label=label, validators=validators)
                field_dict[an_attrib] = ui_elem

        return type(self.name + 'Form', (self.form_base_class,), field_dict)

    def scaffold_list_columns(self):
        # Show all columns in list view, by default
        return list(self.types.keys())

    def scaffold_sortable_columns(self):
        # Sort on all columns with basic type, by default
        ret = []
        for attr, tpe in self.types.items():
            if tpe in (str, int, datetime.datetime, bool):
                ret.append(attr)
        return ret

    DEFAULT_FROM_TYPE = {int: float("inf"),
                         str: chr(0x10FFFF),
                         bool: False,
                         datetime.datetime: datetime.datetime.max,
                         }

    def sort_model_list(self, model_list: List, field: str, reverse: bool = False) -> None:
        """
            In-place sorting of a list of models.
            Assume it's like PG, quoting doc:
                'By default, null values sort as if larger than any non-null value;
                that is, NULLS FIRST is the default for DESC order, and NULLS LAST'
        """
        tpe = self.types[field]
        deflt = self.DEFAULT_FROM_TYPE[tpe]
        model_list.sort(key=lambda mdl: getattr(mdl, field)  # type:ignore
        if getattr(mdl, field) is not None else deflt,  # type:ignore
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
