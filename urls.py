from django.urls import path
from .views import (
    person_management_view, 
    debug_persons, 
    delete_person, 
    get_person, 
    update_person
)

urlpatterns = [
    path('manage/', person_management_view, name='person_management'),
    path('debug/', debug_persons, name='debug_persons'),
    path('delete/<str:id_rec>/', delete_person, name='delete_person'),
    path('person/<str:id_rec>/', get_person, name='get_person'),
    path('update/<str:id_rec>/', update_person, name='update_person'),
]