from django.db import models

# Create your models here.
class Namemap(models.Model):
    name = models.CharField(max_length=255)
    englishname = models.CharField(db_column='EnglishName', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'nameMap'
        unique_together = (('name', 'englishname'),)

class GlobalSummary(models.Model):
    id = models.AutoField(db_column='id',primary_key=True)
    update = models.DateField()
    confirmation = models.IntegerField(blank=True, null=True)
    totalConfirmation = models.IntegerField(blank=True, null=True)  # Field name made lowercase.
    cure = models.IntegerField(blank=True, null=True)
    dead = models.IntegerField(blank=True, null=True)
    confirmAdd = models.IntegerField(blank=True,null=True)
    totalConfirmationAdd = models.IntegerField(blank=True,null=True)
    cureAdd = models.IntegerField(blank=True,null=True) 
    deadAdd = models.IntegerField(blank=True,null=True)
    cureRate = models.FloatField(blank=True,null=True)
    deadRate = models.FloatField(blank=True,null=True)

    class Meta:
        managed = False
        db_table = 'globalSummary'
        unique_together = ('update',)
class Global(models.Model):
    id = models.AutoField(db_column='id',primary_key=True)
    update = models.DateField()
    continent = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    confirmation = models.IntegerField(blank=True, null=True)
    totalconfirmation = models.IntegerField(db_column='totalConfirmation', blank=True, null=True)  # Field name made lowercase.
    suspect = models.IntegerField(blank=True, null=True)
    cure = models.IntegerField(blank=True, null=True)
    dead = models.IntegerField(blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'global'
        unique_together = (('update', 'continent', 'country'),)

class Country(models.Model):
    id = models.AutoField(db_column='id',primary_key=True)
    update = models.DateField()
    country = models.CharField(max_length=255, blank=True, null=True)
    province = models.CharField(max_length=255, blank=True, null=True)
    confirmation = models.IntegerField(blank=True, null=True)
    totalconfirmation = models.IntegerField(db_column='totalConfirmation', blank=True, null=True)  # Field name made lowercase.
    suspect = models.IntegerField(blank=True, null=True)
    cure = models.IntegerField(blank=True, null=True)
    dead = models.IntegerField(blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'country'
        unique_together = (('update', 'country', 'province'),)

class Province(models.Model):
    id = models.AutoField(db_column='id',primary_key=True)
    update = models.DateField()
    country = models.CharField(max_length=255, blank=True, null=True)
    province = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    confirmation = models.IntegerField(blank=True, null=True)
    totalconfirmation = models.IntegerField(db_column='totalConfirmation', blank=True, null=True)  # Field name made lowercase.
    suspect = models.IntegerField(blank=True, null=True)
    cure = models.IntegerField(blank=True, null=True)
    dead = models.IntegerField(blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'province'
        unique_together = (('update', 'country', 'province', 'city'),)        