$(function(){
    $('#gen-image button').click(function(){
        this.action = '/im';
    });

    $('#gen-gif button').click(function(){
        this.action = '/gif';
    });

    $('#last-snapshot').Jcrop({
        onChange: cropIsChanged,
        onSelect: stopCropping,
    });
});

function cropIsChanged(e){
    $('[name="start-point-x"]').val(e.x);
    $('[name="start-point-y"]').val(e.y);
    $('[name="end-point-x"]').val(e.x2);
    $('[name="end-point-y"]').val(e.y2);
}

function stopCropping(e){
    cropIsChanged(e);
    $('html, body').animate({
        scrollTop: $("form").offset().top
    }, 200);
}
