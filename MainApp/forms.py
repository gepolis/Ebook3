from django import forms
from .models import Events


class EventAddForm(forms.ModelForm):
    class Meta:
        model = Events
        # Описываем поля, которые будем заполнять в форме
        fields = ['name', 'description', 'start_date', 'end_date', 'classroom_number', 'organizer', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Название сниппета'}),
            'description': forms.Textarea(attrs={'placeholder': "Описание"}),
            'start_date': forms.DateTimeInput(format=['%d/%m/%y'], attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(format=['%d/%m/%y'], attrs={'type': 'datetime-local'}),
            'classroom_number': forms.NumberInput(),
            'organizer': forms.Select()
        }

    def save(self, commit=True):
        user = super(EventAddForm, self).save(commit=False)
        if commit:
            user.save()
        return user


