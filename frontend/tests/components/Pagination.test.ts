import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import Pagination from "~/components/Pagination.vue";

describe("Pagination", () => {
  it("does not render when totalPages is 1", () => {
    const wrapper = mount(Pagination, {
      props: { current: 1, totalPages: 1 },
    });
    expect(wrapper.find("nav").exists()).toBe(false);
  });

  it("does not render when totalPages is 0", () => {
    const wrapper = mount(Pagination, {
      props: { current: 1, totalPages: 0 },
    });
    expect(wrapper.find("nav").exists()).toBe(false);
  });

  it("renders page numbers", () => {
    const wrapper = mount(Pagination, {
      props: { current: 1, totalPages: 5 },
    });
    const buttons = wrapper.findAll("button");
    // Prev + 5 pages + Next = 7 buttons
    expect(buttons.length).toBe(7);
  });

  it("highlights current page", () => {
    const wrapper = mount(Pagination, {
      props: { current: 3, totalPages: 5 },
    });
    const currentBtn = wrapper.find('button[aria-current="page"]');
    expect(currentBtn.exists()).toBe(true);
    expect(currentBtn.text()).toBe("3");
  });

  it("disables previous button on first page", () => {
    const wrapper = mount(Pagination, {
      props: { current: 1, totalPages: 5 },
    });
    const buttons = wrapper.findAll("button");
    const prevBtn = buttons[0]!;
    expect(prevBtn.attributes("disabled")).toBeDefined();
    expect(prevBtn.attributes("aria-label")).toBe("上一页");
  });

  it("disables next button on last page", () => {
    const wrapper = mount(Pagination, {
      props: { current: 5, totalPages: 5 },
    });
    const buttons = wrapper.findAll("button");
    const nextBtn = buttons[buttons.length - 1]!;
    expect(nextBtn.attributes("disabled")).toBeDefined();
    expect(nextBtn.attributes("aria-label")).toBe("下一页");
  });

  it("emits change event with page number", async () => {
    const wrapper = mount(Pagination, {
      props: { current: 3, totalPages: 5 },
    });
    // Click page 2
    const page2 = wrapper.findAll("button").find(b => b.text() === "2");
    await page2!.trigger("click");
    expect(wrapper.emitted("change")).toBeTruthy();
    expect(wrapper.emitted("change")![0]).toEqual([2]);
  });

  it("emits change for next button", async () => {
    const wrapper = mount(Pagination, {
      props: { current: 2, totalPages: 5 },
    });
    const nextBtn = wrapper.find('button[aria-label="下一页"]');
    await nextBtn.trigger("click");
    expect(wrapper.emitted("change")![0]).toEqual([3]);
  });

  it("emits change for previous button", async () => {
    const wrapper = mount(Pagination, {
      props: { current: 3, totalPages: 5 },
    });
    const prevBtn = wrapper.find('button[aria-label="上一页"]');
    await prevBtn.trigger("click");
    expect(wrapper.emitted("change")![0]).toEqual([2]);
  });

  it("respects maxVisible prop for many pages", () => {
    const wrapper = mount(Pagination, {
      props: { current: 5, totalPages: 50, maxVisible: 5 },
    });
    // Should have prev + 5 visible + next = 7 buttons total
    const buttons = wrapper.findAll("button");
    expect(buttons.length).toBeLessThanOrEqual(7);
  });

  it("has correct aria attributes", () => {
    const wrapper = mount(Pagination, {
      props: { current: 1, totalPages: 5 },
    });
    const nav = wrapper.find("nav");
    expect(nav.attributes("aria-label")).toBe("分页");
  });
});
