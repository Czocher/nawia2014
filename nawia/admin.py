from django.contrib import admin
from django.db.models import get_models, get_app
from django.contrib.auth.models import Permission

admin.site.register(Permission)

appNames = ['authorships', 'topics', 'theses', 'reviews', 'faculty']

for appName in appNames:
    for model in get_models(get_app(appName)):
        admin.site.register(model)

