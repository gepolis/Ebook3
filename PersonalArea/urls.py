"""
URL configuration for volunteer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from django.http import HttpResponse
from . import views

urlpatterns = [
                  path("", views.other.index),
                  path("chat/", views.other.chat),

                  path("users/list/", views.admin.users_list),
                  path("users/list/<str:role>", views.admin.users_list),
                  path("users/create/", views.admin.user_create, name="create_user"),
                  path("users/<int:id>/edit/", views.admin.edit_user),
                  path("users/data/<int:id>", views.admin.user_data),
                  path("users/<int:id>/view/", views.admin.view_user),
                  path("users/<int:user>/login/", views.admin.login_admin_user),
                  path("users/<int:user>/avatar/remove", views.admin.avatar_remove),
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


                  path("classrooms/", views.admin.classrooms_list),
                  path("classrooms/<int:id>", views.admin.classrooms_view),
                  path("settings/avatar/remove", views.other.avatar_remove),
                  path('schedule/', views.psychologist.schedule_index),
                  path('schedule/<int:d>/<int:m>/<int:y>', views.psychologist.schedule_date),
                  path('schedule/calendar/', views.psychologist.calendar),
                  path('schedule/edit', views.psychologist.edit_schedule),
                  path('schedule/has_month_classes/<int:m>/<int:y>', views.psychologist.has_month_classes),
                  # path("classroom/student/<int:user>/delete", views.classroom_delete_student),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

