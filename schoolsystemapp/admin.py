from django.contrib import admin
from schoolsystemapp.models import User, StudentDetail, TeacherDetail, SubjectDetail, GradeBook, ClassSchedule, \
    GradeAverage, Payment, StudentPaymentRecord, ListOfSchool, StudentSchoolRecord, Textbook, AdminDetail, \
    TeacherSchoolRecord, ClassAttendance, StudentMessage, FeedFile

# Register your models here.

admin.site.register(User)
admin.site.register(StudentDetail)
admin.site.register(TeacherDetail)
admin.site.register(SubjectDetail)
admin.site.register(GradeBook)
admin.site.register(ClassSchedule)
admin.site.register(GradeAverage)
admin.site.register(Payment)
admin.site.register(StudentPaymentRecord)
admin.site.register(ListOfSchool)
admin.site.register(StudentSchoolRecord)
admin.site.register(TeacherSchoolRecord)
admin.site.register(Textbook)
admin.site.register(AdminDetail)
admin.site.register(ClassAttendance)
admin.site.register(StudentMessage)
admin.site.register(FeedFile)
