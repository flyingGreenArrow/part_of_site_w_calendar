# if year-1 thats the out of current range - do stop
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, FormView
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth import logout, authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied, RequestAborted

from .forms import user_creation_form, TgWorkForm, WaWorkForm, ViWorkForm, MesActivationForm, LoginForm, FeedbackForm, FeedbackAnswerForm, UploadFileForm, SetNewTimezoneForm, SetRemindersForm, GiveRemindersForm, CheckActivateForm, BlockUsersForm, UsersStatisticForm, NewRemindersNumberForm, VideoForm
from .models import User, Verification, Reminder, VerificationUser, Feedback, PwdChange, Videos, SaveSvgFile

import telebot
import json
import requests
import os
import random
import datetime
import time
import threading

month_list = ['Январь ', 'Февраль ', 'Март ', 'Апрель ', 'Май ', 'Июнь ', 'Июль ', 'Август ', 'Сентябрь ', 'Октябрь ', 'Ноябрь ', 'Декабрь ']
month_list2 = ['Января ', 'Февраля ', 'Марта ', 'Апреля ', 'Мая ', 'Июня ', 'Июля ', 'Августа ', 'Сентября ', 'Октября ', 'Ноября ', 'Декабря ']
year_list = [i for i in range(2020,2091)]

