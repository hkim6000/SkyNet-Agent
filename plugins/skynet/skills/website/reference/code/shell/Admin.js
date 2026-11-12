var AdminJs = (function () {

    var TOK = 'ms_tok';
    var current = '';
    var ttimer = null;
    var waiting = {};

    function el(id) {
        return document.getElementById(id);
    }

    function base() {
        return location.pathname.replace(/[^\/]*$/, '');
    }

    function tok() {
        var m = document.cookie.match(new RegExp('(?:^|; )' + TOK + '=([^;]*)'));
        return m ? decodeURIComponent(m[1]) : '';
    }

    function api(method, list) {
        list = list || [];
        list.push({ key: 'tok', vlu: tok() });
        $ApiRequest('Admin/' + method, JSON.stringify(list));
    }

    function panel(p) {
        return el('db-p-' + p);
    }

    function mark(p) {
        Array.prototype.forEach.call(document.querySelectorAll('#db-menu .db-mi'), function (a) {
            var on = a.getAttribute('data-p') === p;
            a.classList.toggle('db-on', on);
            if (on) {
                a.setAttribute('aria-current', 'page');
                document.title = a.textContent.replace(/\d+$/, '').trim() + ' | Staff';
            } else {
                a.removeAttribute('aria-current');
            }
        });
    }

    function show(p) {
        Array.prototype.forEach.call(document.querySelectorAll('#db-content .db-panel'), function (x) {
            x.hidden = x.id !== 'db-p-' + p;
        });
    }

    function open(p, push) {
        if (!/^Admin[A-Za-z]{1,40}$/.test(p || '')) {
            p = 'AdminHome';
        }
        closeMenu();
        if (push && p !== current) {
            history.pushState({ p: p }, '', 'Admin?p=' + p);
        }
        current = p;
        mark(p);
        var box = panel(p);
        if (box) {
            show(p);
            var js = window[p + 'Js'];
            if (js && js.shown) {
                js.shown();
            }
            api('Menu', [{ key: 'pg', vlu: p }]);
            window.scrollTo(0, 0);
            return;
        }
        box = document.createElement('section');
        box.className = 'db-panel';
        box.id = 'db-p-' + p;
        box.innerHTML = '<div class="db-loading">Loading</div>';
        el('db-content').appendChild(box);
        show(p);
        waiting[p] = true;
        api('Open', [{ key: 'pg', vlu: p }]);
        window.scrollTo(0, 0);
    }

    function opened(p) {
        delete waiting[p];
        mark(current);
    }

    function refused(p) {
        var box = panel(p);
        if (box) {
            box.parentNode.removeChild(box);
        }
        toast('You do not have access to that page.');
        open('AdminHome', true);
    }

    function go(e, p) {
        if (e && (e.ctrlKey || e.metaKey || e.shiftKey || e.button === 1)) {
            return true;
        }
        if (e) {
            e.preventDefault();
        }
        open(p, true);
        return false;
    }

    function refresh() {
        api('Menu', [{ key: 'pg', vlu: current }]);
    }

    function expired() {
        document.cookie = TOK + '=; path=' + base() + '; max-age=0';
        location.href = 'AdminLogin';
    }

    function signout() {
        api('SignOut');
    }

    function toast(msg) {
        var t = el('db-toast');
        t.textContent = msg;
        t.classList.add('db-open');
        clearTimeout(ttimer);
        ttimer = setTimeout(function () {
            t.classList.remove('db-open');
        }, 3400);
    }

    function openMenu() {
        el('db-rail').classList.add('db-open');
        el('db-scrim').classList.add('db-open');
    }

    function closeMenu() {
        el('db-rail').classList.remove('db-open');
        el('db-scrim').classList.remove('db-open');
    }

    function reveal() {
        if (!tok()) {
            expired();
            return;
        }
        el('db-menu').addEventListener('click', function (e) {
            var a = e.target.closest ? e.target.closest('a[data-p]') : null;
            if (a) {
                go(e, a.getAttribute('data-p'));
            }
        });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                closeMenu();
            }
        });
        window.addEventListener('popstate', function (e) {
            var p = e.state && e.state.p ? e.state.p : (new URLSearchParams(location.search).get('p') || 'AdminHome');
            open(p, false);
        });
        var start = el('db-site').getAttribute('data-start') || 'AdminHome';
        history.replaceState({ p: start }, '', 'Admin?p=' + start);
        open(start, false);
    }

    return {
        reveal: reveal,
        open: function (p) { open(p, true); },
        opened: opened,
        refused: refused,
        go: go,
        refresh: refresh,
        current: function () { return current; },
        tok: tok,
        expired: expired,
        signout: signout,
        toast: toast,
        openMenu: openMenu,
        closeMenu: closeMenu
    };
})();

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', AdminJs.reveal);
} else {
    AdminJs.reveal();
}
