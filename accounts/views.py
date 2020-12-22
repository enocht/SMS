import os

from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.db.models.aggregates import Count
from django.db.utils import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from schoolsystemapp.models import ClassSchedule, GradeBook, GradeAverage, Payment, StudentDetail, ListOfSchool, \
    StudentPaymentRecord, Textbook, TeacherDetail, AdminDetail, User, SubjectDetail, StudentSchoolRecord, \
    TeacherSchoolRecord, ClassAttendance, StudentMessage, FeedFile
import geoip2.database
from geoip2.errors import AddressNotFoundError
import string
import random
import datetime
from django import template
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

register = template.Library()

# Create your views here.

# student code generator
# def id_generator(size=6):
#     return random.choice(string.ascii_uppercase) + ''.join(
#         random.choice(string.ascii_uppercase + string.digits) for _ in range(size)) \
#            + random.choice(string.ascii_uppercase)
# while True:
#     new_student_code = id_generator()
#     codes = StudentDetail.objects.filter(student_code=new_student_code)
#     if len(codes) == 0:
#         break
# print(new_student_code)

theme_colors = {'1': 'darkgreen', '2': 'purple', '3': 'royalblue', '4': 'midnightblue', '5': 'chocolate', '6': 'brown',
                '7': 'darkred', '8': 'darkorange', '9': 'maroon', '10': 'deeppink'}

jss_subjects = {1: 'Mathematics', 2: 'English Language', 3: 'Basic Science', 4: 'Social Studies', 5: 'Fine Art',
                6: 'Agricultural Science', 7: 'Civic Education', 8: 'Christian Religious Studies',
                9: 'Physical and Health Education',
                10: 'Business Studies', 11: 'French', 12: 'Computer Studies', 13: 'Home Economics', 14: 'Music',
                15: 'Basic Technology'}

attendance_dates = {}


def date_by_adding_business_days(from_date, add_days):
    business_days_to_add = add_days
    current_date = from_date
    while business_days_to_add > 0:
        current_date += datetime.timedelta(days=1)
        weekday = current_date.weekday()
        if weekday >= 5:  # sunday = 6
            continue
        business_days_to_add -= 1
    return current_date


attendance_dates['1'] = datetime.date.today()
for i in range(2, 6):
    attendance_dates[str(i)] = date_by_adding_business_days(datetime.date.today(), i - 1)


# attendance_dates['2'] = date_by_adding_business_days(datetime.date.today(), 1)
# attendance_dates['3'] = date_by_adding_business_days(datetime.date.today(), 2)
# attendance_dates['4'] = date_by_adding_business_days(datetime.date.today(), 3)
# attendance_dates['5'] = date_by_adding_business_days(datetime.date.today(), 4)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def student_login(request):
    page_title = 'Utron - Student Login'
    if request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    elif request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        request.session['login_username'] = username
        user = authenticate(request, username=username, password=password)
        if user is not None and user.type == "STUDENT":
            request.session['user_ip'] = get_client_ip(request)
            # if username == 'XFEHIW1T':
            # if username == 'NRY7ILZE':
            # print(get_client_ip(request))
            # reader = geoip2.database.Reader(
            #     '/home/Utron/Utron/geoip2/GeoLite2-City_20201027/GeoLite2-City_20201027/GeoLite2-City.mmdb')
            reader = geoip2.database.Reader(
                '/Users/mac/Dev/schoolsystem/geoip2/GeoLite2-City_20201027/GeoLite2-City_20201027/GeoLite2-City.mmdb')
            try:
                response = reader.city(get_client_ip(request))
                request.session['country_code'] = response.country.iso_code
                request.session['country_name'] = response.country.name
                request.session['most_specific_name'] = response.subdivisions.most_specific.name
                request.session['city_name'] = response.city.name
                request.session['postal_code'] = response.postal.code
                request.session['latitude'] = response.location.latitude
                request.session['longitude'] = response.location.longitude
                #     Notification on Login
                mail_subject = 'Utron Login Notification'
                message = render_to_string('message.html', {'request': request.session})
                to_email = 'taiwo.dele@ymail.com'
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                email.send()
            except AddressNotFoundError:
                # print('No Address')
                #     Notification on Login
                mail_subject = 'Utron Login Notification'
                message_2 = render_to_string('message2.html', {'request': request.session})
                to_email_2 = 'taiwo.dele@ymail.com'
                email_2 = EmailMessage(
                    mail_subject, message_2, to=[to_email_2]
                )
                email_2.send()
            login(request, user)
            return redirect('student_dashboard')
            # page_title = 'Utron - Dashboard'
            # return render(request, "accounts/student/student_dashboard.html", {'page_title': page_title})
        else:
            request.session['error'] = "Incorrect username or password"
            return render(request, "accounts/student_login.html", {'page_title': page_title})
    request.session['error'] = False
    return render(request, "accounts/student_login.html", {'page_title': page_title})


def teacher_login(request):
    page_title = 'Utron - Teacher Login'
    if request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        request.session['login_username'] = username
        user = authenticate(request, username=username, password=password)
        if user is not None and user.type == "TEACHER":
            login(request, user)
            # page_title = 'Utron - Dashboard'
            # return render(request, "accounts/teacher/teacher_dashboard.html", {'page_title': page_title})
            return redirect('teacher_dashboard')
        else:
            request.session['error'] = "Incorrect username or password"
            # messages.info(request, "Incorrect email or password")
            return render(request, "accounts/teacher_login.html", {'page_title': page_title})
    request.session['error'] = False
    return render(request, "accounts/teacher_login.html", {'page_title': page_title})


def student_dashboard(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        page_title = 'Utron - Dashboard'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        return render(request, "accounts/student/student_dashboard.html",
                      {'page_title': page_title, 'school_detail': school_detail, 'theme_color': theme_colors})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def teacher_dashboard(request):
    if request.user.is_authenticated and request.user.type == 'TEACHER':
        page_title = 'Utron - Dashboard'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.teacherdetail.school_code_id)
        return render(request, "accounts/teacher/teacher_dashboard.html",
                      {'page_title': page_title, 'school_detail': school_detail, 'theme_color': theme_colors})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    else:
        return redirect('teacher_login')


def student_logout_view(request):
    logout(request)
    return redirect('student_login')


def teacher_logout_view(request):
    logout(request)
    return redirect('teacher_login')


