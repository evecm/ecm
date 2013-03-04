from django.forms import ModelForm, TextInput
from ecm.views.widgets import SplitDatePickerTimeWidget, ModelAutoCompleteField
from ecm.plugins.op.models import Timer

class TimerForm(ModelForm):
    class Meta:
        model = Timer
        widgets = {
            'owner':        TextInput(),
            'timer':        SplitDatePickerTimeWidget(),
            'location':     ModelAutoCompleteField(source = '/ajax/celestials/'),
        }
        fields = ('timer', 'structure', 'location', 'owner', 'notes', 'cycle', 'friendly')
