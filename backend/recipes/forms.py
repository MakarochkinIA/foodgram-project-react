from django import forms
from django.forms.models import BaseInlineFormSet


class RequireOneFormSet(BaseInlineFormSet):
    def clean(self):
        super(RequireOneFormSet, self).clean()
        for error in self.errors:
            if error:
                return
        completed = 0
        for cleaned_data in self.cleaned_data:
            if cleaned_data and not cleaned_data.get('DELETE', False):
                completed += 1

        if completed < 1:
            raise forms.ValidationError("Необходим хотя бы 1 элемент")
