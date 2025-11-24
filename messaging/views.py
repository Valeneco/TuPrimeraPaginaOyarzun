from django.shortcuts import render, redirect, get_object_or_404 
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.views.generic import ListView, DetailView, View
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth import get_user_model
from django.db.models import Count
from .models import Conversation, Message
from .forms import MessageForm

# ----------------------------------------------------
# 1. Conversation List View (Inbox)
# ----------------------------------------------------
class ConversationListView(LoginRequiredMixin, ListView):
    """Shows all conversations for the logged-in user and provides available users for new chats."""
    model = Conversation
    template_name = 'messaging/conversation_list.html'
    context_object_name = 'conversations'

    def get_queryset(self):
        qs = Conversation.objects.filter(participants=self.request.user).order_by('-last_message_at').distinct()
        for conv in qs:
            # Determine the 1-to-1 partner (other participant)
            conv.partner = conv.participants.exclude(pk=self.request.user.pk).first()
            # Count unread messages from partner
            if conv.partner:
                conv.unread_count = conv.messages.filter(is_read=False, sender=conv.partner).count()
            else:
                conv.unread_count = 0
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()
        # All users except the logged-in user
        context['available_users'] = User.objects.exclude(pk=self.request.user.pk)
        return context

# ----------------------------------------------------
# 2. Conversation Detail View (Chat)
# ----------------------------------------------------
class ConversationDetailView(LoginRequiredMixin, DetailView):
    """Shows messages of a conversation and allows sending new messages."""
    model = Conversation
    template_name = 'messaging/conversation_detail.html'
    context_object_name = 'conversation'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user not in obj.participants.all():
            raise Http404("Conversation not found or access denied.")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MessageForm()

        # Mark partner's unread messages as read
        partner_messages = self.object.messages.filter(is_read=False).exclude(sender=self.request.user)
        partner_messages.update(is_read=True)

        # Determine partner 1-to-1
        context['partner'] = self.object.participants.exclude(pk=self.request.user.pk).first()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = MessageForm(request.POST)

        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.conversation = self.object
            new_message.sender = request.user
            new_message.save()
            return HttpResponseRedirect(reverse('conversation_detail', kwargs={'pk': self.object.pk}))

        context = self.get_context_data(object=self.object)
        context['form'] = form
        return self.render_to_response(context)

# ----------------------------------------------------
# 3. Start Conversation View (1-to-1)
# ----------------------------------------------------
class StartConversationView(LoginRequiredMixin, View):
    """
    Finds an existing 1-to-1 conversation or creates a new one.
    Expects 'recipient_id' via POST.
    """
    def post(self, request, *args, **kwargs):
        recipient_id = request.POST.get('recipient_id') 

        if not recipient_id or recipient_id == str(request.user.pk):
            return redirect('conversation_list') 

        try:
            RecipientModel = get_user_model()
            recipient = RecipientModel.objects.get(pk=recipient_id)
        except RecipientModel.DoesNotExist:
            return redirect('conversation_list') 

        current_user = request.user
        
        # Find 1-to-1 conversation using annotate
        conversation = (
            Conversation.objects
            .filter(participants=current_user)
            .filter(participants=recipient)
            .annotate(num_participants=Count('participants'))
            .filter(num_participants=2)
            .first()
        )

        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(current_user, recipient)
            conversation.save()

        return redirect('conversation_detail', pk=conversation.pk)
