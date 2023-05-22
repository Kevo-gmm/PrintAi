import json
from math import ceil
import os
import warnings
from stability_sdk import client
from requests import request
from printaiapp import app
from flask import jsonify, render_template, redirect, session, url_for, flash, url_for, request
from printaiapp.forms import RegistrationForm , LoginForm
from printaiapp.models import User
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from printaiapp import db 
from .models import  Cart, Products
from flask import request
from werkzeug.utils import secure_filename
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from werkzeug.utils import secure_filename
from printaiapp import db, app
from .models import Image_gen
import random
import requests
import time
from dotenv import load_dotenv
import dropbox
from flask import flash
from flask import session, redirect, request, url_for
from flask_mail import Mail
import smtplib
from email.mime.text import MIMEText
import stripe


login_manager = LoginManager(app)



# create a mail instance
mail = Mail(app)

@login_manager.unauthorized_handler
def unauthorized():
    session['next_url'] = request.path
    return redirect(url_for('login_page', next=request.url))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Testing image upload
UPLOAD_FOLDER = 'printaiapp/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load the Dropbox access token from the .env file
load_dotenv()
dbx_access_token = os.environ.get('DROPBOX_ACCESS_TOKEN')

# Create an instance of the Dropbox client
dbx = dropbox.Dropbox(dbx_access_token)



@app.route("/home")
@app.route("/index")
@app.route('/')
def index():
    if current_user.is_authenticated:
        cart_items = Cart.query.filter_by(user_id=current_user.user_id).all()
        cart_item_count = len(cart_items) 
        status = session.get("status", None)
        return render_template("index.html", state="logged_in", status=status, cart_total_item=cart_item_count)     
    else:
        return render_template("index.html", state="not_logged_in")

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    state = request.args.get('state')
    if state == 'logged_in':
        # session["logged_in"] = True
        # session["status"] = "success"
        # session['user_id'] = attempted_user.user_id
        # current_user = session.get("username", None)
        # welcome = f"Welcome {current_user}!"
        # status = session.get("status", None)
        print("google/fb login success")
        next_url = session.pop('next_url', None) or url_for('index')
        return redirect(next_url)     
    else:
        form = LoginForm()
        if form.validate_on_submit():
            attempted_user = User.query.filter_by(email=form.email.data).first()
            if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
                login_user(attempted_user)
                session["logged_in"] = True
                session["status"] = "success"
                session['user_id'] = attempted_user.user_id
                next_url = session.pop('next_url', None) or url_for('index')
                return redirect(next_url)
            
            else: 
                session["status"] = "fail"
                return render_template('login.html', form=form, status="fail")
                # login_status = ('Email or password is  wrong! Please try again')
        session['next_url'] = request.args.get('next')
        return render_template('login.html', form=form, status=None)    
        
@app.route('/logout',)
@login_required
def logout_page():
    logout_user()
    # flash("You have successfully logout!", category='info')
    return redirect(url_for("login_page"))

@app.route("/register" , methods=['GET', 'POST'])
@app.route("/signup" , methods=['GET', 'POST'])
def register():
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists in database
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            session["status"] = "registered"
            # Redirect to login page with a message
            return redirect(url_for('login_page', status="registered"))
        
        remote_address = get_remote_address()
        user_to_create = User(
            first_name = form.first_name.data,
            last_name = form.last_name.data,
            username = form.username.data,
            email = form.email.data,
            password = form.password1.data,
            ip_address=remote_address,
            is_verified=False
        )
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        # flash(f'Successfully logged in as:{user_to_create.username}', category='success')
        
        # generate a random verification code
        verification_code = random.randint(100000, 999999)
        print(verification_code)
        # store the code in the session for later verification
        session['verification_code'] = verification_code
        
        
        # send verification email
        recipients = user_to_create.email
        subject = 'PRINTAI Email Verification Code'
        body = f'Your verification code is: {verification_code}'
        email_confirmation_url = send_email(recipients, subject, body, verification_code)
        return redirect(email_confirmation_url)
    
    if form.errors != {}: #if there are errors from validation
        session['status'] = "fail"
        for err_msg in form.errors.values():
            # print(form.errors)
            err_msg = list(form.errors.values())[0][0]
        return render_template('signup.html', form=form, status="fail", err_msg=err_msg)
    return render_template('signup.html', form=form, status=None)
   
