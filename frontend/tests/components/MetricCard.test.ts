import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import MetricCard from "~/components/MetricCard.vue";

describe("MetricCard", () => {
  it("renders label and value", () => {
    const wrapper = mount(MetricCard, {
      props: { label: "文章数", value: 42 },
    });
    expect(wrapper.text()).toContain("文章数");
    expect(wrapper.text()).toContain("42");
  });

  it("renders -- for null value", () => {
    const wrapper = mount(MetricCard, {
      props: { label: "PV", value: null },
    });
    expect(wrapper.text()).toContain("--");
  });

  it("renders -- for undefined value", () => {
    const wrapper = mount(MetricCard, {
      props: { label: "UV", value: undefined as unknown as string },
    });
    expect(wrapper.text()).toContain("--");
  });

  it("converts number to string", () => {
    const wrapper = mount(MetricCard, {
      props: { label: "Count", value: 0 },
    });
    expect(wrapper.text()).toContain("0");
  });

  it("renders string value as-is", () => {
    const wrapper = mount(MetricCard, {
      props: { label: "Status", value: "Healthy" },
    });
    expect(wrapper.text()).toContain("Healthy");
  });

  it("has correct container classes", () => {
    const wrapper = mount(MetricCard, {
      props: { label: "Test", value: 1 },
    });
    expect(wrapper.classes()).toContain("rounded-lg");
    expect(wrapper.classes()).toContain("bg-bg-surface");
  });
});
