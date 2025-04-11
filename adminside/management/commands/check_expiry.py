from django.core.management.base import BaseCommand  # type: ignore
from django.utils.timezone import localtime, make_aware # type: ignore
from datetime import datetime, timedelta
from pytz import timezone # type: ignore
from staffside.models import Notification
from adminside.models import Inventory
from django.utils.timezone import now # type: ignore


class Command(BaseCommand):
    help = "Check for expiring food items and send notifications"

    def handle(self, *args, **kwargs):
        ist = timezone("Asia/Kolkata")  # Indian Standard Time (IST)

        for item in Inventory.objects.all():
            item.save()
        self.stdout.write(self.style.SUCCESS("Triggered save() on all Inventory items."))
        
        # Get today's date in IST
        today_ist = localtime(now(), ist).date()

        tomorrow_ist = today_ist + timedelta(days=1)
        day_before_expiry_ist = tomorrow_ist + timedelta(days=1)

        # Find items expiring today, tomorrow, or the day before expiry in IST
        expiring_items = Inventory.objects.filter(
            exp_date__in=[today_ist, tomorrow_ist, day_before_expiry_ist], active=True
        )
        print(f"Found {expiring_items.count()} items expiring soon.")

        for item in expiring_items:
            print(f"Item: {item.purchase.food_item}, Expiry Date: {item.exp_date}")

            # Determine if the item is expiring today, tomorrow, or the day before expiry
            if item.exp_date == today_ist:
                expiry_day = "today"
            elif item.exp_date == tomorrow_ist:
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

        self.stdout.write(self.style.SUCCESS("Checked expiry dates and sent notifications in IST."))
