var AdminHomeJs = (function () {

    function api(method, list) {
        list = list || [];
        list.push({ key: 'tok', vlu: AdminJs.tok() });
        $ApiRequest('AdminHome/' + method, JSON.stringify(list));
    }

    function expired() {
        AdminJs.expired();
    }

    function go(e, p) {
        return AdminJs.go(e, p);
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
        go: go
    };
})();

if (!window.AdminJs) {
    location.replace('Admin?p=AdminHome');
} else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', AdminHomeJs.reveal);
} else {
    AdminHomeJs.reveal();
}
