(function($) {

	"use strict";

	var fullHeight = function() {

		$('.js-fullheight').css('height', $(window).height());
		$(window).resize(function(){
			$('.js-fullheight').css('height', $(window).height());
		});

	};
	fullHeight();

	$(".toggle-password").click(function() {

	  $(this).toggleClass("fa-eye fa-eye-slash");
	  var input = $($(this).attr("toggle"));
	  if (input.attr("type") == "password") {
	    input.attr("type", "text");
	  } else {
	    input.attr("type", "password");
	  }
	});

})(jQuery);

window.onload = function () {
	var message = document.getElementById("message");
	if (message) {
	  message.style.display = "block";
	  setTimeout(function () {
		message.style.display = "none";
	  }, 3000);
	}
  };


// ************************Google login************************************

function handleCredentialResponse(response) {
	const responsePayload = decodeJwtResponse(response.credential);
	
	const userData = {
		email: responsePayload.email,
		givenName: responsePayload.given_name,
		familyName: responsePayload.family_name,
		Email_verified: responsePayload.email_verified
	};
	
fetch("https://localhost:5000/google_signup", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(userData)
})
.then(response => {
	// Redirect the user to the dashboard page
	window.location.href = "https://localhost:5000/login?state=logged_in";
})
}
function decodeJwtResponse(data){
   var tokens = data.split(".");
   return JSON.parse(atob(tokens[1]));
}  

// ***********************Facebook login setup******************************************

function checkLoginState() {
	FB.login(function(response) {
		if (response.authResponse) {
			var access_token = response.authResponse.accessToken;
			FB.api('/me', {fields: 'name,email'}, function(response) {
				sendUserInfo(access_token, response.name, response.email);
			});
			
		} else {
			console.log('User cancelled login or did not fully authorize.');
		}
	}, {scope: 'public_profile,email'});
}

function sendUserInfo(access_token, name, email) {
	var xhr = new XMLHttpRequest();
	var url = '/facebook_signup';
	var params = 'access_token=' + access_token + '&name=' + name + '&email=' + email;
	xhr.open('POST', url, true);
	xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhr.onreadystatechange = function() {
		if(xhr.readyState == 4 && xhr.status == 200) {
		var response = JSON.parse(xhr.responseText);
		if (response.result === 'success') {
			// Redirect user to index page
			window.location.href = "https://localhost:5000/login?state=logged_in";
		} else if (response.result === 'existing_user') {
			// User already exists, redirect to index page
			window.location.href = "https://localhost:5000/login?state=logged_in";
		}
		}
	}
	xhr.send(params);
	}
	  

	function logout() {
		FB.getLoginStatus(function(response) {
			if (response.status === 'connected') {
				FB.logout(function(response) {
					console.log(response);
					// Clear user data from session
					sessionStorage.clear();
					// Redirect to login page
					window.location.href = "https://localhost:5000/login";
				});
			} 
		});
	}
	