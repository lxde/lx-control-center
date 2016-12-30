var cat, side = false;

function changeTitle(title) {
    document.title = title;
    document.title = 'nop';
}

function changeCategory(category) {
    document.title = 'category:' + category;
    document.title = 'nop';
}

function setContent(category) {
    cont = $('#' + category + '_html').html();
    $('#ajax').hide().html(cont).fadeIn();
    $('#container').show();
}

function addItem(title, command, category, icon) {
    li = "<li id='" + command + "' class='item' onclick='javascript:changeTitle(\"exec:" + command + "\")' style='background-image: url(" + icon + ")'>" + title + "</li>";
    $('ul#' + category + '_ul').append(li);
}

function editItem(title, old_command, new_command, icon) {
    $('li[id="' + old_command + '"]').attr({
        id: new_command,
        onclick: 'javascript:changeTitle("exec:' + new_command + '")',
        style: 'background-image: url(' + icon + ')'
    }).text(title);
}

function removeItem(command, category) {
    if (command == 'all-items')
        $('#' + category + '_ul li').remove();
    else
        $('li[id="' + command + '"]').remove();
}

function saveOptions() {
    mode = document.getElementById('mode').checked;
    visual_effects = document.getElementById('visual_effects').checked;
    changeTitle('save-options:' + mode + ':' + visual_effects);    
    back();
}

function back() {
    $('#ajax').fadeOut(50);
    $('#side').css('width', '0').fadeOut(80);
    $('#main').fadeIn();
    cat = null;
    side = false;
}

$(function() {
    $('.btn').click(function() {
        category = $(this).data('cat');
        if (cat != category) {
            cat = category;
            if (!side) {
                side = true;
                $('#main').hide();
                $('#side').animate({'width': '190px'}, {easing: 'easeOutBounce', duration: 800}).show();
                $('#container').show();
            }
            if (category == 'options')
                setContent(category);
            else
                changeCategory(category);
        }
    });
});