def send_email(recipients, subject, body, verification_code):
    sender_email = "slynganga59@gmail.com"
    sender_password = "hyoelflnumbhtvfv"
    recipient_email = recipients

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = recipient_email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())
    session["status"] = "emailsent"
    print('email sent')    
    return url_for('email_confirmation', email=recipient_email)
       
@app.route("/email_confirmation/<email>" , methods=['GET', 'POST'])
def email_confirmation(email):
    if request.method == 'POST':
        user = User.query.filter_by(email=email).first()
        # get the verification code entered by the user
        code = request.form['verification_code']
        # get the verification code from the session
        stored_code = session.get('verification_code')
        # compare the codes
        if user.is_verified is False and code == str(stored_code):
            # verification successful, redirect to the index page
            user.is_verified = True
            db.session.commit()
            session["status"] = "verified"
            return redirect(url_for('index', state='logged_in'))
        else:
            session["status"] = "verification_err"
            # verification failed, show an error message
            # flash('Verification code is invalid.')
            return render_template('email_confirmation.html', status="verification_err", email=email)
    # if it's a GET request, render the verification page
    return render_template('email_confirmation.html', title='Email Confirmation', email=email)


@app.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Email does not exist. Please register.")
            return redirect(url_for('register'))

        # Generate and store reset key
        reset_key = str(random.randint(100000, 999999))
        session['reset_key'] = reset_key
        session['email'] = email

        # Send email to user
        subject = "Password Reset"
        body = f"Your password reset key is {reset_key}."
        
        sender_email = "slynganga59@gmail.com"
        sender_password = "hyoelflnumbhtvfv"
        recipient_email = user.email

        message = MIMEText(body)
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = recipient_email

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        session["status"] = "emailsent"
        print(reset_key)
        print('reset key email sent')
        return redirect(url_for('forgot_password_email_confirmation', email=recipient_email))
    return render_template('forgetpassword.html', title='Forgot Password')


@app.route("/forgot_password_email_confirmation/<email>" , methods=['GET', 'POST'])
def forgot_password_email_confirmation(email):
    if request.method == 'POST':
        # get the reset key entered by the user
        key = request.form['reset_key']
        # get the reset key from the session
        stored_code = session.get('reset_key')
        print(stored_code)
        # compare the codes
        if key == str(stored_code):
            session["status"] = "reset-approved"
            print("reset approved")
            return redirect(url_for('reset_password', email=email, status="reset-approved"))
        else:
            session["status"] = "reset_approve_err"
            print("reset approve error")
            return render_template('forgot_password_email_confirmation.html', status="reset_approve_err", email=email)
    # if it's a GET request, render the verification page
    return render_template('forgot_password_email_confirmation.html', title='Forgot Password Email Confirmation', email=email)

@app.route("/reset_password/<email>", methods=['GET', 'POST'])
def reset_password(email):
    if request.method == 'POST':
        # get the new password and confirm password entered by the user
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # check if the passwords match
        if password == confirm_password:
            # get the user from the database and update their password
            user = User.query.filter_by(email=email).first()
            # user.password = generate_password_hash(password, method='sha256')
            user.password = password
            db.session.commit()
            
            # redirect to login page
            print("password has been successfully updated")
            return redirect(url_for('login_page'))
        else:
            # passwords do not match, show an error message
            print('Passwords do not match')
            return redirect(url_for('new_password.html', email=email))

    return render_template('new_password.html', title='Reset Password', email=email)



@app.route("/policy" , methods=["GET", "POST"])
def policy():
    return ("privacy_policy")


