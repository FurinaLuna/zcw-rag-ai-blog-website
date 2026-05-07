import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import Skeleton from "~/components/Skeleton.vue";

describe("Skeleton", () => {
  it("renders block variant by default", () => {
    const wrapper = mount(Skeleton);
    expect(wrapper.find(".animate-pulse").exists()).toBe(true);
    expect(wrapper.find(".rounded.bg-gray-200").exists()).toBe(true);
  });

  it("renders card variant with correct structure", () => {
    const wrapper = mount(Skeleton, { props: { variant: "card" } });
    expect(wrapper.find(".rounded-lg").exists()).toBe(true);
    expect(wrapper.find(".border-gray-100").exists()).toBe(true);
  });

  it("renders text variant with lines", () => {
    const wrapper = mount(Skeleton, {
      props: { variant: "text", lines: 5 },
    });
    const bars = wrapper.findAll(".h-4");
    expect(bars.length).toBe(5);
  });

  it("respects custom width", () => {
    const wrapper = mount(Skeleton, {
      props: { width: "50%" },
    });
    const inner = wrapper.find(".rounded.bg-gray-200");
    expect(inner.attributes("style")).toContain("width: 50%");
  });

  it("respects custom height", () => {
    const wrapper = mount(Skeleton, {
      props: { height: "3rem" },
    });
    const inner = wrapper.find(".rounded.bg-gray-200");
    expect(inner.attributes("style")).toContain("height: 3rem");
  });

  it("renders avatar variant", () => {
    const wrapper = mount(Skeleton, {
      props: { variant: "avatar", size: "48px" },
    });
    const avatar = wrapper.find(".rounded-full");
    expect(avatar.exists()).toBe(true);
    expect(avatar.attributes("style")).toContain("width: 48px");
  });

  it("renders text lines with 3 lines by default", () => {
    const wrapper = mount(Skeleton, {
      props: { variant: "text" },
    });
    const bars = wrapper.findAll(".h-4");
    expect(bars.length).toBe(3);
  });
});
