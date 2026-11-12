var AdminAccountJs = (function () {

    function el(id) {
        return document.getElementById(id);
    }

    function api(method, list) {
        list = list || [];
        list.push({ key: 'tok', vlu: AdminJs.tok() });
        $ApiRequest('AdminAccount/' + method, JSON.stringify(list));
    }

    function expired() {
        AdminJs.expired();
    }

    function loaded(demo) {
        el('ac-go').disabled = demo;
    }

    function change() {
        el('ac-err').textContent = '';
        api('ChangePassword', [{ key: 'acur', vlu: el('ac-cur').value }, { key: 'anew', vlu: el('ac-new').value }, { key: 'anew2', vlu: el('ac-new2').value }]);
        return false;
    }

    function changed() {
        el('ac-cur').value = '';
        el('ac-new').value = '';
        el('ac-new2').value = '';
        AdminJs.toast('Your password is changed.');
    }

    function shown() {
        api('Load');
    }

    function reveal() {
        api('Load');
    }

    return {
        reveal: reveal,
        shown: shown,
        expired: expired,
        loaded: loaded,
        change: change,
        changed: changed
    };
})();

if (!window.AdminJs) {
    location.replace('Admin?p=AdminAccount');
} else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', AdminAccountJs.reveal);
} else {
    AdminAccountJs.reveal();
}
