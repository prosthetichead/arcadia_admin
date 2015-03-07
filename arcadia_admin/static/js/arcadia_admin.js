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
function setGetParameter(paramName, paramValue, url_to_change)
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


function setGetParameter_andGo(paramName, paramValue, url_to_change)
{
    var address = setGetParameter(paramName, paramValue, url_to_change);
    window.location.href = address;
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

     function online_search(searchString, searchProvider, searchResult_DDL)
     {
        searchString = searchString.replace(/[^a-zA-Z0-9]+/g, ' ')
        var loadingDiv = searchResult_DDL.closest('.form-group').find('.loading_div');
        searchResult_DDL.find('option').remove().end();
        loadingDiv.show();
        console.log("online_search: " + searchProvider);
        $.getJSON("/_online_search?search=" + searchString + "&provider=" + searchProvider ,function(data){            
            $.each(data, function(i, record) {                
                var o = new Option(record.name + ' - ' + record.platform, record.id);
                $(o).html(record.name + ' - ' + record.platform);
                searchResult_DDL.append(o);
            });
            searchResult_DDL.change(); // Fire the change event for the drop down.
            loadingDiv.hide();
        });

     }
     $(".online_search-btn").click(function() {
        var searchString = $(this).closest('.form-group').find('.online_search-string').val();
        var searchProvider = $(this).closest('.form-group').find('.online_search-provider').val();
        var searchResult_DDL =  $(this).closest('.form-group').find('.online_search-result');
        console.log("online_search-btn: " + searchProvider);
        online_search(searchString, searchProvider, searchResult_DDL);
     });

     /* click the cloud search button on games list tables */
     $(".game_table_online_search-btn").click(function() {

        var gameID = $(this).closest('tr').attr('id');
        var gameName = $(this).closest('tr').find('.gameName').text();
        var searchProvider = $('#find_online_metadata-Providers').val();
        $('#find_online_metadata-GameID').val(gameID);
        $('#find_online_metadata-String').val(gameName);
        $('#find_online_metadata-dialog').modal('show');

        online_search(gameName, searchProvider, $('#find_online_metadata-Result') );
     });


     /* Online Image Searching */
     $("#change_image-Result").change(function () {

        var provider_game_id = $(this).val();
        var searchProvider = $('#change_image-Providers').val();

        $("#change_image-list").empty();
        $.getJSON("/_game_image_search_online?provider_game_id=" + provider_game_id + "&provider=" + searchProvider , function(data){
             $.each(data, function(i, record) {
                $('#change_image-list').append('<li><img class="change_image-image" src="' + record.thumbUrl + '"/></li>');
             });
        });

     });
     $(document).on("click", ".change_image-image",function() {
        console.log( $(this).prop('src') );
     });


    /* Online Searching - Update item using selected item*/
    $("#find_online_metadata-Update_Btn").click(function() {
        $("#find_online_metadata-loading_div").show();
        var provider =  $("#find_online_metadata-Providers").val();
        var provider_game_id =  $("#find_online_metadata-Result").val();
        var game_id = $("#find_online_metadata-GameID").val();
        $.getJSON("/_update_from_online/game/" + game_id + "?provider=" + provider + "&provider_game_id=" + provider_game_id ,function(data){
            if (data.status == 'complete'){

                $("#find_online_metadata-loading_div").hide();
                $('#find_online_metadata-dialog').modal('hide');
                window.location.reload(true);
            }
        });
    });
