from django import forms
from django.contrib.auth.forms import UserCreationForm

from Accounts.models import Account

from MainApp.models import Events, ClassRoom, EventCategory, PsychologistSchedule


class EditUserForm(forms.ModelForm):
    email = forms.EmailField(required=True, disabled=True)

    class Meta:
        model = Account
        fields = (
            "username", "email", "second_name", "first_name", "middle_name", "date_of_birth", "building", "role",
            "points",'avatar', "peculiarity")
        labels = {
            "username": "Имя пользователя",
            "email": "Почта",
            "second_name": "Фамилия",
            "first_name": "Имя",
            "middle_name": "Отчество",
            "date_of_birth": "Дата рождения",
            "role": "Роль",
            "building": "Корпус",
            "points": "Баллов",
            "avatar": "Изображение",
            "peculiarity": "Особенность"
        }
        widgets = {
            'date_of_birth': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control',
                       'placeholder': 'Select a date',
                       'type': 'date'
                       }),
            'avatar': forms.FileInput(
                attrs={"class":"form-control"}
            )
        }

    def save(self, commit=True):
        user = super(EditUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class EditUserFormHeadTeacher(forms.ModelForm):
    class Meta:
        model = Account
        fields = ("peculiarity",)
        labels = {
            "peculiarity": "Особенность"
        }
        widgets = {
            'avatar': forms.FileInput(
                attrs={"class":"form-control"}
            )
        }

    def save(self, commit=True):
        user = super(EditUserFormHeadTeacher, self).save(commit=False)
        if commit:
            user.save()
        return user

class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Почта")

    class Meta:
        model = Account
        fields = (
            "username", "email", "second_name", "first_name", "middle_name", "password1", "password2", "date_of_birth",
            'building','role', "avatar")
        labels = {
            "username": "Имя пользователя",
            "email": "Почта",
            "second_name": "Фамилия",
            "first_name": "Имя",
            "middle_name": "Отчество",
            "date_of_birth": "Дата рождения",
            "building": "Корпус",
            'role': "Роль",
            'avatar': "Изображение"

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
        fields = (
        'name', 'description', 'start_date', 'end_date', 'organizer', 'type','category', 'subject', 'classroom_number', 'building',
        'image')

        widgets = {
            'name': forms.TextInput(),
            'description': forms.Textarea(),
            'start_date': forms.DateTimeInput(format=['%d/%m/%y'], attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(format=['%d/%m/%y'], attrs={'type': 'datetime-local'}),
            'organizer': forms.Select(),
            'type': forms.Select(attrs={"onchange": "change(this)"}),
            'category': forms.Select(),
            'classroom_number': forms.Select(),
            'building': forms.Select(),
            'image': forms.FileInput(attrs={"class": "form-control"})
        }
        labels = {
            "name": "Название",
            "description": "Описание",
            "start_date": "Дата начала",
            "end_date": "Дата окончания",
            "organizer": "Организатор",
            "building": "Корпус",
            "classroom_number": "Доступно для",
            "image": "Изображение",
            "category": "Методическое объединение",
            "subject": "Предмет",
            "type": "Тип"
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
        fields = ('classroom', 'parallel')

        widgets = {
            'classroom': forms.NumberInput(),
            'parallel': forms.TextInput(attrs={"style": "text-transform:uppercase"}),
        }
        labels = {
            "classroom": "Класс",
            "parallel": "Паралель",
        }

    def unique(self):
        classroom = super(NewClassRoom, self).save(commit=False)
        if ClassRoom.objects.all().filter(classroom=classroom.classroom,
                                          parallel__iexact=str(classroom.parallel).upper()).exists():
            return False
        else:
            return True

    def save(self, commit=True):
        classroom = super(NewClassRoom, self).save(commit=False)
        classroom.parallel = str(classroom.parallel).upper()
        if commit:
            classroom.save()
        return classroom


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = (
            "username", "second_name", "first_name", "middle_name", "date_of_birth", "avatar")
        labels = {
            "username": "Имя пользователя",
            "second_name": "Фамилия",
            "first_name": "Имя",
            "middle_name": "Отчество",
            "date_of_birth": "Дата рождения",
            "avatar": "Изображение",
        }
        widgets = {
            'date_of_birth': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control',
                       'placeholder': 'Select a date',
                       'type': 'date'
                       }),
            'avatar': forms.FileInput(attrs={"class": "form-control"})
        }

    def save(self, commit=True):
        user = super(EditProfileForm, self).save(commit=False)
        if commit:
            user.save()
        return user


class EventCategoryForm(forms.ModelForm):
    class Meta:
        model = EventCategory
        # Описываем поля, которые будем заполнять в форме
        fields = ('name', 'methodists')
        labels = {
            "name": "Название",
            "methodists": "Методисты"
        }

    def save(self, commit=True):
        user = super(EventCategoryForm, self).save(commit=False)
        if commit:
            user.save()
        return user


class EventAddFormMethodist(forms.ModelForm):
    class Meta:
        model = Events
        # Описываем поля, которые будем заполнять в форме
        fields = ('name', 'description', 'start_date', 'end_date', 'category', 'classroom_number', 'building', 'image',
                  "organizer")

        widgets = {
            'name': forms.TextInput(),
            'description': forms.Textarea(),
            'start_date': forms.DateTimeInput(format=['%d/%m/%y'], attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(format=['%d/%m/%y'], attrs={'type': 'datetime-local'}),
            'building': forms.Select(),
            'image': forms.FileInput(attrs={"class": "form-control"})
        }
        labels = {
            "name": "Название",
            "description": "Описание",
            "start_date": "Дата начала",
            "end_date": "Дата окончания",
            "organizer": "Организатор",
            "building": "Корпус",
            "classroom_number": "Доступно для",
            "image": "Изображение",
            "category": "Категория"

        }

    def __init__(self, loggedin_user=None, *args, **kwargs):
        super(EventAddFormMethodist, self).__init__(*args, **kwargs)
        if loggedin_user is not None:
            self.fields['category'].queryset = EventCategory.objects.all().filter(methodists=loggedin_user)


    def save(self, commit=True):
        user = super(EventAddFormMethodist, self).save(commit=False)
        if commit:
            user.save()
        return user


class UploadPhotoReport(forms.Form):
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': True, "class": "form-control", "accept": "image/*"}),
                           label="Изображения", )



class EventAddFormHeadTeacher(forms.ModelForm):
    class Meta:
        model = Events
        # Описываем поля, которые будем заполнять в форме
        fields = ('name', 'description', 'start_date', 'end_date', 'category', 'classroom_number', 'building', 'image',
                  "organizer")

        widgets = {
            'name': forms.TextInput(),
            'description': forms.Textarea(),
            'start_date': forms.DateTimeInput(format=['%d/%m/%y'], attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(format=['%d/%m/%y'], attrs={'type': 'datetime-local'}),
            'building': forms.Select(),
            'image': forms.FileInput(attrs={"class": "form-control"})
        }
        labels = {
            "name": "Название",
            "description": "Описание",
            "start_date": "Дата начала",
            "end_date": "Дата окончания",
            "organizer": "Организатор",
            "building": "Корпус",
            "classroom_number": "Доступно для",
            "image": "Изображение",
            "category": "Категория"

        }


    def __init__(self, loggedin_user=None, *args, **kwargs):
        super(EditUserFormHeadTeacher, self).__init__(*args, **kwargs)
        if loggedin_user is not None:
            self.fields['building'].queryset = Building.objects.all().filter(pk=loggedin_user.building.pk)


class LinkingMosruForm(forms.Form):
    login = forms.CharField(label="Логин mos.ru")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль mos.ru")
    class Meta:
        model = Events


class PsychologistScheduleAddForm(forms.Form):
    date = forms.DateField(label="Дата", widget=forms.DateInput(attrs={'type': 'date'}))
    start_time = forms.TimeField(label="Время начала", widget=forms.TimeInput(attrs={'type': 'time'}))
    end_time = forms.TimeField(label="Время окончания", widget=forms.TimeInput(attrs={'type': 'time'}))
    child = forms.ModelChoiceField(queryset=Account.objects.all().filter(role="student", peculiarity__isnull=False), label="Ученик")
