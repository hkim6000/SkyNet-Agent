var ItemJs = (function () {

    function el(id) {
        return document.getElementById(id);
    }

    function val(id) {
        var e = el(id);
        return e ? (e.value || '').trim() : '';
    }

    function call(method, list) {
        $ApiRequest('Item/' + method, JSON.stringify(list || []));
    }

    function clearErrors() {
        ['name', 'category', 'price', 'stock'].forEach(function (k) {
            el('it-e-' + k).textContent = '';
        });
    }

    function open(title, isNew) {
        el('it-ptitle').textContent = title;
        el('it-del').style.display = isNew ? 'none' : '';
        el('it-panel').classList.add('it-open');
        setTimeout(function () {
            el('it-name').focus();
        }, 50);
    }

    function close() {
        el('it-panel').classList.remove('it-open');
    }

    function openNew() {
        clearErrors();
        el('it-id').value = '';
        el('it-name').value = '';
        el('it-category').value = '';
        el('it-price').value = '0';
        el('it-stock').value = '0';
        el('it-active').checked = true;
        open('Add item', true);
    }

    function edit(id) {
        call('GetItem', [{ key: 'id', vlu: id }]);
    }

    function onItem(item) {
        clearErrors();
        el('it-id').value = item.id;
        el('it-name').value = item.name;
        el('it-category').value = item.category;
        el('it-price').value = item.price;
        el('it-stock').value = item.stock;
        el('it-active').checked = !!item.active;
        open('Edit item', false);
    }

    function save() {
        call('SaveItem', [
            { key: 'id', vlu: val('it-id') },
            { key: 'name', vlu: val('it-name') },
            { key: 'category', vlu: val('it-category') },
            { key: 'price', vlu: val('it-price') },
            { key: 'stock', vlu: val('it-stock') },
            { key: 'active', vlu: el('it-active').checked ? '1' : '' }
        ]);
        return false;
    }

    function onSaved() {
        close();
        call('Refresh');
    }

    function remove() {
        if (!confirm('Delete this item?')) {
            return;
        }
        call('DeleteItem', [{ key: 'id', vlu: val('it-id') }]);
    }

    function onDeleted() {
        close();
        call('Refresh');
    }

    function find(text) {
        var q = (text || '').trim().toLowerCase();
        var rows = document.querySelectorAll('#it-rows tr[data-search]');
        for (var i = 0; i < rows.length; i++) {
            rows[i].style.display = !q || rows[i].getAttribute('data-search').indexOf(q) >= 0 ? '' : 'none';
        }
    }

    function reveal() {
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                close();
            }
        });
    }

    return {
        reveal: reveal,
        openNew: openNew,
        edit: edit,
        onItem: onItem,
        save: save,
        onSaved: onSaved,
        remove: remove,
        onDeleted: onDeleted,
        close: close,
        find: find
    };
})();

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ItemJs.reveal);
} else {
    ItemJs.reveal();
}
