from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = '{{cookiecutter.repo_name}}.core'
    label = 'core'
    verbose_name = 'Cores'
