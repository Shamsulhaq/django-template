from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = '{{cookiecutter.repo_name}}.account'
    label = 'account'
    verbose_name = "Accounts"
