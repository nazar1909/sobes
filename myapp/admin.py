from django.contrib import admin
from .models import AD

@admin.register(AD)
class ADAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date')  # які поля показувати
    list_filter = ('user', 'date')            # фільтри
    search_fields = ('title', 'body')        # пошук по полях

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # суперкористувач бачить все
        return qs.filter(user=request.user)  # інші користувачі бачать тільки свої

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user  # при створенні AD прив'язуємо до користувача
        super().save_model(request, obj, form, change)

# Register your models here.
