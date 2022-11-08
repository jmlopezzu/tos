import tablib

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.http import HttpResponse


class LoginRequiredMixin(object):

    """
    Add protection to some views in the class parents.
    """

    @method_decorator(login_required(login_url=reverse_lazy('login')))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class JSONResponseMixin(object):

    """
    A mixin that can be used to render a JSON response.
    """

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return context


class CSVResponseMixin(object):

    def render_to_csv(self, data, context):
        response = HttpResponse(content_type='text/csv')
        description = context['object'].description
        response[
            'Content-Disposition'
            ] = 'attachment; filename=%s.csv' % (description, )
        response.write(self.build_data(data))
        return response

    def build_data(self, json_data):
        '''
        Function for build and deliver a file with summary data.

        Args:
            json_data (dict): Data tree in json format

        Returns:
            Object : Object data file

        '''
        data = tablib.Dataset()
        nodes = json_data['nodes']

        data.headers = ['Group', 'Label', ]
        for node in nodes:
            data.append([node['group'], node['label'], ])

        return data.csv
