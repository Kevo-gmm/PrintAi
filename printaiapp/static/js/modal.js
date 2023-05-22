// $(function() {
//   var imagesPerPage = 9;
//   var pageCount = Math.ceil({{ images|length }} / imagesPerPage);

//   var currentPage = 1;
//   var firstIndex = 0;
//   var lastIndex = imagesPerPage - 1;

//   function showPage(page) {
//       var container = $('#image-container');
//       container.find('.col').hide();

//       var startIndex = (page - 1) * imagesPerPage;
//       var endIndex = startIndex + imagesPerPage - 1;

//       container.find('.col').slice(startIndex, endIndex + 1).show();
//   }

//   showPage(currentPage);

//   $('.pagination').on('click', 'a.page-link', function(event) {
//       event.preventDefault();

//       var target = $(event.target);
//       var page = target.text();

//       if (page === 'Previous') {
//           if (currentPage > 1) {
//               currentPage--;
//           }
//       } else if (page === 'Next') {
//           if (currentPage < pageCount) {
//               currentPage++;
//           }
//       } else {
//           currentPage = parseInt(page);
//       }

//       showPage(currentPage);

//       $('.pagination .active').removeClass('active');
//       $('.pagination li:nth-child(' + (currentPage + 1) + ')').addClass('active');
//   });
// });

// $(document).ready(function() {
//   $('.use-button').click(function() {
//     var image_url = $(this).data('image');
//     var img = new Image();
//     img.onload = function() {
//       var max_width = $('#box1').width();
//       var max_height = $('#box1').height();
//       var width = img.width;
//       var height = img.height;
//       if (width > max_width) {
//         height *= max_width / width;
//         width = max_width;
//       }
//       if (height > max_height) {
//         width *= max_height / height;
//         height = max_height;
//       }
//       $('#box1').html('<img src="' + image_url + '" width="' + width + '" height="' + height + '">');
//     };
//     img.src = image_url;
//   });
// });

// // Get a reference to the "Use" buttons
// var useButtons = document.querySelectorAll('.custom-btn');

// // Add a click event listener to each "Use" button
// useButtons.forEach(function(button) {
//   button.addEventListener('click', function(event) {
//     // Prevent the default form submission behavior
//     event.preventDefault();
//     // Get the image URL of the clicked image
//     var imageUrl = button.parentNode.parentNode.querySelector('.card-img-top').src;
//     // Set the image source in Box 1
//     document.getElementById('selected-image').src = imageUrl;
//     // Show the modal
//     $('#largeModal').modal('show');
//   });
// });

// // Get a reference to the "Use" buttons
// var useButtons = document.querySelectorAll('.custom-btn');

// // Add a click event listener to each "Use" button
// useButtons.forEach(function (button) {
//   button.addEventListener('click', function (event) {
//     // Prevent the default form submission behavior
//     event.preventDefault();
//     // Get the image URL of the clicked image
//     var imageUrl = button.parentNode.parentNode.querySelector('.card-img-top').src;
//     // Set the image source in Box 1
//     document.getElementById('selected-image').src = imageUrl;

//     // Send the image URL to Printful to create a mockup
//     var url = '/mock';
//     var params = { image_url: imageUrl };
//     fetch(url, {
//       method: 'POST',
//       body: JSON.stringify(params),
//       headers: {
//         'Content-Type': 'application/json'
//       }
//     })
//       .then(response => response.json())
//       .then(data => {
//         // Set the mockup image source in Box 2
//         document.getElementById('mockup-image').src = data.mockup_url;
//         // Show the modal
//         $('#largeModal').modal('show');
//       });
//   });
// });

// Get a reference to the "Use" buttons
var useButtons = document.querySelectorAll(".custom-btn");

// Add a click event listener to each "Use" button
useButtons.forEach(function (button) {
  button.addEventListener("click", function (event) {
    // Prevent the default form submission behavior
    event.preventDefault();
    // Get the image URL of the clicked image
    var imageUrl = button.parentNode.parentNode.querySelector(".card-img-top").src;
    // Set the image source in Box 1
    document.getElementById("selected-image").src = imageUrl;
    // Show the modal
    $("#largeModal").modal("show");
  });
});

$(document).ready(function () {
  // Show/hide items based on gender selection
  $("#gender-select").on("change", function () {
    var gender = $(this).val();
    $("#male-items, #female-items").hide();
    $("#" + gender + "-items").show();
    // Reset selected item to first item in the list
    $("#" + gender + "-item-select").prop("selectedIndex", 0);
  });
  // Set initial state to show male items
  $("#male-items").show();
});

// Add event listener to "Design" button
$("#design-button").click(function () {
  // Show loading button
  $("#design-button").html('<i class="fa fa-spinner fa-spin"></i> Designing...');

  // Retrieve image URL and product/variant IDs
  var imageUrl = $("#selected-image").attr("src");
  var gender = $("#gender-select").val();
  var selectedItem = $("#" + gender + "-item-select option:selected");
  var productId = selectedItem.data("product-id");
  var variantId = selectedItem.data("variant-id");

  // Send data to "/mock" route
  $.ajax({
    type: "POST",
    url: "/mock",
    data: JSON.stringify({
      image_url: imageUrl,
      product_id: productId,
      variant_id: variantId,
    }),
    contentType: "application/json",
  })
    .done(function (data) {
      // console.log('Mockup URL:', data.mockup_url);
      window.location.href =
        "/mock_display?mockup_url=" +
        data.mockup_url +
        "&product_info=" +
        encodeURIComponent(JSON.stringify(data.product_info)) +
        "&variant=" +
        encodeURIComponent(JSON.stringify(data.variant));
      // Reset gender selection and item selection
      $("#gender-select").val("male");
      $("#male-items, #female-items").hide();
      $("#male-items").show();
      $("#" + gender + "-item-select").prop("selectedIndex", 0);
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
      console.error("Error:", errorThrown);
    })
    .always(function () {
      // Hide loading button
      $("#design-button").html("Design");
    });
});

// Add event listener to modal close button
$("#largeModal").on("hidden.bs.modal", function () {
  // Reset gender selection and item selection
  $("#gender-select").val("male");
  $("#male-items, #female-items").hide();
  $("#male-items").show();
  $("#" + gender + "-item-select").prop("selectedIndex", 0);
});