def register(request):
    form = user_creation_form(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            u_name = form.cleaned_data['phone']
            u_pass = form.cleaned_data['password2']
            form.save()
            user = authenticate(username=u_name, password=u_pass)
            login(request, user)
            theUsers=User.objects.all()
            try:
                theUser=[user for user in theUsers if user.phone==u_name]
                theUser=theUser[0]
            except:
                print('exception')
                raise PermissionDenied
            code1 = generate_code()
            code2 = generate_code()
            code3 = generate_code()
            theUser.viber_activation_code = code1
            theUser.whatsapp_activation_code = code2
            theUser.telegram_activation_code = code3
            theUser.save()
            return HttpResponseRedirect('https://napomnim.com/')
    else:
        form = user_creation_form()
    return render(request, 'signup.html', {'form': form})


def user_reminders_journal(request):
# REPEAT 2 TIMES
    theUsers = User.objects.all()
    theUser = None
    try:
        for us in theUsers:
            if us.phone == request.user.phone:
                theUser = us
                print('match')
                break
            else:
                 print('not match')
    except:
        raise PermissionDenied
    in_set=Reminder.objects.filter(user=theUser).filter(send_in=True).order_by('date')
    p=Paginator(in_set[::-1], 11)
    page_number = request.GET.get('page')
    reminder_list = p.get_page(page_number)
    template = 'profile_reminder_in_view.html'
    return render(request, template, {'reminder_list': reminder_list})


def user_reminders_journal_done(request):
    theUsers = User.objects.all()
    theUser = None
    try:
        for us in theUsers:
            if us.phone == request.user.phone:
                theUser = us
                break
            else:
                 print('not match')
    except:
        raise PermissonDenied
    done_set=Reminder.objects.filter(user=theUser).filter(send_done=True).order_by('date')
    p=Paginator(done_set[::-1], 8)
    page_number=request.GET.get('page')
    page_obj=p.get_page(page_number)
    template = 'profile_reminder_done_view.html'
    return render(request, template, {'reminders_list2': done_set, 'page_obj': page_obj})


class MainPageView(TemplateView):
    template_name = 'homepage.html'
    form_class = TgWorkForm
    def get(self, request, *args, **kwargs):
#        left_messages_for_month = theUser.q_of_reminders
        form = self.form_class()
        Q_of_users = len(User.objects.all())
        Q_of_reminders = len(Reminder.objects.all())
        Q_of_processing = len(Reminder.objects.filter(send_in=True))
        if request.user.is_active:
            theUsers = User.objects.all()
            theUser = None
            for us in theUsers:
                if us.phone == request.user.phone:
                    theUser = us
            tz = theUser.timezon
            listmonth = ['Jan', 'Feb', 'Mar', 'Apr', 'May',  'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            sign=tz[3]
            zone=tz[4:]
            zone=sign+zone
            ctime = time.ctime()
            chour = ctime[11:13]
            cminute = ctime[14:16]
            csecond = ctime[17:19]
            cyear = ctime[20:]
            mont = ctime[4:7]
            cmonth = listmonth.index(mont)+1
            cdate = ctime[8:10]
            return render(request, self.template_name, {'tg_r_form': form, 'sign': sign, 'zone': zone})
        else:
            return render(request, self.template_name, {'tg_r_form': form, 'Q_of_users': Q_of_users, 'Q_of_reminders': Q_of_reminders, 'Q_of_processing': Q_of_processing})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if request.user.is_active:
            theUsers = User.objects.all()
            theUser = None
            for us in theUsers:
                if us.phone == request.user.phone:
                   theUser = us
            Q_of_users = len(User.objects.all())
            Q_of_reminders = len(Reminder.objects.all())
            Q_of_processing = len(Reminder.objects.filter(send_in=True))
            if form.is_valid():
                for i in form.cleaned_data:
                    print('-_____-')
                    print(i)
            #user = form.cleaned_data['username']
                user = form.cleaned_data['username']
                text = form.cleaned_data['text_of']
                date = form.cleaned_data['date']  # datetime.date
                time = form.cleaned_data['time']  # datetime.time
                viber_check = form.cleaned_data['widgetV']
                whatsapp_check = form.cleaned_data['widgetW']
                telegram_check = form.cleaned_data['widgetT']
                if telegram_check == True:
                    t, d = timezone_optimization(theUser.timezon, date, time)
                    r = Reminder.objects.create(user=theUser, text=text, messenger='telegram', date=d, time=t, send_in=True, send_done=False, gmttime=time, gmtdate=date)
                    control_date_check(r)
                    print(r)
                    print(type(r))
                    print(r.user)
                    print(r.user.tgid)
                if viber_check == True:
                    gz, gx = timezone_optimization(theUser.timezon, date, time)
                    r = Reminder.objects.create(user=theUser, text=text, messenger='viber', date=gx, time=gz, send_in=True, send_done=False, gmttime=time, gmtdate=date)
                    control_date_check(r)
                    print('viber reminder was set')
                if whatsapp_check == True:
                    t, d = timezone_optimization(theUser.timezon, date, time)
                    r = Reminder.objects.create(user=theUser, text=text, messenger='whatsapp', date=d, time=t, send_in=True, send_done=False, gmttime=time, gmtdate=date)
                    control_date_check(r)
                    print('whatsapp reminder was set')
                theUser.q_of_reminders = theUser.q_of_reminders - 1
                theUser.already_set_reminders = theUser.already_set_reminders + 1
                theUser.save()
                return HttpResponseRedirect("/")
            tz = theUser.timezon
            sign=tz[3]
            zone=tz[4:]
            return render(request, self.template_name, {'tg_r_form': form, 'sign': sign, 'zone': zone})
        else:
            return render(request, self.template_name, {'tg_r_form': form,  'Q_of_users': Q_of_users, 'Q_of_reminders': Q_of_reminders, 'Q_of_processing': Q_of_processing})



# ==============================================================================================
# =================================SECOND LINE TEMPLATES========================================
# ==============================================================================================

def get_user_reminders(phone):
    theUsers = User.objects.all()
    theUser = None
    for us in theUsers:
        if us.phone == phone:
            theUser = us
            break
        #in_set=Reminder.objects.filter(user=theUser).filter(send_in=True).order_by('date')
    reminders_set = Reminder.objects.filter(user=theUser).all()
    print('reminders_set: ', reminders_set)
    print(type(reminders_set))
    array_r = []
    for i in reminders_set:
        print('a',i.id)
        array_r.append([i.text, str(i.date), str(i.gmttime), i.messenger, i.id])  # 2020-09-18
        print('-------------------------')
    print(array_r)

    return array_r


def get_user_reminders_by_date(phone, date):
    theUsers = User.objects.all()
    theUser = None
    for us in theUsers:
        if us.phone == phone:
            theUser = us
            break
        #in_set=Reminder.objects.filter(user=theUser).filter(send_in=True).filter(date=date).order_by('date')
    reminders_set = Reminder.objects.filter(user=theUser).filter(date=date).all()
    array_r = []
    for i in reminders_set:
        array_r.append([i.text, str(i.date), str(i.gmttime), i.messenger])  # 2020-09-18
    print(array_r)

    return array_r


def get_user_reminders_by_week(phone, days):
    theUsers = User.objects.all()
    theUser = None
    for us in theUsers:
        if us.phone == phone:
            theUser = us
            break
    for i in days:
        # iter by dates
        # if match date append to main pull
        # else pass
        print()

        
#================================================================================================

class CalendarTestPage(TemplateView):
    template_name = 'calendar_page.html'
    r_form = TgWorkForm
    reg_form = user_creation_form

    def get(self, request):
        x = datetime.date.today()
        y = str(datetime.date.today())
        cmonth = month_list[int(x.month)-1]
        cyear = x.year
        array_r = get_user_reminders(request.user.phone)
        mlist = month_list
        ylist = year_list
        dates_list, past_month_list, next_month_dates, full_month_dates = calculate_dates(datetime.date.today(), array_r)
        print('today:', y)
        print(type(x.day))
        print(type(dates_list[6][0]))
        register_form = user_creation_form(prefix='registrationf')
        reminder_form = TgWorkForm(prefix='reminderf')
        if request.user.is_active:
            theUsers = User.objects.all()
            theUser = None
            for us in theUsers:
                if us.phone == request.user.phone:
                   theUser = us
        tgcode = theUser.get_telegram_activation_code()
        vibercode = theUser.get_viber_activation_code()
        wscode = theUser.get_whatsapp_activation_code()
        current_day_reminders = []
        hours_vals = [str(i) for i in range(24)]
        for i in range(len(array_r)):
            if array_r[i][1] == y:
                current_day_reminders.append([array_r[i][0], array_r[i][1], array_r[i][2], array_r[i][3], array_r[i][4], array_r[i][2][:2]])
        fm, tv, dv = get_day_of_week(x.month, x.year, x.day)
        return render(request, self.template_name, {'tgcode': tgcode, 'vibercode': vibercode, 'wscode': wscode, 'month_list': mlist, 'year_list': ylist, 'dates_list': dates_list, 'past_month_list': past_month_list, "next_month_dates": next_month_dates, "full_month_dates": full_month_dates, 'today': y, 'today_day': x.day, 'today_today': x, "cmonth": cmonth, "cyear": cyear, "register_form": register_form, "reminder_form": reminder_form, "current_day_reminders": current_day_reminders, "tval": tv, "hours_vals": hours_vals})


    def post(self, request):
        print(request.POST)
        rform = self.r_form(request.POST)
        reg_form = self.reg_form(request.POST)
        if request.user.is_active:
            theUsers = User.objects.all()
            theUser = None
            for us in theUsers:
                if us.phone == request.user.phone:
                   theUser = us

        if 'reminderf' in request.POST:
            print('Reminder form was post')
            if rform.is_valid():
                for i in rform.cleaned_data:
                    print('________reminder_form data:')
                    print(i)
                user = rform.cleaned_data['username']
                text = rform.cleaned_data['text_of']
                date = rform.cleaned_data['date']  # datetime.date
                time = rform.cleaned_data['time']  # datetime.time
                viber_check = rform.cleaned_data['widgetV']
                whatsapp_check = rform.cleaned_data['widgetW']
                telegram_check = rform.cleaned_data['widgetT']
                if telegram_check == True:
                    t, d = timezone_optimization(theUser.timezon, date, time)
                    r = Reminder.objects.create(user=theUser, text=text, messenger='telegram', date=d, time=t, send_in=True, send_done=False, gmttime=time, gmtdate=date)
                    control_date_check(r)
                if viber_check == True:
                    gz, gx = timezone_optimization(theUser.timezon, date, time)
                    r = Reminder.objects.create(user=theUser, text=text, messenger='viber', date=gx, time=gz, send_in=True, send_done=False, gmttime=time, gmtdate=date)
                    control_date_check(r)
                if whatsapp_check == True:
                    t, d = timezone_optimization(theUser.timezon, date, time)
                    r = Reminder.objects.create(user=theUser, text=text, messenger='whatsapp', date=d, time=t, send_in=True, send_done=False, gmttime=time, gmtdate=date)
                    control_date_check(r)
                theUser.q_of_reminders = theUser.q_of_reminders - 1
                theUser.already_set_reminders = theUser.already_set_reminders + 1
                theUser.save()

        if 'registrationf' in request.POST:
            if reg_form.is_valid():
                phone = reg_form.cleaned_data["phone"]
                password1 = reg_form.cleaned_data["password1"]
                password2 = reg_form.cleaned_data["password2"]
                print(phone, password1, password2)
        x = datetime.date.today()
        y = str(datetime.date.today())
        cmonth = month_list[int(x.month)-1]
        cyear = x.year
        array_r = get_user_reminders(request.user.phone)
        mlist = month_list
        ylist = year_list
        dates_list, past_month_list, next_month_dates, full_month_dates = calculate_dates(datetime.date.today(), array_r)
        register_form = user_creation_form(prefix='registrationf')
        reminder_form = TgWorkForm(prefix='reminderf')
        if request.user.is_active:
            theUsers = User.objects.all()
            theUser = None
            for us in theUsers:
                if us.phone == request.user.phone:
                   theUser = us
        tgcode = theUser.get_telegram_activation_code()
        vibercode = theUser.get_viber_activation_code()
        wscode = theUser.get_whatsapp_activation_code()

        return render(request, self.template_name, {'tgcode': tgcode, 'vibercode': vibercode, 'wscode': wscode, 'month_list': mlist, 'year_list': ylist, 'dates_list': dates_list, 'past_month_list': past_month_list, "next_month_dates": next_month_dates, "full_month_dates": full_month_dates, 'today': y, 'today_day': x.day, 'today_today': x, "cmonth": cmonth, "cyear": cyear, "register_form": register_form, "reminder_form": reminder_form})


def get_day_of_week(cmonth, cyear, day):

    return first_monday, tval, day_value


def calculate_dates(date_param, array_r):

    return current_month_dates, past_month_dates, next_month_dates, full_month_dates



# AJAX

# only calendar view
from django.http import JsonResponse
from django.core import serializers

def day_choose(request):
    if request.method == 'GET':
        today = request.GET["dat"];
        date_arr = today.split('-')
        print('date_arr', date_arr)
        x = datetime.date(int(date_arr[0]), int(date_arr[1]), int(date_arr[2]))
        reminders = get_user_reminders_by_date(request.user.phone, x)
        print('choose a ' + str(x) + ' date')
        print('reminders for this day: ', reminders)
        #x=today
        #reminders=get_user_reminders_by_date(request.user.phone, x)
        first_monday, tval, day_value = get_day_of_week(x.month, x.year, x.day)
        tmonth = month_list2[int(x.month)-1]
        tyear = x.year
        tday = x.day

        return JsonResponse({"today": str(x), "tval": tval, "tmonth": tmonth, "tyear": tyear, "tday": tday, "reminders": reminders}, status=200)
    else:
        return HttpResponse('Unsuccessful. Call from: view_type')



def get_week_values(reminders, day_value, cdate):
        init_day = int(cdate.day)
        init_month = int(cdate.month)
        init_year = int(cdate.year)
        if day_value != '0':
            d_param = datetime.date(init_year,init_month,init_day)
            init_date, day_value = c(d_param, day_value)
            init_day = int(init_date.day)
            init_month = int(init_date.month)
            init_year = int(init_date.year)
        days = []
        if int(day_value) == 0:
            for i in range(7):
                days.append([init_day, init_month, init_year])
                init_year, init_month, init_day = dates_values(init_year, init_month, init_day)
        else:
            print('Отсчет начинается не с понедельника')
        week_reminders = []
        for item in reminders:
            for day in days:
                if item[1][8:] == str(day[0]) and item[1][:4] == str(day[2]) and int(item[1][5:7]) == int(day[1]):  # day year month
                    text = str(item[0])
                    d = str(item[1][8:])
                    time = str(item[2][:2])
                    print(f"[{text},{d},{time}]")
                    week_reminders.append([text,d,time,day,days.index(day), str(item[2])])
        print('WEEK reminders: ', week_reminders)
        return days, week_reminders


# likebutton 4
def moove(request):
    if request.method == 'GET':
        print('r:',request)
        post_id = request.GET['post_id']
        cdate = request.GET['dat']
        date_arr = cdate.split('-')
        if int(date_arr[1]) == 12:
            new_date = datetime.date(int(date_arr[0])+1, 1, 1)
        else:
            new_date = datetime.date(int(date_arr[0]), int(date_arr[1])+1, 1)
        array_r = get_user_reminders(request.user.phone)
        current_month_dates, past_month_dates, next_month_dates, full_month_dates = calculate_dates(new_date, array_r)
        cmonth = month_list[int(new_date.month)-1]
        cyear = new_date.year
        new_dates_array = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]
        mlist = month_list
        ylist = year_list
        return JsonResponse({"month_list": mlist, "year_list": ylist, "past_month_dates": past_month_dates, "current_month_dates": current_month_dates, "next_month_dates": next_month_dates, "full_month_dates": full_month_dates, "today": str(new_date), "cmonth": cmonth, "cyear": cyear}, status=200)
    else:
        print('called but unsuccessfullllll')
        return HttpResponse('unsuccessful')


# likebutton 1
def mooveback(request):
    if request.method == 'GET':
        post_id = request.GET['post_id']
        cdate = request.GET['dat']
        date_arr = cdate.split('-')
        if int(date_arr[1]) == 1:
            new_date = datetime.date(int(date_arr[0])-1, 12, 1)
        else:
            new_date = datetime.date(int(date_arr[0]), int(date_arr[1])-1, 1)
        array_r = get_user_reminders(request.user.phone)
        current_month_dates, past_month_dates, next_month_dates, full_month_dates = calculate_dates(new_date, array_r)
        cmonth = month_list[int(new_date.month)-1]
        cyear = new_date.year
        mlist = month_list
        ylist = year_list
        return JsonResponse({ "month_list": mlist, "year_list": ylist, "past_month_dates": past_month_dates, "current_month_dates": current_month_dates, "next_month_dates": next_month_dates, "full_month_dates": full_month_dates, "today": str(new_date), "cmonth": cmonth, "cyear": cyear}, status=200)
    else:
        print('called but unsuccessfullllll')
        return HttpResponse('unsuccessful')


# select 2
def year_change(request):
    if request.method == 'GET':
        year = request.GET["year"]
        month = request.GET["month"]
        if month in month_list:
            month=month_list.index(month)
            newdate = datetime.date(int(year), int(month)+1, 1)
            array_r=[]
            current_month_dates, past_month_dates, next_month_dates, full_month_dates = calculate_dates(newdate, array_r)
        else:
            print('month not in month_list. what??')
        return JsonResponse({"year": year, "month": month, "full_month_dates": full_month_dates}, status=200)
    else:
        print('called but unsuccessfullllll')
        return HttpResponse('unsuccessful. called from year_change')


# select 1
def month_change(request):
    if request.method == 'GET':
        month = request.GET["month"]
        year = request.GET["year"]
        if month+' ' in month_list:
            month = month_list.index(month+' ')
            newdate = datetime.date(int(year), int(month)+1, 1)
            array_r=[]
            current_month_dates, past_month_dates, next_month_dates, full_month_dates = calculate_dates(newdate, array_r)
        else:
            print('month not in month_list. what??')
        return JsonResponse({"month": month, "year": year, "full_month_dates": full_month_dates}, status=200)
    else:
        print('called but unsuccessfullllll')
        return HttpResponse('unsuccessful. called from month_change')



def timezone_optimization(tz, thedate, thetime):
    print('Timezone')
    print('TZ: ', tz)
    print('Date: ', thedate)
    print('Time: ', thetime)
    print('Type date, type time: ' + str(type(thedate)) +" "+ str(type(thetime)))
    print('clocks: ', time.asctime(time.localtime()))
    print('clocks: ', time.ctime(time.time()))
    list = [4,6,9,11]
    list2 = [2]
    cdate_year = thedate.year
    cdate_month = thedate.month
    cdate_day = thedate.day
    ctime_hour = thetime.hour
    ctime_minute = thetime.minute
    ctime_second = thetime.second
    sign=tz[3]
    zone=tz[4:]
    if sign == '+':
        print('+ sign')
        chour = int(ctime_hour)-int(zone)
        if chour < 0:
            chour = 24+chour
            if cdate_day == 1:
                cdate_month = cdate_month - 1
                if cdate_month in list:
                    cdate_day = 30
                elif cdate_month in list2:
                    cdate_day = 28
                else:
                    cdate_day = 31
                    if cdate_month == 12:
                        cdate_year = cdate_year - 1
            else:
                cdate_day = cdate_day - 1
        if chour == 0:
            chour = 0
        cminute = int(ctime_minute)
        csecond = int(ctime_second)
        t = datetime.time(chour, cminute, csecond)
        print('Returned time: ', t)
        d = datetime.date(cdate_year, cdate_month, cdate_day)
        print('Returned date: ', d)
        return t, d
    if sign == '-':
        chour = int(ctime_hour)+int(zone)
        if chour > 23:
            if chour == 24:
                chour = 0
            chour = chour-24
            if cdate_month in list:
                if cdate_day == 30:
                    cdate_month = cdate_month + 1
                    cdate_day = 1
            if cdate_month in list2:
                if cdate_day == 28:
                    cdate_month = cdate_month + 1
                    cdate_day = 1
            elif cdate_month == 12:
                if cdate_day == 31:
                    cdate_year = cdate_year + 1
                    cdate_month = 1
                    cdate_day = 1
            else:
                cdate_day = cdate_day + 1
        cminute = int(ctime_minute)
        csecond = int(ctime_second)
        t = datetime.time(chour, cminute, csecond)
        d = datetime.date(cdate_year, cdate_month, cdate_day)
        return t, d


def generate_code():
    characters = '0123456789abcdefghigklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    code = ''
    for i in range(8):
        x = random.randint(0, len(characters)-1)
        code += characters[x]
    return code




# Upload File
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        label = request.POST['title']
        file = request.FILES['file']
        print(file)
        print(type(file))
        print(label)
        if form.is_valid():
            if '.svg' in label:
                from django.core.files.storage import FileSystemStorage
                fs = FileSystemStorage()
                filename = fs.save(label, file)
                uploaded_url = fs.url(filename)
                print('uploaded to', uploaded_url)
            else:
                handle_uploaded_file(request.FILES['file'], label)
            return HttpResponseRedirect('https://napomnim.com/users/userpage/upload')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


def handle_uploaded_file(f, name):
   # with open(f"static/filestorage/'{name}'", 'wb+') as pic:
       # f.pic.write
    print('handler')
    import PIL
    from PIL import Image
    print('PIL')
    img=Image.open(f)
    img=img.save("/home/steven/n_site/napomnim_site/static/filestorage/%s" % str(name))
    print('saved.')


def upload_videofile(request):
    from django.core.files.storage import FileSystemStorage
    if request.method == 'POST':
        #form = VideoForm(request.POST, request.FILES)
        #title = request.POST['title']
        #print('Title: ', title)
        video = request.FILES['video']
        print('Video: ', video)
        fs=FileSystemStorage()
        filename=fs.save(video.name, video)
        uploaded_file_url = fs.url(filename)
        #content = Videos(title=title, video=video)
        #print('CONTENT: ', content)
        #content.save()
        return render(request, 'video_upload.html', {'uploaded_file_url': uploaded_file_url})
    #else:
    #    form = VideoForm()
    return render(request, 'video_upload.html')

# def display(request):
#    videos = Videos.objects.all()
#    context = { 'videos': videos, }
#    return render(request, 'videos.html, context)


def control_date_check(reminder):
    cdatetime = datetime.datetime.now()
  #   cdatetime = (cdatet.year, cdatet.month, cdatet.day, cdatet.hour, cdatet.minute, cdatet.second)
    rdatetime = datetime.datetime(reminder.date.year, reminder.date.month, reminder.date.day, reminder.time.hour, reminder.time.minute, reminder.time.second)
    z = rdatetime-cdatetime

    r_hour = reminder.time.hour
    r_sec = reminder.time.second
    r_min = reminder.time.minute

    r_year = rdatetime.year
    r_month = rdatetime.month
    r_day = rdatetime.day

    list1=[2]
    list2=[1, 3, 5, 7, 8, 10, 12]
    list3=[4, 6, 9, 11]

    if z.seconds < 300:
        zi = 300-z.seconds
        print('Z SECONDS: ', z.seconds)
        print('ZI: ', zi)
        if zi < 59:
            r_sec = 0
            r_sec = 59

        if zi > 59:
            if zi == 60:
                # 1 min
                r_min += 1
                r_sec = 0
                if r_min > 59:
                    r_min=r_min-60
                    r_hour += 1
                    if r_hour > 23:
                        r_hour = r_hour-24
                        r_day += 1
                        if r_month in list1 and r_day == 28 or r_day == 29:
                            r_month = 3
                            r_day = 1
                        if r_month in list2 and r_day == 31:
                            if r_month == 12:
                                r_year += 1
                                r_month = 1
                                r_day = 1
                            else:
                                r_month += 1
                                r_day = 1
                        if r_month in list3 and r_day == 30:
                            r_month += 1
                            r_day = 1

            if zi == 120:
                # 2 min
                r_min += 2
                r_sec = 0
                if r_min > 59:
                    r_min=r_min-60
                    r_hour += 1
                    if r_hour > 23:
                        r_hour = r_hour-24
                        r_day += 1
                        if r_month in list1 and r_day == 28 or r_day == 29:
                            r_month = 3
                            r_day = 1
                        if r_month in list2 and r_day == 31:
                            if r_month == 12:
                                r_year += 1
                                r_month = 1
                                r_day = 1
                            else:
                                r_month += 1
                                r_day = 1
                        if r_month in list3 and r_day == 30:
                            r_month += 1
                            r_day = 1

            if zi == 180:
                # 3 min
                r_min += 3
                r_sec = 0
                if r_min > 59:
                    r_min=r_min-60
                    r_hour += 1
                    if r_hour > 23:
                        r_hour = r_hour-24
                        r_day += 1
                        if r_month in list1 and r_day == 28 or r_day == 29:
                            r_month = 3
                            r_day = 1
                        if r_month in list2 and r_day == 31:
                            if r_month == 12:
                                r_year += 1
                                r_month = 1
                                r_day = 1
                            else:
                                r_month += 1
                                r_day = 1
                        if r_month in list3 and r_day == 30:
                            r_month += 1
                            r_day = 1

            if zi == 240:
                # 4 min
                r_min += 4
                r_sec = 0
                if r_min > 59:
                    r_min=r_min-60
                    r_hour += 1
                    if r_hour > 23:
                        r_hour = r_hour-24
                        r_day += 1
                        if r_month in list1 and r_day == 28 or r_day == 29:
                            r_month = 3
                            r_day = 1
                        if r_month in list2 and r_day == 31:
                            if r_month == 12:
                                r_year += 1
                                r_month = 1
                                r_day = 1
                            else:
                                r_month += 1
                                r_day = 1
                        if r_month in list3 and r_day == 30:
                            r_month += 1
                            r_day = 1

            else:

                min = divmod(zi, 60)
                min = min[0]
                sec = zi - (min * 60)
                conts = 0
                r_min += min

                if r_min > 59:
                    r_min = r_min-60
                    r_hour += 1
                    if r_hour > 23:
                        r_hour = r_hour-24
                        r_day+=1
                        if r_month in list1 and r_day == 28:
                            r_month = 3
                            r_day=1

                        if r_month in list2 and r_day == 31:
                            if r_month == 12:
                                r_year += 1
                                r_month = 1
                                r_day = 1
                            else:
                                r_month += 1
                                r_day = 1
                        if r_month in list3 and r_day == 30:
                            r_month += 1
                            r_day = 1

                r_sec += sec
                if r_sec > 59:
                    const += 1
                    r_sec = sec-60
                    r_min=min+const
                    if r_min > 59:
                        r_min = r_min-60
                        r_hour += 1
                        if r_hour > 23:
                            r_hour = r_hour-24
                            r_day+=1
                            if r_month in list1 and r_day == 28:
                                r_month = 3
                                r_day = 1
                            if r_month in list2 and r_day == 31:
                                if r_month == 12:
                                    r_year += 1
                                    r_month = 1
                                    r_day = 1
                                else:
                                    r_month += 1
                                    r_day = 1
                            if r_month in list3 and r_day == 30:
                                r_month += 1
                                r_day = 1
    sim=datetime.datetime(r_year, r_month, r_day, r_hour, r_min, r_sec)
    reminder.date=datetime.date(r_year, r_month, r_day)
    reminder.time=datetime.time(r_hour, r_min, r_sec)
    reminder.save()



# =====================ADMIN_FUNC_TOOLS=======================
# Увеличить константу напоминаний пользователю??

class AdminPage(TemplateView):
    template_name = 'admin_main_page.html'

#
#
#----------------Set_new-reminders-number--------------------
class New_reminders_number(TemplateView):
    template_name = 'newremindersnumber.html'
    form_class = NewRemindersNumberForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone_number"]
            value = form.cleaned_data["new_value"]
            print('Set new reminders form valid!')
            theUsers = User.objects.all()
            for user in theUsers:
                if user.phone == phone:
                    user.const_reminders = value
                    user.save()
                else:
                    pass
            return HttpResponseRedirect('https://napomnim.com/users/userpage/adminpage/')
        return render(request, self.template_name, {'form': form})

#
#
#----------------Update-month-reminder-number----------------
class Month_updater(TemplateView):
    template_name = 'setreminders.html'
    form_class = SetRemindersForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            print('Admin set reminder form valid!')
            theUsers = User.objects.all()
            for user in theUsers:
                user.q_of_reminders = user.const_reminders
                user.save()
            return HttpResponseRedirect('https://napomnim.com/users/userpage/adminpage/')
        return render(request, self.template_name, {'form': form})

#
#
#--------------Give-some-reminders-----------------------
class Give_reminders(TemplateView):
    template_name = 'givereminders.html'
    form_class = GiveRemindersForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            print('Admin give reminders form valid!')
            uphone = form.cleaned_data['uphone']
            quan = form.cleaned_data['quan']
            obj = User.objects.get(phone=uphone)
            obj.q_of_reminders += quan
            obj.save()
            return HttpResponseRedirect('https://napomnim.com/users/userpage/adminpage/')
        return render(request, self.template_name, {'form': form})

#
#
#--------------Users_database_set----------------------
class Users_database(TemplateView):
    template_name = 'usersdatabase.html'

    def get(self, request):
        print('Admin check user form valid!')
        dataset = []
        theUsers=User.objects.all()
        for user in theUsers:
            dataset.append(user)

        return render(request, self.template_name, {'dataset': dataset})

#
#
#------------Check-activate----------------------------
class Check_activate(TemplateView):
    template_name = 'checkactivate.html'
    form_class = CheckActivateForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            print('Admin check user form valid!')
            uphone = form.cleaned_data['uphone']
            #theUser = User.objects.get(phone=uphone)
            theUsers=User.objects.all()
            theUser=[user for user in theUsers if user.phone==uphone]
            theUser=theUser[0]

            print('object: theUser ', theUser)
            print('theUser phone: ', theUser.phone)

            q = theUser.q_of_reminders
            c = theUser.const_reminders
            a = theUser.already_set_reminders

            users_tg = theUser.telegram_is_active
            users_vb = theUser.viber_is_active
            users_wt = theUser.whatsapp_is_active

            timezon = theUser.timezon

            viber_quantity = len(Reminder.objects.filter(user=theUser).filter(messenger='Viber'))
            whatsapp_quantity = len(Reminder.objects.filter(user=theUser).filter(messenger='Whatsapp'))
            telegram_quantity = len(Reminder.objects.filter(user=theUser).filter(messenger='Telegram'))

            si_reminders = len(Reminder.objects.filter(user=theUser).filter(send_in=True))
            return render(request, self.template_name, {'form': form, 'q':q, 'c':c, 'a':a, 'users_tg': users_tg, 'users_vb': users_vb, 'users_wt': users_wt, 'timezon': timezon, 'viber_quantity': viber_quantity, 'whatsapp_quantity': whatsapp_quantity, 'telegram_quantity': telegram_quantity, 'si_reminders': si_reminders})

        return render(request, self.template_name, {'form': form})

#
#
#----------Block-user--------------------------------
class Block_users(TemplateView):
    template_name = 'blockusers.html'
    form_class = BlockUsersForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            print('Admin block user form valid!')
            uphone = form.cleaned_data['uphone']
            theUser = User.objects.get(phone=uphone)
            theUser.block_user = 1
            theUser.save()
        return render(request, self.template_name, {'form': form})

#
#
#--------Statistic--------------------------------
class StatisticUsers(TemplateView):
    template_name = 'usersstatistic.html'
    form_class = UsersStatisticForm

    def get(self, request):
        form = self.form_class()
        x = 0
        y = 0
        w = 0
        z = 0

        resultdate = None
        resultime = None

        list = Reminder.objects.filter(send_in=True).order_by('date')
        adate = list[0].date
        for obj in list:
            if obj.date == adate:
                y += 1
                if y > x:
                    x = y
                    resultdate = obj.date
            else:
                y = 0
                adate = obj.date
                y += 1

        list2 = Reminder.objects.filter(date=resultdate).order_by('time')
        atime = list2[0].time
        for obj in list2:
            if obj.time == atime:
                z += 1
                if z > w:
                    w = z
                    resulttime = obj.time
                else:
                    z = 0
                    atime = obj.time
                    z += 1

        viberr=0
        telegramr=0
        whatsappr=0
        for i in list2:
            if i.messenger == 'viber':
                viberr+=1
            if i.messenger == 'telegram':
                telegramr+=1
            if i.messenger == 'whatsapp':
                whatsappr+=1

        return render(request, self.template_name, {'form': form, 'resultdate': resultdate, 'x': x, 'resulttime': resulttime, 'w': w, 'vi':viberr, 'tg': telegramr, 'wt': whatsappr})


    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            print('Admin users statistic form valid!')
            point_date = form.cleaned_data['statistic_date']
            result = []
            dataset = Reminder.objects.filter(date=point_date).order_by('time')
            for obj in dataset:
                result.append(obj)
            x = 0
            y = 0
            w = 0
            z = 0

            param = ""
            resultdate = None
            resultime = None


            list = Reminder.objects.filter(send_in=True).order_by('date')
            adate = list[0].date
            for obj in list:
                if obj.date == adate:
                    y += 1
                    if y > x:
                        x = y
                        resultdate = obj.date
                else:
                    y = 0
                    adate = obj.date
                    y += 1

            list2 = Reminder.objects.filter(date=resultdate).order_by('time')
            atime = list2[0].time
            for obj in list2:
                if obj.time == atime:
                    z += 1
                    if z > w:
                        w = z
                        resulttime = obj.time
                else:
                    z = 0
                    atime = obj.time
                    z += 1

            viberr=0
            telegramr=0
            whatsappr=0
            for i in list2:
                if i.messenger == 'viber':
                    viberr+=1
                if i.messenger == 'telegram':
                    telegramr+=1
                if i.messenger == 'whatsapp':
                    whatsappr+=1

        return render(request, self.template_name, {'form': form, 'resultdate': resultdate, 'x': x, 'resulttime': resulttime, 'w': w, 'result': result, 'num': len(dataset), 'vi':viberr, 'tg': telegramr, 'wt': whatsappr})


class PHelp(TemplateView):
    template_name = 'admin_help_page.html'


class StatisticInfo(TemplateView):
    template_name = 'statinfo.html'


def handler404(request, *args, **argv):
    response = render_to_response('404.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request, *args, **argv):
    response = render_to_response('500.html', {}, context_instance=RequestContext(request))
    response.status_code = 500
    return response

def handler403(request, *args, **argv):
    response=render_to_response('403.html', {}, context_instance=RequestContext(request))
    response.status_code = 403
    return response


