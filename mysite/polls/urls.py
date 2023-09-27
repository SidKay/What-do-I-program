# URLconf file

from django.urls import path

from . import views

# Use URLconf namespacing when working with multiple apps.
# This lets your templates know which url to use.
app_name = 'polls'
urlpatterns = [
	path("", views.index, name="index"),
	path('<int:question_id>/', views.detail, name='detail'),
	path('<int:question_id>/results/', views.results, name='results'),
	path('<int:question_id>/vote/', views.vote, name='vote'),
]