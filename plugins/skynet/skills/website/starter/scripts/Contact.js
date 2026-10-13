var ContactJs = (function () {

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
        $ApiRequest('Contact/' + method, JSON.stringify(list || []));
    }

    function toast(msg) {
        var t = el('ct-toast');
        t.textContent = msg;
        t.classList.add('ct-open');
        clearTimeout(ttimer);
        ttimer = setTimeout(function () {
            t.classList.remove('ct-open');
        }, 3000);
    }

    function openNav() {
        el('ct-nav').classList.add('ct-open');
        el('ct-scrim').classList.add('ct-open');
    }

    function closeNav() {
        el('ct-nav').classList.remove('ct-open');
        el('ct-scrim').classList.remove('ct-open');
    }

    function search(value) {
        var v = (value || '').trim();
        clearTimeout(timer);
        if (v.length < 2) {
            el('ct-sugg').classList.remove('ct-open');
            return;
        }
        timer = setTimeout(function () {
            call('Suggest', [{ key: 'term', vlu: v }]);
        }, 250);
    }

    function openSugg() {
        el('ct-sugg').classList.add('ct-open');
    }

    function newsletter() {
        call('Newsletter', [{ key: 'email', vlu: val('ct-nl-email') }]);
        return false;
    }

    function newsletterDone() {
        el('ct-nl-email').value = '';
        toast('Thanks for signing up');
    }

    function cat(c) {
        el('ct-cat').value = c;
        filter();
    }

    function filter() {
        call('Filter', [{ key: 'cat', vlu: val('ct-cat') }, { key: 'order', vlu: val('ct-sort') }]);
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
            { key: 'name', vlu: val('ct-name') },
            { key: 'email', vlu: val('ct-email') },
            { key: 'topic', vlu: val('ct-topic') },
            { key: 'message', vlu: val('ct-msg') }
        ]);
        return false;
    }

    function sent() {
        el('ct-msg').value = '';
        el('ct-topic').value = '';
        toast('Message sent');
    }

    function reveal() {
        document.addEventListener('click', function (e) {
            var s = el('ct-sugg');
            if (s && !s.parentElement.contains(e.target)) {
                s.classList.remove('ct-open');
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
        newsletter: newsletter,
        newsletterDone: newsletterDone,
        cat: cat,
        filter: filter,
        filtered: filtered,
        send: send,
        sent: sent
    };
})();

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ContactJs.reveal);
} else {
    ContactJs.reveal();
}
