from django.contrib.auth.backends import ModelBackend
from adminside.models import Staff

class StaffAuthBackend(ModelBackend):
    def authenticate(self, request, staff_username=None, password=None, **kwargs):
        try:
            user = Staff.objects.get(staff_username=staff_username)  # ✅ Fetch user by staff_username
            if user.check_password(password):  # ✅ Verify password
                return user
        except Staff.DoesNotExist:
            return None