def student_inbox(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        page_title = 'Dashboard - Inbox'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        return render(request, "accounts/student/inbox.html", {'page_title': page_title,
                                                               'school_detail': school_detail,
                                                               'theme_color': theme_colors})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def student_sent(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        page_title = 'Dashboard - Sent'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        sent_messages = StudentMessage.objects.filter(sender=request.user.id).order_by('-date_time')
        recipient = User.objects.filter(type='STUDENT')
        today = {'date': datetime.datetime.now().date()}
        # request.session['message_id'] = False
        if request.GET.get('message_id'):
            request.session['message_id'] = int(request.GET.get('message_id'))
            message_id = request.session['message_id']
            sent_message = StudentMessage.objects.filter(id=message_id)
            # print(sent_message)
            return render(request, "accounts/student/sent.html", {'page_title': page_title,
                                                                  'school_detail': school_detail,
                                                                  'theme_color': theme_colors,
                                                                  'sent_messages': sent_messages,
                                                                  'recipient': recipient,
                                                                  'today': today,
                                                                  'sent_message': sent_message})
        # print('lol')
        return render(request, "accounts/student/sent.html", {'page_title': page_title,
                                                              'school_detail': school_detail,
                                                              'theme_color': theme_colors,
                                                              'sent_messages': sent_messages,
                                                              'recipient': recipient,
                                                              'today': today})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def student_sent_message_view(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        # print(request.POST)
        page_title = 'Dashboard - Sent'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        # request.session['message_id'] = False
        if request.GET.get('message_id'):
            print('lol')
            request.session['message_id'] = request.GET.get('message_id')
            message_id = request.session['message_id']
            sent_messages = StudentMessage.objects.filter(id=message_id)
        if not request.session['message_id']:
            print(request.session['message_id'])
            return render(request, "accounts/student/message_view.html", {'page_title': page_title,
                                                                          'school_detail': school_detail,
                                                                          'theme_color': theme_colors})
        else:
            print(request.session['message_id'])
            return render(request, "accounts/student/message_view.html", {'page_title': page_title,
                                                                          'school_detail': school_detail,
                                                                          'theme_color': theme_colors})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def student_compose(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        page_title = 'Dashboard - Compose'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        student_list = StudentDetail.objects.filter(school_code=request.user.studentdetail.school_code_id,
                                                    current_class=request.user.studentdetail.current_class)
        all_student_list = User.objects.filter()
        request.session['message_sent_successfully'] = False
        if 'send-message' in request.POST:
            recipient = request.POST.get('recipient')
            subject = request.POST.get('subject')
            message_to_send = request.POST.get('message')
            attachments = request.FILES.getlist('attachments')
            student_email = User.objects.filter(id=recipient).values_list('email', flat=True).order_by()
            for data_2 in student_email:
                student_email = data_2
            try:
                StudentMessage.objects.create(sender=request.user.id,
                                              recipient=recipient, subject=subject, message=message_to_send,
                                              school_id=request.user.studentdetail.school_code).save()
                message_id = StudentMessage.objects.filter(sender=request.user.id).values_list('id',
                                                                                               flat=True).order_by()
                for ids in message_id:
                    foreign_key = ids
                for file in attachments:
                    FeedFile.objects.create(attachments=file, feed_id=foreign_key)
                mail_subject = subject
                message = message_to_send
                to_email = student_email
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                for file in attachments:
                    path = '/Users/'
                    name = str(file)
                    file_path = False
                    for root, dirs, files in os.walk(path):
                        if name in files:
                            file_path = os.path.join(root, name)
                            # print(file_path)
                            break
                    if file_path:
                        email.attach_file(file_path)
                    # email.attach(file.name, file.read(), file.content_type)
                email.send()
                request.session['message_sent_successfully'] = True
            except IntegrityError:
                pass
        return render(request, "accounts/student/compose.html", {'page_title': page_title,
                                                                 'school_detail': school_detail,
                                                                 'theme_color': theme_colors,
                                                                 'student_list': student_list,
                                                                 'all_student_list': all_student_list})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def personal_info(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        page_title = 'Dashboard - Personal Info'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        return render(request, "accounts/student/personal_info.html",
                      {'page_title': page_title, 'school_detail': school_detail, 'theme_color': theme_colors})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def teacher_personal_info(request):
    if request.user.is_authenticated and request.user.type == 'TEACHER':
        page_title = 'Dashboard - Personal Info'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.teacherdetail.school_code_id)
        return render(request, "accounts/teacher/teacher_personal_info.html",
                      {'page_title': page_title, 'school_detail': school_detail, 'theme_color': theme_colors})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    else:
        return redirect('teacher_login')


def contact_info(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        page_title = 'Dashboard - Contact Info'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        student_detail = StudentDetail.objects.filter(user=request.user)
        email = request.GET.get('email')
        phone = request.GET.get('phonenumber')
        email_2 = request.GET.get('email_2')
        phone_2 = request.GET.get('phone_2')
        if email_2 is not None:
            StudentDetail.objects.filter(user=request.user).update(email_address_2=None)
        if phone_2 is not None:
            StudentDetail.objects.filter(user=request.user).update(phone_number_2=None)
        request.session['phone_form_error'] = False
        request.session['email_form_error'] = False
        if email is not None and (
                request.user.studentdetail.email_address_2 is None or request.user.studentdetail.email_address_2 == ''):
            if email.lower() == request.user.email.lower():
                request.session['email_form_error'] = 'Email Exists!'
            else:
                StudentDetail.objects.filter(user=request.user).update(email_address_2=email)
        if phone is not None and (
                request.user.studentdetail.phone_number_2 is None or request.user.studentdetail.phone_number_2 == ''):
            if len(phone) != 10:
                request.session['phone_form_error'] = 'Please input 10 characters!'
            elif phone == request.user.studentdetail.phone_number:
                request.session['phone_form_error'] = 'Phone Number Exists!'
            else:
                StudentDetail.objects.filter(user=request.user).update(phone_number_2=phone)
        return render(request, "accounts/student/contact_info.html",
                      {'page_title': page_title, 'student_detail': student_detail, 'school_detail': school_detail,
                       'theme_color': theme_colors})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def teacher_contact_info(request):
    if request.user.is_authenticated and request.user.type == 'TEACHER':
        page_title = 'Dashboard - Contact Info'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.teacherdetail.school_code_id)
        teacher_detail = TeacherDetail.objects.filter(user=request.user)
        email = request.GET.get('email')
        phone = request.GET.get('phonenumber')
        email_2 = request.GET.get('email_2')
        phone_2 = request.GET.get('phone_2')
        if email_2 is not None:
            TeacherDetail.objects.filter(user=request.user).update(email_address_2=None)
        if phone_2 is not None:
            TeacherDetail.objects.filter(user=request.user).update(phone_number_2=None)
        request.session['phone_form_error'] = False
        request.session['email_form_error'] = False
        if email is not None and (
                request.user.teacherdetail.email_address_2 is None or request.user.teacherdetail.email_address_2 == ''):
            if email.lower() == request.user.email.lower():
                request.session['email_form_error'] = 'Email Exists!'
            else:
                TeacherDetail.objects.filter(user=request.user).update(email_address_2=email)
        if phone is not None and (
                request.user.teacherdetail.phone_number_2 is None or request.user.teacherdetail.phone_number_2 == ''):
            if len(phone) != 10:
                request.session['phone_form_error'] = 'Please input 10 characters!'
            elif phone == request.user.teacherdetail.phone_number:
                request.session['phone_form_error'] = 'Phone Number Exists!'
            else:
                TeacherDetail.objects.filter(user=request.user).update(phone_number_2=phone)
        return render(request, "accounts/teacher/teacher_contact_info.html",
                      {'page_title': page_title, 'teacher_detail': teacher_detail, 'school_detail': school_detail,
                       'theme_color': theme_colors})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    else:
        return redirect('teacher_login')


def training_data(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        page_title = 'Dashboard - Training Data'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        teacher_details = TeacherDetail.objects.filter(school_code=request.user.studentdetail.school_code_id,
                                                       class_teachers_class=request.user.studentdetail.current_class)
        user_details = User.objects.filter(type='TEACHER')
        return render(request, "accounts/student/training_data.html",
                      {'page_title': page_title, 'school_detail': school_detail, 'theme_color': theme_colors,
                       'teacher_details': teacher_details, 'user_details': user_details})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def teaching_data(request):
    if request.user.is_authenticated and request.user.type == 'TEACHER':
        page_title = 'Dashboard - Teaching Data'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.teacherdetail.school_code_id)
        return render(request, "accounts/teacher/teaching_data.html",
                      {'page_title': page_title, 'school_detail': school_detail, 'theme_color': theme_colors})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    else:
        return redirect('teacher_login')


def class_schedule_view(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        page_title = 'Dashboard - Class Schedule'
        class_schedule = ClassSchedule.objects.filter(student_class=request.user.studentdetail.current_class,
                                                      school_code=request.user.studentdetail.school_code_id).order_by(
            'class_start_time')
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        return render(request, "accounts/student/class_schedule.html",
                      {'page_title': page_title, 'class_schedule': class_schedule, 'school_detail': school_detail,
                       'theme_color': theme_colors})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def teacher_class_schedule_view(request):
    if request.user.is_authenticated and request.user.type == 'TEACHER':
        page_title = 'Dashboard - Class Schedule'
        class_schedule = ClassSchedule.objects.filter(school_code=request.user.teacherdetail.school_code_id).order_by(
            'student_class', 'class_start_time')
        school_detail = ListOfSchool.objects.filter(school_code=request.user.teacherdetail.school_code_id)
        return render(request, "accounts/teacher/teacher_class_schedule.html",
                      {'page_title': page_title, 'class_schedule': class_schedule, 'school_detail': school_detail,
                       'theme_color': theme_colors})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('teacher_dashboard')
    else:
        return redirect('teacher_login')


def gradebook(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        page_title = 'Dashboard - Gradebook'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        class_options = request.GET.get('class_options')
        term_options = request.GET.get('term_options')
        student_data = {'class': class_options, 'term': term_options}
        grade_book = GradeBook.objects.filter(student_code_id=request.user.studentdetail.user_id, term=term_options,
                                              student_class=class_options,
                                              school_code_id=request.user.studentdetail.school_code_id)
        teacher_details = TeacherDetail.objects.filter(school_code=request.user.studentdetail.school_code_id)
        user_details = User.objects.filter(type='TEACHER')
        student_details = {'class': request.user.studentdetail.current_class}
        request.session['empty_query'] = 'false'
        if len(grade_book) == 0:
            request.session['empty_query'] = 'true'
        # for i in range(len(grade_book)):
        #     print(grade_book[i])
        return render(request, "accounts/student/gradebook.html",
                      {'page_title': page_title, 'grade_book': grade_book, 'student_data': student_data,
                       'school_detail': school_detail, 'theme_color': theme_colors, 'teacher_details': teacher_details,
                       'user_details': user_details, 'student_details': student_details})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def teacher_gradebook(request):
    if request.user.is_authenticated and request.user.type == 'TEACHER':
        page_title = 'Dashboard - Gradebook'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.teacherdetail.school_code_id)
        class_options = request.GET.get('class')
        subject = request.GET.get('subject')
        user_details = User.objects.filter(type='STUDENT')
        if class_options is not None:
            subject = subject.upper()
            class_options = class_options.strip()
            student_data = {'class': class_options, 'subject': subject}
            grade_book = GradeBook.objects.filter(student_class=class_options,
                                                  school_code=request.user.teacherdetail.school_code_id,
                                                  subject=subject, term=1, student_class_status='ACTIVE')
        else:
            student_data = {'class': class_options, 'subject': subject}
            grade_book = GradeBook.objects.filter(student_class=class_options,
                                                  school_code=request.user.teacherdetail.school_code_id,
                                                  subject=subject, term=1, student_class_status='ACTIVE')
        return render(request, "accounts/teacher/teacher_gradebook.html",
                      {'page_title': page_title, 'grade_book': grade_book, 'student_data': student_data,
                       'school_detail': school_detail, 'theme_color': theme_colors, 'user_details': user_details})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    else:
        return redirect('teacher_login')


def grade_average(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        page_title = 'Dashboard - Grade Average'
        gradeaverage = GradeAverage.objects.filter(student_code_id=request.user.studentdetail.user_id,
                                                   school_code_id=request.user.studentdetail.school_code_id,
                                                   term=request.user.studentdetail.current_term)
        grades = GradeBook.objects.filter(student_code=request.user.studentdetail.user_id)
        # test = GradeBook.objects.values('term').filter(student_code=request.user.studentdetail.user_id).annotate(dcount=Count('term'))
        # test_2 = GradeBook.objects.values('student_class').filter(student_code=request.user.studentdetail.user_id).annotate(dcount=Count('student_class'))
        # print(test)
        # print(test_2)
        # for i in test_2:
        #     print(i['student_class'])
        count = 0
        total_grade = 0
        student_class = ''
        term = ''
        total_subject_count = 0
        for data in grades:
            if data.grade:
                count += 1
                total_grade += int(data.grade)
                student_class = data.student_class
                term = data.term
            total_subject_count += 1
        percentage = total_grade / count
        percentage = "%.2f" % round(percentage, 2)
        # print(count)
        # print(total_subject_count)
        # print(total_grade)
        # print(student_class)
        # print(term)
        # print(percentage)
        grade_average_details = {'count': count, 'total_subject_count': total_subject_count, 'total_grade': total_grade,
                                 'student_class': student_class, 'term': term, 'percentage': percentage}
        # new_list = GradeBook.objects.values('designation').annotate(dcount=Count('designation'))
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        return render(request, "accounts/student/grade_average.html",
                      {'page_title': page_title, 'grade_average': gradeaverage, 'school_detail': school_detail,
                       'theme_color': theme_colors, 'grade_average_details': grade_average_details})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def subjects_taken(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        page_title = 'Dashboard - Subjects Taken'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        subject_list = GradeBook.objects.filter(student_code_id=request.user.studentdetail.user_id,
                                                student_class=request.user.studentdetail.current_class,
                                                term=request.user.studentdetail.current_term)
        student_details = {'class': request.user.studentdetail.current_class}
        teacher_details = TeacherDetail.objects.filter(school_code=request.user.studentdetail.school_code_id)
        user_details = User.objects.filter(type='TEACHER')
        return render(request, "accounts/student/subjects_taken.html",
                      {'page_title': page_title, 'subject_list': subject_list, 'student_details': student_details,
                       'school_detail': school_detail, 'theme_color': theme_colors, 'teacher_details': teacher_details,
                       'user_details': user_details})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def teacher_subjects_taught(request):
    if request.user.is_authenticated and request.user.type == 'TEACHER':
        page_title = 'Dashboard - Subjects Taught'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.teacherdetail.school_code_id)
        return render(request, "accounts/teacher/teacher_subject_taught.html",
                      {'page_title': page_title, 'school_detail': school_detail, 'theme_color': theme_colors})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    else:
        return redirect('teacher_login')


def midterm(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        page_title = 'Dashboard - Midterm'
        class_options = request.GET.get('class_options')
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        term_options = request.GET.get('term_options')
        student_data = {'class': class_options, 'term': term_options}
        grade_book = GradeBook.objects.filter(student_code_id=request.user.studentdetail.user_id, term=term_options,
                                              student_class=class_options)
        teacher_details = TeacherDetail.objects.filter(school_code=request.user.studentdetail.school_code_id)
        user_details = User.objects.filter(type='TEACHER')
        student_details = {'class': request.user.studentdetail.current_class}
        request.session['empty_query'] = 'false'
        if len(grade_book) == 0:
            request.session['empty_query'] = 'true'
        return render(request, "accounts/student/midterm.html",
                      {'page_title': page_title, 'grade_book': grade_book, 'student_data': student_data,
                       'school_detail': school_detail, 'theme_color': theme_colors, 'teacher_details': teacher_details,
                       'user_details': user_details, 'student_details': student_details})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def teacher_midterm(request):
    now = datetime.datetime.now()
    if request.user.is_authenticated and request.user.type == 'TEACHER':
        page_title = 'Dashboard - Midterm'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.teacherdetail.school_code_id)
        class_options = request.GET.get('class')
        subject = request.GET.get('subject')
        class_options_1 = request.GET.get('class_1')
        subject_1 = request.GET.get('subject_1')
        student_code = request.GET.get('student_code')
        grade = request.GET.get('grade')
        class_options_2 = request.GET.get('class_2')
        subject_2 = request.GET.get('subject_2')
        student_code_1 = request.GET.get('student_code_1')
        grade_1 = request.GET.get('grade_1')
        if class_options is not None:
            subject = subject.upper()
            class_options = class_options.strip()
            student_data = {'class': class_options, 'subject': subject}
            grade_book = GradeBook.objects.filter(student_class=class_options,
                                                  school_code=request.user.teacherdetail.school_code_id,
                                                  subject=subject, term=1, student_class_status='ACTIVE')
            request.session['show'] = 'list of students'
        elif class_options_1 is not None:
            subject_1 = subject_1.upper()
            request.session['lol_subject_1'] = subject_1
            class_options_1 = class_options_1.strip()
            request.session['student_class'] = class_options_1
            student_data = {'class': class_options_1, 'subject': subject_1}
            grade_book = GradeBook.objects.filter(student_class=class_options_1,
                                                  school_code=request.user.teacherdetail.school_code_id,
                                                  subject=subject_1, term=1, student_class_status='ACTIVE')
            request.session['show'] = 'add grade'
        elif class_options_2 is not None:
            subject_2 = subject_2.upper()
            request.session['lol_subject_2'] = subject_2
            class_options_2 = class_options_2.strip()
            request.session['student_class'] = class_options_2
            student_data = {'class': class_options_2, 'subject': subject_2}
            grade_book = GradeBook.objects.filter(student_class=class_options_2,
                                                  school_code=request.user.teacherdetail.school_code_id,
                                                  subject=subject_2, term=1, student_class_status='ACTIVE')
            request.session['show'] = 'change grade'
        else:
            student_data = {'class': class_options, 'subject': subject}
            grade_book = GradeBook.objects.filter(student_class=class_options,
                                                  school_code=request.user.teacherdetail.school_code_id,
                                                  subject=subject, term=1, student_class_status='ACTIVE')
            request.session['show'] = False
        if student_code is not None:
            subject_1 = request.session['lol_subject_1'].upper()
            exam_score = GradeBook.objects.filter(student_code=student_code,
                                                  student_class=request.session['student_class'],
                                                  subject=subject_1).values_list('exam_result', flat=True).order_by()
            if exam_score[0] is not None:
                total_grade = int(grade) + int(exam_score[0])
                GradeBook.objects.filter(student_code=student_code,
                                         student_class=request.session['student_class'],
                                         subject=subject_1).update(grade=total_grade, date_grade=now.date(),
                                                                   teacher_code=request.user.username)
            GradeBook.objects.filter(student_code=student_code, student_class=request.session['student_class'],
                                     subject=subject_1).update(midterm_test=grade, date_midterm_test=now.date(),
                                                               teacher_code=request.user.username)
            student_code = User.objects.filter(id=student_code).values_list('username', flat=True).order_by()
            request.session['added'] = 'Midterm test result has been added for ' + str(student_code[0])
            request.session['show'] = 'add grade'
        elif student_code_1 is not None:
            subject_2 = request.session['lol_subject_2'].upper()
            exam_score = GradeBook.objects.filter(student_code=student_code_1,
                                                  student_class=request.session['student_class'],
                                                  subject=subject_2).values_list('exam_result', flat=True).order_by()
            if exam_score[0] is not None:
                total_grade = int(grade_1) + int(exam_score[0])
                GradeBook.objects.filter(student_code=student_code_1,
                                         student_class=request.session['student_class'],
                                         subject=subject_2).update(grade=total_grade, date_grade=now.date(),
                                                                   teacher_code=request.user.username)
            GradeBook.objects.filter(student_code=student_code_1, student_class=request.session['student_class'],
                                     subject=subject_2).update(midterm_test=grade_1, date_midterm_test=now.date(),
                                                               teacher_code=request.user.username)
            student_code_1 = User.objects.filter(id=student_code_1).values_list('username', flat=True).order_by()
            request.session['added'] = 'Midterm test result has been changed for ' + str(student_code_1[0])
            request.session['show'] = 'change grade'
        else:
            request.session['added'] = False
        user_details = User.objects.filter(type='STUDENT')
        return render(request, "accounts/teacher/teacher_midterm.html",
                      {'page_title': page_title, 'grade_book': grade_book, 'student_data': student_data,
                       'school_detail': school_detail, 'theme_color': theme_colors, 'user_details': user_details})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    else:
        return redirect('teacher_login')


def taken_exams(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        page_title = 'Dashboard - Exams Taken'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        class_options = request.GET.get('class_options')
        term_options = request.GET.get('term_options')
        student_data = {'class': class_options, 'term': term_options}
        grade_book = GradeBook.objects.filter(student_code_id=request.user.studentdetail.user_id, term=term_options,
                                              student_class=class_options)
        teacher_details = TeacherDetail.objects.filter(school_code=request.user.studentdetail.school_code_id)
        user_details = User.objects.filter(type='TEACHER')
        student_details = {'class': request.user.studentdetail.current_class}
        request.session['empty_query'] = 'false'
        if len(grade_book) == 0:
            request.session['empty_query'] = 'true'
        return render(request, "accounts/student/taken_exams.html",
                      {'page_title': page_title, 'grade_book': grade_book, 'student_data': student_data,
                       'school_detail': school_detail, 'theme_color': theme_colors, 'teacher_details': teacher_details,
                       'user_details': user_details, 'student_details': student_details})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def teacher_exam_results(request):
    now = datetime.datetime.now()
    if request.user.is_authenticated and request.user.type == 'TEACHER':
        page_title = 'Dashboard - Exam Results'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.teacherdetail.school_code_id)
        class_options = request.GET.get('class')
        subject = request.GET.get('subject')
        class_options_1 = request.GET.get('class_1')
        subject_1 = request.GET.get('subject_1')
        student_code = request.GET.get('student_code')
        grade = request.GET.get('grade')
        class_options_2 = request.GET.get('class_2')
        subject_2 = request.GET.get('subject_2')
        student_code_1 = request.GET.get('student_code_1')
        grade_1 = request.GET.get('grade_1')
        if class_options is not None:
            subject = subject.upper()
            class_options = class_options.strip()
            student_data = {'class': class_options, 'subject': subject}
            grade_book = GradeBook.objects.filter(student_class=class_options,
                                                  school_code=request.user.teacherdetail.school_code_id,
                                                  subject=subject, term=1, student_class_status='ACTIVE')
            request.session['show'] = 'list of students'
        elif class_options_1 is not None:
            subject_1 = subject_1.upper()
            request.session['lol_subject_1'] = subject_1
            class_options_1 = class_options_1.strip()
            request.session['student_class'] = class_options_1
            student_data = {'class': class_options_1, 'subject': subject_1}
            grade_book = GradeBook.objects.filter(student_class=class_options_1,
                                                  school_code=request.user.teacherdetail.school_code_id,
                                                  subject=subject_1, term=1, student_class_status='ACTIVE')
            request.session['show'] = 'add grade'
        elif class_options_2 is not None:
            subject_2 = subject_2.upper()
            request.session['lol_subject_2'] = subject_2
            class_options_2 = class_options_2.strip()
            request.session['student_class'] = class_options_2
            student_data = {'class': class_options_2, 'subject': subject_2}
            grade_book = GradeBook.objects.filter(student_class=class_options_2,
                                                  school_code=request.user.teacherdetail.school_code_id,
                                                  subject=subject_2, term=1, student_class_status='ACTIVE')
            request.session['show'] = 'change grade'
        else:
            student_data = {'class': class_options, 'subject': subject}
            grade_book = GradeBook.objects.filter(student_class=class_options,
                                                  school_code=request.user.teacherdetail.school_code_id,
                                                  subject=subject, term=1, student_class_status='ACTIVE')
            request.session['show'] = False
        if student_code is not None:
            subject_1 = request.session['lol_subject_1'].upper()
            midterm_score = GradeBook.objects.filter(student_code=student_code,
                                                     student_class=request.session['student_class'],
                                                     subject=subject_1).values_list('midterm_test',
                                                                                    flat=True).order_by()
            if midterm_score[0] is not None:
                total_grade = int(grade) + int(midterm_score[0])
            else:
                total_grade = int(grade)
            GradeBook.objects.filter(student_code=student_code, student_class=request.session['student_class'],
                                     subject=subject_1).update(exam_result=grade, date_exam_result=now.date(),
                                                               teacher_code=request.user.username)
            GradeBook.objects.filter(student_code=student_code, student_class=request.session['student_class'],
                                     subject=subject_1).update(grade=total_grade, date_grade=now.date(),
                                                               teacher_code=request.user.username)
            student_code = User.objects.filter(id=student_code).values_list('username', flat=True).order_by()
            request.session['added'] = 'Exam result has been added for ' + str(student_code[0])
            request.session['show'] = 'add grade'
        elif student_code_1 is not None:
            subject_2 = request.session['lol_subject_2'].upper()
            midterm_score = GradeBook.objects.filter(student_code=student_code_1,
                                                     student_class=request.session['student_class'],
                                                     subject=subject_2).values_list('midterm_test',
                                                                                    flat=True).order_by()
            if midterm_score[0] is not None:
                total_grade = int(grade_1) + int(midterm_score[0])
            else:
                total_grade = int(grade_1)
            GradeBook.objects.filter(student_code=student_code_1,
                                     student_class=request.session['student_class'],
                                     subject=subject_2).update(exam_result=grade_1, date_exam_result=now.date(),
                                                               teacher_code=request.user.username)
            GradeBook.objects.filter(student_code=student_code_1,
                                     student_class=request.session['student_class'],
                                     subject=subject_2).update(grade=total_grade, date_grade=now.date(),
                                                               teacher_code=request.user.username)
            student_code_1 = User.objects.filter(id=student_code_1).values_list('username', flat=True).order_by()
            request.session['added'] = 'Exam result has been changed for ' + str(student_code_1[0])
            request.session['show'] = 'change grade'
        else:
            request.session['added'] = False
        user_details = User.objects.filter(type='STUDENT')
        return render(request, "accounts/teacher/teacher_exam_results.html",
                      {'page_title': page_title, 'grade_book': grade_book, 'student_data': student_data,
                       'school_detail': school_detail, 'theme_color': theme_colors, 'user_details': user_details})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    else:
        return redirect('teacher_login')


def payment(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        page_title = 'Dashboard - Payment'
        ids = Payment.objects.values_list('payment_code', flat=True)
        student_payment_details = StudentPaymentRecord.objects.filter(payment_code_id__in=set(ids),
                                                                      student_code_id=request.user.studentdetail.user_id)
        payment_list = Payment.objects.filter(payment_class=request.user.studentdetail.current_class,
                                              school_code_id=request.user.studentdetail.school_code_id)
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        return render(request, "accounts/student/payment.html", {'page_title': page_title, 'payment_list': payment_list,
                                                                 'school_detail': school_detail,
                                                                 'payment_details': student_payment_details,
                                                                 'theme_color': theme_colors})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def invoice(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        page_title = 'Dashboard - Invoice'
        ids = StudentPaymentRecord.objects.values_list('payment_code_id', flat=True).filter(
            student_code_id=request.user.studentdetail.user_id)
        payment_details = Payment.objects.filter(pk__in=set(ids),
                                                 school_code_id=request.user.studentdetail.school_code_id)
        invoice_details = StudentPaymentRecord.objects.filter(student_code_id=request.user.studentdetail.user_id)
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        return render(request, "accounts/student/invoice.html",
                      {'page_title': page_title, 'invoice_details': invoice_details,
                       'school_detail': school_detail,
                       'payment_details': payment_details, 'theme_color': theme_colors})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def textbook(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        page_title = 'Dashboard - Textbook'
        text_book = Textbook.objects.filter(school_code_id=request.user.studentdetail.school_code,
                                            textbook_class=request.user.studentdetail.current_class)
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        return render(request, "accounts/student/textbook.html", {'page_title': page_title, 'textbook': text_book,
                                                                  'school_detail': school_detail,
                                                                  'theme_color': theme_colors})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def calendar(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        page_title = 'Dashboard - Calendar'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        return render(request, "accounts/student/academic_calendar.html", {'page_title': page_title,
                                                                           'school_detail': school_detail,
                                                                           'theme_color': theme_colors})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def report_card(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        page_title = 'Dashboard - Report Card'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        return render(request, "accounts/student/report_card.html", {'page_title': page_title,
                                                                     'school_detail': school_detail,
                                                                     'theme_color': theme_colors})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def transcripts(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        page_title = 'Dashboard - Transcripts'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        return render(request, "accounts/student/transcript.html", {'page_title': page_title,
                                                                    'school_detail': school_detail,
                                                                    'theme_color': theme_colors})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def teacher_attendance(request):
    if request.user.is_authenticated and request.user.type == 'TEACHER':
        page_title = 'Dashboard - Attendance'
        school_detail = ListOfSchool.objects.filter(school_code=request.user.teacherdetail.school_code_id)
        student_list = StudentDetail.objects.filter(school_code=request.user.teacherdetail.school_code_id,
                                                    current_class=request.user.teacherdetail.class_teachers_class)
        all_user = User.objects.filter(type='STUDENT')
        attendance_stats = ClassAttendance.objects.filter(school_id=request.user.teacherdetail.school_code_id)
        attendance_one = ClassAttendance.objects.filter(school_id=request.user.teacherdetail.school_code_id,
                                                        date=attendance_dates['1'])
        attendance_two = ClassAttendance.objects.filter(school_id=request.user.teacherdetail.school_code_id,
                                                        date=attendance_dates['2'])
        attendance_three = ClassAttendance.objects.filter(school_id=request.user.teacherdetail.school_code_id,
                                                          date=attendance_dates['3'])
        attendance_four = ClassAttendance.objects.filter(school_id=request.user.teacherdetail.school_code_id,
                                                         date=attendance_dates['4'])
        attendance_five = ClassAttendance.objects.filter(school_id=request.user.teacherdetail.school_code_id,
                                                         date=attendance_dates['5'])
        if 'update_attendance' in request.GET:
            list_of_students = []
            # new_date = str(datetime.date.today().strftime('%m/%d/%Y'))
            # new_date_2 = str(datetime.date.today().strftime('%Y-%m-%d'))
            for student in student_list:
                list_of_students.append(student.student_code)
            for num in range(len(list_of_students)):
                student_attendance = request.GET.get(list_of_students[num] + '_' + str(attendance_dates['1']))
                student_attendance_2 = request.GET.get(list_of_students[num] + '_' + str(attendance_dates['2']))
                student_attendance_3 = request.GET.get(list_of_students[num] + '_' + str(attendance_dates['3']))
                student_attendance_4 = request.GET.get(list_of_students[num] + '_' + str(attendance_dates['4']))
                student_attendance_5 = request.GET.get(list_of_students[num] + '_' + str(attendance_dates['5']))
                print(student_attendance)
                print(student_attendance_3)
                # if student_attendance_5 == '5':
                #     print('lol')
                student_id = User.objects.filter(username=list_of_students[num]).values_list('id', flat=True)
                for ids in student_id:
                    student_id = ids

                if student_attendance:
                    # print('yes')
                    try:
                        ClassAttendance.objects.create(date=str(attendance_dates['1']), attendance=student_attendance,
                                                       school_id_id=request.user.teacherdetail.school_code_id,
                                                       student_id_id=student_id,
                                                       student_code=list_of_students[num]).save()
                    except IntegrityError:
                        if student_attendance != '5':
                            ClassAttendance.objects.filter(date=str(attendance_dates['1']),
                                                           school_id_id=request.user.teacherdetail.school_code_id,
                                                           student_id_id=student_id,
                                                           student_code=list_of_students[num]).update(
                                attendance=student_attendance)
                        # return redirect('teacher_attendance')
                if student_attendance_2:
                    try:
                        ClassAttendance.objects.create(date=str(attendance_dates['2']), attendance=student_attendance_2,
                                                       school_id_id=request.user.teacherdetail.school_code_id,
                                                       student_id_id=student_id,
                                                       student_code=list_of_students[num]).save()
                    except IntegrityError:
                        if student_attendance_2 != '5':
                            ClassAttendance.objects.filter(date=str(attendance_dates['2']),
                                                           school_id_id=request.user.teacherdetail.school_code_id,
                                                           student_id_id=student_id,
                                                           student_code=list_of_students[num]).update(
                                attendance=student_attendance_2)
                        # return redirect('teacher_attendance')

                if student_attendance_3:
                    # print('yes')
                    try:
                        ClassAttendance.objects.create(date=str(attendance_dates['3']), attendance=student_attendance_3,
                                                       school_id_id=request.user.teacherdetail.school_code_id,
                                                       student_id_id=student_id,
                                                       student_code=list_of_students[num]).save()
                    except IntegrityError:
                        if student_attendance_3 != '5':
                            ClassAttendance.objects.filter(date=str(attendance_dates['3']),
                                                           school_id_id=request.user.teacherdetail.school_code_id,
                                                           student_id_id=student_id,
                                                           student_code=list_of_students[num]).update(
                                attendance=student_attendance_3)
                        # return redirect('teacher_attendance')
                if student_attendance_4:
                    try:
                        ClassAttendance.objects.create(date=str(attendance_dates['4']), attendance=student_attendance_4,
                                                       school_id_id=request.user.teacherdetail.school_code_id,
                                                       student_id_id=student_id,
                                                       student_code=list_of_students[num]).save()
                    except IntegrityError:
                        if student_attendance_4 != '5':
                            ClassAttendance.objects.filter(date=str(attendance_dates['4']),
                                                           school_id_id=request.user.teacherdetail.school_code_id,
                                                           student_id_id=student_id,
                                                           student_code=list_of_students[num]).update(
                                attendance=student_attendance_4)
                        # return redirect('teacher_attendance')
                if student_attendance_5:
                    # print('yes')
                    try:
                        ClassAttendance.objects.create(date=str(attendance_dates['5']), attendance=student_attendance_5,
                                                       school_id_id=request.user.teacherdetail.school_code_id,
                                                       student_id_id=student_id,
                                                       student_code=list_of_students[num]).save()
                    except IntegrityError:
                        if student_attendance_5 != '5':
                            ClassAttendance.objects.filter(date=str(attendance_dates['5']),
                                                           school_id_id=request.user.teacherdetail.school_code_id,
                                                           student_id_id=student_id,
                                                           student_code=list_of_students[num]).update(
                                attendance=student_attendance_5)
                        # return redirect('teacher_attendance')
        return render(request, "accounts/teacher/attendance.html", {'page_title': page_title,
                                                                    'school_detail': school_detail,
                                                                    'theme_color': theme_colors,
                                                                    'student_list': student_list, 'all_user': all_user,
                                                                    'attendance_dates': attendance_dates,
                                                                    'attendance_stats': attendance_stats,
                                                                    'attendance_one': attendance_one,
                                                                    'attendance_two': attendance_two,
                                                                    'attendance_three': attendance_three,
                                                                    'attendance_four': attendance_four,
                                                                    'attendance_five': attendance_five})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    else:
        return redirect('teacher_login')


def student_attendance(request):
    if request.user.is_authenticated and request.user.type == 'STUDENT':
        page_title = 'Dashboard - Attendance'
        date_list = []
        school_detail = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
        all_dates = ClassAttendance.objects.filter(student_code=request.user).values_list('date', flat=True)
        # attendance_statistics = ClassAttendance.objects.filter(student_code=request.user).values_list('attendance', flat=True)
        attendance_statistics = ClassAttendance.objects.filter(student_code=request.user).order_by('date')
        for dates in all_dates:
            date_list.append(dates)
            # print(dates)

        return render(request, "accounts/student/attendance.html", {'page_title': page_title,
                                                                    'school_detail': school_detail,
                                                                    'theme_color': theme_colors,
                                                                    'date_list': date_list,
                                                                    'attendance_statistics': attendance_statistics
                                                                    })
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def navbar_settings(request):
    theme = request.POST.get('theme')
    if theme is not None and theme != '' and request.user.type == 'STUDENT':
        StudentDetail.objects.filter(user=request.user).update(theme_color=theme)
    elif theme is not None and theme != '' and request.user.type == 'TEACHER':
        TeacherDetail.objects.filter(user=request.user).update(theme_color=theme)
    elif theme is not None and theme != '' and request.user.type == 'ADMIN':
        AdminDetail.objects.filter(user=request.user).update(theme_color=theme)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def admin_login(request):
    page_title = 'Utron - Admin Login'
    if request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        request.session['login_username'] = username
        user = authenticate(request, username=username, password=password)
        if user is not None and user.type == "ADMIN":
            login(request, user)
            # page_title = 'Utron - Dashboard'
            # return render(request, "accounts/admin/admin_dashboard.html", {'page_title': page_title})
            return redirect('admin_dashboard')
        else:
            request.session['error'] = "Incorrect username or password"
            # messages.info(request, "Incorrect email or password")
            return render(request, "accounts/admin_login.html", {'page_title': page_title})
    request.session['error'] = False
    return render(request, "accounts/admin_login.html", {'page_title': page_title})


def admin_dashboard(request):
    page_title = 'Utron - Dashboard'
    if request.user.is_authenticated and request.user.type == "ADMIN":
        return render(request, "accounts/admin/admin_dashboard.html",
                      {'page_title': page_title, 'theme_color': theme_colors})
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('admin_login')


def admin_logout(request):
    logout(request)
    return redirect('admin_login')


def admin_new_student(request):
    page_title = 'Dashboard - New Student'
    if request.user.is_authenticated and request.user.type == "ADMIN":
        if 'step-one' in request.GET:
            first_name = request.GET.get('firstname')
            # other_names = request.GET.get('other_names')
            last_name = request.GET.get('lastname')
            email = request.GET.get('email')
            # password = request.GET.get('password')
            birth_date = request.GET.get('birth-date')
            request.session['student_birth_date'] = birth_date
            birth_date_2 = str(birth_date)
            password = str(last_name).lower() + birth_date_2[2:4]
            # first_name += " " + other_names
            user = User.objects.create_user(first_name=first_name.title(), last_name=last_name.title(),
                                            username=request.session['new_student_code'], password=password,
                                            email=email.lower())
            user.save()
            request.session['step'] = 'two'
        elif 'step-two' in request.GET:
            student_id = User.objects.filter(username=request.session['new_student_code']).values_list('id', flat=True)
            for ids in student_id:
                student_id = str(ids)
            student_code = request.session['new_student_code']
            school = request.GET.get('school')
            request.session['school'] = school
            education_id = request.GET.get('education-id')
            fathers_name = request.GET.get('fathers-name').title()
            mothers_name = request.GET.get('mothers-name').title()
            mothers_maiden_name = request.GET.get('mothers-maiden-name').title()
            current_class = request.GET.get('current-class')
            request.session['current_class'] = current_class
            current_term = request.GET.get('current-term')
            request.session['current_term'] = current_term
            sex = request.GET.get('sex')
            # birth_date = request.GET.get('birth-date')
            birth_date = request.session['student_birth_date']
            birth_place = request.GET.get('birth-place')
            state_of_origin = request.GET.get('state-of-origin')
            email_2 = request.GET.get('email-2')
            phone_number = request.GET.get('phone-number')
            phone_number_2 = request.GET.get('phone-number-2')
            address = request.GET.get('address').title()
            postal_code = request.GET.get('postal-code')
            city = request.GET.get('city').title()
            state = request.GET.get('state').title()
            nationality = request.GET.get('nationality').title()
            date_of_admission = request.GET.get('date-of-admission')
            dormitory = request.GET.get('dormitory')
            active_terms = request.GET.get('active-terms')
            terms_remaining = request.GET.get('terms-remaining')
            graduation_date = request.GET.get('graduation-date')
            registration_number = request.GET.get('registration-number')
            try:
                user = StudentDetail.objects.create(user_id=student_id, student_code=student_code,
                                                    current_class=current_class,
                                                    current_term=current_term, sex=sex, birth_date=birth_date,
                                                    birth_place=birth_place, state_of_origin=state_of_origin,
                                                    email_address_2=email_2, phone_number=phone_number,
                                                    phone_number_2=phone_number_2,
                                                    postal_code=postal_code, address=address, city=city, state=state,
                                                    nationality=nationality,
                                                    fathers_name=fathers_name, mothers_name=mothers_name,
                                                    mothers_maiden_name=mothers_maiden_name,
                                                    date_of_admission=date_of_admission, dormitory=dormitory,
                                                    student_status='ACTIVE',
                                                    no_active_terms=active_terms, no_terms_remaining=terms_remaining,
                                                    expected_graduation=graduation_date,
                                                    registration_number=registration_number, education_id=education_id,
                                                    school_code_id=school, admin=request.user.username)
                user.save()
                StudentSchoolRecord.objects.create(user_id=student_id, student_code=student_code, school_code_id=school,
                                                   no_active_terms=active_terms, date_of_admission=date_of_admission,
                                                   registration_number=registration_number,
                                                   student_status='ACTIVE').save()
                request.session['step'] = 'three'
                request.session['student_birth_date'] = False
            except IntegrityError:
                return redirect('admin_add_new_student')
        elif 'step-three' in request.GET:
            language_subject = request.GET.get('language-subject')
            sss_subjects = request.GET.getlist('subjects')
            compulsory_subjects = ['English Language', 'Mathematics', 'Civic Education']
            student_id = User.objects.filter(username=request.session['new_student_code']).values_list('id', flat=True)
            for ids in student_id:
                student_id = str(ids)
            try:
                if 'J' in str(request.session['current_class']):
                    user = GradeBook.objects.create(school_code_id=request.session['school'],
                                                    subject=language_subject.upper(),
                                                    student_class=request.session['current_class'],
                                                    term=request.session['current_term'], student_code_id=student_id
                                                    )
                    user.save()
                    for i in range(len(jss_subjects)):
                        user = GradeBook.objects.create(school_code_id=request.session['school'],
                                                        subject=jss_subjects[i + 1].upper(),
                                                        student_class=request.session['current_class'],
                                                        term=request.session['current_term'],
                                                        student_code_id=student_id
                                                        )
                        user.save()
                else:
                    for i in range(len(compulsory_subjects)):
                        user = GradeBook.objects.create(school_code_id=request.session['school'],
                                                        subject=compulsory_subjects[i].upper(),
                                                        student_class=request.session['current_class'],
                                                        term=request.session['current_term'],
                                                        student_code_id=student_id
                                                        )
                        user.save()
                    for i in range(len(sss_subjects)):
                        user = GradeBook.objects.create(school_code_id=request.session['school'],
                                                        subject=sss_subjects[i].upper(),
                                                        student_class=request.session['current_class'],
                                                        term=request.session['current_term'],
                                                        student_code_id=student_id
                                                        )
                        user.save()
                request.session['step'] = 'four'
            except IntegrityError:
                return redirect('admin_add_new_student')
        else:
            request.session['current_class'] = False
            request.session['step'] = False

            # student code generator
            def id_generator(size=6):
                return random.choice(string.ascii_uppercase) + ''.join(
                    random.choice(string.ascii_uppercase + string.digits) for _ in range(size)) \
                       + random.choice(string.ascii_uppercase)

            while True:
                try:
                    new_student_code = id_generator()
                    codes = StudentDetail.objects.filter(student_code=new_student_code)
                    if len(codes) == 0:
                        request.session['new_student_code'] = new_student_code
                        break
                except IntegrityError:
                    pass

        list_of_schools = ListOfSchool.objects.filter()
        return render(request, "accounts/admin/admin_add_student.html",
                      {'page_title': page_title, 'theme_color': theme_colors, 'list_of_schools': list_of_schools})
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('admin_login')


def admin_new_teacher(request):
    page_title = 'Dashboard - New Teacher'
    if request.user.is_authenticated and request.user.type == "ADMIN":
        request.session['step'] = False
        request.session['teacher_step'] = False
        if 'step-one' in request.GET:
            try:
                first_name = request.GET.get('firstname')
                # other_names = request.GET.get('other_names')
                last_name = request.GET.get('lastname')
                email = request.GET.get('email')
                # password = request.GET.get('password')
                birth_date = request.GET.get('birth-date')
                request.session['teacher_birth_date'] = birth_date
                birth_date_2 = str(birth_date)
                password = str(last_name).lower() + birth_date_2[2:4]
                # first_name += " " + other_names
                user = User.objects.create_user(first_name=first_name.title(), last_name=last_name.title(),
                                                username=request.session['new_teacher_code'], password=password,
                                                email=email.lower(), type='TEACHER')
                user.save()
                request.session['step'] = 'two'
                request.session['teacher_step'] = 'two'
            except IntegrityError:
                pass
        elif 'step-two' in request.GET:
            teacher_id = User.objects.filter(username=request.session['new_teacher_code']).values_list('id', flat=True)
            for ids in teacher_id:
                teacher_id = str(ids)
            teacher_code = request.session['new_teacher_code']
            school = request.GET.get('school')
            request.session['school'] = school
            national_id = request.GET.get('national-id')
            sex = request.GET.get('sex')
            # birth_date = request.GET.get('birth-date')
            birth_date = request.session['teacher_birth_date']
            state_of_origin = request.GET.get('state-of-origin')
            class_teacher = request.GET.get('class-teacher')
            if class_teacher == 'NO':
                class_teacher_class = None
            else:
                class_teacher_class = request.GET.get('class-teacher-class')
            email_2 = request.GET.get('email-2')
            phone_number = request.GET.get('phone-number')
            phone_number_2 = request.GET.get('phone-number-2')
            address = request.GET.get('address').title()
            postal_code = request.GET.get('postal-code')
            city = request.GET.get('city').title()
            state = request.GET.get('state').title()
            nationality = request.GET.get('nationality').title()
            employment_date = request.GET.get('employment-date')
            active_terms = request.GET.get('active-terms')
            try:
                user = TeacherDetail.objects.create(user_id=teacher_id, teacher_code=teacher_code, sex=sex,
                                                    birth_date=birth_date, state_of_origin=state_of_origin,
                                                    class_teacher=class_teacher, email_address_2=email_2,
                                                    phone_number=phone_number, phone_number_2=phone_number_2,
                                                    postal_code=postal_code, address=address, city=city, state=state,
                                                    nationality=nationality, employment_start_date=employment_date,
                                                    no_active_terms=active_terms, national_id_card_no=national_id,
                                                    school_code_id=school, class_teachers_class=class_teacher_class,
                                                    admin=request.user.username)
                user.save()
                TeacherSchoolRecord.objects.create(user_id=teacher_id, teacher_code=teacher_code, school_code_id=school,
                                                   no_active_terms=active_terms, date_of_employment=employment_date,
                                                   teacher_status='ACTIVE').save()
                request.session['teacher_birth_date'] = False
            except IntegrityError:
                return redirect('admin_add_new_student')
            request.session['step'] = 'three'
            request.session['teacher_step'] = 'three'
        elif 'step-three' in request.GET:
            teacher_id = User.objects.filter(username=request.session['new_teacher_code']).values_list('id', flat=True)
            for ids in teacher_id:
                teacher_id = str(ids)

            subject_1 = request.GET.get('subject-1')
            class_1 = request.GET.get('class-1')
            subject_2 = request.GET.get('subject-2')
            class_2 = request.GET.get('class-2')
            subject_3 = request.GET.get('subject-3')
            class_3 = request.GET.get('class-3')
            subject_4 = request.GET.get('subject-4')
            class_4 = request.GET.get('class-4')
            subject_5 = request.GET.get('subject-5')
            class_5 = request.GET.get('class-5')

            try:
                TeacherDetail.objects.filter(user_id=teacher_id).update(subject_1=subject_1, subject_2=subject_2,
                                                                        subject_3=subject_3,
                                                                        subject_4=subject_4, subject_5=subject_5,
                                                                        subject_class_1=class_1,
                                                                        subject_class_2=class_2,
                                                                        subject_class_3=class_3,
                                                                        subject_class_4=class_4,
                                                                        subject_class_5=class_5)
                request.session['step'] = 'four'
                request.session['teacher_step'] = 'four'
            except IntegrityError:
                return redirect('admin_add_new_teacher')
        else:
            request.session['current_class'] = False

            # student code generator
            def id_generator(size=6):
                return random.choice(string.ascii_uppercase) + ''.join(
                    random.choice(string.ascii_uppercase + string.digits) for _ in range(size)) \
                       + random.choice(string.ascii_uppercase)

            while True:
                try:
                    new_teacher_code = id_generator()
                    codes = StudentDetail.objects.filter(student_code=new_teacher_code)
                    if len(codes) == 0:
                        request.session['new_teacher_code'] = new_teacher_code
                        break
                except IntegrityError:
                    pass

        list_of_schools = ListOfSchool.objects.filter()
        return render(request, "accounts/admin/admin_add_teacher.html",
                      {'page_title': page_title, 'theme_color': theme_colors, 'list_of_schools': list_of_schools})
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('admin_login')


def add_class_schedule(request):
    page_title = 'Dashboard - Class Schedule'
    list_of_schools = ListOfSchool.objects.filter()
    if request.user.is_authenticated and request.user.type == "ADMIN":
        request.session['success'] = False
        request.session['schedule_error'] = False
        if 'submit-schedule' in request.GET:
            try:
                student_class = request.GET.get('class')
                start_time = request.GET.get('time')
                school = request.GET.get('school')
                monday = request.GET.get('monday').upper()
                tuesday = request.GET.get('tuesday').upper()
                wednesday = request.GET.get('wednesday').upper()
                thursday = request.GET.get('thursday').upper()
                friday = request.GET.get('friday').upper()
                user = ClassSchedule.objects.create(student_class=student_class, class_start_time=start_time,
                                                    school_code_id=school, monday=monday, tuesday=tuesday,
                                                    wednesday=wednesday,
                                                    thursday=thursday, friday=friday)
                user.save()
                request.session['success'] = True
            except IntegrityError:
                request.session['schedule_error'] = True
                return render(request, "accounts/admin/admin_add_class_schedule.html",
                              {'page_title': page_title, 'theme_color': theme_colors,
                               'list_of_schools': list_of_schools})
        return render(request, "accounts/admin/admin_add_class_schedule.html",
                      {'page_title': page_title, 'theme_color': theme_colors, 'list_of_schools': list_of_schools})
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('admin_login')


def modify_student(request):
    page_title = 'Dashboard - Student Details'
    list_of_schools = ListOfSchool.objects.filter()
    if request.user.is_authenticated and request.user.type == "ADMIN":
        student_list = []
        request.session['show_modify_details'] = False
        student_detail_1 = []
        student_detail_2 = []
        if 'get-student-list' in request.GET:
            request.session['list_button'] = False
            school = request.GET.get('school')
            request.session['modify-school'] = school
            current_class = request.GET.get('current-class')
            request.session['modify-class'] = current_class
            student_list = StudentDetail.objects.filter(current_class=current_class, school_code_id=school)
            if len(student_list) > 0:
                request.session['list_button'] = True
            request.session['list_class'] = current_class
            request.session['list_school'] = school
        elif 'get-student-details' in request.GET:
            user_id = request.GET.get('student')
            request.session['show_modify_details'] = True
            student_list = StudentDetail.objects.filter(current_class=request.session['modify-class'],
                                                        school_code_id=request.session['modify-school'])
            student_detail_1 = User.objects.filter(id=user_id)
            student_detail_2 = StudentDetail.objects.filter(user_id=user_id)
        else:
            request.session['list_button'] = False
            request.session['list_class'] = False
            request.session['list_school'] = False
        return render(request, "accounts/admin/admin_modify_student.html",
                      {'page_title': page_title, 'theme_color': theme_colors, 'list_of_schools': list_of_schools,
                       'student_list': student_list, 'student_detail_1': student_detail_1,
                       'student_detail_2': student_detail_2})
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('admin_login')


def modify_teacher(request):
    page_title = 'Dashboard - Teacher Details'
    list_of_schools = ListOfSchool.objects.filter()
    if request.user.is_authenticated and request.user.type == "ADMIN":
        teacher_list = []
        request.session['show_modify_details'] = False
        request.session['modify_teacher_success'] = False
        teacher_detail_1 = []
        teacher_detail_2 = []
        user_details = User.objects.filter(type='TEACHER')
        if 'get-teacher-list' in request.GET:
            request.session['list_button'] = False
            school = request.GET.get('school')
            request.session['modify-school'] = school
            teacher_list = TeacherDetail.objects.filter(school_code_id=school)
            if len(teacher_list) > 0:
                request.session['list_button'] = True
            request.session['list_school'] = school
        elif 'get-teacher-details' in request.GET:
            user_id = request.GET.get('student')
            request.session['modify_teacher_id'] = user_id
            request.session['show_modify_details'] = True
            teacher_list = TeacherDetail.objects.filter(school_code_id=request.session['modify-school'])
            teacher_detail_1 = User.objects.filter(id=user_id)
            teacher_detail_2 = TeacherDetail.objects.filter(user_id=user_id)
        elif 'save-teacher-details' in request.GET:
            email = request.GET.get('email')
            school = request.GET.get('school')
            email_2 = request.GET.get('email-2')
            phone_number = request.GET.get('phone-number')
            phone_number_2 = request.GET.get('phone-number-2')
            address = request.GET.get('address')
            postal_code = request.GET.get('postal-code')
            city = request.GET.get('city')
            state = request.GET.get('state')
            active_terms = request.GET.get('active-terms')
            # print(request.session['modify_teacher_id'], email.lower(), school, email_2, phone_number,
            #       phone_number_2, address.title(), postal_code, city.title(), state.title(), active_terms)
            User.objects.filter(id=request.session['modify_teacher_id']).update(email=email.lower())
            TeacherDetail.objects.filter(user_id=request.session['modify_teacher_id']).update(email_address_2=email_2,
                                                                                              school_code_id=school,
                                                                                              phone_number=phone_number,
                                                                                              phone_number_2=phone_number_2,
                                                                                              address=address.title(),
                                                                                              postal_code=postal_code,
                                                                                              city=city.title(),
                                                                                              state=state.title(),
                                                                                              no_active_terms=active_terms)
            request.session['modify_teacher_success'] = True
        else:
            request.session['list_button'] = False
            request.session['list_school'] = False
        return render(request, "accounts/admin/admin_modify_teacher.html",
                      {'page_title': page_title, 'theme_color': theme_colors, 'list_of_schools': list_of_schools,
                       'teacher_list': teacher_list, 'teacher_detail_1': teacher_detail_1,
                       'teacher_detail_2': teacher_detail_2, 'user_details': user_details})
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('admin_login')


def reset_password(request):
    page_title = 'Dashboard - Reset Password'
    list_of_schools = ListOfSchool.objects.filter()
    if request.user.is_authenticated and request.user.type == "ADMIN":
        teacher_list = []
        teacher_detail_1 = []
        student_list = []
        student_detail_1 = []
        request.session['modify_teacher_success'] = False
        request.session['show_modify_details'] = False
        request.session['reset_password_success'] = False
        request.session['reset_teacher_password'] = False
        if 'get-student-list' in request.GET:
            request.session['list_button'] = False
            school = request.GET.get('school')
            request.session['reset_student_school'] = school
            current_class = request.GET.get('current-class')
            request.session['reset_student_class'] = current_class
            student_list = StudentDetail.objects.filter(current_class=current_class, school_code_id=school)
            if len(student_list) > 0:
                request.session['list_button'] = True
            request.session['list_class'] = current_class
            request.session['list_school'] = school
            request.session['reset_student_password'] = True
        elif 'reset-student-password' in request.GET:
            dob = ''
            user_id = request.GET.get('student')
            student_last_name = User.objects.filter(id=user_id).values_list('last_name', flat=True).order_by()
            for i in student_last_name:
                student_last_name = str(i).lower().strip()
            student_dob = StudentDetail.objects.filter(user_id=user_id).values_list('birth_date', flat=True).order_by()
            for i in student_dob:
                dob = str(i)
            new_password = student_last_name + dob[2:4]
            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()
            student_list = StudentDetail.objects.filter(current_class=request.session['reset_student_class'],
                                                        school_code_id=request.session['reset_student_school'])
            student_detail_1 = User.objects.filter(id=user_id)
            request.session['reset_password_success'] = True
            request.session['reset_student_password'] = True
        elif 'get-teacher-list' in request.GET:
            request.session['list_button'] = False
            school = request.GET.get('school')
            request.session['reset-teacher-school'] = school
            teacher_list = TeacherDetail.objects.filter(school_code_id=school)
            if len(teacher_list) > 0:
                request.session['list_button'] = True
            request.session['list_school'] = school
            request.session['reset_teacher_password'] = True
        elif 'reset-password-teacher' in request.GET:
            dob = ''
            user_id = request.GET.get('teachers')
            teacher_last_name = User.objects.filter(id=user_id).values_list('last_name', flat=True).order_by()
            for i in teacher_last_name:
                teacher_last_name = str(i).lower().strip()
            teacher_dob = TeacherDetail.objects.filter(user_id=user_id).values_list('birth_date', flat=True).order_by()
            for i in teacher_dob:
                dob = str(i)
            new_password = teacher_last_name + dob[2:4]
            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()
            # request.session['modify_teacher_id'] = user_id
            request.session['reset_password_success'] = True
            teacher_list = TeacherDetail.objects.filter(school_code_id=request.session['reset-teacher-school'])
            teacher_detail_1 = User.objects.filter(id=user_id)
            request.session['reset_teacher_password'] = True
        else:
            request.session['list_button'] = False
            request.session['list_class'] = False
            request.session['list_school'] = False

        return render(request, "accounts/admin/admin_reset_password.html",
                      {'page_title': page_title, 'theme_color': theme_colors, 'list_of_schools': list_of_schools,
                       'student_list': student_list, 'student_detail_1': student_detail_1, 'teacher_list': teacher_list,
                       'teacher_detail_1': teacher_detail_1})
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('admin_login')


def admin_add_payment(request):
    page_title = 'Dashboard - Add Payment'
    list_of_schools = ListOfSchool.objects.filter()
    if request.user.is_authenticated and request.user.type == "ADMIN":
        request.session['add_school_payment'] = False
        if request.method == "POST":
            school = request.POST.get('school')
            payment_name = request.POST.get('payment_name').upper()
            payment_class = request.POST.get('payment_class')
            term = request.POST.get('term')
            amount = request.POST.get('amount')
            deadline = request.POST.get('deadline')
            breakdown = request.FILES['breakdown']
            now = datetime.datetime.now()
            payment_code = payment_name + '-' + payment_class + '-' + term + '-' + str(now.year)
            try:
                Payment.objects.create(school_code_id=school, payment_code=payment_code, payment_class=payment_class,
                                       term=term, name=payment_name, amount=amount, deadline=deadline,
                                       breakdown=breakdown)
                request.session['add_school_payment'] = True
            except IntegrityError:
                return redirect('admin_add_payment')
        return render(request, "accounts/admin/admin_add_payment.html",
                      {'page_title': page_title, 'theme_color': theme_colors, 'list_of_schools': list_of_schools})
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('admin_login')


def admin_add_student_payment(request):
    page_title = 'Dashboard - Student Payment Record'
    list_of_schools = ListOfSchool.objects.filter()
    if request.user.is_authenticated and request.user.type == "ADMIN":
        request.session['add_student_payment'] = False
        if request.method == "POST":
            school = request.POST.get('school')
            payment_code = request.POST.get('payment_code')
            payment_date = request.POST.get('payment_date')
            student_code = request.POST.get('student_code')
            invoice_number = request.POST.get('invoice_number')
            invoice_file = request.FILES['invoice']
            try:
                StudentPaymentRecord.objects.create(school_code_id=school, payment_code_id=payment_code,
                                                    student_code_id=student_code, payment_date=payment_date,
                                                    invoice_number=invoice_number, invoice=invoice_file,
                                                    status='ACTIVE')
                request.session['add_student_payment'] = True
            except IntegrityError:
                return redirect('admin_add_student_payment')
        payment_codes = Payment.objects.all()
        student_list = StudentDetail.objects.all()
        return render(request, "accounts/admin/admin_add_student_payment_record.html",
                      {'page_title': page_title, 'theme_color': theme_colors, 'list_of_schools': list_of_schools,
                       'payment_codes': payment_codes, "student_list": student_list})
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('admin_login')


def admin_add_textbook(request):
    page_title = 'Dashboard - Add Textbook'
    list_of_schools = ListOfSchool.objects.filter()
    if request.user.is_authenticated and request.user.type == "ADMIN":
        request.session['textbook_added'] = False
        if request.method == "POST":
            school = request.POST.get('school')
            textbook_class = request.POST.get('class')
            textbook_file = request.FILES['textbook']
            try:
                Textbook.objects.create(school_code_id=school, textbook_class=textbook_class, textbook=textbook_file)
                request.session['textbook_added'] = True
            except IntegrityError:
                return redirect('admin_add_textbook')
        return render(request, "accounts/admin/admin_add_textbook.html",
                      {'page_title': page_title, 'theme_color': theme_colors, 'list_of_schools': list_of_schools})
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('admin_login')


def admin_modify_class_schedule(request):
    page_title = 'Dashboard - Modify Class Schedule'
    list_of_schools = ListOfSchool.objects.filter()
    if request.user.is_authenticated and request.user.type == "ADMIN":
        request.session['edit_class_schedule'] = False
        class_schedule = []
        start_times = ClassSchedule.objects.all()
        request.session['success'] = False
        if 'get-schedule' in request.GET:
            request.session['edit_class_schedule'] = True
            school = request.GET.get('school')
            request.session['class_schedule_school'] = school
            student_class = request.GET.get('student_class')
            start_time = request.GET.get('start_time')
            # if start_time[-4:] == 'p.m.' and start_time[:2].strip() != '12':
            #     start_time = str(int(start_time[:2]) + 12) + ':00'
            # elif start_time[-4:] == 'a.m.':
            #     start_time = start_time[:2].strip() + ':00'
            # elif start_time[:2].strip() == '12':
            #     start_time = start_time[:2].strip() + ':00'
            class_schedule = ClassSchedule.objects.filter(school_code_id=school, class_start_time=start_time,
                                                          student_class=student_class)
        elif 'update-schedule' in request.GET:
            student_class_2 = request.GET.get('class')
            start_time_2 = request.GET.get('time')
            school_2 = request.GET.get('school_2')
            monday = request.GET.get('monday').upper()
            tuesday = request.GET.get('tuesday').upper()
            wednesday = request.GET.get('wednesday').upper()
            thursday = request.GET.get('thursday').upper()
            friday = request.GET.get('friday').upper()
            # if start_time_2[-4:] == 'p.m.' and start_time_2[:2].strip() != '12':
            #     start_time_2 = str(int(start_time_2[:2]) + 12) + ':00'
            # elif start_time_2[-4:] == 'a.m.':
            #     start_time_2 = start_time_2[:2].strip() + ':00'
            # elif start_time_2[:2].strip() == '12':
            #     start_time_2 = start_time_2[:2].strip() + ':00'
            ClassSchedule.objects.filter(school_code_id=school_2, class_start_time=start_time_2,
                                         student_class=student_class_2).update(monday=monday, tuesday=tuesday,
                                                                               wednesday=wednesday, thursday=thursday,
                                                                               friday=friday)
            request.session['success'] = True
        return render(request, "accounts/admin/admin_modify_class_schedule.html",
                      {'page_title': page_title, 'theme_color': theme_colors, 'list_of_schools': list_of_schools,
                       'start_times': start_times, 'class_schedule': class_schedule})
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('admin_login')


def admin_modify_payment(request):
    page_title = 'Dashboard - Modify Payment'
    list_of_schools = ListOfSchool.objects.filter()
    if request.user.is_authenticated and request.user.type == "ADMIN":
        payment_details = []
        request.session['payment_details'] = False
        request.session['success'] = False
        if 'get-payments' in request.GET:
            school = request.GET.get('school')
            request.session['modify_payment_school'] = school
            payment_code = request.GET.get('payment_codes')
            payment_details = Payment.objects.filter(school_code_id=school, payment_code=payment_code)
            request.session['payment_details'] = True
        elif 'update_payment' in request.GET:
            school = request.GET.get('school_2')
            payment_code = request.GET.get('payment_code_1')
            amount = request.GET.get('amount')
            deadline = request.GET.get('deadline')
            Payment.objects.filter(school_code_id=school, payment_code=payment_code).update(amount=amount,
                                                                                            deadline=deadline)
            request.session['success'] = True
        payment_codes = Payment.objects.all()
        return render(request, "accounts/admin/admin_modify_payment.html",
                      {'page_title': page_title, 'theme_color': theme_colors, 'list_of_schools': list_of_schools,
                       'payment_codes': payment_codes, 'payment_details': payment_details})
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('admin_login')


def admin_modify_textbook(request):
    page_title = 'Dashboard - Modify Textbook'
    list_of_schools = ListOfSchool.objects.filter()
    if request.user.is_authenticated and request.user.type == "ADMIN":
        request.session['textbook_added'] = False
        if request.method == "POST":
            school = request.POST.get('school')
            textbook_class = request.POST.get('class')
            m = Textbook.objects.get(school_code_id=school, textbook_class=textbook_class)
            m.textbook = request.FILES['textbook']
            m.save()
            request.session['textbook_added'] = True
        textbooks = Textbook.objects.all()
        return render(request, "accounts/admin/admin_modify_textbook.html",
                      {'page_title': page_title, 'theme_color': theme_colors, 'list_of_schools': list_of_schools,
                       'textbooks': textbooks})
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('admin_login')


def modify_student_class(request):
    page_title = 'Dashboard - Student Class'
    list_of_schools = ListOfSchool.objects.filter()
    if request.user.is_authenticated and request.user.type == "ADMIN":
        student_list = []
        request.session['show_modify_details'] = False
        student_detail_1 = []
        student_detail_2 = []
        if 'get-student-list' in request.GET:
            request.session['list_button'] = False
            school = request.GET.get('school')
            request.session['modify-school'] = school
            current_class = request.GET.get('current-class')
            request.session['modify-class'] = current_class
            student_list = StudentDetail.objects.filter(current_class=current_class, school_code_id=school)
            if len(student_list) > 0:
                request.session['list_button'] = True
            request.session['list_class'] = current_class
            request.session['list_school'] = school
        elif 'get-student-details' in request.GET:
            user_id = request.GET.get('student')
            request.session['show_modify_details'] = True
            student_list = StudentDetail.objects.filter(current_class=request.session['modify-class'],
                                                        school_code_id=request.session['modify-school'])
            student_detail_1 = User.objects.filter(id=user_id)
            student_detail_2 = StudentDetail.objects.filter(user_id=user_id)
        else:
            request.session['list_button'] = False
            request.session['list_class'] = False
            request.session['list_school'] = False
        return render(request, "accounts/admin/admin_modify_student_class.html",
                      {'page_title': page_title, 'theme_color': theme_colors, 'list_of_schools': list_of_schools,
                       'student_list': student_list, 'student_detail_1': student_detail_1,
                       'student_detail_2': student_detail_2})
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('admin_login')


def admin_modify_subjects_taught(request):
    page_title = 'Dashboard - Modify Subjects Taught'
    list_of_schools = ListOfSchool.objects.filter()
    if request.user.is_authenticated and request.user.type == "ADMIN":
        teacher_list = []
        request.session['show_modify_details'] = False
        request.session['modify_teacher_success'] = False
        teacher_detail_1 = []
        teacher_detail_2 = []
        user_details = User.objects.filter(type='TEACHER')
        if 'get-teacher-list' in request.GET:
            request.session['list_button'] = False
            school = request.GET.get('school')
            request.session['modify-school'] = school
            teacher_list = TeacherDetail.objects.filter(school_code_id=school)
            if len(teacher_list) > 0:
                request.session['list_button'] = True
            request.session['list_school'] = school
        elif 'get-teacher-details' in request.GET:
            user_id = request.GET.get('student')
            request.session['modify_teacher_id'] = user_id
            request.session['show_modify_details'] = True
            teacher_list = TeacherDetail.objects.filter(school_code_id=request.session['modify-school'])
            teacher_detail_1 = User.objects.filter(id=user_id)
            teacher_detail_2 = TeacherDetail.objects.filter(user_id=user_id)
        elif 'save-teacher-details' in request.GET:
            subject_1 = request.GET.get('subject-1')
            subject_2 = request.GET.get('subject-2')
            subject_3 = request.GET.get('subject-3')
            subject_4 = request.GET.get('subject-4')
            subject_5 = request.GET.get('subject-5')
            subject_class_1 = request.GET.get('class-1')
            subject_class_2 = request.GET.get('class-2')
            subject_class_3 = request.GET.get('class-3')
            subject_class_4 = request.GET.get('class-4')
            subject_class_5 = request.GET.get('class-5')
            # print(subject_1, subject_2, subject_3, subject_4, subject_5, subject_class_1, subject_class_2,
            #       subject_class_3, subject_class_4, subject_class_5)
            TeacherDetail.objects.filter(user_id=request.session['modify_teacher_id']).update(subject_1=subject_1,
                                                                                              subject_2=subject_2,
                                                                                              subject_3=subject_3,
                                                                                              subject_4=subject_4,
                                                                                              subject_5=subject_5,
                                                                                              subject_class_1=subject_class_1,
                                                                                              subject_class_2=subject_class_2,
                                                                                              subject_class_3=subject_class_3,
                                                                                              subject_class_4=subject_class_4,
                                                                                              subject_class_5=subject_class_5)
            request.session['modify_teacher_success'] = True
        else:
            request.session['list_button'] = False
            request.session['list_school'] = False
        return render(request, "accounts/admin/admin_modify_subjects_taught.html",
                      {'page_title': page_title, 'theme_color': theme_colors, 'list_of_schools': list_of_schools,
                       'teacher_list': teacher_list, 'teacher_detail_1': teacher_detail_1,
                       'teacher_detail_2': teacher_detail_2, 'user_details': user_details})
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('admin_login')


def student_change_password(request):
    page_title = 'Dashboard - Change Password'
    list_of_schools = ListOfSchool.objects.filter(school_code=request.user.studentdetail.school_code_id)
    if request.user.is_authenticated and request.user.type == "STUDENT":
        request.session['password_ok'] = False
        request.session['error'] = False
        request.session['password_change_successful'] = False
        if 'verify-password' in request.GET:
            current_password = request.GET.get('current_password')
            user = authenticate(request, username=request.user, password=current_password)
            if user is not None:
                request.session['password_ok'] = True
            else:
                request.session['error'] = 'Incorrect Password!'
        elif 'change-password' in request.GET:
            new_password = request.GET.get('new_password')
            new_password_2 = request.GET.get('new_password_2')
            if new_password == new_password_2:
                user = User.objects.get(username=request.user)
                user.set_password(new_password)
                user.save()
                request.session['password_change_successful'] = 'Password Change Successful'
            else:
                request.session['password_ok'] = True
                request.session['error'] = 'Passwords do not Match!'
        return render(request, "accounts/student/change_password.html",
                      {'page_title': page_title, 'theme_color': theme_colors, 'school_detail': list_of_schools})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "TEACHER":
        return redirect('teacher_dashboard')
    else:
        return redirect('student_login')


def teacher_change_password(request):
    page_title = 'Dashboard - Change Password'
    list_of_schools = ListOfSchool.objects.filter()
    if request.user.is_authenticated and request.user.type == "TEACHER":
        request.session['password_ok'] = False
        request.session['error'] = False
        request.session['password_change_successful'] = False
        if 'verify-password' in request.GET:
            current_password = request.GET.get('current_password')
            user = authenticate(request, username=request.user, password=current_password)
            if user is not None:
                request.session['password_ok'] = True
            else:
                request.session['error'] = 'Incorrect Password!'
        elif 'change-password' in request.GET:
            new_password = request.GET.get('new_password')
            new_password_2 = request.GET.get('new_password_2')
            if new_password == new_password_2:
                user = User.objects.get(username=request.user)
                user.set_password(new_password)
                user.save()
                request.session['password_change_successful'] = 'Password Change Successful'
            else:
                request.session['password_ok'] = True
                request.session['error'] = 'Passwords do not Match!'
        return render(request, "accounts/teacher/teacher_change_password.html",
                      {'page_title': page_title, 'theme_color': theme_colors, 'school_detail': list_of_schools})
    elif request.user.is_authenticated and request.user.type == "ADMIN":
        return redirect('admin_dashboard')
    elif request.user.is_authenticated and request.user.type == "STUDENT":
        return redirect('student_dashboard')
    else:
        return redirect('teacher_login')
