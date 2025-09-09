from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

User = get_user_model()


@receiver(pre_save, sender=User)
def update_last_activity(sender, instance, **kwargs):
    if instance.pk:
        original = User.objects.get(pk=instance.pk)
        if original.last_login != instance.last_login:
            instance.last_activity = timezone.now()
