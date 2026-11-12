var AdminLoginJs = (function () {

    var choosing = false;

    function el(id) {
        return document.getElementById(id);
    }

    function base() {
        return location.pathname.replace(/[^\/]*$/, '');
    }

    function go() {
        el('lg-err').textContent = '';
        var list = [{ key: 'luser', vlu: el('lg-user').value.trim() }, { key: 'lpass', vlu: el('lg-pass').value }];
        if (choosing) {
            list.push({ key: 'lnew', vlu: el('lg-new').value });
            list.push({ key: 'lnew2', vlu: el('lg-new2').value });
            $ApiRequest('AdminLogin/SetPassword', JSON.stringify(list));
        } else {
            $ApiRequest('AdminLogin/SignIn', JSON.stringify(list));
        }
        return false;
    }

    function choose() {
        choosing = true;
        el('lg-choose').hidden = false;
        el('lg-go').textContent = 'Save and sign in';
        el('lg-new').focus();
    }

    function signedIn(tok) {
        document.cookie = 'ms_tok=' + tok + '; path=' + base() + '; samesite=lax';
        location.href = 'Admin';
    }

    function reveal() {
        var u = el('lg-user');
        if (u && !u.value) {
            u.focus();
        }
    }

    return {
        reveal: reveal,
        go: go,
        choose: choose,
        signedIn: signedIn
    };
})();

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', AdminLoginJs.reveal);
} else {
    AdminLoginJs.reveal();
}
