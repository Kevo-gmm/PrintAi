# PrintAI

CLONE THE APP AND TO RUN IT python3 run.py

By using localhost `http://localhost:<port>` as the 'Authorized JavaScript Origins' field in the Google API Console, the following error will prevent you from using Google authentication:

> Error parsing configuration from HTML: Unsecured login_uri provided.

Google and facebook login require secured login_uri `https`

When using localhost for development and testing purposes, you can use a self-signed SSL certificate to secure the connection.

I've already loaded the certificate `cert.pem` and private key `key.pem` files and configured Flask to use the certificate, so all you need to do is:

- copy the certificate file `cert.pem` to the `/usr/local/share/ca-certificates` directory: `sudo cp /path-to-cert/cert.pem /usr/local/share/ca-certificates/`
- Update the trusted certificates: `sudo update-ca-certificates
`
- Restart the app, localhost should now run in `https`

## Guide:

### login:

- Google signup: Go to the Google Developers Console and create a new project.
- At the create credentials dropdown, choose OAuth Client ID
- Select application type which is Web application
- At authorized Javascript origins add urls to your web application
- After entering all the details, you will be provided with a client ID which you need to replace
  at this line in the login and signup html:  
   data-client_id="360177023512-3hut95jc7shfr2dv7bjl8v6q0bnr32d6.apps.googleusercontent.com"
- Also setup OAuth consent screen at the Developers console : requests authorizations for one or more scopes of access from a Google Account.

- Facebook also requires you to signup
- Go to the Facebook for Developers website and create a new account. Create a new app in your account by going to the "My Apps" section and selecting "Add New App".
- Within your app settings, go to the "Settings" section and configure the basic settings, such as the app name, contact email, and privacy policy URL. Also, add the domains that your app will be hosted on in the "App Domains" section.
- Create Facebook Login credentials: Within your app settings, go to the "Facebook Login" section and configure the settings, such as the "Valid OAuth redirect URIs". Also, create the Facebook Login credentials by going to the "Settings" section and selecting "Basic".
- Then, copy the App ID and App Secret values.

## Functions:

## add_to_cart route:

This Python Flask app contains a route named add_to_cart that handles a POST request for adding an item to the user's cart.

- _Functionality_:

When a POST request is sent to the add_to_cart route, the function first attempts to retrieve the user object from the database using the ID stored in the user's session. If there is no user ID in the session, the user is redirected to the login page.

The function then retrieves the item_quantity, product_name, mockup_url, and variant_id from the POST request form. It then queries the database to check if the product exists in the Products table, using the product_name field. If the product is not found, the function returns a string "Product not found".

If the product is found, the function creates a new Cart object with the given product details, including the user ID, and adds it to the database. The function then redirects the user to the view_cart route.

- Inputs
  The add_to_cart route expects a POST request with the following form fields:

item_quantity: the quantity of the product to be added to the cart (optional, default value is 1)
product_name: the name of the product to be added to the cart
mockup_url: the URL of the mockup image for the product (optional)
variant_id: the ID of the product variant (optional)
Outputs

If the product is not found, the function returns a string "Product not found". Otherwise, the function redirects the user to the view_cart route.

## set_quantity route

This Python Flask app contains a route named set_quantity that handles a POST request for setting the quantity of an item in the user's cart.

- _Functionality_:

When a POST request is sent to the set_quantity route, the function first attempts to retrieve the user object from the database using the ID stored in the user's session. If there is no user ID in the session, the user is redirected to the login page.

The function then retrieves the item_id parameter from the URL, and the quantity value from the POST request form. It then queries the database to check if the item exists in the user's cart. If the item is not found, the function returns a string "Item not found".

If the item is found, the function checks if the quantity value is a positive integer or zero. If the quantity is valid, the function updates the quantity field of the item in the database and redirects the user to the update_total_price route.

If the quantity value is not valid, the function returns an error message "Error: Quantity must be a positive integer or zero."

- Inputs
  The set_quantity route expects a POST request with the following form field:

quantity: the new quantity of the item in the cart
The item_id parameter is passed as part of the URL.

- Outputs
  If the item is not found, the function returns a string "Item not found". If the quantity value is not valid, the function returns an error message "Error: Quantity must be a positive integer or zero." Otherwise, the function updates the quantity field of the item in the database and redirects the user to the update_total_price route.

## add items to the cart:

Users can add items to their cart by submitting a form using the /add_to_cart endpoint. The form must include the product name, quantity, mockup URL, and variant ID. The system retrieves the product information from the database and creates a new Cart item with the user ID, product ID, and other information.

## Update item quantity:

Users can update the quantity of an item in their cart by submitting a form using the /set_quantity endpoint. The form must include the new quantity for the item. The system checks that the quantity is a positive integer or zero before updating the item's quantity in the database.

## View the cart:

Users can view the items in their cart by visiting the /view_cart endpoint. The system retrieves all Cart items for the current user and calculates the total price of the items in the cart. The user can also remove individual items from the cart or empty the entire cart.

## display_images route

This Python Flask app contains a route named display_images that renders the explore.html template to display a paginated list of unique images.

- _Functionality_:

The display_images route starts by checking if the current user is authenticated. If the user is authenticated, it retrieves all cart items for that user and gets the cart item count. If the user is not authenticated, the cart item count is set to None.

The function then retrieves the page number from the request arguments and sets the number of images to be displayed per page. It also gets the search query from the request arguments and strips any whitespace.

