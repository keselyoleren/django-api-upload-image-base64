from rest_framework import serializers, generics
from api.models import Image
from rest_framework.response import Response
import six
import base64
import uuid
from django.core.files.base import ContentFile
from rest_framework import status

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, six.string_types):
            if "data:" in data and ";base64," in data:
                header, data = data.split(';base64,')
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invail_image')

            file_name = str(uuid.uuid4())[:12]
            file_extension = "jpg"
            complate_file_name = "%s.%s" % (file_name, file_extension)
            data = ContentFile(decoded_file, complate_file_name)
        return super(Base64ImageField, self).to_internal_value(data)

class UploadImageSerialize(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Image
        fields = "__all__"

    def create(self, valideted_data):
        img  = Image()
        img.image = valideted_data['image']
        img.save()
        return img


class ImageApiVoew(generics.CreateAPIView):
    serializer_class = UploadImageSerialize
    queryset  = Image.objects.all()

    def post(self, request):
        serializer  = UploadImageSerialize(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    