@app.route('/google_signup', methods=['POST'])
def google_signup():
    user_data = request.get_json()
    remote_address = get_remote_address()
   
     # Check if user with email already exists
    existing_user = User.query.filter_by(email=user_data['email']).first()

    if existing_user:
        print("Google user already exists")
        login_user(existing_user)
        # Update session with existing user's information
        session["logged_in"] = True
        session["user_id"] = existing_user.user_id
        session["username"] = existing_user.username
        
        # flash(f'Successfully logged in as:{existing_user.username}', category='success')
        return redirect(url_for('index', current_user=existing_user.username))
    else:
        user_to_create = User(
            first_name = user_data['givenName'],
            last_name = user_data['familyName'],
            username = user_data['givenName'],
            email = user_data['email'],
            password = "88888888",  #set by default but user can reset
            ip_address=remote_address,
            is_verified=user_data['Email_verified']
        )
        db.session.add(user_to_create)
        db.session.commit()
        print("new google user created")
        
        login_user(user_to_create)
        # Update session with new user's information
        session["logged_in"] = True
        session["user_id"] = user_to_create.user_id
        session["username"] = user_to_create.username

        return jsonify({'result': 'success'})
    
    
@app.route('/facebook_signup', methods=['POST'])
def facebook_signup():
    # user_data = request.get_json()
    remote_address = get_remote_address()
   
     # Check if user with email already exists
    existing_user = User.query.filter_by(email=request.form['email']).first()

    if existing_user:
        print("FB user already exists")
        login_user(existing_user)
        # Update session with existing user's information
        session["logged_in"] = True
        session["user_id"] = existing_user.user_id
        session["username"] = existing_user.username
        print(existing_user.username)

        # flash(f'Successfully logged in as:{existing_user.username}', category='success')
        return jsonify({'result': 'success'})
    else:
        user_to_create = User(
            # first_name = request.form['name'],
            # last_name = request.form['email'],
            username = request.form['name'],
            email = request.form['email'],
            password = "88888888",
            ip_address=remote_address,
            is_verified=True
        )
        db.session.add(user_to_create)
        db.session.commit()
        print("New FB user created")
        login_user(user_to_create)

        
        # Update session with new user's information
        session["logged_in"] = True
        session["user_id"] = user_to_create.user_id
        session["username"] = user_to_create.username

        return jsonify({'result': 'success'})


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    try:
        # retrieve user object from the database using the ID stored in the session
        # user = User.query.get(session.get('user_id'))
        item_quantity = int(request.form.get('item_quantity', 1))
        product_name = request.form.get('product_name')
        mockup_url = request.form.get('mockup_url')
        variant_id = request.form.get('variant_id')
        print(product_name)


        product = Products.query.filter(Products.product_name.ilike(product_name)).first()
        if not product:
            return "Product not found"

        items_to_create = Cart(
            name=product_name,
            quantity=item_quantity,
            price=product.price,
            variant_id=variant_id,
            product_id=product.product_id,
            product_unique_id=product.unique_id,
            total_price=round(product.price * int(item_quantity), 2),
            mockup_url=mockup_url,
            user_id=current_user.user_id
        )
        db.session.add(items_to_create)
        db.session.commit()
    except AttributeError:
        return redirect(url_for('login_page', next=request.url))
    return redirect(url_for('view_cart'))

# set the quantity
@app.route("/set_quantity/<int:item_id>", methods=["POST"])
def set_quantity(item_id):
    try:
        # retrieve user object from the database using the ID stored in the session
        user = User.query.get(session.get('user_id'))

        item = Cart.query.get(item_id)
        item_quantity = request.form.get('quantity')
    except AttributeError:
        return redirect(url_for('login_page', next=request.url))
    
    # check if the quantity is a positive integer or zero
    if item_quantity.isdigit() and int(item_quantity) >= 0:
        item.quantity = int(item_quantity)
        db.session.commit(),
        return redirect(url_for('update_total_price', item_id=item_id, user=user))
    else:
        # return an error message if the quantity is not a positive integer or zero
        return "Error: Quantity must be a positive integer or zero."

# Total as per quanity
@app.route("/update_total_price/<int:item_id>", methods=["GET","POST"])
def update_total_price(item_id):
    item = Cart.query.get(item_id)
    item_quantity = item.quantity
    total_price = item.price * int(item_quantity)
    item.total_price = total_price
    db.session.commit()
    return redirect(url_for('view_cart'))

