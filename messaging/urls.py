from django.urls import path, include
from . import views

urlpatterns = [
    # 1. Bandeja de entrada (lista de conversaciones)
    path('inbox/', views.ConversationListView.as_view(), name='conversation_list'),
    
    # 2. Detalle de la conversación (ID de la conversación)
    path('inbox/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
    
    # 3. Iniciar o buscar una conversación
    path('start/', views.StartConversationView.as_view(), name='start_conversation'),

]