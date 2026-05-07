import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import StatusBadge from "~/components/StatusBadge.vue";

describe("StatusBadge", () => {
  it("renders draft status", () => {
    const wrapper = mount(StatusBadge, { props: { status: "draft" } });
    expect(wrapper.text()).toBe("草稿");
    expect(wrapper.classes()).toContain("bg-yellow-100");
  });

  it("renders published status", () => {
    const wrapper = mount(StatusBadge, { props: { status: "published" } });
    expect(wrapper.text()).toBe("已发布");
    expect(wrapper.classes()).toContain("bg-green-100");
  });

  it("renders archived status", () => {
    const wrapper = mount(StatusBadge, { props: { status: "archived" } });
    expect(wrapper.text()).toBe("已归档");
    expect(wrapper.classes()).toContain("bg-gray-100");
  });

  it("renders unknown status as raw text", () => {
    const wrapper = mount(StatusBadge, { props: { status: "unknown" } });
    expect(wrapper.text()).toBe("unknown");
    expect(wrapper.classes()).toContain("bg-gray-100");
  });
});
