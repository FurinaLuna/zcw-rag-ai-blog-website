export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig();
  const endpoint = config.public.monitorEndpoint as string;

  class EventQueue {
    private queue: any[] = [];
    private maxSize = 20;
    private flushInterval = 5000;
    private timer: ReturnType<typeof setTimeout> | null = null;
    private sessionId: string;

    constructor() {
      this.sessionId = this.getSessionId();
      this.timer = setInterval(() => this.flush(), this.flushInterval);
      window.addEventListener("beforeunload", () => this.flushBeacon());
      window.addEventListener("visibilitychange", () => {
        if (document.visibilityState === "hidden") this.flushBeacon();
      });
    }

    private getSessionId(): string {
      let sid = sessionStorage.getItem("_monitor_sid");
      if (!sid) {
        sid = `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
        sessionStorage.setItem("_monitor_sid", sid);
      }
      return sid;
    }

    push(event: any) {
      this.queue.push(event);
      if (this.queue.length >= this.maxSize) this.flush();
    }

    async flush() {
      if (this.queue.length === 0) return;
      const events = this.queue.splice(0, this.maxSize);
      try {
        await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ events }),
          keepalive: true,
        });
      } catch {}
    }

    flushBeacon() {
      if (this.queue.length === 0) return;
      const blob = new Blob(
        [JSON.stringify({ events: [...this.queue] })],
        { type: "application/json" }
      );
      navigator.sendBeacon(endpoint, blob);
      this.queue = [];
    }

    destroy() {
      if (this.timer) clearInterval(this.timer);
      this.flush();
    }
  }

  const queue = new EventQueue();

  function report(type: string, data: Record<string, any> = {}) {
    queue.push({
      event_type: type,
      page_url: window.location.pathname,
      event_data: data,
      session_id: queue["sessionId"],
    });
  }

  // PV collector
  let lastPage = window.location.pathname;
  report("pv", { referrer: document.referrer });

  const router = useRouter();
  router.afterEach((to) => {
    if (to.path !== lastPage) {
      lastPage = to.path;
      report("pv", { referrer: document.referrer });
    }
  });

  // Error collector
  window.addEventListener("error", (e) => {
    report("error", {
      error_type: "js_error",
      message: e.message,
      filename: e.filename,
      lineno: e.lineno,
      colno: e.colno,
      stack: e.error?.stack?.slice(0, 500),
    });
  });

  window.addEventListener("unhandledrejection", (e) => {
    report("error", {
      error_type: "promise_error",
      message: e.reason?.message || String(e.reason),
      stack: e.reason?.stack?.slice(0, 500),
    });
  });

  // Web Vitals collector
  import("web-vitals").then(({ onLCP, onCLS, onINP, onFCP, onTTFB }) => {
    onLCP(({ value, rating }) => report("web_vital", { metric: "LCP", value, rating }));
    onCLS(({ value, rating }) => report("web_vital", { metric: "CLS", value, rating }));
    onINP(({ value, rating }) => report("web_vital", { metric: "INP", value, rating }));
    onFCP(({ value, rating }) => report("web_vital", { metric: "FCP", value, rating }));
    onTTFB(({ value, rating }) => report("web_vital", { metric: "TTFB", value, rating }));
  }).catch(() => {});

  return {
    provide: {
      monitor: { report },
    },
  };
});
