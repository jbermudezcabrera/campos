from enums import ButtonType, Labelling, Validation
from validators import RegExp
from sources import get_fields_source
from fields import *
from forms import *

__author__ = 'Juan Manuel Bermúdez Cabrera'


def get_forms(obj, **source_kw):
    """Creates ready to use New and Edit forms using `obj` as fields source.

    Finds a :class:`~campos.sources.FieldSource` to extract fields from `obj`
    and pass `source_kw` to source's constructor.

    :param obj: the object used to obtain fields
    :param source_kw: keyword arguments to pass to source constructor,
                      see :class:`~campos.sources.FieldSource` for more details
    :return: a :class:`tuple` like :class:`~campos.forms.CreationForm` ,
             :class:`~campos.forms.EditionForm`
    :rtype: :class:`tuple`
    """
    new = CreationForm.from_source(obj, **source_kw)
    edit = EditionForm.from_source(obj, **source_kw)
    return new, edit
