function changeTitle(title) {
    document.title = title;
    document.title = 'nop';
}

function changeCategory(category) {
    document.title = 'category:' + category;
    document.title = 'nop';
}

function setContent(category) {
    document.getElementById('advanced_html').style.display = 'block';
}

function addItem(title, command, category, icon) {
    li = document.createElement('li');
    li.setAttribute('id', command);
    li.setAttribute('class', 'item');
    li.setAttribute('onclick', 'javascript:changeTitle("exec:' + command + '")');
    li.setAttribute('style', 'background-image: url(' + icon + ')');
    li.innerHTML = title;
    document.getElementById('advanced_ul').appendChild(li);
}

function editItem(title, old_command, new_command, icon) {
    li = document.getElementById(old_command);
    li.setAttribute('style', 'background-image: url(' + icon + ')');
    li.innerHTML = title;
    if (old_command != new_command) {
        li.setAttribute('id', new_command);
        li.setAttribute('onclick', 'javascript:changeTitle("exec:' + new_command + '")');
    }
}

function removeItem(command, category) {
    if (command == 'all-items')
        document.getElementById('advanced_ul').innerHTML = '';
    else {
        li = document.getElementById(command);
        parent = li.parentNode;
        parent.removeChild(li);
    }
    setContent(category);
}

function saveOptions() {
    mode = document.getElementById('mode').checked;
    visual_effects = document.getElementById('visual_effects').checked;
    changeTitle('save-options:' + mode + ':' + visual_effects);    
    document.getElementById('advanced_html').style.display = 'block';
    document.getElementById('options_html').style.display = 'none';
}

function showOptions() {
    document.getElementById('advanced_html').style.display = 'none';
    document.getElementById('options_html').style.display = 'block';
}
