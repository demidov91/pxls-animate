var jcrop_api;

// width == height
BOTH_DIMENSIONS = 2000

var isInitialCrop = true;

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
    }, function(){
		jcrop_api = this;
		setCropByInputs();
	});

    $('form input[type="number"]').bind('input', setCropByInputs);	
});

function cropIsChanged(e){
	$('[name="start-point-x"]').val(e.x);
    $('[name="start-point-y"]').val(e.y);
    $('[name="end-point-x"]').val(e.x2);
    $('[name="end-point-y"]').val(e.y2);
}

function stopCropping(e){
    cropIsChanged(e);
	if (isInitialCrop){
		isInitialCrop = false;
		return;
	}
    $('html, body').animate({
        scrollTop: $("form").offset().top
    }, 200);
}

function setCropByInputs(){
	if (!jcrop_api) return;
	var x1 = $('[name="start-point-x"]').val();
	var y1 = $('[name="start-point-y"]').val();
	var x2 = $('[name="end-point-x"]').val();
	var y2 = $('[name="end-point-y"]').val();

	var coords = [x1, y1, x2, y2];
	
	if (!areCorrectCoordinates(coords)) return;	

	jcrop_api.setSelect(coords);
}

function isCorrectCoordinate(str_coordinate){
	var int_coordinate = parseInt(str_coordinate);
	return (0 <= int_coordinate) && (int_coordinate < BOTH_DIMENSIONS);	
}

function areCorrectCoordinates(coordinates){
	for (coord in coordinates){
		if (!isCorrectCoordinate(coord)) return;
	}
	return true;
}
