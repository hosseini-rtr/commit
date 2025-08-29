# Social Network Application

A Django-based social media application similar to Twitter/X with features like posts, likes, comments, and user following.

## Project Structure

The application has been refactored into smaller, focused Django apps:

### Apps

1. **users** - User management and authentication

   - User model (extends AbstractUser)
   - Authentication views (login, logout, register)
   - User profile views
   - Templates: login, register, profile

2. **posts** - Post management

   - Post model with text content and image support
   - Post creation, editing, and display views
   - Main index page with pagination
   - Templates: index, layout, components (post_form, posts)

3. **interactions** - User interactions with posts

   - Like, Dislike, and Comment models
   - Like/unlike functionality
   - Comment system
   - AJAX-based interactions

4. **social** - Social features
   - Follow/Unfollow functionality
   - Following feed
   - User relationship management
   - Templates: following

## Features

- **User Authentication**: Register, login, logout
- **Posts**: Create, edit, and view posts with text and images
- **Interactions**: Like/dislike posts, add comments
- **Social Network**: Follow/unfollow users, view following feed
- **User Profiles**: View user profiles with posts and follower counts
- **Responsive Design**: Bootstrap-based UI

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Create superuser: `python manage.py createsuperuser`
5. Run the development server: `python manage.py runserver`

## URL Structure

- `/` - Main posts feed (posts:index)
- `/login` - User login (users:login)
- `/register` - User registration (users:register)
- `/profile/<username>/` - User profile (users:profile)
- `/following_page` - Following feed (social:following_page)
- `/post` - Create new post (posts:post)
- `/edit_post/<id>` - Edit post (posts:edit_post)
- `/like/<id>` - Like/unlike post (interactions:like)

## Models

### Users App

- `User` - Custom user model extending AbstractUser

### Posts App

- `Post` - Post model with author, content, date, and image

### Interactions App

- `Like` - User-post like relationship
- `Dislike` - User-post dislike relationship
- `Comment` - User comments on posts

### Social App

- `Follow` - User following relationships

## Admin Interface

All models are registered in the Django admin with appropriate configurations:

- User management through Django's built-in UserAdmin
- Post management with filtering and search
- Interaction tracking with post content previews
- Follow relationship management

## Static Files

Static files are organized in the `static/social_network/` directory:

- `styles.css` - Main stylesheet
- `logo.png` - Application logo
- `profile.png` - Default profile image

The project uses Django's static file management with:

- `STATICFILES_DIRS` pointing to the project-level `static/` directory
- `STATIC_ROOT` for production deployment
- `collectstatic` command for gathering all static files

## Media Files

User-uploaded images are stored in the `media/` directory with the structure:

- `img/` - Post images

## Development

The project uses Django 3.0+ and follows Django best practices:

- App-specific URLs with namespaces
- Template inheritance and includes
- Model relationships and related names
- AJAX for dynamic interactions
- Bootstrap for responsive design
