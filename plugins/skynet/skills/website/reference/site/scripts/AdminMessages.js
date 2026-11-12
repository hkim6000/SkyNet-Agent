var AdminMessagesJs = (function () {

    var ttimer = null;
    var askBox = null, askDone = null, askCheck = null, askBack = null;
    var dirty = false;

    function el(id) {
        return document.getElementById(id);
    }

    function val(id) {
        var e = el(id);
        return e ? (e.value || '').trim() : '';
    }

    function api(method, list) {
        list = list || [];
        list.push({ key: 'tok', vlu: AdminJs.tok() });
        $ApiRequest('AdminMessages/' + method, JSON.stringify(list));
    }

    function expired() {
        AdminJs.expired();
    }

    function toast(msg) {
        var t = el('mx-toast');
        t.textContent = msg;
        t.classList.add('mx-open');
        clearTimeout(ttimer);
        ttimer = setTimeout(function () {
            t.classList.remove('mx-open');
        }, 3400);
    }


    function openModal(title) {
        var m = el('mx-modal');
        el('mx-mtitle').textContent = title || '';
        dirty = false;
        m.classList.add('mx-open');
        m.setAttribute('aria-hidden', 'false');
        m.scrollTop = 0;
    }

    function shut() {
        var m = el('mx-modal');
        if (m) {
            m.classList.remove('mx-open');
            m.setAttribute('aria-hidden', 'true');
        }
        dirty = false;
    }

    function closeModal() {
        var m = el('mx-modal');
        if (!m || !m.classList.contains('mx-open')) {
            return;
        }
        if (dirty) {
            ask({ title: 'Leave without saving?', text: 'Your changes will be lost.', ok: 'Leave', no: 'Keep editing', danger: true }, shut);
            return;
        }
        shut();
    }

    function markDirty() {
        dirty = true;
    }

    function clean() {
        dirty = false;
    }

    function askParts() {
        return { h: askBox.querySelector('h2'), p: askBox.querySelector('p'), i: askBox.querySelector('input'), e: askBox.querySelector('em'), b: askBox.querySelectorAll('button') };
    }

    function askClose(ok) {
        if (!askBox || !askBox.classList.contains('mx-open')) {
            return;
        }
        var x = askParts(), f = askDone, v = x.i.value.trim();
        askBox.classList.remove('mx-open');
        askDone = null;
        askCheck = null;
        if (askBack && askBack.focus && document.body.contains(askBack)) {
            askBack.focus();
        }
        askBack = null;
        if (ok && f) {
            f(v);
        }
    }

    function askOk() {
        var x = askParts();
        var m = askCheck ? askCheck(x.i.value.trim()) : '';
        if (m) {
            x.e.textContent = m;
            x.i.focus();
            return;
        }
        askClose(true);
    }

    function askBuild() {
        askBox = document.createElement('div');
        askBox.className = 'mx-ask';
        askBox.innerHTML = '<div class="mx-askbox" role="alertdialog" aria-modal="true"><h2></h2><p></p><input type="text" maxlength="300" autocomplete="off"><em class="mx-err" role="alert"></em><div class="mx-askacts"><button type="button" class="mx-btn mx-btn-ghost"></button><button type="button" class="mx-btn"></button></div></div>';
        document.getElementById('mx-site-root').appendChild(askBox);
        var x = askParts();
        x.b[0].addEventListener('click', function () { askClose(false); });
        x.b[1].addEventListener('click', askOk);
        x.i.addEventListener('input', function () { x.e.textContent = ''; });
        askBox.addEventListener('mousedown', function (e) { if (e.target === askBox) { askClose(false); } });
        window.addEventListener('keydown', function (e) {
            if (!askBox.classList.contains('mx-open')) {
                return;
            }
            if (e.key === 'Escape') {
                e.preventDefault();
                e.stopPropagation();
                askClose(false);
            } else if (e.key === 'Enter' && e.target !== x.b[0]) {
                e.preventDefault();
                e.stopPropagation();
                askOk();
            } else if (e.key === 'Tab') {
                var f = [x.i, x.b[0], x.b[1]].filter(function (n) { return n.offsetParent !== null; });
                var at = f.indexOf(document.activeElement);
                e.preventDefault();
                f[(at + (e.shiftKey ? f.length - 1 : 1)) % f.length].focus();
            }
        }, true);
    }

    function ask(o, done) {
        if (!askBox) {
            askBuild();
        }
        var x = askParts(), input = typeof o.value === 'string';
        askBack = document.activeElement;
        askDone = done;
        askCheck = o.check || null;
        x.h.textContent = o.title || '';
        x.p.textContent = o.text || '';
        x.e.textContent = '';
        x.b[0].textContent = o.no || 'Cancel';
        x.b[1].textContent = o.ok || 'OK';
        x.b[1].className = 'mx-btn' + (o.danger ? ' mx-askdel' : '');
        askBox.firstChild.classList.toggle('mx-askin', input);
        x.i.value = input ? o.value : '';
        x.i.placeholder = o.place || '';
        askBox.classList.add('mx-open');
        if (input) {
            x.i.focus();
        } else {
            x.b[o.danger ? 0 : 1].focus();
        }
    }

    function collect(root, extra) {
        var list = extra || [];
        document.querySelectorAll('#' + root + ' [data-k]').forEach(function (n) {
            if (n.type === 'checkbox') {
                list.push({ key: n.getAttribute('data-k'), vlu: n.checked ? '1' : '0' });
            } else if (n.type === 'password') {
                list.push({ key: n.getAttribute('data-k'), vlu: n.value });
            } else {
                list.push({ key: n.getAttribute('data-k'), vlu: (n.value || '').trim() });
            }
        });
        return list;
    }

    var pgn = 1;
    var mf = '';
    var stimer = null;

    function listKeys() {
        return [{ key: 'mf', vlu: mf }, { key: 'term', vlu: val('mx-term') }, { key: 'pgn', vlu: String(pgn) }];
    }

    function loaded(f) {
        mf = f;
    }

    function filter(f) {
        mf = f;
        pgn = 1;
        api('Load', listKeys());
    }

    function search() {
        clearTimeout(stimer);
        stimer = setTimeout(function () {
            pgn = 1;
            api('List', listKeys());
        }, 250);
    }

    function go(n) {
        pgn = n;
        api('List', listKeys());
    }

    function open(id) {
        var list = listKeys();
        list.push({ key: 'id', vlu: id });
        api('Open', list);
    }

    function opened(title, marked) {
        openModal(title);
        if (marked) {
            AdminJs.refresh();
        }
    }

    function save(id) {
        var list = collect('mx-form', listKeys());
        list.push({ key: 'id', vlu: id });
        api('Save', list);
        return false;
    }

    function unread(id) {
        var list = listKeys();
        list.push({ key: 'id', vlu: id });
        api('Unread', list);
    }

    function saved(msg) {
        clean();
        shut();
        toast(msg);
        AdminJs.refresh();
    }

    function drop(id, name) {
        ask({ title: 'Delete the message from ' + name + '?', text: 'The request and its notes are removed for good.', ok: 'Delete message', no: 'Keep it', danger: true }, function () {
            var list = listKeys();
            list.push({ key: 'id', vlu: id });
            api('Drop', list);
        });
    }

    function shown() {
        if (el('mx-modal') && el('mx-modal').classList.contains('mx-open')) {
            return;
        }
        api('Load', listKeys());
    }

    function here() {
        var r = el('mx-site-root');
        return !!r && r.getClientRects().length > 0;
    }

    function reveal() {
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && here()) {
                if (askBox && askBox.classList.contains('mx-open')) {
                    return;
                }
                closeModal();
            }
        });
        var m = el('mx-modal');
        m.addEventListener('input', markDirty);
        m.addEventListener('change', markDirty);
        m.addEventListener('mousedown', function (e) {
            if (e.target === m) {
                closeModal();
            }
        });
        api('Load', listKeys());
    }

    return {
        reveal: reveal,
        shown: shown,
        expired: expired,
        toast: toast,
        closeModal: closeModal,
        loaded: loaded,
        filter: filter,
        search: search,
        go: go,
        open: open,
        opened: opened,
        save: save,
        unread: unread,
        saved: saved,
        drop: drop
    };
})();

if (!window.AdminJs) {
    location.replace('Admin?p=AdminMessages');
} else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', AdminMessagesJs.reveal);
} else {
    AdminMessagesJs.reveal();
}
