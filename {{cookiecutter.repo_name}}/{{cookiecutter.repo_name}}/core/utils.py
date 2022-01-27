import os
import random
import string
import uuid

from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify


# To get extension from upload file
def get_filename_exist(file_path):
    base_name = os.path.basename(file_path)
    name, ext = os.path.splitext(base_name)
    return name, ext


# To save Book image with new name by function
def example_image_path(instance, file_name):
    user_id = slugify(instance.id)
    new_filename = random.randint(1, 1000001)
    name, ext = get_filename_exist(file_name)
    final_filename = f'{new_filename}{ext}'
    return f"user/{user_id}/profile/{final_filename}"


def create_token() -> str:
    return uuid.uuid4()


def create_otp() -> str:
    otp = ''
    for i in range(6):
        otp += str(random.randint(0, 9))
    return otp


def build_absolute_uri(path) -> str:
    return f"{settings.SITE_URL}/{path}"


def random_string_generator(size=8, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance
    has a model with a slug field and a title character (char) field.
    """

    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.name, allow_unicode=True)
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        if not slug:
            new_slug = "spacium-{randstr}".format(
                randstr=random_string_generator(size=4)
            )
        else:
            new_slug = "{slug}-{id}".format(
                slug=slug,
                id=instance.id)
        return unique_slug_generator(instance, new_slug=new_slug)

    return slug


def unique_order_id_generator(instance):
    """
        This is for a Django project with order_id field.
    """
    day = timezone.now().day
    month = timezone.now().month
    year = timezone.now().year
    number = '0001'
    order_new_id = f"{year}{month}{day}{number}"
    qs = instance.__class__.objects.all()
    if qs.filter(order_id=order_new_id).exists():
        print("orders:", qs, flush=True)
        print("first:", qs.last().order_id, flush=True)
        return int(qs.last().order_id) + 1
    return order_new_id


def random_referral_code_generator(instance):
    Klass = instance.__class__
    new_code = f"{random_string_generator(8)}".upper().replace(" ", "0")
    qs_exists = Klass.objects.filter(referral_code=new_code).exists()
    if qs_exists:
        return random_referral_code_generator(instance)
    return new_code


def product_model_prefix(instance):
    init = instance.quick_category.slug
    pre_fix = init[0:3]
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(product_model_prefix=pre_fix).exists()
    if qs_exists:
        pre_fix = random_string_generator(3, init)
    return pre_fix.upper()


def unique_product_id_generator(instance, new_id=None):
    instance = instance
    category = instance.base.category
    Klass = instance.__class__
    qs = Klass.objects.filter(base__category=category.id)
    if qs.exists():
        last = qs.last().model_no
        last = last.split(category.product_model_prefix, 1)
        last = int(last[1])
    else:
        last = 10000
    return str(last + 1)