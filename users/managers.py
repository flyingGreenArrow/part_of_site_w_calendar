from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone, email, password, **extra_fields):
        if not phone:
            raise ValueError("Телефон должен быть указан")

        user = self.model(phone=phone, email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.is_active = True
        # basic user
        user.q_of_reminders = 40
        user.const_reminders = 40
        already_set_reminders = 0
        return user

    def create_superuser(self, phone, email, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must content is_admin=True.')

        user = self._create_user(phone, email, password=password, **extra_fields)
        user.is_admin=True
        user.is_active=True
        user.q_of_reminders = 1000
        user.const_reminders = 1000
        already_set_reminders = 0
        user.save(using=self._db)

        return user
