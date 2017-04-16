$(function(){
    $('#get-image button').click(function(){
        $('form')[0].action = 'http://pxls.pautuzin.by/im';
    });

    $('#get-gif button').click(function(){
        $('form')[0].action = 'http://pxls.pautuzin.by/gif';
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
