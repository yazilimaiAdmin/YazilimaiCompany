let timer;

window.startPing = function (dotnetHelper) {
    timer = setInterval(function () {
        dotnetHelper.invokeMethodAsync('PingServer');
    }, 60000); // Ping every minute
}

window.stopPing = function () {
    clearInterval(timer);
}