# View the cart
@app.route('/view_cart')
def view_cart():
    try:
        # retrieve user object from the database using the ID stored in the session
        # user = User.query.get(session.get('user_id'))
        items = Cart.query.filter_by(user_id=current_user.user_id).all()
        total = round(sum(item.total_price for item in items), 2)
        mockup_url = request.args.get('mockup_url')
        product_info = request.args.get('product_info')
    except AttributeError:
        return redirect(url_for('login_page', next=request.url))    
    return render_template('view_cart.html', items=items, total=total, mockup_url=mockup_url, product_info=product_info)

# Remove item from the cart
@app.route('/remove_item/<int:item_id>', methods=["POST"])
@login_required
def remove_item(item_id):
    # retrieve user object from the database using the ID stored in the session
    # user = User.query.get(session.get('user_id'))

    item = Cart.query.get(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('view_cart'))

# Empty the whole cart function
def empty_cart():
    items = Cart.query.filter_by(user_id=current_user.user_id).all()
    for item in items:
        db.session.delete(item)
    db.session.commit()

@app.route('/empty_cart', methods=["POST"])
def empty():
    try:
        # retrieve user object from the database using the ID stored in the session
        user = User.query.get(session.get('user_id'))
        empty_cart()
    except AttributeError:
        return redirect(url_for('login_page', next=request.url))
    return redirect(url_for('view_cart'))

# Display image Unique images in explore
@app.route("/explore")
def display_images():
    cart_item_count = None
    if current_user.is_authenticated:
        state="logged_in"
        cart_items = Cart.query.filter_by(user_id=current_user.user_id).all()
        cart_item_count = len(cart_items)
    else:
        state="not_logged_in"
    
    page = request.args.get('page', 1, type=int)  # get the page number from the request arguments
    per_page = 6  # Number of images per page
    search_query = request.args.get('search', '').strip()

    if search_query:
            # Use the search query to filter images by prompt
            images = Image_gen.query.filter(Image_gen.prompt.like(f'%{search_query}%')) \
                                .order_by(Image_gen.image_id.desc()) \
                                .paginate(page=page, per_page=per_page)

    else:
            images = Image_gen.query.order_by(Image_gen.image_id.desc()).paginate(page=page, per_page=per_page)
    
    images_by_prompt = {}
    for image in images.items:
        prompt = image.prompt
        if prompt not in images_by_prompt:
            images_by_prompt[prompt] = []
        images_by_prompt[prompt].append(image)
        
    num_pages = ceil(images.total / per_page)
     
    return render_template("explore.html", images_by_prompt=images_by_prompt, images=images,  page=page, per_page=per_page, num_pages=num_pages, search_query=search_query, state=state, cart_total_item=cart_item_count, next=request.url)

@app.template_filter()
def jinja2_max(value, arg):
    return max(value, arg)

@app.template_filter()
def jinja2_min(value, arg):
    return min(value, arg)


# Generate Image
@app.route('/generate', methods=["GET", "POST"])
def gen_image():
    if current_user.is_authenticated:
        state="logged_in"
        cart_items = Cart.query.filter_by(user_id=current_user.user_id).all()
        cart_item_count = len(cart_items) 
    else:
        state="not_logged_in"
  
    if request.method == "GET":
        return render_template("index.html")

    os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
    os.environ['STABILITY_KEY'] = 'sk-uwqZVM7n8yyZUkChDQ0FrjGzVB8ofnz0H8PDWauaPwymarHL'
    stability_api = client.StabilityInference(
        key=os.environ['STABILITY_KEY'],
        verbose=True,
        engine="stable-diffusion-v1-5"
    )

    seed = random.randint(0, 2**32 - 1)
    answers = stability_api.generate(
        prompt = request.form.get("prompt"),
        seed=seed,
        steps=30,
        cfg_scale=7.0,
        width=512,
        height=512,
        samples=4,
        sampler=generation.SAMPLER_K_DPMPP_2M
    )

    images = []
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed. Please modify the prompt and try again.")
                continue
            if artifact.type == generation.ARTIFACT_IMAGE:
                for i in range(1):
                    filename = secure_filename(str(artifact.seed)) + '_' + str(i) + '.png'
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    with open(file_path, 'wb') as f:
                        f.write(artifact.binary)
                    # Upload the image to Dropbox
                    try:
                        with open(file_path, 'rb') as f:
                            dbx.files_upload(f.read(), '/' + filename)
                        image_url = dbx.sharing_create_shared_link('/' + filename).url.replace('?dl=0', '?raw=1')
                    except Exception as e:
                        return('Generate a new dropbox access token.!!!')
                        print('=============================ERROR============================')
                        print(e)
                        # return str(e)
                    try:
                        # retrieve user object from the database using the ID stored in the session
                        user = User.query.get(session.get('user_id'))
                        
                        image = Image_gen(image_url=image_url, seed=filename, prompt=request.form.get("prompt"), creator_id=current_user.user_id)
                    except AttributeError:
                        return redirect(url_for('login_page')) 
                    
                    images.append(image)        
    db.session.add_all(images)
    db.session.commit()
    print(f"Number of images: {len(images)}")
    return render_template('index.html', images=images, user=user, state=state, cart_total_item=cart_item_count, next=request.url)



