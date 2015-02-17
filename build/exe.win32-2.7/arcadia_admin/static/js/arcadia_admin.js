 $(document).on('change', '.btn-file :file', function() {
    var input = $(this),
    numFiles = input.get(0).files ? input.get(0).files.length : 1,
    label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
    input.trigger('fileselect', [numFiles, label]);
    });


    $(".btn_delete_game").click(function() {
        var row_id = $(this).closest('tr').attr('id');
        delete_game(row_id, 0);
    });

    $(".btn_online_search").click(function() {
        var game_id = $(this).closest('tr').attr('id');
        $.getJSON("/game/" + game_id + "/_online_search", function(data){

        });
    });


function delete_game(game_id, platform_id) {
    var p = { game_id:game_id, platform_id:platform_id };
    var params = jQuery.param( p );
    $.getJSON("/_delete_games?" + params, function(data){
        if (data.result = 'OK') {
            if (game_id != '__ALL') {
                $('#' + game_id).hide();
            }
            else {
                location.reload(true);
            }
        };
    });
}

/*
*	Adds or changes a GET parameter
*	See http://stackoverflow.com/a/13064060/703581
*	Adapted to handle '#' in the URL
*   modified by ashley colman to not reload the page but to take a url string and return the url
*/
function setGetParameter(paramName, paramValue, url_to_change="")
{
    var url = url_to_change;
    if (url == "")
	    url = window.location.href;
	var splitAtAnchor = url.split('#');
	url = splitAtAnchor[0];
	var anchor = typeof splitAtAnchor[1] === 'undefined' ? '' : '#' + splitAtAnchor[1];
    if (url.indexOf(paramName + "=") >= 0)
    {
        var prefix = url.substring(0, url.indexOf(paramName));
        var suffix = url.substring(url.indexOf(paramName));
        suffix = suffix.substring(suffix.indexOf("=") + 1);
        suffix = (suffix.indexOf("&") >= 0) ? suffix.substring(suffix.indexOf("&")) : "";
        url = prefix + paramName + "=" + paramValue + suffix;
    }
    else
    {
    if (url.indexOf("?") < 0)
        url += "?" + paramName + "=" + paramValue;
    else
        url += "&" + paramName + "=" + paramValue;
    }
    return url + anchor;
}

/*
*   Changes the sort order by sending Parameter in the url
*/
    $(".sort_order_change").click(function() {
        var sort_order = sessionStorage.sort_order;
        if (sort_order == 'desc') {
            sort_order = 'asc';
            $(this).toggleClass('sort_asc');
        }
        else {
            sort_order = 'desc';
            $(this).toggleClass('sort_desc');
        };
        sessionStorage.sort_order = sort_order;

        var row_id = $(this).closest('th').attr('id');

        // build our new URL
        var url = setGetParameter('sort', row_id);
        var url = setGetParameter('order', sort_order, url);

        window.location.href = url;
    });