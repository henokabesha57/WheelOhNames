from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.contrib.auth.decorators import login_required
import json
from .models import WheelEntry, WheelSession

def index(request):
    session, _ = WheelSession.objects.get_or_create(id=1)
    entries = session.entries.all()
    
    # Get the last winner from the session
    last_winner = session.current_winner.name if session.current_winner else None
    
    context = {
        'entries': entries,
        'entries_json': json.dumps([{
            'id': e.id,
            'name': e.name,
            'color': e.color,
            'weight': e.weight
        } for e in entries]),
        'total_spins': session.spin_count,
        'last_winner': last_winner
    }
    return render(request, 'index.html', context)

@login_required
def admin_panel(request):
    session, _ = WheelSession.objects.get_or_create(id=1)
    entries = session.entries.all()
    
    context = {
        'session': session,
        'entries': entries
    }
    return render(request, 'admin_panel.html', context)