from django.contrib import admin
from django.contrib.auth.models import User, Group

admin.site.site_header = "PROWEB HR"
admin.site.site_title  = "PROWEB HR"
admin.site.index_title = "Boshqaruv paneli"

admin.site.unregister(User)
admin.site.unregister(Group)


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_staff', 'is_superuser', 'last_login']
    list_filter = ['is_staff', 'is_superuser']
    search_fields = ['username', 'email']


admin.site.register(User, UserAdmin)
admin.site.register(Group)
