from django.db import models
from django.utils.translation import gettext_lazy as _


class Survivor(models.Model):
    class GenderChoices(models.TextChoices):
        FEMALE = 'F', _('Female')
        MALE = 'M', _('Male')
        OTHER = 'O', _('Other')

    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=GenderChoices)
    # could have also used postgis for better geolocation handling
    # since it is not a requirement, we will use float for the sake of simplicity
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_infected = models.BooleanField(default=False)

    def __str__(self):
        return f'Name: {self.name}, Is_infected: {self.is_infected}'


class InfectionReport(models.Model):
    reporter = models.ForeignKey(Survivor, related_name='reports_made', on_delete=models.CASCADE)
    reported = models.ForeignKey(Survivor, related_name='reports_received', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('reporter', 'reported')

    def __str__(self):
        return f'{self.reporter.name} reported {self.reported.name} is infected.'
