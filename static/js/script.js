function multiply(data, koef){
    var multiplied = [];
    for (i=0; i < data.length; i++){
        multiplied.push(Math.round(data[i] * koef));
    }
    return multiplied;
}


$(function(){
    App = {
        jStartX: $('[name="start-point-x"]'),
        jStartY: $('[name="start-point-y"]'),
        jEndX: $('[name="end-point-x"]'),
        jEndY: $('[name="end-point-y"]'),
        jImage: $('#last-snapshot'),
        isInitialCrop: true,
        BOTH_DIMENSIONS: 2000,

        init: function(){
            $('#get-image button').click(function(){
                $('form')[0].action = 'http://pxls.pautuzin.by/im';
            });

            $('#get-gif button').click(function(){
                $('form')[0].action = 'http://pxls.pautuzin.by/gif';
            });

            this.fit_viewport();

            var app = this;
            this.jImage.Jcrop({
                onChange: this.cropIsChanged.bind(this),
                onSelect: this.stopCropping.bind(this),
            }, function(){
                app.jcrop_api = this;
                app.setCropByInputs();
            });

            $('form input[type="number"]').bind('input', this.setCropByInputs.bind(this));
        },

        stopCropping: function (e){
            this.cropIsChanged(e);
            if (this.isInitialCrop){
                this.isInitialCrop = false;
                return;
            }
            $('html, body').animate({
                scrollTop: $("#header").offset().top
            }, 200);
        },

        cropIsChanged: function(e){
            var coordinates = this.toApiCoordinates([e.x, e.y, e.x2, e.y2]);
            if (!this.areCorrectCoordinates(coordinates)) return;
            this.jStartX.val(coordinates[0]);
            this.jStartY.val(coordinates[1]);
            this.jEndX.val(coordinates[2]);
            this.jEndY.val(coordinates[3]);
        },

        setCropByInputs: function (){
            if (!this.jcrop_api) return;
            var coords = this.toThumbnailCoordinates([
                this.jStartX.val(), this.jStartY.val(), this.jEndX.val(), this.jEndY.val()
            ]);

            if (!this.areCorrectCoordinates(coords)){
                this.jcrop_api.release();
                return;
            }

            this.jcrop_api.setSelect(coords);
        },

        isCorrectCoordinate: function (str_coordinate){
            var int_coordinate = parseInt(str_coordinate);
            return ;
        },

        areCorrectCoordinates: function (coordinates){
            int_coordinates = [];
            for (i=0; i< coordinates.length; i++){
                int_coordinates.push(parseInt(coordinates[i]));
            }

            for (coord in int_coordinates){
                if (!((0 <= coord) && (coord < this.BOTH_DIMENSIONS))) return;
            }

            if (int_coordinates[0] > int_coordinates[2] || int_coordinates[1] > int_coordinates[3]) return;

            return true;
        },

        fit_viewport: function (){
            var doubleMargin = this.jImage.outerWidth(true) - this.jImage.outerWidth();

            var width = $(window).width() - doubleMargin;

            if (width >= this.BOTH_DIMENSIONS){
                this.thumbnail = null;
                this.jImage.attr('src', this.jImage.data('url'));
            } else {
                this.jImage.attr('width', width);
                this.thumbnail = width / this.BOTH_DIMENSIONS;
                this.jImage.attr('src', this.jImage.data('url') + '?thumbnail=' + this.thumbnail);
            }
        },

        toApiCoordinates: function(coordinates) {
            if (this.thumbnail){
                return this.clearApiCoordinates(multiply(coordinates, 1 / this.thumbnail));
            }

            return coordinates;
        },

        toThumbnailCoordinates: function(coordinates) {
            return this.thumbnail ? multiply(coordinates, this.thumbnail): coordinates;
        },

        clearApiCoordinates: function(int_coordinates){
            var clearedCoordinates = [];
            for (i=0; i< int_coordinates.length; i++){
                if (int_coordinates[i] < 0){
                    clearedCoordinates.push(0);
                } else if (int_coordinates[i] >= this.BOTH_DIMENSIONS) {
                    clearedCoordinates.push(this.BOTH_DIMENSIONS - 1);
                } else {
                    clearedCoordinates.push(int_coordinates[i]);
                }
            }
            return clearedCoordinates;
        }
    }
    App.init();
});
