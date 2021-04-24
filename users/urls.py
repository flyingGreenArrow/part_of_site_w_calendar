from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .views import upload_file, register, ProfileMainView, ProfileFeedbackView, ProfileFeedbackConnection, ProfileActivateView, TgMainPageView, UserDataSender, WaMainPageView, index, ViMainPageView, user_reminders_journal, user_reminders_journal_done, user_login, get_admin_feedbacks, ProfileInstructionsView, AdminPage, Month_updater, Give_reminders, Check_activate, Block_users, StatisticUsers, PHelp, StatisticInfo, New_reminders_number, Users_database, upload_videofile, CalendarTestPage, moove, mooveback, day_select, view_type, day_choose, day_back_step, day_forward_step, view_model_list, view_model_block, month_change, year_change, reminder_form
# ProfileRemindersView,

tgtoken = "1260509373:AAHm6JxMI06pck_efqGZNOkXEEGzZi57uUY"
watoken = "ox093hw8bwozdanl"

urlpatterns = [
    #path('signup/', SignUpView.as_view(), name='signup'),
    path('signup/', register, name='signup'),
    path('login/', user_login, name='login'),
  # Calendar
    path('calendar/', CalendarTestPage.as_view(), name='calendar'),
    # ajax
    path('moove/', moove, name='mv'),
    path('mooveback/', mooveback, name='mvback'),
    path('day_select/', day_select, name ='ds'),
    path('view_type/', view_type, name='vt'),
    path('day_choose/', day_choose, name='dc'),
    path('day_back_step/', day_back_step, name='dbs'),
    path('day_forward_step/', day_forward_step, name='dfs'),
    path('view_model_list/', view_model_list, name='vml'),
    path('view_model_block/', view_model_block, name='vmb'),
    path('year_change/', year_change, name='yc'),
    path('month_change/', month_change, name='mc'),
    path('reminder_form/', reminder_form, name='rform'),


# Кабинет администратора
    path('userpage/adminpage/', AdminPage.as_view(), name='adminpage'),
# admin_main_page.html

# Установить новое количество напоминаний пользователю (в месяц)
    path('userpage/adminpage/newremindersnumber/', New_reminders_number.as_view(), name='newremindersnumber'),
# newremindersnumber.html

# Обновить напоминания на месяц
    path('userpage/adminpage/setreminders/', Month_updater.as_view(), name='setreminders'),
# setreminders.html

# Дать пользователю N штук напоминаний
    path('userpage/adminpage/givereminders/', Give_reminders.as_view(), name='givereminders'),
# givereminders.html

# Проверить активации пользователя
    path('userpage/adminpage/usersdatabase/', Users_database.as_view(), name='usersdatabase'),
# usersdatabase.html

# Проверить активации пользователя
    path('userpage/adminpage/checkactivate/', Check_activate.as_view(), name='checkactivate'),
# checkactivate.html

# Заблокировать пользователя
    path('userpage/adminpage/blockusers/', Block_users.as_view(), name='blockusers'),
# blockusers.html

# Статистика напоминаний, плотность напоминаний в минуту/день/час/неделю
    path('userpage/adminpage/usersstatistic/', StatisticUsers.as_view(), name='statusers'),
# userstatistic.html

    path('userpage/adminpage/statinfo/', StatisticInfo.as_view(), name='statinfo'),
# statinfo.html

    path('userpage/adminpage/phelp/', PHelp.as_view(), name='phelp'),

	]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404='users.views.handler404'
handler403='users.views.handler403'
handler500='users.views.handler500'
