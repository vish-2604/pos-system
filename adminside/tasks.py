# from celery import shared_task # type: ignore
# from django.utils.timezone import now, timedelta # type: ignore
# from staffside.models import Notification
# from adminside.models import Inventory

# @shared_task
# def check_expiry():
#     today = now().date()
#     tomorrow = today + timedelta(days=1)
#     day_before_expiry = tomorrow + timedelta(days=1)

#     expiring_items = Inventory.objects.filter(
#         exp_date__in=[today, tomorrow, day_before_expiry], active=True
#     )

#     for item in expiring_items:
#         expiry_day = "today" if item.exp_date == today else "tomorrow" if item.exp_date == tomorrow else "the day before expiry"
#         notification_message = f"{item.purchase.food_item} is expiring {expiry_day} ({item.exp_date})!"

#         if not Notification.objects.filter(message=notification_message).exists():
#             Notification.objects.create(
#                 user=item.purchase.branch.manager,
#                 message=notification_message
#             )

#     return f"Checked expiry dates: {expiring_items.count()} items expiring soon."
