#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


import dateutil.parser
import babel
from flask import Flask, abort, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import  null, or_

from flask_wtf.csrf import CSRFProtect

from models import db, Artist, Venue, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

migrate = Migrate(app,db)

csrf = CSRFProtect(app)
csrf.init_app(app)

# TODO: connect to a local postgresql database


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # dispaly all venue information on the venue page
  data = []
  venue_locations = Venue.query.order_by(Venue.state, Venue.city).all()

  for venue in venue_locations:
      current_time = datetime.now()
      data.append({
          'city': venue.city,
          'state': venue.state,
          'venues': [{
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len(Show.query.filter_by(venue_id= venue.id).filter(Show.start_time > current_time).all())
            }]
          })
  
  return render_template('pages/venues.html', areas=data);



@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial 

  search_term = request.form.get('search_term', '')

  searchKeyword = f"%{search_term}%"

  # Search venue based on either name, city or state
  searchResults = Venue.query.filter(or_(
                   Venue.name.ilike(searchKeyword),
                   Venue.state.ilike(searchKeyword),
                   Venue.city.ilike(searchKeyword)
                  )).all()
  
  response = {
    "count": len(searchResults),
    "data": searchResults
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id

  venue = Venue.query.get(venue_id)

  currentime = datetime.now()
  
  list_of_past_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time < currentime).all()

  list_0f__upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time > currentime).all()


  past_show_date = Show.query.filter_by(venue_id = venue_id).filter(Show.start_time < currentime).all()

  upcoming_show_date = Show.query.filter_by(venue_id = venue_id).filter(Show.start_time > currentime).all()

  pastShows = []
  upcomingShows = []


  for show in past_show_date:
      artist  = Artist.query.get(show.artist_id)

      show_data ={
        'artist_data': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': f'{show.start_time}'
      }

      pastShows.append(show_data)



  for show in upcoming_show_date:
      artist  = Artist.query.get(show.artist_id)

      show_data ={
        'artist_data': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': f'{show.start_time}'
      }

      upcomingShows.append(show_data)



  venueInfo = {
      'id': venue.id,
      'name': venue.name,
      'city': venue.city,
      'state': venue.state,
      'address': venue.address,
      'phone': venue.phone,
      'image_link': venue.image_link,
      'facebook_link': venue.facebook_link,
      'genres': venue.genres,
      'website_link': venue.website_link,
      'seeking_talent':venue.seeking_talent,
      'seeking_description':venue.seeking_description,
      'past_shows': pastShows,
      'upcomming_shows': upcomingShows,
      'past_shows_count': len(list_of_past_shows),
      'upcoming_shows_count': len(list_0f__upcoming_shows)
    }


  return render_template('pages/show_venue.html', venue=venueInfo)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    try:
       form = VenueForm(request.form, meta={})
       venue = Venue(
           name = form.name.data,
           city = form.city.data,
           state = form.state.data,
           address = form.address.data,
           phone = form.phone.data,
           image_link = form.image_link.data,
           facebook_link = form.facebook_link.data,
           genres = request.form.getlist('genres'),
           website_link = form.website_link.data,
           seeking_talent = 
           True if request.form.get('seeking_talent') else False,
           seeking_description = form.seeking_description.data
          )
       
       db.session.add(venue)
       db.session.commit()
       # on successful db insert, flash success
       flash(f'Venue: {venue.name} was successfully listed!')
    except Exception as e:
       # TODO: on unsuccessful db insert, flash an error instead.
       flash(f'An Error occured creating the Venue {venue.name}, Error: {e}')
       db.session.rollback()
    finally:
       db.session.close()
       return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # fetch all the records from the artist table database 
  artistInfo = Artist.query.all()
  
  return render_template('pages/artists.html', artists=artistInfo)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # implementation of how to search a keyword
  search_term = request.form.get('search_term', '')

  searchKeyword = f"%{search_term.lower()}%"

  # Search artist based on either name, city or state
  searchResults = Artist.query.filter(or_(
                   Artist.name.ilike(searchKeyword),
                   Artist.state.ilike(searchKeyword),
                   Artist.city.ilike(searchKeyword)
                  )).all()
  
  response = {
    "count": len(searchResults),
    "data": searchResults
  }


  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id

  artist  = Artist.query.get(artist_id)

  currentime = datetime.now()
  
  list_of_past_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time < currentime).all()

  list_0f__upcoming_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time > currentime).all()


  past_show_date = Show.query.filter_by(artist_id = artist_id).filter(Show.start_time < currentime).all()

  upcoming_show_date = Show.query.filter_by(artist_id = artist_id).filter(Show.start_time > currentime).all()

  pastShows = []
  upcomingShows = []


  for show in past_show_date:
      venue  = Venue.query.get(show.venue_id)

      show_data ={
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': f'{show.start_time}'
      }

      pastShows.append(show_data)



  for show in upcoming_show_date:
      venue  = Venue.query.get(show.venue_id)

      show_data ={
        'venue_data': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': f'{show.start_time}'
      }

      upcomingShows.append(show_data)

  artistInfo={
    'id': artist.id,
    'name': artist.name,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'genres': [artist.genres],
    'image_link': artist.image_link,
    'facebook_link': artist.facebook_link,
    'website': artist.website_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'past_shows': pastShows,
    'upcomming_shows': upcomingShows,
    'past_shows_count': len(list_of_past_shows),
    'upcoming_shows_count': len(list_0f__upcoming_shows)
  }
  
  return render_template('pages/show_artist.html', artist=artistInfo)

