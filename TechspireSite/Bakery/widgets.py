from django.forms import widgets


class LargeTextInput(widgets.TextInput):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.setdefault('attrs', {})
        attrs.setdefault('size', 80)
        super(LargeTextInput, self).__init__(*args, **kwargs)