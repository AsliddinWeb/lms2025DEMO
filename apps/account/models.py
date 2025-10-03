from django.db import models
from django.contrib.auth.models import AbstractUser

from django.db.models.signals import post_save
from django.dispatch import receiver

# Manager
from django.contrib.auth.base_user import BaseUserManager


# Custom Managers
class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        extra_fields.setdefault("is_active", True)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('role', User.Role.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, password, **extra_fields)


class StudentManager(UserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.STUDENT)


class TeacherManager(UserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.TEACHER)


# User Model
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        STUDENT = 'student', 'Student'
        TEACHER = 'teacher', 'Teacher'

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.ADMIN)
    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.pk:  # If it's a new instance
            self.role = self.role or self.base_role
        super(User, self).save(*args, **kwargs)


# Student Model (Proxy)
class Student(User):
    base_role = User.Role.STUDENT
    student = StudentManager()

    class Meta:
        proxy = True

    def welcome(self):
        return 'Faqat talabalar uchun'


# Student Profile
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Foydalanuvchi', related_name='student_profile')

    first_name = models.CharField(max_length=255, verbose_name='Ismi')
    last_name = models.CharField(max_length=255, verbose_name='Familiyasi')
    father_name = models.CharField(max_length=255, verbose_name='Otasining ismi')

    phone = models.CharField(max_length=15, null=True, blank=True, verbose_name='Telefon raqami')
    picture = models.ImageField(blank=True, null=True, verbose_name='Rasm')
    birth_date = models.DateField(verbose_name='Tug‘ilgan sana', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


@receiver(post_save, sender=Student)
def create_student_profile(sender, instance, created, **kwargs):
    if created and instance.role == User.Role.STUDENT:
        StudentProfile.objects.create(user=instance)


# Teacher Model (Proxy)
class Teacher(User):
    base_role = User.Role.TEACHER
    teacher = TeacherManager()

    class Meta:
        proxy = True

    def welcome(self):
        return 'Faqat ustozlar uchun'


# Teacher Profile
class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Foydalanuvchi', related_name='teacher_profile')

    first_name = models.CharField(max_length=255, verbose_name='Ismi')
    last_name = models.CharField(max_length=255, verbose_name='Familiyasi')
    father_name = models.CharField(max_length=255, verbose_name='Otasining ismi')

    phone = models.CharField(max_length=15, null=True, blank=True, verbose_name='Telefon raqami')
    picture = models.ImageField(blank=True, null=True, verbose_name='Rasm')
    birth_date = models.DateField(verbose_name='Tug‘ilgan sana', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


@receiver(post_save, sender=Teacher)
def create_teacher_profile(sender, instance, created, **kwargs):
    if created and instance.role == User.Role.TEACHER:
        TeacherProfile.objects.create(user=instance)
