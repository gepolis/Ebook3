from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Account, Building


class NewTeacherForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Account
        fields = (
        "username", "email", "second_name", "first_name", "middle_name", "password1", "password2", "date_of_birth")
        widgets = {
            'date_of_birth': forms.DateInput(attrs={"type": "date"})
        }

    def save(self, commit=True):
        user = super(NewTeacherForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = "teacher"
        if commit:
            user.save()
        return user


class NewStudentForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Account
        fields = (
        "username", "email", "second_name", "first_name", "middle_name", "password1", "password2", "date_of_birth")
        widgets = {
            'date_of_birth': forms.DateInput(attrs={"type": "date"})
        }

    def save(self, commit=True):
        user = super(NewStudentForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = "student"
        if commit:
            user.save()
        return user


class NewBuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = ("name", "type")
        lables = {
            "name": "Название",
            "type": "Тип"
        }

    def save(self, commit=True):
        user = super(NewBuildingForm, self).save(commit=False)
        if commit:
            user.save()
        return user
