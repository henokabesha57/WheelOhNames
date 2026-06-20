from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import WheelEntry, WheelSession, SpinHistory
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.shortcuts import render, get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

class WheelEntryAdmin(ModelAdmin):
    list_display = ['name', 'color', 'weight', 'is_active']
    list_editable = ['weight', 'is_active']
    list_filter = ['is_active']

class WheelSessionAdmin(ModelAdmin):
    list_display = ['id', 'is_spinning', 'current_winner', 'spin_count']
    readonly_fields = ['created_at']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('control-panel/', self.admin_site.admin_view(self.control_panel), name='wheel_control_panel'),
            path('rig-spin/<int:session_id>/<int:entry_id>/', self.admin_site.admin_view(self.rig_spin), name='rig_spin'),
            path('random-spin/<int:session_id>/', self.admin_site.admin_view(self.random_spin), name='random_spin'),
            path('reset-session/<int:session_id>/', self.admin_site.admin_view(self.reset_session), name='reset_session'),
        ]
        return custom_urls + urls
    
    def control_panel(self, request):
        session, _ = WheelSession.objects.get_or_create(id=1)
        entries = session.entries.filter(is_active=True)
        
        context = {
            'session': session,
            'entries': entries,
            'title': 'Wheel Control Panel',
        }
        return render(request, 'admin/wheel_control_panel.html', context)
    
    def rig_spin(self, request, session_id, entry_id):
        session = get_object_or_404(WheelSession, id=session_id)
        winner = get_object_or_404(WheelEntry, id=entry_id)
        
        # Store the rigged winner
        session.winner_selected_by_admin = winner
        session.save()
        
        # Send WebSocket message to trigger the spin with rigged winner
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"wheel_{session_id}",
            {
                'type': 'rigged_spin',
                'winner_id': winner.id,
                'winner_name': winner.name,
                'winner_color': winner.color
            }
        )
        
        self.message_user(request, f"Spin initiated! The wheel will land on: {winner.name}")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/wheel/wheelsession/'))
    
    def random_spin(self, request, session_id):
        session = get_object_or_404(WheelSession, id=session_id)
        
        # Clear any rigged selection
        session.winner_selected_by_admin = None
        session.save()
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"wheel_{session_id}",
            {
                'type': 'random_spin',
            }
        )
        
        self.message_user(request, "Random spin initiated!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/wheel/wheelsession/'))
    
    def reset_session(self, request, session_id):
        session = get_object_or_404(WheelSession, id=session_id)
        session.winner_selected_by_admin = None
        session.current_winner = None
        session.is_spinning = False
        session.save()
        
        # Broadcast reset to all clients
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"wheel_{session_id}",
            {
                'type': 'reset_wheel',
            }
        )
        
        self.message_user(request, "Wheel reset successfully!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/wheel/wheelsession/'))

admin.site.register(WheelEntry, WheelEntryAdmin)
admin.site.register(WheelSession, WheelSessionAdmin)
admin.site.register(SpinHistory)