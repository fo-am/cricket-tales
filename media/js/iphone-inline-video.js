var makeVideoPlayableInline = function() {
    "use strict";
    function e(e) {
        var n = {
            start: function t() {

                if (!n.lastCall) {
                    n.lastCall = Date.now()
                }
                var t = Date.now() - n.lastCall;
                n.id = requestAnimationFrame(n.start);
                n.lastCall = Date.now();
                e(t)
            },
            stop: function r() {
                cancelAnimationFrame(n.id);
                delete n.id;
                delete n.lastCall
            }
        };
        return n
    }

    function n(e, n, t, r) {
        var i = function a(n) {
            var i = t && e[t];
            delete e[t];
            if (Boolean(i) === Boolean(r)) {
                n.stopImmediatePropagation()
            }
        };
        e.addEventListener(n, i, false);
        return {
            forget: function u() {
                return e.removeEventListener(n, i, false)
            }
        }
    }

    function t(e, n, t) {
        Object.defineProperty(e, n, {
            get: function r() {
                return t[n]
            },
            set: function i(e) {
                t[n] = e
            }
        })
    }
    var r = typeof Symbol === "undefined" ? function(e) {
        return "@" + (e ? e : "@") + Math.random().toString(26)
    } : Symbol;
    var i = /iPhone|iPod/i.test(navigator.userAgent);
    var a = r("iiv");
    var u = r("iive");
    var d = r("native-play");
    var o = r("native-pause");

    function s(e) {
        var n = new Audio;
        n.src = e.currentSrc || e.src;
        return n
    }

    function v(e) {
        var n = this;
        var t = void 0;
        if (n.hasAudio) {
            t = n.driver.currentTime
        } else {
            t = n.video.currentTime + e / 1e3
        }
        n.video.currentTime = Math.min(n.video.duration, t);
        if (n.video.ended) {
            n.video.pause();
            return false
        }
    }

    function l() {
        var e = this;
        var n = e[a];
        if (e.webkitDisplayingFullscreen) {
            e[d]();
            return
        }
        if (!e.buffered.length) {
            e.load()
        }
        n.driver.play();
        console.log("play")
        n.updater.start();
        e.dispatchEvent(new Event("play"));
        e.dispatchEvent(new Event("playing"))
    }

    function f() {
        var e = this;
        var n = e[a];
        n.updater.stop();
        n.driver.pause();
        console.log("pause")
        e.dispatchEvent(new Event("pause"));
        if (e.ended) {
            e[u] = true;
            e.dispatchEvent(new Event("ended"))
        }
        if (e.webkitDisplayingFullscreen) {
            e[o]()
        }
    }

    function c(n, t) {
        var r = n[a] = {};
        r.hasAudio = t;
        r.video = n;
        r.updater = e(v.bind(r));
        if (t) {
            r.driver = s(n)
        } else {
            r.driver = {
                muted: true,
                paused: true,
                pause: function i() {
                    r.driver.paused = true
                },
                play: function u() {
                    r.driver.paused = false;
                    if (n.currentTime === n.duration) {
                        n.currentTime = 0
                    }
                }
            }
        }
        n.addEventListener("webkitbeginfullscreen", function() {
            if (!n.paused) {
                n.pause();
                n[d]()
            } else if (t && !r.driver.buffered.length) {
                r.driver.load()
            }
        });
        if (t) {
            n.addEventListener("webkitendfullscreen", function() {
                r.driver.currentTime = r.video.currentTime
            })
        }
    }

    function p(e) {
        var r = e[a];
        e[d] = e.play;
        e[o] = e.pause;
        e.play()
        e.play = l;
        e.pause = f;
        t(e, "paused", r.driver);
        t(e, "muted", r.driver);
        n(e, "seeking");
        n(e, "seeked");
        n(e, "ended", u, false)
    }

    function m(e) {
        var n = arguments.length <= 1 || arguments[1] === undefined ? true : arguments[1];
        var t = arguments.length <= 2 || arguments[2] === undefined ? true : arguments[2];
        if (t && !i) {
            return
        }
        c(e, n);
        p(e);
        if (!n && e.autoplay) {
            e.play()
        }
    }
    return m
}();