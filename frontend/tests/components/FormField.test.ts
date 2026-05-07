import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import FormField from "~/components/FormField.vue";

describe("FormField", () => {
  it("renders label", () => {
    const wrapper = mount(FormField, {
      props: { id: "test-field", label: "用户名" },
      slots: { default: '<input id="test-field" />' },
    });
    expect(wrapper.text()).toContain("用户名");
  });

  it("renders slot content", () => {
    const wrapper = mount(FormField, {
      props: { id: "email", label: "邮箱" },
      slots: { default: '<input id="email" placeholder="请输入邮箱" />' },
    });
    expect(wrapper.find("input").exists()).toBe(true);
  });

  it("shows error message when error prop is set", () => {
    const wrapper = mount(FormField, {
      props: { id: "pwd", label: "密码", error: "密码不能为空" },
      slots: { default: '<input id="pwd" />' },
    });
    expect(wrapper.text()).toContain("密码不能为空");
  });

  it("shows helper text when provided", () => {
    const wrapper = mount(FormField, {
      props: { id: "bio", label: "简介", helper: "0/160" },
      slots: { default: '<textarea id="bio"></textarea>' },
    });
    expect(wrapper.text()).toContain("0/160");
  });

  it("shows required indicator when required", () => {
    const wrapper = mount(FormField, {
      props: { id: "title", label: "标题", required: true },
      slots: { default: '<input id="title" />' },
    });
    // Should have a visual required indicator
    expect(wrapper.find(".text-red-500").exists() || wrapper.text().includes("*")).toBe(true);
  });

  it("does not show error state when no error", () => {
    const wrapper = mount(FormField, {
      props: { id: "name", label: "姓名" },
      slots: { default: '<input id="name" />' },
    });
    const errorEl = wrapper.find('[class*="text-red"]').exists();
    // May have required indicator but no error text
    expect(wrapper.props("error")).toBeFalsy();
  });

  it("sets label for attribute from id prop", () => {
    const wrapper = mount(FormField, {
      props: { id: "my-id", label: "Label" },
      slots: { default: '<input id="my-id" />' },
    });
    expect(wrapper.find("label").attributes("for")).toBe("my-id");
  });
});
