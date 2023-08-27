from django.urls import path
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path("", views.other.index),
    path("chat/", views.other.chat),

    path("users/list/", views.administration.users_list),
    path("users/list/<str:role>", views.administration.users_list),
    path("users/create/", views.administration.user_create, name="create_user"),
    path("users/<int:id>/edit/", views.administration.edit_user),
    path("users/data/<int:id>", views.administration.user_data),
    path("users/<int:id>/view/", views.administration.view_user),
    path("users/<int:user>/login/", views.administration.login_admin_user),
    path("users/<int:user>/avatar/remove", views.administration.avatar_remove),
    path("events/<int:id>/view/", views.aam.events_view),
    path("events/category/list/", views.admin.category_list, name="category_list"),
    path("events/category/<int:id>/edit/", views.admin.category_edit),
    path("events/<int:id>/accept/<int:user>", views.aam.event_accept_user),
    path("events/<int:id>/reject/<int:user>", views.aam.event_reject_user),
    path("events/<int:id>/add/<int:user>", views.admin.event_add_user),
    path("events/<int:id>/export", views.aam.event_export),
    path("events/<int:id>/unarchived", views.aam.event_unarchived),
    path("events/<int:id>/archive", views.aam.event_archive),
    path("events/<int:id>/points/give", views.aam.give_points),
    path("events/<int:id>/photo/report", views.aam.photo_report),
    path("events/<int:id>/photo/report/<int:image>/delete", views.aam.photo_delete),
    path("events/<int:id>/detail", views.other.event_detail),
    path("events/category/data/<int:id>", views.admin.category_data),
    path("events/invites/", views.student.student_invites),
    path("events/all_events/", views.other.all_events),

    path("building/list/", views.admin.building_list),
    path("building/add/", views.admin.add_building),
    path("events/list/<str:search>", views.aam.events_list),
    path("events/archive/", views.aam.events_archive_list),
    path('settings/', views.other.edit_profile),
    path("events/create/", views.aam.event_create),

    path("classroom/create/", views.teacher.create_classroom),
    path("events/", views.other.events),
    path("events/<int:id>/invite", views.teacher.invite_classroom_event),

    path("classroom/invite/create/", views.teacher.create_invite),
    path("classroom/invite/update/", views.teacher.update_invite),
    path("classroom/invite/<uuid:classroom>/", views.student.invite),
    path("classroom/students/", views.teacher.classroom_students),

    path("classroom/student/<int:user>/view", views.teacher.classroom_view_student),
    path("classroom/student/<int:user>/export", views.other.classroom_view_export),

    path("events/<int:event>/request", views.student.event_request),
    path("my/events/", views.student.my_events),

    path("classrooms/", views.administration.classrooms_list, name="classrooms_list"),
    path("classrooms/<int:id>", views.administration.classrooms_view, name="classrooms_view"),
    path("settings/avatar/remove", views.other.avatar_remove, name="avatar_remove"),
    path('schedule/', views.psychologist.schedule_index, name="schedule_index"),
    path('schedule/<int:d>/<int:m>/<int:y>', views.psychologist.schedule_date, name="schedule_date"),
    path('schedule/calendar/', views.psychologist.calendar, name="calendar"),
    path('schedule/edit', views.psychologist.edit_schedule, name="edit_schedule"),
    path('schedule/has_month_classes/<int:m>/<int:y>', views.psychologist.has_month_classes, name="has_month_classes"),
    path('schedule/view/<int:id>', views.psychologist.view_schedule, name="view_schedule"),
    path('classes', views.psychologist.classes, name="classes"),
    path("settings/security/change-password/", views.other.change_password, name="change_password"),
    path("settings/security/devices/", views.other.devices, name="security"),
    path("settings/security/devices/delete/<str:device>", views.other.delete_device, name="delete_device"),
# path("classroom/student/<int:user>/delete", views.classroom_delete_student),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
