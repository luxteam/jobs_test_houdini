window.onload = function WindowLoad(event) {
    var tables = $('.twoSetupTimes')
    Array.prototype.forEach.call(tables, function(table) {
        $('#' + table.id).on('column-switch.bs.table', function () {
            hiddenColumns = $('#' + table.id).bootstrapTable('getHiddenColumns').map(function (it) {return it.field}) // get string with hidden columns
            if (JSON.stringify(hiddenColumns).indexOf('setupTime') < 0){ // if setup time column is shown
                $(this).bootstrapTable('showColumn', 'fullTimeTaken')
                $(this).bootstrapTable('hideColumn', 'syncTimeTaken')
            }else{
                $(this).bootstrapTable('hideColumn', 'fullTimeTaken')
                $(this).bootstrapTable('showColumn', 'syncTimeTaken')
            }
        })
    })
}

/**
 * Function for sorting test results by status. Uses 'data-sorter' attribute by bootstrap tables.
 * Case statuses (from highest to lowest sort priority):
 * - error - crash during test execution
 * - failed - pixel/time/ram diff too large
 * - passed - case executed without crushes; acceptable diff
 * - skipped - case wasn't launched
 */
function statusSorter(x, y) {
    var a = x.toLowerCase();
    var b = y.toLowerCase();

    if (a === b) return 0;

    if (a.includes('error')) {
        return -1;
    }

    if (a.includes('failed') && !b.includes('error')) {
        return -1;
    }

    if (a.includes('passed') && !b.includes('failed') && !b.includes('error')) {
        return -1;
    }

    return 1;
}

window.openFullImgSize = {
    'click img': function(e, value, row, index) {
        var renderImg = document.getElementById('renderedImgPopup');
        var baselineImg = document.getElementById('baselineImgPopup');

        document.getElementById('pairComparisonDiv').style.display = "";
        document.getElementsByName('increaseImgSizeButton')[0].disabled = false;
        document.getElementsByName('reduceImgSizeButton')[0].disabled = false;

        renderImg.src = "";
        baselineImg.src = "";

        var src_prefixes = ["thumb64_", "thumb256_"];
        renderImg.src = row.rendered_img.split('"')[1];

        if (row.baseline_img.includes("img")) {
            baselineImg.src = row.baseline_img.split('"')[1];
        }
        for (var i in src_prefixes) {
            renderImg.src = renderImg.src.replace(src_prefixes[i], "");
            if (row.baseline_img.includes("img")) {
                baselineImg.src = baselineImg.src.replace(src_prefixes[i], "");
            }
        }

        document.getElementById("imgsCompareTable").style.display = "";
        document.getElementById("imgsDiffTable").style.display = "none";
        document.getElementById('imgsDiffTable').is_reshalla = undefined;
        document.getElementById('thresholdRange').style.display = "none";
        document.getElementById('thresholdView').style.display = "none";

        openModalWindow('imgsModal');
    }
}

function metaAJAX(value, row, index, field) {
    return value.replace('data-src', 'src');
}

window.copyTestCaseName = {
    'click button': function(e, value, row, index) {

        try {
            var node = document.createElement('input');
            var current_url = window.location.href;
            var url_parser = new URL(current_url);
            if (url_parser.searchParams.get("searchText")) {
                url_parser.searchParams.delete("searchText");
            }
            url_parser.searchParams.set("searchText", row.test_case);

            // duct tape for clipboard correct work
            node.setAttribute('value', url_parser.toString());
            document.body.appendChild(node);
            node.select();
            document.execCommand('copy');
            node.remove();
            // popup with status for user
            infoBox("Link copied to clipboard.")
        } catch(e) {
            infoBox("Can't copy to clipboard.")
        }
    }
}

function performanceNormalizeFormatter(value, row, index, field) {
    for (key in row) {
        if (isFinite(parseFloat((value * 100 / row[key]).toFixed(2)))) {
            return (value * 100 / row[key]).toFixed(2) + " %"
        }
    }
    return "Skipped"
}

function performanceNormalizeStyleFormatter(value, row, index, field) {
    var values = [];
    for (key in row) {
        if (key != 0 && !isNaN(parseInt(key))) {
            if (isFinite(parseFloat(row[key]))) {values.push(parseFloat(row[key]))}
        }
    }

    var opacity = parseFloat(value) === 0.0 ? 0 : 1;
    var min = Math.min.apply(Math, values),
    ratio = (Math.max.apply(Math, values) - min) / 100;

    value = Math.round((value - min) / ratio);

    return {
        classes: "",
        css: {"background-color": getGreenToRed(value, opacity)}
    };
}

function getGreenToRed(percent, opacity){
    rmax = 209;
    rmin = 128;
    gmax = 209;
    gmin = 117;
    bmax = 155;
    bmin = 85;
    r = Math.floor((rmax - rmin) * percent / 100 + rmin);
    g = Math.floor((gmax - gmin) * (100 - percent) / 100 + gmin);
    b = Math.floor((bmax - bmin) * (100 - percent) / 100 + bmin);
    return 'rgb(' + r + ',' + g + ',' + b + ',' + opacity + ')';
}

function searchTextInBootstrapTable(status) {
    $('.jsTableWrapper [id]').bootstrapTable('resetSearch', status);
}