from django import forms
from django.forms.util import flatatt
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
#from django.utils.simplejson import JSONEncoder
from ecm.utils import _json as json
from django.utils.encoding import smart_unicode
from django.conf.urls.static import static

class DatePickerWidget(forms.DateInput):
    @property
    def media(self):
        js = ['ecm/js/lib/jquery.ui.js']
        css = { 'all': ('ecm/css/jquery-ui-1.8.13.custom.css') }
        return forms.Media(js=[static(path) for path in js])

class SplitDatePickerTimeWidget(forms.SplitDateTimeWidget):
    def __init__(self, attrs=None):
        widgets = [DatePickerWidget, forms.TimeInput]
        forms.MultiWidget.__init__(self, widgets, attrs)

    def format_output(self, rendered_widgets):
        str_form = """
            <div class="control-group">
                <label for="id_timer_0" class="control-label">%s:</label>
                <div class="controls controls-row">
                    %s
                </div>
            </div>
            <div class="control-group">
                <label for="id_timer_1" class="control-label">%s:</label>
                <div class="controls controls-row">
                    %s
                </div>
            </div>
        """
        return mark_safe( str_form % (_('Date'), rendered_widgets[0],_('Time'),rendered_widgets[1]))

class ModelAutoCompleteField(forms.TextInput):
    def __init__(self, source, options={}, attrs={}):
        self.options = None
        self.attrs = {'autocomplete': 'off'}
        self.source = source
        if len(options) > 0:
            self.options = json.dumps(options)
        self.attrs.update(attrs)

    def render_js(self, field_id, limit=10):
        if isinstance(self.source, list):
            source = json.dumps(self.source)
        elif isinstance(self.source, str):
            source = "'%s'" % escape(self.source)
        else:
            raise ValueError('source type is not valid')
        options = ''
        if self.options:
            options += ',%s' % self.options
        return u'function formatResult(row)\n\
                {return row[1];}\n\
        function formatItem(row) {\n\
            return row[1];\n\
        }\n\
        $(\'#%s\').autocomplete(%s%s, {max: %s, formatResult: formatResult, formatItem: formatItem});\n\
        $("#%s").result(function(event, data, formatted) {\n\
        $("#%s").val(data[1]);\n\
        });' % (field_id, source, options, limit, field_id, field_id)

    def render(self, name, value=None, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        if value:
            final_attrs['value'] = escape(smart_unicode(value))

        if not self.attrs.has_key('id'):
            final_attrs['id'] = 'id_%s' % name
        if not self.attrs.has_key('limit'):
            final_attrs['limit'] = '10'
        return mark_safe(u'''<input type="text" %(attrs)s/>
        <script type="text/javascript">$(function() {
        %(js)s});</script>
        ''' % {
            'attrs' : flatatt(final_attrs),
            'js' : self.render_js(final_attrs['id'], final_attrs['limit']),
        })
