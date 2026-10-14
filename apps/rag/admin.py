from django.contrib import admin
from django.utils.html import format_html
from .models import KnowledgeBase, ChatSession, ChatMessage


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category_badge', 'is_active', 'views_count', 'helpful_count')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'content', 'keywords')
    list_editable = ('is_active',)
    
    def category_badge(self, obj):
        return format_html(
            '<span style="background: #c9a961; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-size: 0.7rem; font-weight: 700; '
            'text-transform: uppercase;">{}</span>',
            obj.get_category_display()
        )
    category_badge.short_description = 'Category'


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('is_user', 'content', 'created_at')
    can_delete = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'title', 'message_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('session_id', 'user__email', 'title')
    inlines = [ChatMessageInline]
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'