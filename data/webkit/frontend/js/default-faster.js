var cat, side = false;

function changeTitle(title) {
    document.title = title;
    document.title = 'nop';
}

function changeCategory(category) {
    if (cat != category) {
        cat = category;
        document.title = 'category:' + category;
        document.title = 'nop';
        setContent(category);
    }
}

function setContent(category) {
    if (!side) {
        side = true;
        document.getElementById('side').style.width = '190px';
    }
    ajax = document.getElementById('ajax');
    ajax.innerHTML = document.getElementById(category + '_html').innerHTML;
    ajax.style.display = 'block';
    document.getElementById('main').style.display = 'none';
    document.getElementById('container').style.display = 'block';
}

function addItem(title, command, category, icon) {
    document.getElementById('ajax').innerHTML = '';
    li = document.createElement('li');
    li.setAttribute('id', command);
    li.setAttribute('class', 'item');
    li.setAttribute('onclick', 'javascript:changeTitle("exec:' + command + '")');
    li.setAttribute('style', 'background-image: url(' + icon + ')');
    li.innerHTML = title;
    document.getElementById(category + '_ul').appendChild(li);
}

function editItem(title, old_command, new_command, icon) {
    document.getElementById('ajax').innerHTML = '';
    li = document.getElementById(old_command);
    li.setAttribute('style', 'background-image: url(' + icon + ')');
    li.innerHTML = title;
    if (old_command != new_command) {
        li.setAttribute('id', new_command);
        li.setAttribute('onclick', 'javascript:changeTitle("exec:' + new_command + '")');
    }
}

function removeItem(command, category) {
    document.getElementById('ajax').innerHTML = '';
    if (command == 'all-items')
        document.getElementById(category + '_ul').innerHTML = '';
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
    back();
}

function back() {
    document.getElementById('main').style.display = 'block';
    document.getElementById('container').style.display = 'none';
    cat = null;
    side = false;
}
