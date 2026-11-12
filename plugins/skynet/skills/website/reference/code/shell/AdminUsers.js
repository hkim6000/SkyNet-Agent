var AdminUsersJs = (function () {

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
        $ApiRequest('AdminUsers/' + method, JSON.stringify(list));
    }

    function expired() {
        AdminJs.expired();
    }

    function toast(msg) {
        var t = el('us-toast');
        t.textContent = msg;
        t.classList.add('us-open');
        clearTimeout(ttimer);
        ttimer = setTimeout(function () {
            t.classList.remove('us-open');
        }, 3400);
    }


    function openModal(title) {
        var m = el('us-modal');
        el('us-mtitle').textContent = title || '';
        dirty = false;
        m.classList.add('us-open');
        m.setAttribute('aria-hidden', 'false');
        m.scrollTop = 0;
    }

    function shut() {
        var m = el('us-modal');
        if (m) {
            m.classList.remove('us-open');
            m.setAttribute('aria-hidden', 'true');
        }
        dirty = false;
    }

    function closeModal() {
        var m = el('us-modal');
        if (!m || !m.classList.contains('us-open')) {
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
        if (!askBox || !askBox.classList.contains('us-open')) {
            return;
        }
        var x = askParts(), f = askDone, v = x.i.value.trim();
        askBox.classList.remove('us-open');
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
        askBox.className = 'us-ask';
        askBox.innerHTML = '<div class="us-askbox" role="alertdialog" aria-modal="true"><h2></h2><p></p><input type="text" maxlength="300" autocomplete="off"><em class="us-err" role="alert"></em><div class="us-askacts"><button type="button" class="us-btn us-btn-ghost"></button><button type="button" class="us-btn"></button></div></div>';
        document.getElementById('us-site-root').appendChild(askBox);
        var x = askParts();
        x.b[0].addEventListener('click', function () { askClose(false); });
        x.b[1].addEventListener('click', askOk);
        x.i.addEventListener('input', function () { x.e.textContent = ''; });
        askBox.addEventListener('mousedown', function (e) { if (e.target === askBox) { askClose(false); } });
        window.addEventListener('keydown', function (e) {
            if (!askBox.classList.contains('us-open')) {
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
        x.b[1].className = 'us-btn' + (o.danger ? ' us-askdel' : '');
        askBox.firstChild.classList.toggle('us-askin', input);
        x.i.value = input ? o.value : '';
        x.i.placeholder = o.place || '';
        askBox.classList.add('us-open');
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

    function open(id) {
        api('Open', [{ key: 'id', vlu: id }]);
    }

    function opened(title) {
        openModal(title);
        setTimeout(function () {
            var f = el('us-f-name');
            if (f) {
                f.focus();
            }
        }, 30);
    }

    function manager() {
        var box = el('us-rights');
        if (box) {
            box.hidden = !!(el('us-f-admin') && el('us-f-admin').checked);
        }
    }

    function save(id) {
        var list = collect('us-form');
        list.push({ key: 'id', vlu: id });
        api('Save', list);
        return false;
    }

    function saved(msg) {
        clean();
        shut();
        toast(msg);
        AdminJs.refresh();
    }

    function issued(name) {
        clean();
        el('us-mtitle').textContent = 'Password for ' + name;
        toast('Saved');
    }

    function copy() {
        var t = el('us-pw') ? el('us-pw').textContent : '';
        if (navigator.clipboard && t) {
            navigator.clipboard.writeText(t).then(function () { toast('Password copied'); }, function () { toast('Select the password and copy it'); });
        } else {
            toast('Select the password and copy it');
        }
    }

    function reset(id, name) {
        ask({ title: 'Give ' + name + ' a new password?', text: 'Their old password stops working and they are signed out everywhere. You will see the new password once.', ok: 'New password', no: 'Cancel' }, function () {
            api('Reset', [{ key: 'id', vlu: id }]);
        });
    }

    function drop(id, name) {
        ask({ title: 'Remove ' + name + '?', text: 'They can no longer sign in. Their past activity stays in the log. To stop them for a while, untick Active instead.', ok: 'Remove', no: 'Keep', danger: true }, function () {
            api('Drop', [{ key: 'id', vlu: id }]);
        });
    }

    function shown() {
        if (el('us-modal') && el('us-modal').classList.contains('us-open')) {
            return;
        }
        api('Load');
    }

    function here() {
        var r = el('us-site-root');
        return !!r && r.getClientRects().length > 0;
    }

    function reveal() {
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && here()) {
                if (askBox && askBox.classList.contains('us-open')) {
                    return;
                }
                closeModal();
            }
        });
        var m = el('us-modal');
        m.addEventListener('input', markDirty);
        m.addEventListener('change', markDirty);
        m.addEventListener('mousedown', function (e) {
            if (e.target === m) {
                closeModal();
            }
        });
        api('Load');
    }

    return {
        reveal: reveal,
        shown: shown,
        expired: expired,
        toast: toast,
        closeModal: closeModal,
        open: open,
        opened: opened,
        manager: manager,
        save: save,
        saved: saved,
        issued: issued,
        copy: copy,
        reset: reset,
        drop: drop
    };
})();

if (!window.AdminJs) {
    location.replace('Admin?p=AdminUsers');
} else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', AdminUsersJs.reveal);
} else {
    AdminUsersJs.reveal();
}
