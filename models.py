from django.db import models
from django.contrib.auth.models import User

class ZkguPerson(models.Model):
    ID_REC = models.CharField(max_length=255, unique=True, db_index=True)
    LASTNAME = models.CharField(max_length=100, default="", null=True)
    FIRSTNAME = models.CharField(max_length=100, default="", null=True) 
    MIDNAME = models.CharField(max_length=100, default="", null=True)
    DELETION_MARK = models.IntegerField(null=True, default=0)
    last_update = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.ID_REC} - {self.LASTNAME} {self.FIRSTNAME}"
    
    class Meta:
        db_table = 'zkgu_person'
        ordering = ['id']
        indexes = [
            models.Index(fields=['ID_REC']),
            models.Index(fields=['last_update']),
        ]

class ZkguPersonSync(models.Model):
    person = models.ForeignKey(ZkguPerson, on_delete=models.CASCADE)
    sync_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('synced', 'Synced'),
        ('failed', 'Failed')
    ], default='pending')
    api_response = models.JSONField(null=True, blank=True)
    last_sync = models.DateTimeField(auto_now=True)
    retry_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.person.ID_REC} - {self.sync_status}"
    
    class Meta:
        db_table = 'zkgu_person_sync'
        ordering = ['-last_sync']

class APIToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Token for {self.user.username}"
    
    class Meta:
        db_table = 'api_tokens'