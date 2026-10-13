var HomeJs = (function () {

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
        $ApiRequest('Home/' + method, JSON.stringify(list || []));
    }

    function toast(msg) {
        var t = el('hm-toast');
        t.textContent = msg;
        t.classList.add('hm-open');
        clearTimeout(ttimer);
        ttimer = setTimeout(function () {
            t.classList.remove('hm-open');
        }, 3000);
    }

    function openNav() {
        el('hm-nav').classList.add('hm-open');
        el('hm-scrim').classList.add('hm-open');
    }

    function closeNav() {
        el('hm-nav').classList.remove('hm-open');
        el('hm-scrim').classList.remove('hm-open');
    }

    function search(value) {
        var v = (value || '').trim();
        clearTimeout(timer);
        if (v.length < 2) {
            el('hm-sugg').classList.remove('hm-open');
            return;
        }
        timer = setTimeout(function () {
            call('Suggest', [{ key: 'term', vlu: v }]);
        }, 250);
    }

    function openSugg() {
        el('hm-sugg').classList.add('hm-open');
    }

    function newsletter() {
        call('Newsletter', [{ key: 'email', vlu: val('hm-nl-email') }]);
        return false;
    }

    function newsletterDone() {
        el('hm-nl-email').value = '';
        toast('Thanks for signing up');
    }

    function cat(c) {
        el('hm-cat').value = c;
        filter();
    }

    function filter() {
        call('Filter', [{ key: 'cat', vlu: val('hm-cat') }, { key: 'order', vlu: val('hm-sort') }]);
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
            { key: 'name', vlu: val('hm-name') },
            { key: 'email', vlu: val('hm-email') },
            { key: 'topic', vlu: val('hm-topic') },
            { key: 'message', vlu: val('hm-msg') }
        ]);
        return false;
    }

    function sent() {
        el('hm-msg').value = '';
        el('hm-topic').value = '';
        toast('Message sent');
    }

    function reveal() {
        document.addEventListener('click', function (e) {
            var s = el('hm-sugg');
            if (s && !s.parentElement.contains(e.target)) {
                s.classList.remove('hm-open');
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
    document.addEventListener('DOMContentLoaded', HomeJs.reveal);
} else {
    HomeJs.reveal();
}
