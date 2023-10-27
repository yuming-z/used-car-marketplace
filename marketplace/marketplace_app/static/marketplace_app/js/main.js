// Our timer for refreshing the whole page every 60 seconds.
setTimeout(function(){ window.location.reload(); }, 60000);

// star rating
$('.star').on('click', function() {
    const rating = $(this).data('rating');
    const description = $(this).data('description');
    const descriptionElement = $('#selected-description');
    
    $('.star').removeClass('selected-star');
    $(this).addClass('selected-star');
    $(this).prevAll().addClass('selected-star');

    descriptionElement.text(description);
    $('[name="rating"]').val(rating);

    $('<input>').attr({
        type: 'hidden',
        name: 'rating',
        value: rating
    }).appendTo('form');
});

