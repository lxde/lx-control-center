function changeTitle(title) {
    document.title = title;
    document.title = 'nop';
}

function changeCategory(category) {
    document.title = 'category:' + category;
    document.title = 'nop';
}

function setContent(category) {
    $('#advanced_html').hide().fadeIn();
}

function addItem(title, command, category, icon) {
    li = "<li id='" + command + "' class='item' onclick='javascript:changeTitle(\"exec:" + command + "\")' style='background-image: url(" + icon + ")'>" + title + "</li>";
    $('#advanced_ul').append(li);
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
    $('#options_html').hide();
    $('#advanced_html').fadeIn();
}

function showOptions() {
    $('#advanced_html').hide();
    $('#options_html').fadeIn();
}
