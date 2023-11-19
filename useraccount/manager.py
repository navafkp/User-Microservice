from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    # define a manager for user model
    def create_user(self, email, password = None, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email=self.normalize_email(email)
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user