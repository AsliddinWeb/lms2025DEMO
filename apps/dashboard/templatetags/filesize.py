from django import template

register = template.Library()

@register.filter
def filesize_mb(value):
    """Baytdan MB ga o‘tkazish"""
    try:
        mb = int(value) / (1024 * 1024)
        return f"{mb:.2f} MB"
    except (ValueError, TypeError):
        return "0 MB"
