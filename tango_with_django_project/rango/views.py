from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Template
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query
from django.shortcuts import redirect
import json
from rango.functions import *

def redirecting(request):
	return redirect('/rango/')

def index(request):
    # # Construct a dictionary to pass to the template engine as its context.
    # # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    # context_dict = {'boldmessage': "I am bold font from the context"}

    # # Return a rendered response to send to the client.
    # # We make use of the shortcut function to make our lives easier.
    # # Note that the first parameter is the template we wish to use.

    # return render(request, 'rango/index.html', context_dict)
    # ========================================================

	# Query the database for a list of ALL categories currently stored.
	# Order the categories by no. likes in descending order.
	# Retrieve the top 5 only - or all if less than 5.
	# Place the list in our context_dict dictionary which will be passed to the template engine.
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]
	context_dict = {'categories': category_list, 'pages': page_list}

	# # Render the response and send it back!
	# return render(request, 'rango/index.html', context_dict)

	# scenario cookie 1
	# # Get the number of visits to the site.
	# # We use the COOKIES.get() function to obtain the visits cookie.
	# # If the cookie exists, the value returned is casted to an integer.
	# # If the cookie doesn't exist, we default to zero and cast that.
	# visits = int(request.COOKIES.get('visits', '0'))
	# reset_last_visit_time = False

	# # Does the cookie last_visit exist?
	# if 'last_visit' in request.COOKIES:
	# 	# Yes it does! Get the cookie's value.
	# 	last_visit = request.COOKIES['last_visit']
	# 	# Cast the value to a Python date/time object.
	# 	last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

	# 	# If it's been more than a day since the last visit...
	# 	if(datetime.now() - last_visit_time).days > 0:
	# 		visits = visits + 1
	# 		# ...and flag that the cookie last visit needs to be updated
	# 		reset_last_visit_time = True
	# else:
	# 	# Cookie last_visit doesn't exist, so flag that it should be set.
	# 	reset_last_visit_time = True
	
	# context_dict['visits'] = visits

	# # Obtain our Response object early so we can add cookie information.
	# response = render(request, 'rango/index.html', context_dict)
	# if reset_last_visit_time:
	# 	response.set_cookie('last_visit', datetime.now())
	# 	response.set_cookie('visits', visits)

	# # Return response back to the user, updating any cookies that need changed.
	# return response

	#scenario cookie 2 (in session)
	visits = request.session.get('visits')
	if not visits:
		visits = 0
	reset_last_visit_time = False

	last_visit = request.session.get('last_visit')
	if last_visit:
		last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
		if (datetime.now() - last_visit_time).seconds > 0:
			# ...reassign the value of the cookie to +1 of what it was before...
			visits = visits + 1
			# ...and update the last visit cookie, too.
			reset_last_visit_time = True

	else:
		# Cookie last_visit doesn't exist, so create it to the current date/time.
		reset_last_visit_time = True

	context_dict['visits'] = visits
	request.session['visits'] = visits
	if reset_last_visit_time:
		request.session['last_visit'] = str(datetime.now())

	response = render(request, 'rango/index.html', context_dict)
	return response

def about(request):
	if request.session.get('visits'):
		visits = request.session.get('visits')
	else:
		visits = 0

	context_dict = {}
	context_dict['visits'] = visits
	context_dict['myword'] = {'wordme': "hai hai hai this is abut page"}
	return render(request, 'rango/about.html', context_dict)

@login_required
def category(request, category_name_slug):
	context_dict = {}

	result_list = []
	if request.method == 'POST':
		q = request.POST['query'].strip()
		if q:
			# for result in Category.objects.filter(name__contains=q).order_by('-name'):
			# 	result_list.append({
			# 		'name': result.name
			# 		})
			result_list = Category.objects.filter(name__icontains=q).order_by('name')
			context_dict['query'] = q
			context_dict['result_list'] = result_list
			#result_list = Category.objects.get(name__contains=q)
	try:
		# Can we find a category name slug with the given name?
		# If we can't, the .get() method raises a DoesNotExist exception.
		# So the .get() method returns one model instance or raises an exception.
		category = Category.objects.get(slug=category_name_slug)
		context_dict['category_name']=category.name

		# Retrieve all of the associated pages.
		# Note that filter returns >= 1 model instance.
		pages = Page.objects.filter(category=category).order_by('-views')

		# Adds our results list to the template context under name pages.
		context_dict['pages'] = pages

		# We also add the category object from the database to the context dictionary.
		# We'll use this in the template to verify that the category exists.
		context_dict['category'] = category

		category.views += 1
		category.save()
		
	except Category.DoesNotExist:

		# We get here if we didn't find the specified category.
		# Don't do anything - the template displays the "no category" message for us.
		pass

	# Go render the response and return it to the client.
	return render(request, 'rango/category.html', context_dict)

@login_required
def add_category(request):
	#A HTTP POST?
	if request.method == 'POST':
		form = CategoryForm(request.POST)
		# Have we been provided with a valid form?
		if form.is_valid():
			# Save the new category to the database.
			form.save(commit=True)

			#cat = form.save(commit=True)
			#print cat, cat.slug

			# Now call the index() view.
            # The user will be shown the homepage.
			return index(request)
		else:
			# The supplied form contained errors - just print them to the terminal.
			print form.errors
	else:
		# If the request was not a POST, display the form to enter details.
		form = CategoryForm()

	# Bad form (or form details), no form supplied...
	# Render the form with error messages (if any).
	return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
	context_dict = {}
	try:
		cat = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		cat = False

	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if cat:
				page = form.save(commit=False)
				page.category = cat
				page.views = 0
				page.save()
				# probably better to use a redirect here.
				return category(request, category_name_slug)
			else:
				print form.errors
	else:
		form = PageForm()

	context_dict = {'form':form, 'category':cat}
	
	return render(request, 'rango/add_page.html', context_dict)

