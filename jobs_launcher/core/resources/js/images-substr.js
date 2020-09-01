function showImagesSubtraction(baselineId, renderId, reshalla) {
    if (!($("#baselineImgPopup").attr('src') && $("#renderedImgPopup").attr('src'))) {
        infoBox("[Error] Can't read source image.", "#9b5e61");
        return;
    }
    document.getElementById('pairComparisonDiv').style.display = "";
    document.getElementsByName('increaseImgSizeButton')[0].disabled = false;
    document.getElementsByName('reduceImgSizeButton')[0].disabled = false;

    var imagesTable = document.getElementById("imgsCompareTable");
    var diffTable = document.getElementById('imgsDiffTable');
    var thresholdRange = document.getElementById('thresholdRange');
    var thresholdView = document.getElementById('thresholdView');
    document.getElementById("imagesCarousel").style.display = "none";

    // if diff image is shown now and its type is same as type of clicked button
    if (diffTable.is_reshalla != undefined && diffTable.is_reshalla == reshalla) {
        imagesTable.style.display = "";
        diffTable.style.display = "none";
        thresholdRange.style.display = "none";
        thresholdView.style.display = "none";
        diffTable.is_reshalla = undefined
        return;
    }

    if(reshalla) {
        thresholdRange.style.display = "none";
        thresholdView.style.display = "none";
        renderCanvasReshalla(baselineId, renderId);
    }
    else {
        thresholdRange.style.display = "";
        thresholdView.style.display = "";
        renderCanvasData(baselineId, renderId, parseFloat(document.getElementById("thresholdRange").getAttribute('value')));
    }

    imagesTable.style.display = "none";
    diffTable.style.display = "";
    diffTable.is_reshalla = reshalla;
}

function renderCanvasData(baselineId, renderId, thresholdValue) {
    document.getElementById('thresholdRange').setAttribute("value", thresholdValue);
    var diffCanvas = document.getElementById('imgsDifferenceCanvas');

    var img1 = document.getElementById(baselineId);
    var img2 = document.getElementById(renderId);

    diffCanvas.width = img1.naturalWidth;
    diffCanvas.height = img1.naturalHeight;

    var ctx = diffCanvas.getContext("2d");
    ctx.clearRect(0, 0, diffCanvas.width, diffCanvas.height);

    ctx.drawImage(img1, 0, 0);
    var imgData1 = ctx.getImageData(0, 0, diffCanvas.width, diffCanvas.height);
    ctx.drawImage(img2, 0, 0);
    var imgData2 = ctx.getImageData(0, 0, diffCanvas.width, diffCanvas.height);

    var diff = ctx.createImageData(diffCanvas.width, diffCanvas.height);
    pixelmatch(imgData1.data, imgData2.data, diff.data, diffCanvas.width, diffCanvas.height, {threshold: thresholdValue});
    ctx.putImageData(diff, 0, 0);
}

function renderCanvasReshalla(baselineId, renderId) {
    var diffCanvas = document.getElementById('imgsDifferenceCanvas');

    var baselineImg = document.getElementById(baselineId);
    var renderedImg = document.getElementById(renderId);

    var renderImgData = cv.imread(renderedImg);
    var baselineImgData = cv.imread(baselineImg);

    var renderImgDataProc = new cv.Mat();
    var baselineImgDataProc = new cv.Mat();

    cv.GaussianBlur(renderImgData, renderImgDataProc, new cv.Size(5, 5), 0, 0, cv.BORDER_DEFAULT);
    cv.GaussianBlur(baselineImgData, baselineImgDataProc, new cv.Size(5, 5), 0, 0, cv.BORDER_DEFAULT);

    var imgDataDiffProc = new cv.Mat();
    cv.absdiff(baselineImgDataProc, renderImgDataProc, imgDataDiffProc);

    var median = new cv.Mat();
    cv.medianBlur(imgDataDiffProc, median, 9);

    var kernel = cv.getStructuringElement(1, new cv.Size(5, 5), new cv.Point(2, 2));
    cv.morphologyEx(median, median, cv.MORPH_CLOSE, kernel);

    cv.cvtColor(median, median, cv.COLOR_BGR2GRAY);
    cv.threshold(median, median, 10, 255, cv.THRESH_BINARY);

    cv.imshow(diffCanvas, median);
};