#  print the mockup of an image
@app.route('/mock', methods=['GET', 'POST'])
def mock():
    if request.method == 'POST':
         # Get the image URL from the request data
         # Get the image URL and product/variant IDs from the request data
        image_url = request.json['image_url']
        product_id = request.json['product_id']
        variant_id = request.json['variant_id']
        # image_url = request.json['image_url']
        print(image_url)
        print(product_id)
        print(variant_id)

        # Replace "www.dropbox.com/s/" with "dl.dropboxusercontent.com/s/" and add "?raw=1" at the end
        image_url = image_url.replace("www.dropbox.com/s/", "dl.dropboxusercontent.com/s/") + "?raw=1"

        # Call the Printful API to create a mockup
        url = 'https://api.printful.com/mockup-generator/create-task/' + str(product_id)
        access_token = '4uwDoH3qCB8mkX0Hh90CGm8EGFpjkvCjKYba4Evr'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # All the product placements
        product_placements = {
            # T-shirt
            '328': {
                '9957': {
                    'type': 'front',
                    'image_url': image_url,
                    'position': {
                        'area_width': 600,
                        'area_height': 900,
                        'width': 300,
                        'height': 400,
                        'top': 350,
                        'left': 150
                    },
                },
            },
            # Organic Cotton T-shirt
            '623': {
                '16058': {
                    'type': 'front',
                    'image_url': image_url,
                    'position': {
                        'area_width': 2100,
                        'area_height': 2100,
                        'width': 2100,
                        'height': 2100,
                        'top': 50,
                        'left': 50
                    },
                },
            },
            # Hoodie
            '522': {
                '13107': {
                    'type': 'front',
                    'image_url': image_url,
                    'position': {
                        'area_width': 2100,
                        'area_height': 2100,
                        'width': 2100,
                        'height': 2100,
                        'top': 50,
                        'left': 50
                    },
                },
            },
            # Tank-top
            '248': {
                '8628': {
                    'type': 'front',
                    'image_url': image_url,
                    'position': {
                        'area_width': 2100,
                        'area_height': 2100,
                        'width': 2100,
                        'height': 2100,
                        'top': 50,
                        'left': 50
                    },
                },
            },
            # long sleeve tee
            '511': {
                '12869': {
                    'type': 'front',
                    'image_url': image_url,
                    'position': {
                        'area_width': 2100,
                        'area_height': 2100,
                        'width': 2100,
                        'height': 2100,
                        'top': 50,
                        'left': 50
                    },
                },
            },
            # unisex hoodie
            '380': {
                '10779': {
                    'type': 'front',
                    'image_url': image_url,
                    'position': {
                        'area_width': 2100,
                        'area_height': 2100,
                        'width': 2100,
                        'height': 2100,
                        'top': 50,
                        'left': 50
                    },
                },
            },
            # sweat shirt
            '411': {
                '11254': {
                    'type': 'front',
                    'image_url': image_url,
                    'position': {
                        'area_width': 2200,
                        'area_height': 2200,
                        'width': 2200,
                        'height': 2200,
                        'top': 50,
                        'left': 50
                    },
                },
            },
            # Iphone case
            '181': {
                '16240': {
                    'type': 'default',
                    'image_url': image_url,
                    'position': {
                        'area_width': 1800,
                        'area_height': 1800,
                        'width': 1800,
                        'height': 1800,
                        'top': 0,
                        'left': 0
                    },
                },
            },
            # mouse pad
            '518': {
                '13097': {
                    'type': 'default',
                    'image_url': image_url,
                    'position': {
                        'area_width': 700,
                        'area_height': 700,
                        'width': 700,
                        'height': 700,
                        'top': 0,
                        'left': 0
                    },
                },
            },
            # mug 
            '19': {
                '1320': {
                    'type': 'default',
                    'image_url': image_url,
                    'position': {
                        'area_width': 2700,
                        'area_height': 1050,
                        'width': 2700,
                        'height': 1050,
                        'top': 0,
                        'left': 100
                    },
                },
            },
            # framed canvas
            '614': {
                '16034': {
                    'type': 'default',
                    'image_url': image_url,
                    'position': {
                        'area_width': 5500,
                        'area_height': 6700,
                        'width': 5700,
                        'height': 6900,
                        'top': 0,
                        'left': 0
                    },
                },
            },
            # Canvas
            '3': {
                '823': {
                    'type': 'default',
                    'image_url': image_url,
                    'position': {
                        'area_width': 12600,
                        'area_height': 9000,
                        'width': 12600,
                        'height': 9000,
                        'top': 0,
                        'left': 0
                    },
                },
            },
            # women rackback
            '163': {
                '6651': {
                    'type': 'front',
                    'image_url': image_url,
                    'position': {
                        'area_width': 700,
                        'area_height': 700,
                        'width': 700,
                        'height': 700,
                        'top': 50,
                        'left': 50
                    },
                },
            },
             # Hoodie dress
            '448': {
                '11698': {
                    'type': 'front',
                    'image_url': image_url,
                    'position': {
                        'area_width': 2100,
                        'area_height': 2100,
                        'width': 2000,
                        'height': 2100,
                        'top': 50,
                        'left': 0
                    },
                },
            },
            # Hoodie dress
            '526': {
                '13285': {
                    'type': 'front',
                    'image_url': image_url,
                    'position': {
                        'area_width': 2100,
                        'area_height': 2100,
                        'width': 2000,
                        'height': 2100,
                        'top': 50,
                        'left': 0
                    },
                },
            },
        }
        # Use the product and variant IDs to get the placement information
        placement_info = product_placements.get(str(product_id), {}).get(str(variant_id), {})

        # image placement
        # Add the placement information to the data dictionary
        data = {
            'variant_ids': variant_id,
            'files': [
                placement_info
            ]
        }

        response = requests.post(url, headers=headers, json=data)
        print(response.text)
        task_key = response.json()['result']['task_key']
        print(response)
        print(task_key)
       

        # Poll the Printful API until the mockup is ready
        while True:
            response = requests.get(f'https://api.printful.com/mockup-generator/task?task_key={task_key}', headers=headers)
            result = response.json()['result']
            if result['status'] == 'completed':
                mockup_url = result['mockups'][0]['mockup_url']
                # Get the product info
                print(mockup_url)
                url = f'https://api.printful.com/products/{product_id}'
                response = requests.get(url, headers=headers)
                product_info = response.json()['result']


                # Create a new Products object
                variant = next((v for v in product_info['variants'] if v['id'] == variant_id), None)
                product = Products.create_from_variant(variant, product_id=product_id)

                # Add the product to the database
                db.session.add(product)
                db.session.commit()

                data = {
                    'mockup_url': mockup_url,
                    'product_info': product_info,
                    'variant': variant
                }
                return jsonify(data)
                
            else:
                time.sleep(1)

