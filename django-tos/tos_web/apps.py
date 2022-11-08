from django.apps import AppConfig


class TosWebConfig(AppConfig):

    '''
    Class for set signals for tos_web app and
    avoid cyclic reference
    '''

    name = 'tos_web'
    verbose_name = 'ToS web'

    def ready(self):
        import tos_web.handlers
        return super().ready()
