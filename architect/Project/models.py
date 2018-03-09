import hashlib
import base64

from django.db import models
from django.core.exceptions import ValidationError

from cinp.orm_django import DjangoCInP as CInP

from architect.TimeSeries.models import CostTS, AvailabilityTS, ReliabilityTS, RawTimeSeries
from architect.Contractor.models import Complex, BluePrint
from architect.fields import MapField, script_name_regex, plan_name_regex
from architect.tcalc.parser import lint

cinp = CInP( 'Project', '0.1', doc="""This is the loader for the Project as a whole
""" )
