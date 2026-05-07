import { describe, it, expect, vi } from "vitest";
import { mount } from "@vue/test-utils";
import BackToTop from "~/components/BackToTop.client.vue";

describe("BackToTop", () => {
  it("is hidden when scrollY <= 400", () => {
    window.scrollY = 0;
    const wrapper = mount(BackToTop);
    expect(wrapper.find("button").attributes("style")).toContain("display: none");
  });

  it("is visible when scrollY > 400", async () => {
    window.scrollY = 500;
    const wrapper = mount(BackToTop);
    window.dispatchEvent(new Event("scroll"));
    await wrapper.vm.$nextTick();
    expect(wrapper.find("button").attributes("style")).toBeFalsy();
  });

  it("has correct aria-label", () => {
    const wrapper = mount(BackToTop);
    expect(wrapper.attributes("aria-label")).toBe("回到顶部");
  });

  it("calls window.scrollTo on click", async () => {
    const scrollTo = vi.fn();
    window.scrollTo = scrollTo;
    window.scrollY = 500;
    const wrapper = mount(BackToTop);
    window.dispatchEvent(new Event("scroll"));
    await wrapper.vm.$nextTick();
    await wrapper.trigger("click");
    expect(scrollTo).toHaveBeenCalledWith({ top: 0, behavior: "smooth" });
  });

  it("renders SVG icon", () => {
    const wrapper = mount(BackToTop);
    expect(wrapper.find("svg").exists()).toBe(true);
  });
});
