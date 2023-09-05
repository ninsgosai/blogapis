from django.contrib.auth import password_validation, authenticate
from django.core.exceptions import ValidationError
from utils import GlobalConstant
from blogging.models import *
from django.core.validators import validate_email
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from datetime import datetime
from django.core.mail import send_mail

def send_email(subject, message, recipient_list):
    send_mail(subject, message, 'from@example.com', recipient_list, fail_silently=False)

class LoginSerializer(serializers.Serializer):  # noqa
    email = serializers.CharField(max_length=128, write_only=True, required=True)
    password = serializers.CharField(max_length=128, write_only=True, required=True)

    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].error_messages['required'] = '%s field is required' % field
            self.fields[field].error_messages['blank'] = '%s field may not be blank.' % field
            self.fields[field].error_messages['null'] = '%s field may not be null.' % field

    def validate_email(self, value):  # noqa
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError(_(GlobalConstant.Data['invalid_email_address']))

        return value

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(email=email, password=password)
        if not user:
            raise ValidationError(GlobalConstant.Data['unable_login'])

        attrs['user'] = user
        return attrs
    

class UserSignUpSerializer(serializers.Serializer):  # noqa
    email = serializers.CharField(max_length=128, write_only=False, required=True)
    password = serializers.CharField(max_length=128, write_only=True, required=True)
    confirm_password = serializers.CharField(max_length=128, write_only=True, required=True)
    name = serializers.CharField(max_length=256, required=True)

    def __init__(self, *args, **kwargs):
        super(UserSignUpSerializer, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].error_messages['required'] = '%s field is required' % field
            self.fields[field].error_messages['blank'] = '%s field may not be blank.' % field

    def validate_email(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise serializers.ValidationError(_(GlobalConstant.Data['invalid_email_address']))
        return email


    def validate(self, data):
        UserEmail = data.get("email")
        user_email = Users.objects.filter(email=UserEmail).first()

        # Validate the email
        user_email = Users.objects.filter(email=UserEmail.strip().lstrip().rstrip().replace(" ", "")).first()
        if user_email:
            raise serializers.ValidationError({"email": _(GlobalConstant.Data['email_address_exists'])})


        # Validate the email
        if data.get("email"):
            if user_email and user_email.deleted_at is None and user_email == UserEmail.strip().lstrip().rstrip().replace(
                    " ", ""):
                raise serializers.ValidationError({"email": _(GlobalConstant.Data['email_address_exists'])})


        if data['password'] and data['confirm_password']:
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError({"confirm_password": GlobalConstant.Data['password_not_match']})

        password_validation.validate_password(data['password'])

        return data

    def create(self, validated_data):
        role = Role.objects.get(role_name="Regular User")
        user = Users.objects.create_user(
            email=validated_data.get('email'),
            name=validated_data.get('name'),
            role=role
        )
        password = validated_data.get('password')
        user.set_password(password)
        user.save()
        return user.id
    
from rest_framework import serializers

class BlogSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=128, write_only=True, required=True)
    content = serializers.CharField(write_only=True, required=True)

    def __init__(self, *args, **kwargs):
        super(BlogSerializer, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].error_messages['required'] = '%s field is required' % field
            self.fields[field].error_messages['blank'] = '%s field may not be blank.' % field

    def create(self, validated_data, **kwargs):
        # Get the request object from the context
        request = self.context['request'].user
        blog_post = BlogPost(
            title=validated_data['title'],
            content=validated_data['content'],
            author=Users.objects.get(pk=request.id),
            publication_date=datetime.now()
        )
        blog_post.save()
        return blog_post
    
    def update(self, blog_post, validated_data):
        # Get the request object from the context
        request = self.context['request'].user
        blog_post.title = validated_data['title']
        blog_post.content = validated_data['content']
        blog_post.author = Users.objects.get(pk=request.id)
        blog_post.publication_date = datetime.now()
        blog_post.save()
        return blog_post
    
    def to_representation(self, instance):
        rep = super(BlogSerializer,self).to_representation(instance)
        rep['id'] = instance.id
        rep['title'] = instance.title
        rep['content'] = instance.content
        rep['publication_date'] = str(instance.publication_date)
        rep['comments'] = []
        if Comment.objects.filter(blog_post = instance.id).exists():
            lst = []
            for i in Comment.objects.filter(blog_post=instance.id):
                dic = {"id":i.id,"author":i.author.name,"text":i.text,"created_at":str(i.created_at)}
                lst.append(dic)
            rep['comments'] = lst
        return rep

class CommentSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=128, write_only=True, required=True)

    def __init__(self, *args, **kwargs):
        super(CommentSerializer, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].error_messages['required'] = '%s field is required' % field
            self.fields[field].error_messages['blank'] = '%s field may not be blank.' % field
        # self.context['request'] = kwargs['request']
        # Add the request object as a keyword argument
        # self.request = kwargs['request']

    def create(self, validated_data, **kwargs):
        # Get the request object from the context
        request = self.context['request'].user
        blogid = BlogPost.objects.get(id=self.context['request'].POST['blog_id'])
        blog_post = Comment(
            blog_post=blogid,
            author=Users.objects.get(pk=request.id),
            text=validated_data['text'],
            created_at=datetime.now()
        )
        blog_post.save()
        try:
           send_mail("your_blog_post just got commened by someone","Some one your blog post just got commened at ", "http://127.0.0.1:8000/api/v1/blog/"+str(blogid.id),recipient_list=[blogid.author.email])
        except Exception as e:
            print("email fail to sent.")
        return blog_post
    
    def update(self, blog_post, validated_data):
        # Get the request object from the context
        request = self.context['request'].user
        blog_post.text = validated_data['text']
        blog_post.save()
        return blog_post
    
    def to_representation(self, instance):
        rep = super(BlogSerializer,self).to_representation(instance)
        rep['id'] = instance.id
        rep['title'] = instance.title
        rep['content'] = instance.content
        rep['publication_date'] = str(instance.publication_date)
        return rep


