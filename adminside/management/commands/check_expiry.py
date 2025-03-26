from django.core.management.base import BaseCommand  # type: ignore
from django.utils.timezone import now, timedelta  # type: ignore
from staffside.models import Notification
from adminside.models import Inventory

class Command(BaseCommand):
    help = "Check for expiring food items and send notifications"

    def handle(self, *args, **kwargs):
        today = now().date()
        tomorrow = today + timedelta(days=1)
        day_before_expiry = tomorrow + timedelta(days=1)  # The day before expiry date

        # Find items expiring today, tomorrow, or the day before expiry
        expiring_items = Inventory.objects.filter(
            exp_date__in=[today, tomorrow, day_before_expiry], active=True
        )
        print(f"Found {expiring_items.count()} items expiring soon.")

        for item in expiring_items:
            print(f"Item: {item.purchase.food_item}, Expiry Date: {item.exp_date}")
            # Determine if the item is expiring today, tomorrow, or the day before expiry
            if item.exp_date == today:
                expiry_day = "today"
            elif item.exp_date == tomorrow:
                expiry_day = "tomorrow"
            else:
                expiry_day = "the day before expiry"

            notification_message = f"{item.purchase.food_item} is expiring {expiry_day} ({item.exp_date})!"

            # Prevent duplicate notifications
            if not Notification.objects.filter(message=notification_message).exists():
                Notification.objects.create(
                    user=item.purchase.branch.manager,  # Adjust recipient
                    message=notification_message
                )

        self.stdout.write(self.style.SUCCESS("Checked expiry dates and sent notifications."))
