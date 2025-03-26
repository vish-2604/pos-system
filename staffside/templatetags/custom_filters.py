from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiplies two numbers in a Django template"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ""

@register.filter
def extract_name(value):
    if "_" in value:
        parts = value.rsplit("_", 1) 
        item_name = parts[0]  
        size = parts[1]  
        size_mapping = {
            "small": "S",
            "medium": "M",
            "large": "L"
        }
        size_short = size_mapping.get(size.lower(), size) 
        return f"{item_name} ({size_short})"
    return value 


@register.filter
def percentage(value, percent):
    """Calculate a percentage increase or decrease."""
    try:
        return round(float(value) * (1 + float(percent) / 100), 2)
    except (ValueError, TypeError):
        return value

