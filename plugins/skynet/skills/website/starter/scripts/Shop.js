var ShopJs = (function () {

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
        $ApiRequest('Shop/' + method, JSON.stringify(list || []));
    }

    function toast(msg) {
        var t = el('sh-toast');
        t.textContent = msg;
        t.classList.add('sh-open');
        clearTimeout(ttimer);
        ttimer = setTimeout(function () {
            t.classList.remove('sh-open');
        }, 3000);
    }

    function openNav() {
        el('sh-nav').classList.add('sh-open');
        el('sh-scrim').classList.add('sh-open');
    }

    function closeNav() {
        el('sh-nav').classList.remove('sh-open');
        el('sh-scrim').classList.remove('sh-open');
    }

    function search(value) {
        var v = (value || '').trim();
        clearTimeout(timer);
        if (v.length < 2) {
            el('sh-sugg').classList.remove('sh-open');
            return;
        }
        timer = setTimeout(function () {
            call('Suggest', [{ key: 'term', vlu: v }]);
        }, 250);
    }

    function openSugg() {
        el('sh-sugg').classList.add('sh-open');
    }

    function newsletter() {
        call('Newsletter', [{ key: 'email', vlu: val('sh-nl-email') }]);
        return false;
    }

    function newsletterDone() {
        el('sh-nl-email').value = '';
        toast('Thanks for signing up');
    }

    function cat(c) {
        el('sh-cat').value = c;
        filter();
    }

    function filter() {
        call('Filter', [{ key: 'cat', vlu: val('sh-cat') }, { key: 'order', vlu: val('sh-sort') }]);
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
            { key: 'name', vlu: val('sh-name') },
            { key: 'email', vlu: val('sh-email') },
            { key: 'topic', vlu: val('sh-topic') },
            { key: 'message', vlu: val('sh-msg') }
        ]);
        return false;
    }

    function sent() {
        el('sh-msg').value = '';
        el('sh-topic').value = '';
        toast('Message sent');
    }

    function reveal() {
        document.addEventListener('click', function (e) {
            var s = el('sh-sugg');
            if (s && !s.parentElement.contains(e.target)) {
                s.classList.remove('sh-open');
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
    document.addEventListener('DOMContentLoaded', ShopJs.reveal);
} else {
    ShopJs.reveal();
}
