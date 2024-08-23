from django import template
from datetime import date
register = template.Library()
from datetime import datetime

@register.filter(name='in_list')
def in_list(value, arg):
    """Check if value is in the provided comma-separated list."""
    return value in arg.split(',')

@register.filter
def startswith(value, arg):
    """Usage: {% if value|startswith:"arg" %}"""
    return value.startswith(arg)



@register.filter
def calculate_age(birth_date):
    if not birth_date:
        return 'N/A'
    
    if isinstance(birth_date, str):
        try:
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        except ValueError:
            return 'N/A'
    
    if isinstance(birth_date, date):
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    else:
        return 'N/A'

