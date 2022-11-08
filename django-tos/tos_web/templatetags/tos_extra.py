import hashlib

from django import template
register = template.Library()


@register.filter('is_textarea')
def is_textarea(field):
    return field.as_widget().startswith('<textarea')


@register.filter('is_file')
def is_file(field):
    return 'type="file"' in field.as_widget()


@register.filter('sha1')
def generate_sha1(value):
    return hashlib.sha1(value.encode('utf-8')).hexdigest()


@register.filter('datequery')
def datequery(value):
    return value.strftime("%A %d. %B %Y")
