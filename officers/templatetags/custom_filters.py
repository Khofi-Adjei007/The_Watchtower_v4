from django import template
from datetime import date, datetime

register = template.Library()

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
    """Calculate age from birth date."""
    if not birth_date:
        return 'N/A'

    if isinstance(birth_date, str):
        date_formats = ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y'] 
        for fmt in date_formats:
            try:
                birth_date = datetime.strptime(birth_date, fmt).date()
                break
            except ValueError:
                continue
        else:
            return 'N/A'

    if isinstance(birth_date, date):
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    else:
        return 'N/A'

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})
