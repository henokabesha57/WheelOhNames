from django.db import models
from django.contrib.auth.models import User
import json

class WheelEntry(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#FF6B6B')
    weight = models.FloatField(default=1.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class WheelSession(models.Model):
    # Change this to use a through model or add related_name
    entries = models.ManyToManyField(
        WheelEntry, 
        related_name='sessions',  # Add this to avoid conflict
        blank=True
    )
    is_spinning = models.BooleanField(default=False)
    current_winner = models.ForeignKey(
        WheelEntry, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='winner_of_session'  # Add this to avoid conflict
    )
    winner_selected_by_admin = models.ForeignKey(
        WheelEntry, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='admin_selected_winners'  # Add this to avoid conflict
    )
    spin_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_random_winner(self, rigged_winner=None):
        """Returns a winner, either rigged or random"""
        entries = list(self.entries.filter(is_active=True))
        if not entries:
            return None
        
        if rigged_winner and rigged_winner in entries:
            return rigged_winner
        
        # Weighted random selection
        weights = [entry.weight for entry in entries]
        import random
        return random.choices(entries, weights=weights, k=1)[0]

class SpinHistory(models.Model):
    session = models.ForeignKey(
        WheelSession, 
        on_delete=models.CASCADE,
        related_name='spin_history'  # Add this for clarity
    )
    winner = models.ForeignKey(
        WheelEntry, 
        on_delete=models.CASCADE,
        related_name='spin_wins'  # Add this for clarity
    )
    was_rigged = models.BooleanField(default=False)
    spin_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.winner.name} - {'Rigged' if self.was_rigged else 'Random'}"