@app.route('/mock_display', methods=['GET', 'POST'])
# @login_required
def mock_display():
    mockup_url = request.args.get('mockup_url')
    product_info = json.loads(request.args.get('product_info'))
    variant = json.loads(request.args.get('variant'))
    product = Products.query.filter_by(product_id=variant["product_id"]).first()
    try:
        if request.method == 'POST':
            product_id = request.form['product_id']
            product_name = request.form['product_name'].encode('utf-8')
            item_quantity = 1  # default quantity
            items_to_create = Cart(
                name=product_name,
                quantity=item_quantity,
                price=product.price,
                product_id=product_id,
                total_price=round(product.price * int(item_quantity), 2)
            )
            db.session.add(items_to_create)
            db.session.commit()
            print(product_id)
            flash('Product added to cart', 'success')
            return redirect(url_for('mock_display', mockup_url=mockup_url, product_info=product_info, variant=variant))
        cart_items = Cart.query.filter_by(user_id=current_user.user_id).all()
        cart_item_count = len(cart_items) 
    except AttributeError:
        return redirect(url_for('login_page', next=request.url))
    
    return render_template('mock.html', mockup_url=mockup_url, product_info=product_info, variant=variant, product=product, cart_total_item=cart_item_count, next=request.url)

# order from
@app.route('/order')
def order():
    return render_template('address_page.html')

