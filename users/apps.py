from django.apps import AppConfig
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler


class UsersConfig(AppConfig):
    name = 'users'
