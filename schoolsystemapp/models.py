from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


# Create your models here.


class User(AbstractUser):
    class Types(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        TEACHER = "TEACHER", "Teacher"
        ADMIN = "ADMIN", "Admin"

    # What type of user are we?
    type = models.CharField(_('Type'), max_length=50, choices=Types.choices, default=Types.STUDENT)

    # First Name and Last Name Do Not Cover Name Patters
    # Around the Globe.
    name = models.CharField(_("Name of User"), blank=True, max_length=255)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})


class StudentManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.STUDENT)


class TeacherManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.TEACHER)


class AdminManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.ADMIN)


class ListOfSchool(models.Model):
    school_code = models.CharField(max_length=15, primary_key=True)
    school_name = models.CharField(max_length=255, unique=True)
    account_name = models.CharField(max_length=258, default=None, blank=True)
    account_number = models.CharField(max_length=15, default=None, blank=True)
    bank_name = models.CharField(max_length=128, default=None, blank=True)


class StudentDetail(models.Model):
    user = models.OneToOneField(User.Types.STUDENT, on_delete=models.CASCADE, unique=True)
    student_code = models.CharField(max_length=8, unique=True)
    current_class = models.CharField(max_length=5)

    class TermChoices(models.TextChoices):
        FIRST = '1', _('FIRST')
        SECOND = '2', _('SECOND')
        THIRD = '3', _('THIRD')

    current_term = models.CharField(max_length=1, choices=TermChoices.choices)

    class SexChoices(models.TextChoices):
        MALE = 'M', _('MALE')
        FEMALE = 'F', _('FEMALE')

    sex = models.CharField(max_length=1, choices=SexChoices.choices)
    birth_date = models.DateField()
    birth_place = models.CharField(max_length=128)
    state_of_origin = models.CharField(max_length=128)
    email_address_2 = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=10)
    phone_number_2 = models.CharField(max_length=10, blank=True, null=True)
    postal_code = models.CharField(max_length=128)
    address = models.CharField(max_length=256)
    city = models.CharField(max_length=128)
    state = models.CharField(max_length=128)
    nationality = models.CharField(max_length=128)
    fathers_name = models.CharField(max_length=256)
    mothers_name = models.CharField(max_length=256)
    mothers_maiden_name = models.CharField(max_length=256)
    date_of_admission = models.DateField()

    class StatusChoices(models.TextChoices):
        ACTIVE = 'ACTIVE', _('ACTIVE')
        INACTIVE = 'INACTIVE', _('INACTIVE')

    dormitory = models.CharField(max_length=256, blank=True, null=True)
    student_status = models.CharField(max_length=8, choices=StatusChoices.choices)
    no_active_terms = models.PositiveSmallIntegerField(default=0)
    no_terms_remaining = models.PositiveSmallIntegerField(default=0)
    expected_graduation = models.DateField()
    school_code = models.ForeignKey(ListOfSchool, on_delete=models.CASCADE)
    registration_number = models.CharField(max_length=128)
    education_id = models.CharField(max_length=128, blank=True, null=True)
    theme_color = models.CharField(default='darkgreen', max_length=128)
    admin = models.CharField(max_length=128, blank=True, null=True)


class Student(User):
    base_type = User.Types.STUDENT
    objects = StudentManager()

    @property
    def more_details(self):
        return self.studentdetail

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = User.Types.STUDENT
        return super().save(*args, **kwargs)


class TeacherDetail(models.Model):
    user = models.OneToOneField(User.Types.TEACHER, on_delete=models.CASCADE, unique=True)
    teacher_code = models.CharField(max_length=8, unique=True)
    birth_date = models.DateField()

    class SexChoices(models.TextChoices):
        MALE = 'M', _('MALE')
        FEMALE = 'F', _('FEMALE')

    sex = models.CharField(max_length=1, choices=SexChoices.choices)
    email_address_2 = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=10)
    phone_number_2 = models.CharField(max_length=10, blank=True, null=True)
    postal_code = models.CharField(max_length=128)
    address = models.CharField(max_length=256)
    city = models.CharField(max_length=128)
    state = models.CharField(max_length=128)
    state_of_origin = models.CharField(max_length=128)
    nationality = models.CharField(max_length=128)
    subject_1 = models.CharField(max_length=128, null=True, blank=True)
    subject_class_1 = models.CharField(max_length=128, null=True, blank=True)
    subject_2 = models.CharField(max_length=128, null=True, blank=True)
    subject_class_2 = models.CharField(max_length=128, null=True, blank=True)
    subject_3 = models.CharField(max_length=128, null=True, blank=True)
    subject_class_3 = models.CharField(max_length=128, null=True, blank=True)
    subject_4 = models.CharField(max_length=128, null=True, blank=True)
    subject_class_4 = models.CharField(max_length=128, null=True, blank=True)
    subject_5 = models.CharField(max_length=128, null=True, blank=True)
    subject_class_5 = models.CharField(max_length=128, null=True, blank=True)
    national_id_card_no = models.CharField(max_length=15, null=True)
    employment_start_date = models.DateField()
    no_active_terms = models.PositiveSmallIntegerField(default=0)
    employment_end_date = models.DateField(null=True, blank=True)
    school_code = models.ForeignKey(ListOfSchool, on_delete=models.CASCADE)

    class StatusChoices(models.TextChoices):
        ACTIVE = 'ACTIVE', _('ACTIVE')
        INACTIVE = 'INACTIVE', _('INACTIVE')

    class ClassTeacherChoices(models.TextChoices):
        YES = 'YES', _('YES')
        NO = 'NO', _('NO')

    class_teacher = models.CharField(max_length=3, choices=ClassTeacherChoices.choices, default='NO')
    class_teachers_class = models.CharField(max_length=5, null=True, blank=True)
    teacher_status = models.CharField(max_length=8, choices=StatusChoices.choices, default='ACTIVE')
    theme_color = models.CharField(default='darkgreen', max_length=128)
    admin = models.CharField(max_length=128, blank=True, null=True)


