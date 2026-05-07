import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import DataTable from "~/components/DataTable.vue";

const columns = [
  { key: "title", label: "标题" },
  { key: "status", label: "状态", align: "right" as const },
];

const rows = [
  { title: "文章1", status: "已发布" },
  { title: "文章2", status: "草稿" },
];

describe("DataTable", () => {
  it("renders table headers", () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows },
    });
    expect(wrapper.text()).toContain("标题");
    expect(wrapper.text()).toContain("状态");
  });

  it("renders table rows", () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows },
    });
    expect(wrapper.text()).toContain("文章1");
    expect(wrapper.text()).toContain("已发布");
  });

  it("does not render table when loading is true", () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows: [], loading: true },
    });
    expect(wrapper.find("table").exists()).toBe(false);
  });

  it("does not render table when error is set", () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows: [], error: "出错了" },
    });
    expect(wrapper.find("table").exists()).toBe(false);
    expect(wrapper.text()).toContain("出错了");
  });

  it("renders error state", () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows: [], error: "加载失败" },
    });
    expect(wrapper.text()).toContain("加载失败");
  });

  it("renders error with custom message", () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows: [], error: "自定义错误" },
    });
    expect(wrapper.text()).toContain("自定义错误");
  });

  it("renders empty state", () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows: [], empty: true, emptyText: "暂无数据" },
    });
    expect(wrapper.text()).toContain("暂无数据");
  });

  it("renders dense mode with smaller text", () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows, dense: true },
    });
    expect(wrapper.find("table").classes()).toContain("text-xs");
  });

  it("applies right align class", () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows },
    });
    const headers = wrapper.findAll("th");
    const rightCol = headers[1]!;
    expect(rightCol.classes()).toContain("text-right");
  });
});
