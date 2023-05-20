$(document).ready(function () {
    // #When the "Use" button is clicked, update the preview image in the modal
    $('.use-button').click(function () {
        var imageUrl = $(this).data('image');
        $('#selected-image').attr('src', imageUrl);
    });

    // When the gender selection is changed, update the item dropdown menu
        $(document).ready(function() {
        // Select the male option by default
        $('#gender-select').val('male');

        // Show male items and hide female items
        $('#male-items').show();
        $('#female-items').hide();

        // Change items when the gender is selected
        $('#gender-select').change(function () {
            var gender = $(this).val();
            if (gender === 'male') {
            $('#male-items').show();
            $('#female-items').hide();
            } else {
            $('#male-items').hide();
            $('#female-items').show();
            }
        });

        $('#design-button').click(function () {
            
            $('#design-button').html('<i class="fa fa-spinner fa-spin"></i> Designing...');
            var image_url = $('#selected-image').attr('src');
            var product_id = $('#male-item-select option:selected').data('product-id');
            var variant_id = $('#male-item-select option:selected').data('variant-id');

            console.log('image_url:', image_url);
            console.log('product_id:', product_id);
            console.log('variant_id:', variant_id);

           $.ajax({
                url: '/mock',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    image_url: image_url,
                    product_id: product_id,
                    variant_id: variant_id
                }),
                success: function (data) {
                    console.log(data);
                    var mockup_url = encodeURIComponent(data.mockup_url);
                    var product_info = encodeURIComponent(JSON.stringify(data.product_info));
                    var variant = encodeURIComponent(JSON.stringify(data.variant));
                    window.location.href = '/mock_display?mockup_url=' + mockup_url + '&product_info=' + product_info + '&variant=' + variant;
                }
            });
        });
        });
});
