from django.contrib import admin
from rfweb.rfwebapp.models import Suit, Keyword, Test

class TestInline(admin.StackedInline):
    model = Test
    extra = 5
    fieldsets = (
        (None, {'fields': ('name',)}),
        ('Details', {'classes': ('collapse',),
                     'fields': ('doc',)})
    )

class KeywordInline(admin.StackedInline):
    model = Keyword
    extra = 5
    fieldsets = (
        (None, {'fields': ('name',)}),
        ('Details', {'classes': ('collapse',),
                     'fields': ('args', 'doc',)})
    )

class SuitAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name',)}),
        ('Details', {'classes': ('collapse',),
                     'fields': ('version', 'doc')})
        )
    inlines = [KeywordInline, TestInline]

admin.site.register(Suit, SuitAdmin)