class Teacher(User):
    base_type = User.Types.TEACHER
    objects = TeacherManager()

    @property
    def more_details(self):
        return self.teacherdetail

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = User.Types.TEACHER
        return super().save(*args, **kwargs)


class AdminDetail(models.Model):
    user = models.OneToOneField(User.Types.ADMIN, on_delete=models.CASCADE, unique=True)
    theme_color = models.CharField(default='darkgreen', max_length=128)


class Admin(User):
    base_type = User.Types.ADMIN
    objects = AdminManager()

    @property
    def more_details(self):
        return self.admindetail

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = User.Types.ADMIN
        return super().save(*args, **kwargs)


class SubjectDetail(models.Model):
    subject = models.CharField(max_length=256)
    subject_class = models.CharField(max_length=5)

    class DayChoices(models.TextChoices):
        MONDAY = 'MON', _('MONDAY')
        TUESDAY = 'TUES', _('TUESDAY')
        WEDNESDAY = 'WED', _('WEDNESDAY')
        THURSDAY = 'THURS', _('THURSDAY')
        FRIDAY = 'FRI', _('FRIDAY')

    day = models.CharField(max_length=5, choices=DayChoices.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    teacher_code = models.ForeignKey(User.Types.TEACHER, on_delete=models.CASCADE)
    school_code = models.ForeignKey(ListOfSchool, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('subject', 'subject_class', 'day', 'teacher_code', 'start_time', 'school_code'),)


class ClassSchedule(models.Model):
    student_class = models.CharField(max_length=5)
    class_start_time = models.TimeField()
    monday = models.CharField(max_length=256, blank=True)
    tuesday = models.CharField(max_length=256, blank=True)
    wednesday = models.CharField(max_length=256, blank=True)
    thursday = models.CharField(max_length=256, blank=True)
    friday = models.CharField(max_length=256, blank=True)
    school_code = models.ForeignKey(ListOfSchool, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('student_class', 'class_start_time', 'school_code'),)


class GradeBook(models.Model):
    school_code = models.ForeignKey(ListOfSchool, on_delete=models.CASCADE)
    subject = models.CharField(max_length=256)
    student_class = models.CharField(max_length=5)

    class TermChoices(models.TextChoices):
        FIRST = '1', _('FIRST')
        SECOND = '2', _('SECOND')
        THIRD = '3', _('THIRD')

    term = models.CharField(max_length=1, choices=TermChoices.choices)
    midterm_test = models.PositiveSmallIntegerField(blank=True, null=True)
    date_midterm_test = models.DateField(blank=True, null=True)
    exam_result = models.PositiveSmallIntegerField(blank=True, null=True)
    date_exam_result = models.DateField(blank=True, null=True)
    grade = models.PositiveSmallIntegerField(blank=True, null=True)
    date_grade = models.DateField(blank=True, null=True)
    student_code = models.ForeignKey(User, on_delete=models.CASCADE)
    # student_code = models.CharField(max_length=8)
    teacher_code = models.CharField(max_length=8, null=True, blank=True)

    class StatusChoices(models.TextChoices):
        ACTIVE = 'ACTIVE', _('ACTIVE')
        INACTIVE = 'INACTIVE', _('INACTIVE')

    student_class_status = models.CharField(max_length=8, choices=StatusChoices.choices, default='ACTIVE')

    class Meta:
        unique_together = (('school_code', 'subject', 'student_class', 'term', 'student_code'),)


class GradeAverage(models.Model):
    school_code = models.ForeignKey(ListOfSchool, on_delete=models.CASCADE)
    student_code = models.ForeignKey(User.Types.STUDENT, on_delete=models.CASCADE)
    # student_code = models.ForeignKey(StudentDetail.student_code, on_delete=models.CASCADE)
    student_class = models.CharField(max_length=5)

    class TermChoices(models.TextChoices):
        FIRST = '1', _('FIRST')
        SECOND = '2', _('SECOND')
        THIRD = '3', _('THIRD')

    term = models.CharField(max_length=1, choices=TermChoices.choices)
    no_of_subjects = models.PositiveSmallIntegerField(default=0)
    grade_total = models.PositiveSmallIntegerField(default=0)
    percentage = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = (('school_code', 'student_code', 'student_class', 'term'),)


class Payment(models.Model):
    school_code = models.ForeignKey(ListOfSchool, on_delete=models.CASCADE)
    payment_code = models.CharField(max_length=128, primary_key=True)
    name = models.CharField(max_length=128)
    payment_class = models.CharField(max_length=5)

    class TermChoices(models.TextChoices):
        FIRST = '1', _('FIRST')
        SECOND = '2', _('SECOND')
        THIRD = '3', _('THIRD')

    term = models.CharField(max_length=1, choices=TermChoices.choices)
    amount = models.CharField(max_length=128)
    deadline = models.DateField()
    breakdown = models.FileField(upload_to='payment-breakdowm/%Y/%m/%d/', default=None)

    class Meta:
        unique_together = (('school_code', 'payment_code'),)


class StudentPaymentRecord(models.Model):
    school_code = models.ForeignKey(ListOfSchool, on_delete=models.CASCADE)
    payment_code = models.ForeignKey(Payment, on_delete=models.CASCADE)
    student_code = models.ForeignKey(User.Types.STUDENT, on_delete=models.CASCADE)
    payment_date = models.DateField()
    status = models.CharField(max_length=128)
    invoice_number = models.CharField(max_length=128)
    invoice = models.FileField(upload_to='invoices/%Y/%m/%d/', default=None)

    class Meta:
        unique_together = (('student_code', 'payment_code'),)


class StudentSchoolRecord(models.Model):
    user = models.ForeignKey(User.Types.STUDENT, on_delete=models.CASCADE)
    student_code = models.CharField(max_length=8)
    school_code = models.ForeignKey(ListOfSchool, on_delete=models.CASCADE)
    no_active_terms = models.PositiveSmallIntegerField()
    date_of_admission = models.DateField()
    registration_number = models.CharField(max_length=128)

    class StatusChoices(models.TextChoices):
        ACTIVE = 'ACTIVE', _('ACTIVE')
        INACTIVE = 'INACTIVE', _('INACTIVE')

    student_status = models.CharField(max_length=8, choices=StatusChoices.choices)

    class Meta:
        unique_together = (('user', 'student_code', 'school_code'),)


class TeacherSchoolRecord(models.Model):
    user = models.ForeignKey(User.Types.TEACHER, on_delete=models.CASCADE)
    teacher_code = models.CharField(max_length=8)
    school_code = models.ForeignKey(ListOfSchool, on_delete=models.CASCADE)
    no_active_terms = models.PositiveSmallIntegerField()
    date_of_employment = models.DateField()

    class StatusChoices(models.TextChoices):
        ACTIVE = 'ACTIVE', _('ACTIVE')
        INACTIVE = 'INACTIVE', _('INACTIVE')

    teacher_status = models.CharField(max_length=8, choices=StatusChoices.choices)

    class Meta:
        unique_together = (('user', 'teacher_code', 'school_code'),)


class Textbook(models.Model):
    school_code = models.ForeignKey(ListOfSchool, on_delete=models.CASCADE)
    textbook_class = models.CharField(max_length=5)
    textbook = models.FileField(upload_to='textbooks/%Y/%m/%d/', default=None)

    class Meta:
        unique_together = (('school_code', 'textbook_class'),)


class ClassAttendance(models.Model):
    student_id = models.ForeignKey(User.Types.STUDENT, on_delete=models.CASCADE)
    student_code = models.CharField(max_length=8, default=None)
    date = models.DateField()
    attendance = models.SmallIntegerField(default=5)
    school_id = models.ForeignKey(ListOfSchool, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('student_id', 'date'),)


class StudentMessage(models.Model):
    date_time = models.DateTimeField(auto_now_add=True)
    sender = models.CharField(max_length=258, default=None, blank=True)
    recipient = models.IntegerField()
    subject = models.CharField(max_length=258, default=None, blank=True)
    message = models.TextField()
    # attachments = models.ManyToManyField(FeedFile)
    school_id = models.ForeignKey(ListOfSchool, on_delete=models.CASCADE)

    # class Meta:
    #     unique_together = (('student_id', 'date'),)


class FeedFile(models.Model):
    attachments = models.FileField(upload_to='message_attachments/%Y/%m/%d/', default=None)
    feed = models.ForeignKey(StudentMessage, on_delete=models.CASCADE, default=None)
