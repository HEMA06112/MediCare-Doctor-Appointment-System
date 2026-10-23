from django.contrib import admin
from app.models import *

# Register your models here.
admin.site.register(Doctor)

from.models import Doctor,Department
admin.site.register(Department)


from .models import Doctor, Patient
admin.site.register(Patient)

from .models import Contact
admin.site.register(Contact)