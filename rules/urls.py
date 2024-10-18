from django.urls import path
from . import views

urlpatterns = [
    path('create_rule/', views.create_rule, name='create_rule'),
    path('combine_rules/', views.combine_rules, name='combine_rules'),
    path('evaluate_rule/', views.evaluate_rule, name='evaluate_rule'),
    path('get_created_rule/', views.get_created_rule, name='get_created_rule'),
    path('delete_all_rules/', views.delete_all_rules, name='delete_all_rules'),
    path('evaluate/', views.rule_evaluation_page, name='evaluate_rule_ui')
]
