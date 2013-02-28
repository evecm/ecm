from django.core.urlresolvers import reverse
from django.forms import ModelForm, TimeInput, TimeField, DateField
from ecm.apps.eve.models import CelestialObject
from ecm.views.widgets import DatePickerWidget, SplitDatePickerTimeWidget, ModelAutoCompleteField
from ecm.plugins.op.models import Timer

class TimerForm(ModelForm):
    date = DateField()
    time = TimeField()

    class Meta:
        model = Timer
        widgets = {
            'time':         TimeInput(format='%H:%M'),
            'date':         DatePickerWidget(),
            'location':     ModelAutoCompleteField(source = '/ajax/solarsystems/'),
            'moon':     ModelAutoCompleteField(source = '/ajax/moons/', attrs = {'limit' : '150'})
        }
        fields = ('date', 'time', 'structure', 'location', 'moon', 'notes', 'cycle', 'friendly')
