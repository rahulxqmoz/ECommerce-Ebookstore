import calendar
from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def star_range(value):
    return range(value)


@register.filter
def get_month_name(month_number):
    # Ensure month_number is an integer
    month_number = int(month_number)
    # Adjust month_number to be 1-based (calendar.month_name uses 1 for January)
    month_number += 0
    return calendar.month_name[month_number]