from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


def get_sentinel_user():
    return Profile.objects.get(school='Deleted User')


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    school = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.user.get_full_name()} / {self.school}'

    @classmethod
    def create(cls, user, **kwargs):
        return cls(user=user, school=kwargs['school'])


class Post(models.Model):
    no = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Profile, on_delete=models.SET(get_sentinel_user))
    timestamp = models.DateTimeField()
    content = models.TextField()
    comments = models.ManyToManyField('Comment', null=True, blank=True)

    def __str__(self):
        return f'{self.no}: {self.title} / {self.author}'

    @classmethod
    def create(cls, title, author, timestamp, content):
        return cls(title=title, author=author, timestamp=timestamp, content=content)


class Comment(models.Model):
    no = models.AutoField(primary_key=True)
    parent = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    author = models.ForeignKey(Profile, on_delete=models.SET(get_sentinel_user))
    timestamp = models.DateTimeField()
    content = models.TextField()

    def __str__(self):
        return f'{self.no}) {self.author}: {self.content}'

    @classmethod
    def create(cls, parent, author, timestamp, content):
        return cls(parent=parent, author=author, timestamp=timestamp, content=content)