def register(request):
	# A boolean value for telling the template whether the registration was successful.
	# Set to False initially. Code changes value to True when registration succeeds.
	registered = False

	# If it's a HTTP POST, we're interested in processing form data.
	if request.method == 'POST':
		# Attempt to grab information from the raw form information.
		# Note that we make use of both UserForm and UserProfileForm.
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		# If the two forms are valid...
		if user_form.is_valid() and profile_form.is_valid():
			# Save the user's form data to the database.
			user = user_form.save()

			# Now we hash the password with the set_password method.
			# Once hashed, we can update the user object.
			user.set_password(user.password)
			user.save()

			# Now sort out the UserProfile instance.
			# Since we need to set the user attribute ourselves, we set commit=False.
			# This delays saving the model until we're ready to avoid integrity problems.
			profile = profile_form.save(commit=False)
			profile.user = user

			# Did the user provide a profile picture?
			# If so, we need to get it from the input form and put it in the UserProfile model.
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			# Now we save the UserProfile model instance.
			profile.save()

			# Update our variable to tell the template registration was successful.
			registered = True

		# Invalid form or forms - mistakes or something else?
		# Print problems to the terminal.
		# They'll also be shown to the user.
		else:
			print user_form.errors, profile_form.errors

	# Not a HTTP POST, so we render our form using two ModelForm instances.
	# These forms will be blank, ready for user input.
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()
 
 	# Render the template depending on the context.
	return render(request, 
			'rango/register.html',
			{'user_form': user_form, 'profile_form':profile_form, 'registered': registered}
		)

def user_login(request):
	# If the request is a HTTP POST, try to pull out the relevant information.
	if request.method == 'POST':
		# Gather the username and password provided by the user.
		# This information is obtained from the login form.
		username = request.POST['username']
		password = request.POST['password'] 

		# Use Django's machinery to attempt to see if the username/password
		# combination is valid - a User object is returned if it is.
		user = authenticate(username=username, password=password)

		# If we have a User object, the details are correct.
		# If None (Python's way of representing the absence of a value), no user
		# with matching credentials was found.
		if user:	
			# Is the account active? It could have been disabled.
			if user.is_active:
				# If the account is valid and active, we can log the user in.
				# We'll send the user back to the homepage.
				login(request, user)
				return HttpResponseRedirect('/rango/')
			
			else:
			# An inactive account was used - no logging in!
				# return HttpResponse("Your Rango Account is disabled<br/><a href="/rango/login/">Back to Login</a>")
				return render(request, 'rango/login.html',
					{'err': 'Your Rango Account is disabled'})
		else:
			# Bad login details were provided. So we can't log the user in.
			print "Invalid login details: {0}, {1}".format(username, password)
			# return HttpResponse('Invalid login details supplied<br/><a href="/rango/login/">Back to Login</a>')

			return render(request, 'rango/login.html',
				{'username': username, 'err': 'invalid username or password'})

	# The request is not a HTTP POST, so display the login form.
	# This scenario would most likely be a HTTP GET.
	else:
		# No context variables to pass to the template system, hence the
		# blank dictionary object...
		return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
	return HttpResponse("Since you're logged in, you can see this text!")

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
	# Since we know the user is logged in, we can now just log them out.
	logout(request)

	# Take the user back to the homepage.
	return HttpResponseRedirect('/rango/')

def search(request):
	result_list = []
	if request.method == 'POST':
		q = request.POST['query'].strip()
		if q:
			result_list = run_query(q)

	return render(request, 'rango/search.html', {'result_list': result_list})

def track_url(request, page_id):
	# if request.method == 'GET':
	# 	if 'page_id' in request.GET:
			# page_id = request.GET['page_id'].strip()
	# pages = Page.objects.filter(id=page_id)
	# if pages:
	# 	for page in pages:
	# 		page.views += 1
	# 		page.save()
	# 	return HttpResponseRedirect(page.url)
	# return HttpResponseRedirect('/rango/')
	url = '/rango/'
	try:
		page = Page.objects.get(id=page_id)
		page.views += 1
		page.save()
		url = page.url
	except:
		pass
	return redirect(url)

def register_profile(request):
	return render(request, 'registration/profile_registration.html', {})

def profile(request):
	return render(request, 'rango/profile.html', {})

@login_required
def like_category(request):
	cat_id = None
	if request.method == 'GET':
		cat_id = request.GET['category_id']
		print cat_id

	response_data = {}
	if cat_id:
		try:
			cat = Category.objects.get(id=int(cat_id))
			if cat:
				print cat.name
				cat.likes += 1
				cat.save()
				response_data['likes'] = cat.likes
				response_data['success'] = True
		except:
			return False
			response_data['likes'] = 0
			response_data['success'] = False
	return HttpResponse(json.dumps(response_data), content_type="application/json")

def suggest_category(request):
	cat_list = []
	starts_with = ''

	if request.method == 'GET':
		starts_with = request.GET['suggestion']

	cat_list = get_category_list(8, starts_with)
	return render(request, 'rango/cats.html', {'cats': cat_list})