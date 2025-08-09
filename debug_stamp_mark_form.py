import os
import io

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AxeCollection.settings")
import django

django.setup()

from axes.models import Stamp, Manufacturer, Axe, AxeImage
from axes.forms import StampImageMarkForm
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def main():
    m = Manufacturer.objects.create(name="M", country_code="SE")
    a = Axe.objects.create(manufacturer=m, model="Modell")
    img = Image.new("RGB", (10, 10), "red")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    up = SimpleUploadedFile("t.jpg", buf.read(), content_type="image/jpeg")
    axe_img = AxeImage.objects.create(axe=a, image=up, order=1)
    stamp = Stamp.objects.create(name="S")

    valid_data = {
        "stamp": stamp.id,
        "x": 10.123456789,
        "y": 20.987654321,
        "width": 50.0,
        "height": 30.0,
    }
    form = StampImageMarkForm(data=valid_data)
    print("is_valid:", form.is_valid())
    print("errors:", form.errors)
    if form.is_valid():
        inst = form.save(commit=False)
        inst.axe_image = axe_img
        inst.save()
        print("saved ok; x=", float(inst.x_coordinate), "y=", float(inst.y_coordinate))


if __name__ == "__main__":
    main()
