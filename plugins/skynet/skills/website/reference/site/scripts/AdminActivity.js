var AdminActivityJs = (function () {

    var ttimer = null;
    var stimer = null;
    var pgn = 1;
    var of = '';

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
        $ApiRequest('AdminActivity/' + method, JSON.stringify(list));
    }

    function expired() {
        AdminJs.expired();
    }

    function toast(msg) {
        var t = el('al-toast');
        t.textContent = msg;
        t.classList.add('al-open');
        clearTimeout(ttimer);
        ttimer = setTimeout(function () {
            t.classList.remove('al-open');
        }, 3400);
    }

    function listKeys() {
        return [{ key: 'who', vlu: val('al-who') }, { key: 'of', vlu: of }, { key: 'term', vlu: val('al-term') }, { key: 'pgn', vlu: String(pgn) }];
    }

    function outcome(f) {
        of = f;
        pgn = 1;
        document.querySelectorAll('#al-main .al-chip').forEach(function (b) {
            b.classList.toggle('al-act', b.getAttribute('data-of') === f);
        });
        api('List', listKeys());
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
        var m = el('al-main');
        if (m) {
            m.scrollIntoView({ block: 'start' });
        }
    }

    function shown() {
        api('List', listKeys());
    }

    function reveal() {
        of = '';
        pgn = 1;
        api('Load', listKeys());
    }

    return {
        reveal: reveal,
        shown: shown,
        expired: expired,
        toast: toast,
        outcome: outcome,
        search: search,
        go: go
    };
})();

if (!window.AdminJs) {
    location.replace('Admin?p=AdminActivity');
} else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', AdminActivityJs.reveal);
} else {
    AdminActivityJs.reveal();
}
