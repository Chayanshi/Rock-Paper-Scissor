from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path
from app.views import *

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('game_play',game_play.as_view()),
   path('create_room',create_room.as_view()),
   path('reset_game',reset_game.as_view()),
   path('',index),
   path('game_choose',game_choose,name="game_choose"),
   path('company_play',company_play,name="company_play"),
   path('final_play/<str:choice>',final_play,name="final_play"),
]