var AboutJs = (function () {

    var timer = null;
    var ttimer = null;

    function el(id) {
        return document.getElementById(id);
    }

    function val(id) {
        var e = el(id);
        return e ? (e.value || '').trim() : '';
    }

    function call(method, list) {
        $ApiRequest('About/' + method, JSON.stringify(list || []));
    }

    function toast(msg) {
        var t = el('ab-toast');
        t.textContent = msg;
        t.classList.add('ab-open');
        clearTimeout(ttimer);
        ttimer = setTimeout(function () {
            t.classList.remove('ab-open');
        }, 3000);
    }

    function openNav() {
        el('ab-nav').classList.add('ab-open');
        el('ab-scrim').classList.add('ab-open');
    }

    function closeNav() {
        el('ab-nav').classList.remove('ab-open');
        el('ab-scrim').classList.remove('ab-open');
    }

    function search(value) {
        var v = (value || '').trim();
        clearTimeout(timer);
        if (v.length < 2) {
            el('ab-sugg').classList.remove('ab-open');
            return;
        }
        timer = setTimeout(function () {
            call('Suggest', [{ key: 'term', vlu: v }]);
        }, 250);
    }

    function openSugg() {
        el('ab-sugg').classList.add('ab-open');
    }

    function cat(c) {
        el('ab-cat').value = c;
        filter();
    }

    function filter() {
        call('Filter', [{ key: 'cat', vlu: val('ab-cat') }, { key: 'order', vlu: val('ab-sort') }]);
    }

    function filtered(c, s) {
        var p = new URLSearchParams();
        if (c) {
            p.set('c', c);
        }
        if (s) {
            p.set('s', s);
        }
        var qs = p.toString();
        history.replaceState(null, '', 'Shop' + (qs ? '?' + qs : ''));
    }

    function send() {
        call('Send', [
            { key: 'name', vlu: val('ab-name') },
            { key: 'email', vlu: val('ab-email') },
            { key: 'topic', vlu: val('ab-topic') },
            { key: 'message', vlu: val('ab-msg') }
        ]);
        return false;
    }

    function sent() {
        el('ab-msg').value = '';
        el('ab-topic').value = '';
        toast('Message sent');
    }

    function reveal() {
        document.addEventListener('click', function (e) {
            var s = el('ab-sugg');
            if (s && !s.parentElement.contains(e.target)) {
                s.classList.remove('ab-open');
            }
        });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                closeNav();
            }
        });
    }

    return {
        reveal: reveal,
        toast: toast,
        openNav: openNav,
        closeNav: closeNav,
        search: search,
        openSugg: openSugg,
        cat: cat,
        filter: filter,
        filtered: filtered,
        send: send,
        sent: sent
    };
})();

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', AboutJs.reveal);
} else {
    AboutJs.reveal();
}
