from __future__ import unicode_literals
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from .managers import UserManager
import datetime

from django_mysql.models import JSONField


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(_('Phone'), max_length=12, unique=True, help_text=_(str("Номер вводите в международном формате, без знака &#034+&#034")))
    email = models.EmailField(_('email'), max_length=255,)
    is_active = models.BooleanField(_('is_active'), default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    timezon = models.CharField(_('timezone'), max_length=6, unique=False, default="GMT+2", null=True, blank=True)
    viber_is_active = models.BooleanField(_('viber is active'), unique=False, default=False, null=True, blank=True)
    vbid = models.CharField(_('viber chat id'), max_length=30, unique=False, null=True, blank=True)
    telegram_is_active = models.BooleanField(_('telegram is active'), unique=False, default=False, null=True, blank=True)
    tgid = models.CharField(_('telegram chat id'), max_length=20, unique=False, null=True, blank=True)
    whatsapp_is_active = models.BooleanField(_('whatsapp is active'), unique=False, default=False, null=True, blank=True)
    wtid = models.CharField(_('whatsapp chat id'), max_length=30, unique=False, null=True, blank=True)
    viber_activation_code = models.CharField(_('viber activation code'), max_length=10, unique=False, default=False, null=True, blank=True)
    whatsapp_activation_code = models.CharField(_('whatsapp activation code'), max_length=10, unique=False, default=False, null=True, blank=True)
    telegram_activation_code = models.CharField(_('telegram activation code'), max_length=10, unique=False, default=False, null=True, blank=True)
    # vsego 40
    q_of_reminders = models.IntegerField(_('num of reminders for user'), unique=False, default=40, null=True, blank=True)
    # 40 or set custom
    const_reminders = models.IntegerField(_('left'), unique=False, default=40, null=True, blank=True)
    already_set_reminders = models.IntegerField(_('Num of all messages'), unique=False, default=0, null=True, blank=True)
    viber_check = models.BooleanField(_('send_to_viber'), unique=False, default=False, null=True, blank=True)
    whatsapp_check = models.BooleanField(_('send_to_whatsapp'), unique=False, default=False, null=True, blank=True)
    telegram_check = models.BooleanField(_('send_to_telegram'), unique=False, default=False, null=True, blank=True)
    pwd_id_status = models.IntegerField(_('changeidstats'), unique=False, default=0, null=True, blank=True)
    date_of_registration = models.DateField(_('date_of_registration'), unique=False, default=datetime.date.today(), null=True, blank=True)
    # Tg admin commands fields
    givelocaln_state = models.IntegerField(_('givelocaln'), unique=False, default=0, null=True, blank=True)
    setglobaln_state = models.IntegerField(_('givelocaln'), unique=False, default=0, null=True, blank=True)
    check_activate = models.IntegerField(_('givelocaln'), unique=False, default=0, null=True, blank=True)
    block_user = models.IntegerField(_('givelocaln'), unique=False, default=0, null=True, blank=True)
#    ctr = models.BooleanField(_('bool'), unique=False,default=True,null=True,blank=True)

    objects = UserManager()
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email',]

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_phone(self):
        return self.phone


class Reminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, )
    text = models.CharField(max_length=1000)
    messenger = models.CharField(max_length=10)
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    send_in = models.BooleanField(default=True)
    send_done = models.BooleanField(default=False)
# необязательная переменная класа, которая записывает, были ли дата и время напоминания переопределены,
# если часовой пояс пользователя отличается от gtm+3
    # correct_datetime = models.BooleanField(default=True, blank=True, null=True)
    gmttime = models.TimeField(blank=True, null=True)
    gmtdate = models.DateField(blank=True, null=True)

    def get_reminders_by_user(self, userid):
        obj = Reminder.objects.filter(user=userid).order_by('date')
        return obj

    def get_reminders_by_messend(self, userid, messend):
        obj = Reminder.objects.filter(user = userid).filter(messend).order_by('date')
        return obj

    def _reminder_was_sent(self):
        self.send_done == True
        self.send_in == False
        return print("ok")

    def _get_in_status_reminders(self):
        obj = Reminder.objects.filter(send_in = True)
        return obj

    def _get_done_status_reminders(self):
        obj = Reminder.objects.filter(send_done = True).order_by('date')
        return obj


"""
Сообщение в мессенджере - создание эксземпляра класса new inst = Verification.activate_code(8p)
В шаблоне настроек профиля - поле для ввода кода для каждого мессенджера (ниже бутстрап)
сабмит + вызов Verification.controller(code)
"""

class VerificationUser(models.Model):
    #user = models.ForeignKey(User, on_delete=models.CASCADE, )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, )
    code = models.CharField(max_length=8)
    messenger = models.CharField(max_length=20)
    chat_id = models.CharField(max_length=30, null=True)

    def activateuser(self, messenger):
        if self.messenger.lower() == 'viber':
            self.user.viber_is_active = True
            self.user.vbid = self.chat_id
            self.user.save()
        if self.messenger.lower() == 'telegram':
            self.user.telegram_is_active = True
            self.user.tgid = self.chat_id
            self.user.save()
        if self.messenger.lower() == 'whatsapp':
            self.user.whatsapp_is_active = True
            self.user.wtid = self.chat_id
            self.user.save()
        return print('activate')


    def controller(self, User, code):
        # obj = Verification.objects.all().filter(set=False)  # cписок объектов класса
        #for e in objs:

        if self.set is True:
            pass

        if self.active_code == code:
            self.set=True
            self.activateuser(self, User)
            print("User have been passed!")
        return print('ok')


"""
class VerificationSavedData(models.Model):
    chatid = models.CharField()
    messenger= models.CharField()
"""

class PwdChange(models.Model):
    chatid = models.CharField(max_length=40, null=True, blank=True)
    status = models.IntegerField(default=0, null=True, blank=True)

