from django.db import models

class Students(models.Model):
    rollno = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=20)
    phonenumber = models.CharField(max_length=15)

    class Meta:
        db_table = 'students'
        managed = False  # This tells Django not to create/modify this table


class jnr_core(models.Model):
    rno = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    branch = models.CharField(max_length=10)
    section = models.CharField(max_length=5)
    subject1 = models.IntegerField()
    subject2 = models.IntegerField()
    subject3 = models.IntegerField()
    phone = models.CharField(max_length=15)

    class Meta:
        db_table = 'jnr_core'

    def __str__(self):
        return f"{self.rno} - {self.name}"

class snr_core(models.Model):
    rno = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    branch = models.CharField(max_length=10)
    section = models.CharField(max_length=5)
    subject1 = models.IntegerField()
    subject2 = models.IntegerField()
    subject3 = models.IntegerField()
    phone = models.CharField(max_length=15)

    class Meta:
        db_table = 'snr_core'

    def __str__(self):
        return f"{self.rno} - {self.name}"


