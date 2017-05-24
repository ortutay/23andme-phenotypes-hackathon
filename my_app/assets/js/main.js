'use strict';

// Base initializers
(function() {
    MY_APP.consoleMessage();
})();


// Run all MY_APP ready queued callbacks
(function() {
    window.MY_APP._callbacks.forEach(function(callback) {
        callback();
    });
})();
