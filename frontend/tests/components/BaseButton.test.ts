import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import BaseButton from "~/components/BaseButton.vue";

describe("BaseButton", () => {
  it("renders with default props", () => {
    const wrapper = mount(BaseButton, { slots: { default: "点击" } });
    expect(wrapper.text()).toBe("点击");
    expect(wrapper.attributes("type")).toBe("submit");
  });

  it("respects the type prop", () => {
    const wrapper = mount(BaseButton, {
      props: { type: "button" },
      slots: { default: "Click" },
    });
    expect(wrapper.attributes("type")).toBe("button");
  });

  it("disables button when disabled prop is true", () => {
    const wrapper = mount(BaseButton, {
      props: { disabled: true },
      slots: { default: "不能点" },
    });
    const btn = wrapper.find("button");
    expect(btn.attributes("disabled")).toBeDefined();
  });

  it("disables button when loading prop is true", () => {
    const wrapper = mount(BaseButton, {
      props: { loading: true },
      slots: { default: "加载中" },
    });
    const btn = wrapper.find("button");
    expect(btn.attributes("disabled")).toBeDefined();
    expect(wrapper.find("span[aria-busy]").exists()).toBe(false);
  });

  it("shows loading spinner when loading", () => {
    const wrapper = mount(BaseButton, {
      props: { loading: true },
      slots: { default: "加载" },
    });
    expect(wrapper.find(".animate-spin").exists()).toBe(true);
  });

  it("applies block class when block is true", () => {
    const wrapper = mount(BaseButton, {
      props: { block: true },
      slots: { default: "全宽" },
    });
    expect(wrapper.classes()).toContain("w-full");
  });

  it("applies primary variant styles by default", () => {
    const wrapper = mount(BaseButton, {
      slots: { default: "主按钮" },
    });
    expect(wrapper.classes()).toContain("bg-accent");
  });

  it("applies secondary variant styles", () => {
    const wrapper = mount(BaseButton, {
      props: { variant: "secondary" },
      slots: { default: "次要" },
    });
    expect(wrapper.classes()).toContain("border");
  });

  it("applies danger variant styles", () => {
    const wrapper = mount(BaseButton, {
      props: { variant: "danger" },
      slots: { default: "危险" },
    });
    expect(wrapper.classes()).toContain("text-red-600");
  });

  it("applies ghost variant styles", () => {
    const wrapper = mount(BaseButton, {
      props: { variant: "ghost" },
      slots: { default: "幽灵" },
    });
    expect(wrapper.classes()).toContain("text-text-secondary");
  });

  it("sets aria-label when provided", () => {
    const wrapper = mount(BaseButton, {
      props: { ariaLabel: "关闭弹窗" },
      slots: { default: "X" },
    });
    expect(wrapper.attributes("aria-label")).toBe("关闭弹窗");
  });

  it("sets aria-busy when loading", () => {
    const wrapper = mount(BaseButton, {
      props: { loading: true },
      slots: { default: "加载" },
    });
    expect(wrapper.attributes("aria-busy")).toBe("true");
  });

  it("applies size styles", () => {
    const sm = mount(BaseButton, { props: { size: "sm" }, slots: { default: "S" } });
    expect(sm.attributes("style")).toContain("height: 32px");

    const lg = mount(BaseButton, { props: { size: "lg" }, slots: { default: "L" } });
    expect(lg.attributes("style")).toContain("height: 48px");
  });
});
