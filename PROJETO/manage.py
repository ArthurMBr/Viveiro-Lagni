#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # ***** IMPORTANTE: Substitua 'SEU_NOME_DA_PASTA_SETTINGS' pelo nome que você me informou *****
    # Por exemplo, se sua pasta settings.py se chama 'meuerp', a linha será:
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meuerp.settings')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'viveiro_lagni.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()