If there is a search query, the function filters the Image_gen table by the prompt using the search query and orders the images by image ID in descending order. It then paginates the results and assigns them to the images variable.

If there is no search query, the function retrieves all images from the Image_gen table, orders them by image ID in descending order, and paginates the results. The results are assigned to the images variable.

The function then creates a dictionary called images_by_prompt, where each key represents a unique prompt and the value is a list of images that have that prompt.

Finally, the function calculates the number of pages needed to display all the images and passes the necessary variables to the explore.html template, along with the rendered images and prompts dictionary.

- Inputs
  The display_images route expects a GET request with the following query parameters:
  page: the page number of the images to display (optional, default value is 1)
  search: the search query to filter images by prompt (optional)

- Outputs
  The display_images route renders the explore.html template, which displays a paginated list of unique images.

## generate route

This Python Flask app contains a route named generate that handles a POST request for generating an image using the Stability API and uploading it to Dropbox.

- _Functionality_:

When a POST request is sent to the generate route, the function first checks if the user is logged in. If the user is logged in, the function retrieves the user's cart items from the Cart table in the database and calculates the total number of cart items. If the user is not logged in, the function sets the state variable to "not_logged_in".

The function then sets the Stability API credentials and generates an image using the Stability API. The function saves the generated image to the UPLOAD_FOLDER directory on the server and uploads it to Dropbox. The function then creates a new Image_gen object with the image details, including the user ID, and adds it to the database. The function retrieves the user object from the database using the ID stored in the session.

The function then returns the rendered index.html template with the generated images, user, state, and cart_total_item values.

- Inputs
  The generate route expects a POST request with the following form fields:
  prompt: the prompt for generating the image
  Outputs

The function returns the rendered index.html template with the generated images, user, state, and cart_total_item values.

## mock route

This Python Flask app contains a route named mock that handles a POST request for creating a mockup of an image using the Printful API.

- _Functionality_:

When a POST request is sent to the mock route, the function retrieves the image URL, product ID, and variant ID from the request data. It then replaces "www.dropbox.com/s/" with "dl.dropboxusercontent.com/s/" and adds "?raw=1" at the end to ensure that the image is downloaded in its raw format.

The function then calls the Printful API to create a mockup by sending a POST request to the "mockup-generator/create-task" endpoint with the product ID in the URL and the image URL and variant ID in the request body. The function sets the headers with the access token and content type required by the API.

If the API call is successful, the function returns the mockup image URL in the response. If the API call is unsuccessful, the function returns an error message.

- Inputs
  The mock route expects a POST request with the following JSON data:

      {
      "image_url": "<image URL>",
      "product_id": <product ID>,
      "variant_id": <variant ID>
      }

- Outputs
  If the API call is successful, the function returns a JSON response with the mockup image URL:

      {
      "mockup_url": "<mockup image URL>"
      }

If the API call is unsuccessful, the function returns a JSON response with an error message:

    {
    "error": "<error message>"
    }

## mock_display route

This Python Flask app contains a route named mock_display that handles a GET and POST request for displaying a mockup image and adding the product to the user's cart.

- _Functionality_:

When a GET request is sent to the mock_display route, the function retrieves the mockup URL, product information, and variant details from the request arguments. The function also retrieves the product details from the database using the variant's product ID. If the user is logged in, the function retrieves the user's cart items from the Cart table in the database and calculates the total number of cart items. If the user is not logged in, the function redirects to the login page.

The function then renders the mock.html template with the mockup URL, product information, variant details, product, cart_total_item, and the URL to redirect the user after successful login.

When a POST request is sent to the mock_display route, the function retrieves the product ID, product name, and quantity from the form data. The function then creates a new Cart object with the cart item details and adds it to the database. The function then redirects the user to the mock_display route with the same mockup URL, product information, and variant details, and flashes a success message.

- Inputs
  The mock_display route expects a GET request with the following query string parameters:
  mockup_url: the URL of the mockup image to be displayed
  product_info: a JSON string containing the product information
  variant: a JSON string containing the variant details
  The mock_display route expects a POST request with the following form fields:
  product_id: the ID of the product to be added to the cart
  product_name: the name of the product to be added to the cart

- Outputs
  The function returns the rendered mock.html template with the mockup URL, product information, variant details, product, cart_total_item, and the URL to redirect the user after successful login.

## create_order route

This Python Flask app contains a route named create_order that handles a POST request for creating an order using the Printful API and processing a payment using Stripe.

- _Functionality_:

When a POST request is sent to the create_order route, the function retrieves the shipping address and cart items from the request form data. The function then calculates the total price of the cart items.

The function creates a list of items to be added to the Printful API order, looping through each cart item and retrieving the product info and variants from the Printful API. The function creates an item object for each cart item with the product ID, variant ID, mockup URL, and price.

The function then creates an order object for the Printful API with the recipient's shipping address and the items list. The function calls the Printful API to create the order using the order object and retrieves the order ID from the response.

If the Printful API call is successful, the function creates a Stripe checkout session with the total price and redirects the user to the session URL. If the Printful API call fails, the function returns a JSON error message.

- Inputs
  The create_order route expects a POST request with the following form fields:
  name: the name of the recipient
  address1: the recipient's address line 1
  city: the recipient's city
  state: the recipient's state
  country: the recipient's country
  zip: the recipient's zip code

- Outputs
  The function redirects the user to the Stripe checkout session URL if the Printful API call is successful, or returns a JSON error message if the Printful API call fails.
