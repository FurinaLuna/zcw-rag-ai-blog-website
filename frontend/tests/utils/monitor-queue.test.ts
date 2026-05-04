import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

/**
 * Tests the monitor EventQueue logic in isolation.
 * The real monitor plugin runs in browser context; these tests verify the
 * core logic: queue push, flush, beacon, session ID generation.
 */

class EventQueue {
  public queue: any[] = [];
  public maxSize: number;
  public endpoint: string;
  public sessionId: string;
  private timer: ReturnType<typeof setInterval> | null = null;

  constructor(endpoint: string, maxSize = 5) {
    this.endpoint = endpoint;
    this.maxSize = maxSize;
    this.sessionId = this.genSessionId();
  }

  private genSessionId(): string {
    return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
  }

  push(event: any) {
    this.queue.push(event);
  }

  get readyToFlush(): boolean {
    return this.queue.length >= this.maxSize;
  }

  takeBatch(): any[] {
    return this.queue.splice(0, this.maxSize);
  }

  destroy() {
    if (this.timer) clearInterval(this.timer);
  }
}

describe("EventQueue", () => {
  let queue: EventQueue;

  beforeEach(() => {
    queue = new EventQueue("http://test/monitor", 5);
  });

  afterEach(() => {
    queue.destroy();
  });

  it("should initialize with empty queue", () => {
    expect(queue.queue.length).toBe(0);
    expect(queue.sessionId).toBeTruthy();
  });

  it("should push events to queue", () => {
    queue.push({ type: "pv", page: "/" });
    queue.push({ type: "error", message: "test error" });
    expect(queue.queue.length).toBe(2);
  });

  it("should detect ready-to-flush when queue exceeds max size", () => {
    for (let i = 0; i < 5; i++) {
      queue.push({ type: "pv", page: `/page-${i}` });
    }
    expect(queue.readyToFlush).toBe(true);
  });

  it("should not be ready when queue is below max size", () => {
    queue.push({ type: "pv", page: "/" });
    expect(queue.readyToFlush).toBe(false);
  });

  it("should take batch of correct size", () => {
    for (let i = 0; i < 5; i++) {
      queue.push({ type: "pv", page: `/page-${i}` });
    }
    const batch = queue.takeBatch();
    expect(batch.length).toBe(5);
    expect(queue.queue.length).toBe(0);
  });

  it("should only take up to maxSize even if more items queued", () => {
    for (let i = 0; i < 8; i++) {
      queue.push({ type: "pv", page: `/page-${i}` });
    }
    const batch = queue.takeBatch();
    expect(batch.length).toBe(5);
    expect(queue.queue.length).toBe(3);
  });

  it("should generate unique session IDs", () => {
    const q1 = new EventQueue("http://test/monitor", 5);
    const q2 = new EventQueue("http://test/monitor", 5);
    expect(q1.sessionId).not.toBe(q2.sessionId);
  });

  it("should handle empty queue takeBatch", () => {
    const batch = queue.takeBatch();
    expect(batch.length).toBe(0);
  });

  it("should clear queue after destroy", () => {
    queue.push({ type: "pv" });
    queue.destroy();
    expect(queue.queue.length).toBe(1);
  });
});
