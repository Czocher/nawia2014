from django.contrib import admin
from django.db.models import get_models, get_app
from django.contrib.auth.models import Permission

admin.site.register(Permission)

for model in get_models(get_app('nawia')):
    admin.site.register(model)

