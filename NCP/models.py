from django.db import models

# Create your models here.
class NovelCoronavirusPneumonia(models.Model):
    # id = models.AutoField()
    update = models.DateField()
    continentName = models.CharField(db_column='continentName', max_length=64, blank=True, null=True)  
    countryName = models.CharField(db_column='countryName', max_length=64, blank=True, null=True)  
    provinceName = models.CharField(db_column='provinceName', max_length=64, blank=True, null=True)  
    cityName = models.CharField(db_column='cityName', max_length=64, blank=True, null=True)  
    currentConfirmedCount = models.IntegerField(db_column='currentConfirmedCount', blank=True, null=True)  
    confirmedCount = models.IntegerField(db_column='confirmedCount', blank=True, null=True)  
    suspectedCount = models.IntegerField(db_column='suspectedCount', blank=True, null=True)  
    curedCount = models.IntegerField(db_column='curedCount', blank=True, null=True)  
    deadCount = models.IntegerField(db_column='deadCount', blank=True, null=True)  
    comment = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NCP'
        unique_together = (('update', 'continentName', 'countryName', 'provinceName', 'cityName'),)