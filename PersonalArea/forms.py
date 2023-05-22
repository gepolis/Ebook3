from django import forms
from django.contrib.auth.forms import UserCreationForm

from Accounts.models import Account

from MainApp.models import Events, ClassRoom


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Account
        fields = (
        "username", "email", "second_name", "first_name", "middle_name", "password1", "password2", "date_of_birth", "role")
        labels = {
            "username": "Имя пользователя",
            "email": "Почта",
            "second_name": "Фамилия",
            "first_name": "Имя",
            "middle_name": "Отчество",
            "date_of_birth": "Дата рождения",
            "role": "Роль"

        }
        widgets = {
            'date_of_birth': forms.DateInput(attrs={"type": "date"})
        }

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class EventAddForm(forms.ModelForm):
    class Meta:
        model = Events
        # Описываем поля, которые будем заполнять в форме
        fields = ('name','description','start_date','end_date','organizer','classroom_number','building', 'image')

        widgets = {
            'name': forms.TextInput(),
            'description': forms.Textarea(),
            'start_date': forms.DateTimeInput(format=['%d/%m/%y'], attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(format=['%d/%m/%y'], attrs={'type': 'datetime-local'}),
            'organizer': forms.Select(),
            'classroom_number': forms.SelectMultiple(attrs={"style": "height: 350px"}),
            'building': forms.Select()
        }
        labels = {
            "name": "Название",
            "description": "Описание",
            "start_date": "Дата начала",
            "end_date": "Дата окончания",
            "organizer": "Организатор",
            "building": "Корпус",
            "classroom_number": "Доступно для",
            "image": "Изображение"

        }

    def save(self, commit=True):
        user = super(EventAddForm, self).save(commit=False)
        if commit:
            user.save()
        return user



class NewClassRoom(forms.ModelForm):
    class Meta:
        model = ClassRoom
        # Описываем поля, которые будем заполнять в форме
        fields = ('classroom','parallel')

        widgets = {
            'classroom': forms.NumberInput(),
            'parallel': forms.TextInput(),
        }
        labels = {
            "classroom": "Класс",
            "parallel": "Паралель",
        }

    def save(self, commit=True):
        classroom = super(NewClassRoom, self).save(commit=False)
        if commit:
            classroom.save()
        return classroom