#  Update Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  #Done
  
  artistRecords = Artist.query.get(artist_id)
  form = ArtistForm(obj=artistRecords)

  return render_template('forms/edit_artist.html', form=form, artist=artistRecords)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  #Done
  
      form = ArtistForm(request.form, meta ={})

      artist = Artist.query.get(artist_id)
      try:
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.image_link = form.image_link.data
        artist.facebook_link = form.facebook_link.data
        artist.genres = request.form.getlist('genres')
        artist.website_link = form.website_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
      
        
        db.session.commit()

        flash('Artist ' +request.form['name'] + ' was successfully updated')
      except:
        db.session.rollback()
        flash('An error occured. Artist ' +request.form['name'] + ' could not be successfully updated!')
      finally:
        db.session.close()
        return redirect(url_for('show_artist', artist_id=artist_id))

  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  #Query to get record values from venue with ID <venue_id>
  
  venueRecords = Venue.query.get(venue_id)
  form = VenueForm(obj=venueRecords)
  
  return render_template('forms/edit_venue.html', form=form, venue=venueRecords)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  #Check if the form to be updated is valid and saved to the databse
  
      form = VenueForm(request.form)

      venue = Venue.query.get(venue_id)
      try:
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.image_link = form.image_link.data
        venue.facebook_link = form.facebook_link.data
        venue.genres = request.form.getlist('genres')
        venue.website_link = form.website_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data

        db.session.commit()

        flash('Venue ' +request.form['name'] + ' was successfully updated')
      except:
        db.session.rollback()
        flash('An error occured. Venue ' +request.form['name'] + ' could not be successfully updated!')
      finally:
        db.session.close()
        return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    
    try:
       form = ArtistForm(request.form, meta={})
       artist = Artist(
       name = form.name.data,
       city = form.city.data,
       state = form.state.data,
       phone = form.phone.data,
       image_link = form.image_link.data,
       facebook_link = form.facebook_link.data,
       genres = request.form.getlist('genres'),
       website_link = form.website_link.data,
       seeking_venue = True if request.form.get('seeking_venue') else False,
       seeking_description = form.seeking_description.data

       )
       db.session.add(artist)
       db.session.commit()
        # on successful db insert, flash success
       flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
       db.session.rollback()
       # TODO: on unsuccessful db insert, flash an error instead.
       flash('An Error occured Artist ' + request.form['name'] + ' could not be successfully listed!')
    finally:
       db.session.close()
       return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows

  showsInfo = []

  shows = Show.query.all()

  for show in shows:
    artist = Artist.query.filter_by(id=show.artist_id).first()
    venue = Venue.query.filter_by(id=show.venue_id).first()

    showsInfo.append({
      'artist_id': artist.id,
      'artist_name': artist.name,
      'venue_id': venue.id,
      'venue_name': venue.name,
      'start_time': f"{show.start_time}"
    })

  return render_template('pages/shows.html', shows=showsInfo)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # TODO: insert form data as a new Show record in the db, instead

  form = ShowForm(request.form, meta={})

  if form is not None:
     try:
         artist_id = form.artist_id.data
         venue_id = form.venue_id.data
         start_time = form.start_time.data

         show = Show( venue_id= venue_id,artist_id= artist_id, start_time=start_time)

         db.session.add(show)
         db.session.commit()

         # on successful db insert, flash success
         flash('Show was successfully listed!')
     except:
         db.session.rollback()
        
         flash('An error occurred. Show could not be listed.')
     finally:
         db.session.close()
         return render_template('pages/shows.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
