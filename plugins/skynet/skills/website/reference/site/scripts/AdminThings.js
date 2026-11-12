var AdminThingsJs = (function () {

    var ttimer = null;
    var askBox = null, askDone = null, askCheck = null, askBack = null;
    var dirty = false;
    var MAX = 12, pkSel = [], pkTimer = null;

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
        $ApiRequest('AdminThings/' + method, JSON.stringify(list));
    }

    function expired() {
        AdminJs.expired();
    }

    function toast(msg) {
        var t = el('tg-toast');
        t.textContent = msg;
        t.classList.add('tg-open');
        clearTimeout(ttimer);
        ttimer = setTimeout(function () {
            t.classList.remove('tg-open');
        }, 3400);
    }


    function openModal(title) {
        var m = el('tg-modal');
        el('tg-mtitle').textContent = title || '';
        dirty = false;
        m.classList.add('tg-open');
        m.setAttribute('aria-hidden', 'false');
        m.scrollTop = 0;
    }

    function shut() {
        var m = el('tg-modal');
        if (m) {
            m.classList.remove('tg-open');
            m.setAttribute('aria-hidden', 'true');
        }
        dirty = false;
    }

    function closeModal() {
        var m = el('tg-modal');
        if (!m || !m.classList.contains('tg-open')) {
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
        if (!askBox || !askBox.classList.contains('tg-open')) {
            return;
        }
        var x = askParts(), f = askDone, v = x.i.value.trim();
        askBox.classList.remove('tg-open');
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
        askBox.className = 'tg-ask';
        askBox.innerHTML = '<div class="tg-askbox" role="alertdialog" aria-modal="true"><h2></h2><p></p><input type="text" maxlength="300" autocomplete="off"><em class="tg-err" role="alert"></em><div class="tg-askacts"><button type="button" class="tg-btn tg-btn-ghost"></button><button type="button" class="tg-btn"></button></div></div>';
        document.getElementById('tg-site-root').appendChild(askBox);
        var x = askParts();
        x.b[0].addEventListener('click', function () { askClose(false); });
        x.b[1].addEventListener('click', askOk);
        x.i.addEventListener('input', function () { x.e.textContent = ''; });
        askBox.addEventListener('mousedown', function (e) { if (e.target === askBox) { askClose(false); } });
        window.addEventListener('keydown', function (e) {
            if (!askBox.classList.contains('tg-open')) {
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
        x.b[1].className = 'tg-btn' + (o.danger ? ' tg-askdel' : '');
        askBox.firstChild.classList.toggle('tg-askin', input);
        x.i.value = input ? o.value : '';
        x.i.placeholder = o.place || '';
        askBox.classList.add('tg-open');
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
        numberStrip();
    }

    function save(id) {
        var list = collect('tg-form');
        list.push({ key: 'id', vlu: id });
        list.push({ key: 'photos', vlu: JSON.stringify(stripPaths()) });
        api('Save', list);
        return false;
    }

    function saved(msg) {
        clean();
        shut();
        toast(msg);
        api('Load');
    }

    function esc(t) {
        return String(t == null ? '' : t).replace(/[&<>"']/g, function (ch) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch];
        });
    }

    function touch() {
        markDirty();
    }


    function stripPaths() {
        return [].map.call(document.querySelectorAll('#tg-strip .tg-si'), function (s) {
            return s.getAttribute('data-src');
        });
    }

    function numberStrip() {
        var items = document.querySelectorAll('#tg-strip .tg-si');
        [].forEach.call(items, function (s, i) {
            s.querySelector('.tg-sn').textContent = i + 1;
        });
        var c = el('tg-pcount');
        if (c) {
            c.textContent = items.length;
        }
    }

    function sMove(btn, d) {
        var s = btn.closest('.tg-si');
        if (d < 0 && s.previousElementSibling) {
            s.parentNode.insertBefore(s, s.previousElementSibling);
        } else if (d > 0 && s.nextElementSibling) {
            s.parentNode.insertBefore(s.nextElementSibling, s);
        }
        numberStrip();
        touch();
    }

    function sDrop(btn) {
        btn.closest('.tg-si').remove();
        numberStrip();
        touch();
    }

    function stripItem(src, thumb) {
        return '<div class="tg-si" data-src="' + esc(src) + '"><img src="' + esc(thumb) + '" alt=""><i class="tg-sn"></i><div class="tg-sctl"><button type="button" aria-label="Move earlier" onclick="AdminThingsJs.sMove(this,-1)">&#9664;</button><button type="button" aria-label="Move later" onclick="AdminThingsJs.sMove(this,1)">&#9654;</button><button type="button" aria-label="Remove" onclick="AdminThingsJs.sDrop(this)">&#10005;</button></div></div>';
    }

    function pickPhotos() {
        pkSel = stripPaths();
        el('tg-pkq').value = '';
        el('tg-pkmsg').textContent = '';
        var d = el('tg-pk');
        d.classList.add('tg-open');
        d.setAttribute('aria-hidden', 'false');
        pkList();
    }

    function pkList() {
        api('Pick', [{ key: 'pterm', vlu: (el('tg-pkq').value || '').trim() }]);
    }

    function pkSearch() {
        clearTimeout(pkTimer);
        pkTimer = setTimeout(pkList, 300);
    }

    function pkMark() {
        [].forEach.call(document.querySelectorAll('#tg-pkgrid .tg-pki'), function (b) {
            var i = pkSel.indexOf(b.getAttribute('data-src'));
            b.classList.toggle('tg-on', i >= 0);
            b.setAttribute('aria-pressed', i >= 0 ? 'true' : 'false');
            b.querySelector('.tg-pkn').textContent = i >= 0 ? i + 1 : '';
        });
        el('tg-pkcount').textContent = pkSel.length + ' of ' + MAX + ' chosen. Click a photo to add or remove it; the numbers show the order.';
    }

    function pkListed() {
        pkMark();
    }

    function pkToggle(b) {
        var src = b.getAttribute('data-src'), i = pkSel.indexOf(src);
        if (i >= 0) {
            pkSel.splice(i, 1);
        } else if (pkSel.length >= MAX) {
            toast('Up to ' + MAX + ' photos. Remove one first.');
            return;
        } else {
            pkSel.push(src);
        }
        pkMark();
    }

    function pkUse() {
        var thumbs = {};
        [].forEach.call(document.querySelectorAll('#tg-strip .tg-si'), function (s) {
            thumbs[s.getAttribute('data-src')] = s.querySelector('img').getAttribute('src');
        });
        [].forEach.call(document.querySelectorAll('#tg-pkgrid .tg-pki'), function (b) {
            thumbs[b.getAttribute('data-src')] = b.getAttribute('data-thumb');
        });
        el('tg-strip').innerHTML = pkSel.map(function (s) {
            return stripItem(s, thumbs[s] || s);
        }).join('');
        numberStrip();
        touch();
        pkClose();
    }

    function pkOpen() {
        var d = el('tg-pk');
        return !!d && d.classList.contains('tg-open');
    }

    function pkClose() {
        var d = el('tg-pk');
        if (d) {
            d.classList.remove('tg-open');
            d.setAttribute('aria-hidden', 'true');
        }
        el('tg-pkfile').value = '';
    }

    function pkUpload() {
        el('tg-pkmsg').textContent = 'Uploading.';
        api('Upload');
    }

    function pkUploaded(msg) {
        el('tg-pkfile').value = '';
        el('tg-pkmsg').textContent = msg;
        pkMark();
    }

    function here() {
        var r = el('tg-site-root');
        return !!r && r.getClientRects().length > 0;
    }

    function shown() {
        api('Load');
    }

    function reveal() {
        document.addEventListener('keydown', function (e) {
            if (e.key !== 'Escape' || !here() || (askBox && askBox.classList.contains('tg-open'))) {
                return;
            }
            if (pkOpen()) {
                pkClose();
            } else {
                closeModal();
            }
        });
        var m = el('tg-modal');
        m.addEventListener('input', markDirty);
        m.addEventListener('change', markDirty);
        api('Load');
    }

    return {
        reveal: reveal, shown: shown, expired: expired, toast: toast, closeModal: closeModal, open: open, opened: opened, save: save, saved: saved,
        pickPhotos: pickPhotos, pkSearch: pkSearch, pkToggle: pkToggle, pkUse: pkUse, pkClose: pkClose, pkUpload: pkUpload, pkListed: pkListed, pkUploaded: pkUploaded, sMove: sMove, sDrop: sDrop
    };
})();

if (!window.AdminJs) {
    location.replace('Admin?p=AdminThings');
} else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', AdminThingsJs.reveal);
} else {
    AdminThingsJs.reveal();
}
