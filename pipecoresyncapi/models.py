from django.db import models

# Create your models here.
class PipdriveDeals(models.Model):
    deal_id = models.IntegerField(primary_key=True, unique=True)
    deal_name = models.CharField(max_length=255, unique=True, blank=False)
    deal_address = models.CharField(max_length=255, unique=True)
    deal_zip_code = models.CharField(max_length=20, blank=True, null=True)
    deal_phone_number = models.CharField(max_length=20, unique=True , blank=True, null=True)
    deal_email_address = models.EmailField(max_length=100, unique=True, blank=True, null=True)    
    