import string
from random import choice

el = string.ascii_letters + string.digits
rand_str = lambda n: ''.join(choice(el) for _ in range(n))



import datetime
import pytz

def get_datetime(timestamp):
    utctime = datetime.datetime.fromtimestamp(float(timestamp), tz=pytz.utc)
    return utctime.astimezone(pytz.timezone('Asia/Jakarta'))


def get_date_str(timestamp):
    return get_datetime(timestamp).strftime('%Y-%m-%d')

def get_date(timestamp):
    return datetime.datetime.strptime(get_date_str(timestamp), "%Y-%m-%d")

def get_hour(timestamp):
    return get_datetime(timestamp).strftime("%H")

def get_year(timestamp):
    return get_datetime(timestamp).strftime("%Y")

def current_datetime():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Jakarta'))


__all__ = ('SelectField', 'SelectWidget')

from wtforms.fields import SelectField as BaseSelectField, StringField
from wtforms.validators import ValidationError
from wtforms.widgets import HTMLString, html_params
from wtforms.widgets import Select as BaseSelectWidget
from markupsafe import escape

class SelectWidget(BaseSelectWidget):
    """
    Add support of choices with ``optgroup`` to the ``Select`` widget.
    """
    @classmethod
    def render_option(cls, value, label, mixed):
        """
        Render option as HTML tag, but not forget to wrap options into
        ``optgroup`` tag if ``label`` var is ``list`` or ``tuple``.
        """
        if isinstance(label, (list, tuple)):
            children = []

            for item_value, item_label in label:
                item_html = cls.render_option(item_value, item_label, mixed)
                children.append(item_html)

            html = u'<optgroup label="%s">%s</optgroup>'
            data = (escape(str(value)), u'\n'.join(children))
        else:
            coerce_func, data = mixed
            selected = coerce_func(value) == data

            options = {'value': value}

            if selected:
                options['selected'] = u'selected'

            html = u'<option %s>%s</option>'
            data = (html_params(**options), escape(str(label)))

        return HTMLString(html % data)


class SelectField(BaseSelectField):
    """
    Add support of ``optgorup``'s' to default WTForms' ``SelectField`` class.
    So, next choices would be supported as well::
        (
            ('Fruits', (
                ('apple', 'Apple'),
                ('peach', 'Peach'),
                ('pear', 'Pear')
            )),
            ('Vegetables', (
                ('cucumber', 'Cucumber'),
                ('potato', 'Potato'),
                ('tomato', 'Tomato'),
            ))
        )
    """
    widget = SelectWidget()

    def iter_choices(self):
        """
        We should update how choices are iter to make sure that value from
        internal list or tuple should be selected.
        """
        for value, label in self.choices:
            yield (value, label, (self.coerce, self.data))

    def pre_validate(self, form, choices=None):
        """
        Don't forget to validate also values from embedded lists.
        """
        default_choices = choices is None
        choices = choices or self.choices

        for value, label in choices:
            found = False

            if isinstance(label, (list, tuple)):
                found = self.pre_validate(form, label)

            if found or value == self.data:
                return True

        if not default_choices:
            return False

        raise ValidationError(self.gettext(u'Not a valid choice'))


class ButtonWidget(object):
    input_type = 'submit'

    html_params = staticmethod(html_params)

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()

        return HTMLString('<button {params}>{label}</button>'.format(
            params=self.html_params(name=field.name, **kwargs),
            label=field.label.text)
        )


class ButtonField(StringField):
    widget = ButtonWidget()