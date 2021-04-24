from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.hashers import check_password
from django.shortcuts import render
#from django.contrib.auth.models import User
from .models import User, Videos

import datetime


class user_creation_form(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(user_creation_form, self).__init__(*args, **kwargs)
        for field in ['phone', 'password1', 'password2']:
            if field == 'phone':
                self.fields[field].label = 'Номер мобильного телефона'
            if field == 'password1':
                self.fields[field].help_text = 'Минимум 8 символов. Должен состоять из цифр и латинских букв.'
                self.fields[field].label = 'Пароль'
            if field == 'password2':
                self.fields[field].help_text = ''
                self.fields[field].label = 'Подтверждение пароля'


    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('phone', )

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        sym = 'abcdefghigklmnopqrstuvwxyz-=+/*!@#$%^&()_'
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Пользователь с таким номером телефона уже существует")
        if '+' in phone:
            raise forms.ValidationError("Ошибка! \n Вы ввели номер не в международном формате")
        if len(phone) != 12:
            if phone == '666' or phone  == '777' or phone == '12344':
                pass
            else:
                raise forms.ValidationError("Ошибка! \n Неверный формат номера")
        for i in sym:
            if i in phone:
                raise forms.ValidationError("Ошибка! \n Номер должен состоять только из цифр")
        return phone


class user_change_form(UserChangeForm):

    class Meta:
        model = User
        fields = ('phone', )


class LoginForm(forms.Form):
    username = forms.CharField(label='Телефон')
    username.help_text = '12 цифр'
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def clean(self):
        phone = self.cleaned_data['username']
        if len(phone) != 12:
            if phone == '666' or phone  == '777' or phone == '12344':
                pass
            else:
                raise forms.ValidationError("Ошибка! \n Неверный формат номера")
        password = self.cleaned_data['password']
        user = User.objects.get(phone=phone)
        passw = user.password
        valid = check_password(password, passw)
        print(valid)
        if valid == False:
            self.add_error('password', 'Неверный пароль')
        else:
            pass

        return self.cleaned_data


class TgWorkForm(forms.Form):
    username = forms.CharField(label='Your username', max_length=50, widget=forms.TextInput(), required=False)
    text_of = forms.CharField(label='Note text', max_length=1000, widget=forms.TextInput())
    date = forms.DateField(label='Date', initial=datetime.date.today)
    time = forms.TimeField(label='Time', initial=datetime.time)
    widgetV = forms.BooleanField(label='Viber', required=False)
    widgetW = forms.BooleanField(label='Whatsapp', required=False)
    widgetT = forms.BooleanField(label='Telegram', required=False)


    def clean(self):
        usr = self.cleaned_data.get('username')
        wV=self.cleaned_data.get('widgetV')
        wW=self.cleaned_data.get('widgetW')
        wT=self.cleaned_data.get('widgetT')
        a=self.cleaned_data.get('date')
        b=self.cleaned_data.get('time')
        print(wV)
        print(wW)
        print(wT)
        theuser = user_data(usr)

        if wV and theuser.viber_is_active == False:
            raise forms.ValidationError("Ошибка! Вы не активировали Viber.")

        if wW and theuser.whatsapp_is_active == False:
            raise forms.ValidationError("Ошибка! Вы не активировали Whatsapp.")

        if wT and theuser.telegram_is_active == False:
            raise forms.ValidationError("Ошибка! Вы не активировали Telegram.")

        if wV == False and wW == False and wT == False:
            #raise forms.ValidationError("errrrr")
            self.add_error('widgetT', 'Вы не выбрали мессенджер')
        print('valid')


def user_data(phone):
    userset = User.objects.all()
    current_user = None
    for user in userset:
        if user.phone == phone:
            current_user = user
            return current_user
        else:
            pass


class MesActivationForm(forms.Form):
    v_phone = forms.CharField(label='VPhone', max_length=12, widget=forms.TextInput(), required=False)
    v_code = forms.CharField(label='VB Code', max_length=8, widget=forms.TextInput(), required=False)
    w_phone = forms.CharField(label='WPhone', max_length=12, widget=forms.TextInput(), required=False)
    w_code = forms.CharField(label='WA Code', max_length=8, widget=forms.TextInput(), required=False)
    t_phone = forms.CharField(label='TPhone', max_length=12, widget=forms.TextInput(), required=False)
    t_code = forms.CharField(label='TG Code', max_length=8, widget=forms.TextInput(), required=False)

# AdminPage Forms
class NewRemindersNumberForm(forms.Form):
    phone_number = forms.CharField(max_length=12, widget=forms.TextInput())
    new_value = forms.IntegerField()

class SetRemindersForm(forms.Form):
    set = forms.CharField(max_length=10, widget=forms.TextInput(), required=False)


class GiveRemindersForm(forms.Form):
    uphone = forms.CharField(max_length=12, widget=forms.TextInput())
    quan = forms.IntegerField()


class CheckActivateForm(forms.Form):
    uphone = forms.CharField(max_length=12, widget=forms.TextInput())


class BlockUsersForm(forms.Form):
    uphone = forms.CharField(max_length=12, widget=forms.TextInput())


class UsersStatisticForm(forms.Form):
    statistic_date = forms.DateField(label='Date', initial=datetime.date.today)

