from django.contrib import admin
from cvgen import models


for model in models.__dict__.values():
    if hasattr(model, '__module__') and model.__module__ == 'cvgen.models' and not getattr(model._meta, 'abstract', False):
        admin.site.register(model)