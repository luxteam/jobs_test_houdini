var carouselTask;

function setActive(elem) {
    elem.classList.add('active_header');
}

$.extend($.expr[':'], {
  'containsCI': function(elem, i, match, array)
  {
    return (elem.textContent || elem.innerText || '').toLowerCase()
    .indexOf((match[3] || "").toLowerCase()) >= 0;
  }
});

function resizeImg(img){
    if (img.style.width == ""){
        img.style.width = "30%";
    }

    if (img.style.width == "30%"){
        img.style.width = "100%";
    } else {
        img.style.width = "30%";
    }
}

function timeFormatterFull(value, row, index, field) {
    if (isFinite(value)) {
        var time = new Date('July 20, 69 00:00:00');
        time.setSeconds(parseInt(value), (parseFloat(value) % 1) * 1000);
        if (!isFinite(time.getSeconds())) {return value;}
        if (time.getHours() > 0){
            return time.getHours() + 'h ' + time.getMinutes() + 'm ' + time.getSeconds() + 's '
        } else {
            return time.getMinutes() + 'm ' + time.getSeconds() + 's ' + time.getMilliseconds() + 'ms'
        }
    }
}

function openModalWindow(id) {
    var modal = document.getElementById(id);
    modal.style.display = "flex";

    var diffCanvas = document.getElementById('imgsDiffTable');
    var imagesTable = document.getElementById("imgsCompareTable");

    if (diffCanvas && diffCanvas.style.display == "block") {
        imagesTable.style.display = "";
        diffCanvas.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
            document.getElementById("imagesCarousel").style.display = "none";
            clearInterval(carouselTask);
        }
    }
}

function closeModalWindow(id) {
    document.getElementById(id).style.display = "none";
    document.getElementById("imagesCarousel").style.display = "none";
    clearInterval(carouselTask);
}

function increaseImgSize() {
    var step = 3.5;
    var imagesSelectorList = [['#imgsDifferenceCanvas', step * 4], ['#renderedImgPopup', step], ['#baselineImgPopup', step]];

    imagesSelectorList.forEach(function(item) {
        $(item[0]).css("width", function( index, value ) {
	        return parseInt(value, 10) + document.documentElement.clientWidth / 100 * item[1];
        });
    });
}

function reduceImgSize() {
    var step = 3.5;
    var imagesSelectorList = [['#imgsDifferenceCanvas', step * 4], ['#renderedImgPopup', step], ['#baselineImgPopup', step]];

    imagesSelectorList.forEach(function(item) {
        $(item[0]).css("width", function( index, value ) {
	        return parseInt(value, 10) - document.documentElement.clientWidth / 100 * item[1];
        });
    });
}

function infoBox(message, bgcolor = false) {
    $("#infoBox").html("<p>" + message + "</p>");
    $("#infoBox").fadeIn('slow');
    if (bgcolor) {
        $("#infoBox").css({
            "background-color": bgcolor,
            "opacity": 0.4
            });
    }

    setTimeout(function(){$("#infoBox").fadeOut('slow');} , 2000);
}

function getQueryVariable(variable) {
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i=0; i < vars.length; i++) {
        var pair = vars[i].split("=");
        if(pair[0] === variable) {
            return pair[1];
        }
    }
    return(false);
}

jQuery(document).ready( function() {
    var searchText = getQueryVariable('searchText');
    if (searchText) {
        $('.jsTableWrapper [id]').bootstrapTable('resetSearch', searchText);
    }
});

$(document).ready(function init(){
    $( "h3:containsCI('NVIDIA')" ).css( "color", "rgba(118, 185, 0, 1)" );
    $( "table.baseTable th:containsCI('NVIDIA')" ).css( "color", "rgba(118, 185, 0, 1)" );
    $( "h3:containsCI('GeForce')" ).css( "color", "rgba(118, 185, 0, 1)"
    );
    $( "table.baseTable th:containsCI('GeForce')" ).css( "color", "rgba(118, 185, 0, 1)" );

    $( "h3:containsCI('Radeon')" ).css( "color", "rgba(92, 136, 200, 1)" );
    $( "table.baseTable th:containsCI('Radeon')" ).css( "color", "rgba(92, 136, 200, 1)" );
    $( "h3:containsCI('AMD')" ).css( "color", "rgba(92, 136, 200, 1)" );
    $( "table.baseTable th:containsCI('AMD')" ).css( "color", "rgba(92, 136, 200, 1)" );
});


// TODO: upgrade Bootstrap
//TODO: upgrade Bootstrap-table

function showCarousel(baselineId, renderId) {

    if (!($("#baselineImgPopup").attr('src') && $("#renderedImgPopup").attr('src'))) {
        infoBox("[Error] Can't read source image.", "#9b5e61");
        return;
    }

    var carousel = document.getElementById('imagesCarousel');
    var pairComparisonDiv = document.getElementById('pairComparisonDiv');
    var increaseButton = document.getElementsByName('increaseImgSizeButton')[0];
    var reduceButton = document.getElementsByName('reduceImgSizeButton')[0];
    document.getElementById('thresholdRange').style.display = "none";
    document.getElementById('thresholdView').style.display = "none";

    if (carousel.style.display === "none") {
        carousel.style.display = "block";
        pairComparisonDiv.style.display = "none";
        increaseButton.disabled = true;
        reduceButton.disabled = true;
    }
    else {
        carousel.style.display = "none";
        pairComparisonDiv.style.display = "";
        increaseButton.disabled = false;
        reduceButton.disabled = false;
        clearInterval(carouselTask);
        return;
    }

    var renderImg = document.getElementById(renderId);
    var baselineImg = document.getElementById(baselineId);
    var showImg = document.getElementById('imagesCarouselImg');

    showImg.src = baselineImg.src;

    carouselTask = setInterval(function(){
        setTimeout(function(){showImg.src = renderImg.src;}, 300);
        setTimeout(function(){showImg.src = baselineImg.src;}, 600);
    }, 1200);
}