@app.route('/cart_items', methods=['GET'])
def get_cart_items():
    # Retrieve user object from the database using the ID stored in the session
    # user = User.query.get(session.get('user_id'))

    # Retrieve all cart items for the current user
    cart_items = Cart.query.filter_by(user_id=current_user.user_id).all()
    print(cart_items)
    
    # Create a list of cart item dictionaries to return as JSON
    cart_items_list = []
    for item in cart_items:
        cart_item = {
            'name': item.name,
            'quantity': item.quantity,
            'price': item.price,
            'product_id': item.product_id,
            'variant_id': item.variant_id,
            'total_price': item.total_price,
            'mockup_url': item.mockup_url
        }
        cart_items_list.append(cart_item)
    
    # Return the cart items as JSON
    return jsonify(cart_items_list)

stripe.api_key = 'sk_test_51MgYUeKNg9R7a1OxvgPAHxob2nTHwF1VbnM103xXLB5btxcjMfwFZqHJI1C59RxpxtGTIuA9l617VV3mAfdrnKe900JRYlEqPT'

# printful create order and stripe payment
@app.route('/create_order', methods=['POST'])
def create_order():
    # Get shipping address and cart items from request data
    shipping_info = {
        'name': request.form['name'],
        'address1': request.form['address1'],
        'city': request.form['city'],
        'state': request.form['state'],
        'country': request.form['country'],
        'zip': request.form['zip']
    }
    cart_items = Cart.query.filter_by(user_id=current_user.user_id).all()
    total_price = sum([cart_item.total_price for cart_item in cart_items])

    # Create items list for Printful API order
    items = []

    for cart_item in cart_items:
        # Get product info and variants from the Printful API
        product_id = cart_item.product_id
        variant_id = cart_item.variant_id
        mockup_url = cart_item.mockup_url
        price = cart_item.price

        item = {
            'product_id': product_id,
            'variant_id': variant_id,
            'quantity': 1,
            'files': [
                {
                    'type': 'default',
                    'url': mockup_url
                }
            ],
            'options': {
                'stitch_color': 'white'
            }
        }
        items.append(item)
    # Create order object for Printful API
    order = {
        'recipient': {
            'name': shipping_info['name'],
            'address1': shipping_info['address1'],
            'city': shipping_info['city'],
            'state_code': shipping_info['state'],
            'country_code': shipping_info['country'],
            'zip': shipping_info['zip']
        },
        'items': items
    }

    # Call Printful API to create the order
    access_token = '4uwDoH3qCB8mkX0Hh90CGm8EGFpjkvCjKYba4Evr'
    headers = {'Authorization': f'Bearer {access_token}'}
    orders_url = 'https://api.printful.com/orders'
    orders_response = requests.post(orders_url, headers=headers, json=order)
    response_data = orders_response.json()

    # Get order ID from Printful API response
    order_id = response_data['result']['id']

    if orders_response.status_code == 200:
        # Create Stripe checkout session with total price
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Cart Total',
                    },
                    'unit_amount': int(total_price * 100), # convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('success', _external=True)
        )
        return redirect(session.url, code=303)
    else:
        return jsonify({'message': 'Failed to create order'})

# success message
@app.route('/success')
def success():
    empty_cart()
    return  render_template('success.html')

