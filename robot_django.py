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

import os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cricket_tales.settings")
import django
from crickets.models import *
from django.utils import timezone
from django.db.models import Max
from random import randint

import robot.process
import robot.exicatcher
import robot.settings

django.setup()

#########################################################################
# adding movies and updating burrows

def update_burrow_with_movie(movie):
    burrowname = movie.name.split("/")[0]
    try:
        existing = Burrow.objects.get(name=burrowname)
    except Burrow.DoesNotExist:
        print("adding burrow: "+burrowname)
        existing = Burrow(name = burrowname, pos_x=0, pos_y=0)
        existing.save()
    if movie.burrow!=existing:
        #print("registering movie: "+movie.name+" with "+burrowname)
        movie.burrow=existing
        movie.save()

def add_movie(cricketname,moviename,index_filename,start_frame,fps,num_frames):
    # exit if it exists already
    existing = Movie.objects.filter(name=moviename)
    if len(existing)!=0:
        print("not adding, found "+moviename)
        return

    crickets = Cricket.objects.filter(name=cricketname)
    if len(crickets)>0:
        print("adding "+moviename)
        m = Movie(cricket = crickets[0],
                  name = moviename,
                  created_date = timezone.now(),
                  status = 0,
                  src_index_file = index_filename,
                  start_frame = start_frame,
                  fps = fps,
                  length_frames = num_frames)
        m.save()
        # find and connect, or make new burrow here
        update_burrow_with_movie(m)
    else:
        print("add movie error, could not find cricket:"+cricketname)

def set_movie_status(moviename,status):
    try:
        existing = Movie.objects.get(name=moviename)
        existing.status = status
        existing.save()
        return True
    except Movie.DoesNotExist:
        return False

def get_movie_status(moviename):
    try:
        existing = Movie.objects.get(name=moviename)
        return existing.status
    except Movie.DoesNotExist:
        return -1

# don't process, just add django records with state set to 0
def add_movie_record(path,subdir,start,frames,fps):
    sf = os.path.splitext(path)
    moviename = sf[0]+".generic.sfs"
    so = os.path.splitext(os.path.basename(path))
    outname = subdir+"/"+so[0]+"-"+str(start)
    add_movie("Unknown",outname,path,start,fps,len(frames))

# calculate frames and generate django records
def add_movie_records_from_index(duration,fps,path,subdir):
    frames = robot.exicatcher.read_index(path)
    num_frames = len(frames)
    seg_length = int(round(duration*fps)) # ideal length
    num_segs = num_frames/seg_length
    #print("leftover frames:"+str(num_frames%seg_length))
    # adjust length to include all frames (if it doesn't quite match)
    #print("seg length:"+str(seg_length))
    #print("num segs:"+str(num_segs))
    for segnum in range(0,num_segs):
        start = segnum*seg_length
        end = start+seg_length
        if segnum==num_segs-1: # is this the last segment?
            # extend to end of the video
            end = num_frames
            #print("extending: "+str(end-start)+" frames")

        add_movie_record(path,subdir,start,frames[start:end],fps)


def update_video_status():
    for movie in Movie.objects.all():
        if robot.process.check_done(movie.name):
            if not robot.process.check_video_lengths(movie.name):
                print("movies too short: "+movie.name)
                # force redo
                set_movie_status(movie.name,0)
            elif movie.status == 0:
                print("found a movie turned off good files, turning on: "+movie.name)
                set_movie_status(movie.name,1)

        if not robot.process.check_done(movie.name) and movie.status == 1:
            print("!!! found a movie turned ON without files, turning off: "+movie.name)
            set_movie_status(movie.name,0)

def update_burrows():
    for movie in Movie.objects.all():
        update_burrow_with_movie(movie)


def shuffle_burrows():
    poslist = []
    for burrow in Burrow.objects.all():
        print(burrow.name)
        p = find_new_location(poslist)
        poslist.append(p)
        burrow.pos_x = p[0]
        burrow.pos_y = p[1]
        burrow.save()


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


def process_random_video():
    # pick a random one, also checks already processed ones
    make_video(random_one(Movie))

#################################################################
## video process which need access to django...

# calculate frames and actually do the work, set movie state
def make_video(movie):
    print("making "+movie.name)
    frames = robot.exicatcher.read_index(movie.src_index_file)
    frames = frames[movie.start_frame:movie.start_frame+movie.length_frames]
    moviename = os.path.splitext(movie.src_index_file)[0]+".generic.sfs"
    outname = movie.name
    # check django record exists

    # check subdirectory exists and create it if not
    if not os.path.exists(robot.settings.dest_root+movie.burrow.name):
        os.makedirs(robot.settings.dest_root+movie.burrow.name)

    # trust the status, so will overwrite existing files
    if movie.status==0:
        robot.exicatcher.extract(moviename, frames, "frames/frame", False)
        robot.process.renamer(movie.start_frame,movie.length_frames)
        robot.process.create_thumb(movie.name)
        robot.process.run_converter(movie.name,movie.fps)
        robot.process.delete_frames()
        movie.status = 1
        movie.save()
    else:
        #print(outname+": status is 1 - is already done...?")
        # status is 1 so check files actually exist..
        if not robot.process.check_done(movie.name):
            print("status is 1 but no files, setting status to 0, will get next time")
            movie.status = 0
            movie.save()

#########################################################################
# updating data from player activity, expensive stuff to do every few mins

def update_crickets_activity():
    print("crickets...")
    for cricket in Cricket.objects.all():
        #print("cricket:"+str(cricket))
        fans = Event.objects.filter(movie__cricket=cricket)\
                            .exclude(user__isnull=True)\
                            .values('user__username')\
                            .annotate(count=Count('user'))\
                            .order_by('-count')
        if len(fans)>0:
            cricket.biggest_fan=fans[0]["user__username"]
            print("biggest fan is: "+cricket.biggest_fan)
        cricket.num_contributors = len(fans)
        print("with "+str(cricket.num_contributors)+" contributors")
        cricket.total_events = Event.objects.filter(movie__cricket=cricket).count()
        print("total events: "+str(cricket.total_events))
        cricket.save()

def update_burrows_activity():
    print("burrows...")
    for burrow in Burrow.objects.all():
        fans = Event.objects.filter(movie__burrow=burrow)\
                            .exclude(user__isnull=True)\
                            .values('user__username')\
                            .annotate(count=Count('user'))\
                            .order_by('-count')
        if len(fans)>0:
            burrow.biggest_contributor=fans[0]["user__username"]
        burrow.num_contributors = len(fans)
        #print("with "+str(cricket.num_contributors)+" contributors")
        burrow.total_events = Event.objects.filter(movie__burrow=burrow).count()
        burrow.num_movies = Movie.objects.filter(burrow=burrow).count()
        burrow.num_movies_ready = Movie.objects.filter(burrow=burrow,status=1).count()
        #print("total events: "+str(cricket.total_events))
        burrow.save()

def update_movies_activity():
    print("movies...")
    for movie in Movie.objects.all():
        num_events = Event.objects.filter(movie=movie).count()
        if movie.num_events != num_events:
            movie.num_events = num_events
            movie.save()

def update_all_activity():
    update_crickets_activity()
    update_burrows_activity()
    update_movies_activity()