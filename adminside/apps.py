from django.apps import AppConfig
import threading
from django.core.management import call_command
from django.utils.timezone import now, timedelta
import sys


class AdminsideConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'adminside'

    def ready(self):
        if "runserver" in sys.argv:  
            threading.Thread(target=call_command, args=("check_expiry",)).start()




    
