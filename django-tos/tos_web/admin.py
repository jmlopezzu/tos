import csv
from datetime import date

from django.contrib import admin
from django.db.models.query import QuerySet
from django.db.models.fields.files import FieldFile
from django.http import HttpResponse

from .models import UserProfile
from .models import Query
from .models import Invitation
from .models import Verification


def prep_field(request, obj, field, manyToManySep=';'):
    """ Returns the field as a unicode string. If the field is a callable, it
    attempts to call it first, without arguments.
    """
    if '__' in field:
        bits = field.split('__')
        field = bits.pop()

        for bit in bits:
            obj = getattr(obj, bit, None)

            if obj is None:
                return ""

    attr = getattr(obj, field)

    if isinstance(attr, (FieldFile,)):
        attr = request.build_absolute_uri(attr.url)

    output = attr() if callable(attr) else attr

    if isinstance(output, (list, tuple, QuerySet)):
        output = manyToManySep.join([str(item) for item in output])
    return str(output) if output else ""


def export_csv_action(description="Export as CSV", fields=None, exclude=None,
                      header=True, manyToManySep=';'):
    """ This function returns an export csv action. """

    def export_as_csv(modeladmin, request, queryset):
        """ Generic csv export admin action.
        Based on http://djangosnippets.org/snippets/2712/
        """

        opts = modeladmin.model._meta
        field_names = [field.name for field in opts.fields]
        labels = []

        if exclude:
            field_names = [f for f in field_names if f not in exclude]

        elif fields:
            field_names = [field for field, _ in fields]
            labels = [label for _, label in fields]

        response = HttpResponse(content_type='text/csv')
        namefile = "rec_invitations_%s" % (date.today(), )
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % (
            namefile, )

        writer = csv.writer(response)

        if header:
            writer.writerow(labels if labels else field_names)

        for obj in queryset:
            writer.writerow(
                [prep_field(request, obj, field, manyToManySep)
                 for field in field_names])
        return response
    export_as_csv.short_description = description
    export_as_csv.acts_on_all = True
    return export_as_csv


@admin.register(UserProfile)
class UserAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'email', 'acceptance', 'created',
                    'modified', )
    list_filter = ('created', 'acceptance', )
    search_fields = ('email', )


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    list_display = ('description', 'user', 'created', 'modified', 'raw_data', )
    search_fields = ('user', )


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = (
        'inviter', 'email', 'count', 'state', 'created', 'modified', )
    search_fields = ['email', 'inviter__email']
    list_filter = ('state', 'count', 'created', 'modified', )
    actions = (
        export_csv_action("Export Invitations Report",
                          fields=[
                              ('email', 'Invitado'),
                              ('inviter__email', 'Invitante'),
                              ('count', 'Reiteraciones'),
                              ('created', 'Fecha de Invitacion',),
                              ('modified', 'ambio Estado-Reiteracion'), ],
                          header=True,
                          manyToManySep=';'
                          ),)


@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', )
    search_fields = ('user__email', )
