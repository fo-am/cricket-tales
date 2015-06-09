# Cricket Tales Movie Robot
# Copyright (C) 2015 Dave Griffiths
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max
from random import randint

# fast random selection
def random_one(model):
   max_ = model.objects.aggregate(Max('id'))['id__max']
   i = 0
   while i < 1:
       try:
           return model.objects.get(pk=randint(1, max_))
           i += 1
       except model.DoesNotExist:
           pass

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    score = models.FloatField(default=0)
    num_events = models.IntegerField(default=0)

    def __unicode__(self):
        return self.user.username

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

class Cricket(models.Model):
    name = models.CharField(max_length=200)
    created_date = models.DateTimeField('date created')
    image = models.ImageField(upload_to='cricket_images')
    # stuff updated from periodic update.py
    biggest_fan = models.CharField(max_length=200, default="None yet")
    num_contributors = models.CharField(max_length=200, default=0)
    total_events = models.CharField(max_length=200, default=0)
    def __unicode__(self):
        return self.name;

class Personality(models.Model):
    cricket = models.ForeignKey(Cricket)
    num_matings = models.IntegerField(default=0)
    time_in_nests = models.FloatField(default=0)

class Burrow(models.Model):
    name = models.CharField(max_length=200)
    pos_x = models.FloatField(default=0)
    pos_y = models.FloatField(default=0)
    # stuff updated from periodic update.py
    num_movies = models.IntegerField(default=0)
    num_movies_ready = models.IntegerField(default=0)
    biggest_contributor = models.CharField(max_length=200, default="None yet")
    num_contributors = models.CharField(max_length=200, default=0)
    total_events = models.CharField(max_length=200, default=0)
    def __unicode__(self):
        return self.name;

class Movie(models.Model):
    cricket = models.ForeignKey(Cricket)
    burrow = models.ForeignKey(Burrow, null=True, blank=True, default = None)
    name = models.CharField(max_length=200)
    views = models.IntegerField(default=0)
    created_date = models.DateTimeField('date created')
    status = models.IntegerField(default=0)
    src_index_file = models.CharField(max_length=4096)
    start_frame = models.IntegerField(default=0)
    fps = models.FloatField(default=0)
    length_frames = models.IntegerField(default=0)
    # stuff updated from periodic update.py
    num_events = models.IntegerField(default=0)
    def __unicode__(self):
        return str(self.cricket)+" : "+str(self.name);

# optimisation one to many to avoid doing lookups on all the events
# in order to find which movies players have clicked on
# these are created automatically by robot.py
# premature optimisation
class PlayersToMovies(models.Model):
    user = models.ForeignKey(User)
    movie = models.ForeignKey(Movie)

class EventType(models.Model):
    name = models.CharField(max_length=200)
    def __unicode__(self):
        return str(self.name);

class Event(models.Model):
    movie = models.ForeignKey(Movie)
    type = models.ForeignKey(EventType)
    user = models.ForeignKey(User, null=True, blank=True, default = None)
    start_time = models.FloatField(default=0)
    end_time = models.FloatField(default=0)
    def __unicode__(self):
        return self.type.name+" "+str(self.start_time)+" : "+str(self.movie);
